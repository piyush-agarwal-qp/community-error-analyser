#!/usr/bin/env python3
"""
error_report.py — Automated 500 error analysis for Communities weekly report.

Reads errors_combined.json (fetched by run_all.py via fetcher.py),
clusters by hash, classifies DC + portal/panel side, and writes error_report.md
with the PDM block and engineering update block.

No AI required — pure rule-based clustering and classification.

Usage:
    python error_report.py --from 2026-06-19 --to 2026-06-25
    python error_report.py --input /path/to/errors_combined.json --from X --to Y
"""

import argparse
import collections
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

# ── DC classification ─────────────────────────────────────────────────────────

def classify_dc(host: str) -> str:
    h = host.lower()
    if "pveu" in h or "onepoll" in h:
        return "EU"
    if h.startswith("qa") or "qaapp" in h or "qaweb" in h or h == "qa11" or "saqa" in h:
        return "QA"
    return "US"


# ── Portal / Panel side classification ───────────────────────────────────────

PORTAL_URL_SIGNALS = {
    "PortalDashBoardAJSHandler", "portal.PortalDashBoard",
    "/a/panel.do", "/a/panelLogin", "/a/panelLogout", "/a/panelSignup",
    "/a/showMemberAccount", "/a/showMemberSurveys", "/a/takePanelPoll",
    "/a/showMemberProfile", "/a/saveMemberProfile", "/a/showMemberRewards",
    "/a/showMemberBadges", "/a/showMemberIdeas", "/a/showMemberDiscussions",
    "/a/showMemberPolls", "/a/memberRedeemReward", "/a/memberIdeaVote",
    "/a/memberTopicReply", "/a/portalHome", "/a/portalContent",
    "/a/showPortalDocuments", "/a/clearPortalNotifications",
    "/a/abuse.do", "/a/usub", "/a/exitSurvey",
    "showPanelMemberDashBoard", "showMemberSurveys", "showRewardTab",
    "showMemberAccount", "framework2AdHocPortal",
}

PANEL_URL_SIGNALS = {
    "showPanelUserReport", "searchSurveyCampaignBatch",
    "panelLanguageTranslationImport", "showDiscussionModeration",
    "showPanelProjectHistory", "showPanelIdeasSetup", "editLanguage",
    "inviteUsers", "twitterSignIn", "showPanelHTMLPages",
    "/a/engagementMetrics", "/a/showDataShare", "/a/router.do",
    "/a/panelAdminLogin", "/a/showExportPanel", "/a/panelMemberFilterSearch",
    "/a/panelAdminEmail", "/a/reminderCount", "/a/panelHealthDashboard",
    "/a/newPanelWizard", "/a/panelDelete", "/a/communityWizard",
    "/a/createCommunity", "/a/bulkMemberImport", "/a/showMemberDetails",
    "/a/deletePanelMember", "/a/bulkDeleteMembers", "/a/searchMember",
    "/a/showMembers", "/a/showOrgUsersPanel",
    "stopBroadcastProcess", "editPanelMember",
}


def classify_side(url: str, st: str) -> str:
    combined = (url or "") + " " + (st or "")
    for sig in PORTAL_URL_SIGNALS:
        if sig.lower() in combined.lower():
            return "portal"
    # Extract referrer from stacktrace
    m = re.search(r'"referer"\s*:\s*"([^"]+)"', st or "")
    ref = m.group(1) if m else ""
    for sig in PORTAL_URL_SIGNALS:
        if sig.lower() in ref.lower():
            return "portal"
    for sig in PANEL_URL_SIGNALS:
        if sig.lower() in ref.lower():
            return "panel"
    for sig in PANEL_URL_SIGNALS:
        if sig.lower() in url.lower():
            return "panel"
    return "other"


# ── Error type extraction ─────────────────────────────────────────────────────

def extract_error_type(st: str) -> str:
    if not st:
        return "unknown"
    # JSP errors: real exception after <BR><BR>
    search = st.split("<BR><BR>", 1)[1] if "<BR><BR>" in st else st
    for line in re.split(r"<BR>|\n", search):
        line = line.strip()
        if not line or line.startswith("at ") or line.startswith("..."):
            continue
        if line.startswith("Caused by:"):
            line = line[len("Caused by:"):].strip()
        return line[:200]
    return st[:200]


def extract_endpoint(url: str, st: str) -> str:
    if url:
        return url
    m = re.search(r"\[(/a/[a-zA-Z0-9/_.\-]+)", st or "")
    if m:
        return m.group(1)
    m = re.search(r"(?:^|\s)(/a/[a-zA-Z0-9/_.\-]+)", st or "")
    return m.group(1) if m else ""


# ── Severity ──────────────────────────────────────────────────────────────────

def classify_severity(count: int, dcs: set, side: str) -> str:
    if "QA" in dcs and len(dcs) == 1:
        return "low"
    if count >= 20 and len(dcs) > 1:
        return "critical"
    if count >= 10:
        return "high"
    if count >= 3:
        return "medium"
    return "low"


# ── Clustering ────────────────────────────────────────────────────────────────

def cluster(rows: list[dict]) -> list[dict]:
    by_hash: dict[str, list] = collections.defaultdict(list)
    for r in rows:
        by_hash[str(r.get("hash", "0"))].append(r)

    clusters = []
    for h, rs in sorted(by_hash.items(), key=lambda x: -len(x[1])):
        dcs   = {classify_dc(r["host"]) for r in rs}
        sides = {classify_side(r.get("url", ""), r.get("st", "")) for r in rs}
        side  = "portal" if "portal" in sides else "panel" if "panel" in sides else "other"
        endpoint = extract_endpoint(rs[0].get("url", ""), rs[0].get("st", ""))
        error_type = extract_error_type(rs[0].get("st", ""))
        count = len(rs)
        clusters.append({
            "hash":       h,
            "count":      count,
            "error_type": error_type,
            "endpoint":   endpoint,
            "dcs":        sorted(dcs),
            "side":       side,
            "severity":   classify_severity(count, dcs, side),
            "hosts":      sorted({r["host"] for r in rs})[:6],
            "ids":        [r["id"] for r in rs[:3]],
            "st":         rs[0].get("st", ""),
        })

    return sorted(clusters, key=lambda c: (
        {"critical": 0, "high": 1, "medium": 2, "low": 3}[c["severity"]], -c["count"]
    ))


# ── Markdown rendering ────────────────────────────────────────────────────────

SEVERITY_EMOJI = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "⚪"}


def render_report(start: str, end: str, clusters: list[dict], total: int) -> str:
    all_dcs = ["US", "EU", "QA"]

    # DC × side breakdown
    dc_summary: dict[str, dict] = {dc: {"portal": 0, "panel": 0, "other": 0} for dc in all_dcs}
    for c in clusters:
        for dc in c["dcs"]:
            if dc in dc_summary:
                dc_summary[dc][c["side"]] += 1

    lines = [
        f"# weekly error report — {start} to {end}",
        "",
        f"**date range:** {start} → {end}",
        f"**total errors:** {total}{'  _(query limit hit — real volume higher)_' if total >= 500 else ''}",
        f"**clusters:** {len(clusters)}",
        "",
        "---",
        "",
        "## summary table",
        "",
        "| # | severity | error type | count | dc | side |",
        "|---|----------|-----------|-------|-----|------|",
    ]

    for i, c in enumerate(clusters, 1):
        et = c["error_type"][:80].replace("|", "\\|")
        lines.append(
            f"| {i} | {c['severity']} | {et} | {c['count']} | {'+'.join(c['dcs'])} | {c['side']} |"
        )

    lines += [
        "",
        "---",
        "",
        "## dc & side breakdown",
        "",
        "| dc | portal | panel | other |",
        "|----|--------|-------|-------|",
    ]
    for dc in all_dcs:
        s = dc_summary[dc]
        if s["portal"] + s["panel"] + s["other"] == 0:
            continue
        lines.append(f"| {dc.lower()} | {s['portal']} | {s['panel']} | {s['other']} |")

    lines += ["", "---", "", "## cluster details", ""]

    for i, c in enumerate(clusters, 1):
        et = c["error_type"][:120]
        st_preview = c["st"][:600].strip() if c["st"] else "(no stacktrace)"
        lines += [
            f"### {i}. {et[:60]} *({c['severity']}, {c['count']} errors)*",
            "",
            f"**dc / side:** {' + '.join(dc.lower() for dc in c['dcs'])} · {c['side']}",
            f"**endpoint:** {c['endpoint'] or '(unknown)'}",
            f"**affected hosts:** {', '.join(c['hosts'])}",
            f"**error ids (sample):** {', '.join(str(x) for x in c['ids'])} *({c['count']} total)*",
            "",
            "**stack trace:**",
            "```",
            st_preview,
            "```",
            "",
            "---",
            "",
        ]

    # PDM block
    us = dc_summary["US"]
    eu = dc_summary["EU"]
    qa = dc_summary["QA"]
    pdm = "\n".join([
        f"{total} errors logged ({start} → {end})",
        "",
        f"us dc — {us['panel']} panel, {us['portal']} portal",
        f"eu dc — {eu['panel']} panel, {eu['portal']} portal",
    ])
    if qa["panel"] + qa["portal"] + qa["other"] > 0:
        pdm += f"\nqa    — {qa['panel']} panel, {qa['portal']} portal  (non-production)"

    lines += [
        "## pdm report",
        "",
        "```",
        pdm,
        "```",
        "",
        "---",
        "",
    ]

    # Engineering update
    prod_clusters = [c for c in clusters
                     if not (c["dcs"] == ["QA"])
                     and (c["count"] >= 5 or c["severity"] in ("critical", "high"))]
    eng_header = (
        f"{total} errors | "
        f"panel-{us['panel']}, portal-{us['portal']} (us) | "
        f"panel-{eu['panel']}, portal-{eu['portal']} (eu)"
    )
    eng_bullets = []
    for c in prod_clusters:
        et = c["error_type"].lower()[:80]
        ep = c["endpoint"] or "unknown endpoint"
        eng_bullets.append(f"~ {c['count']:<4}: {et} — {ep}")

    lines += [
        "## engineering update",
        "",
        "```",
        eng_header,
        "",
        *eng_bullets,
        "```",
    ]

    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main(start_date: str = None, end_date: str = None,
         input_file: str = None, output_dir: Path = None) -> dict:

    if not start_date or not end_date:
        today = date.today()
        days_back = (today.weekday() - 3) % 7 or 7
        last_thursday = today - timedelta(days=days_back)
        last_friday = last_thursday - timedelta(days=6)
        start_date, end_date = str(last_friday), str(last_thursday)

    if output_dir is None:
        output_dir = SCRIPT_DIR / "reports" / f"{start_date}_to_{end_date}"

    if input_file is None:
        input_file = output_dir / "errors_combined.json"

    if not Path(input_file).exists():
        print(f"[errors] {input_file} not found — run fetcher first", file=sys.stderr)
        return {"module": "errors", "status": "error", "error": "no input file"}

    print(f"[errors] reading {input_file}")
    data = json.loads(Path(input_file).read_text())
    rows = data.get("rows", [])
    print(f"[errors] {len(rows)} rows → clustering...")

    clusters = cluster(rows)
    print(f"[errors] {len(clusters)} clusters found")

    md = render_report(start_date, end_date, clusters, len(rows))

    output_dir.mkdir(parents=True, exist_ok=True)
    md_file = output_dir / "error_report.md"
    md_file.write_text(md)
    print(f"[errors] saved → {md_file}")

    # DC counts for assembler
    all_dcs = ["US", "EU", "QA"]
    dc_summary: dict[str, dict] = {dc: {"portal": 0, "panel": 0, "other": 0} for dc in all_dcs}
    for c in clusters:
        for dc in c["dcs"]:
            if dc in dc_summary:
                dc_summary[dc][c["side"]] += 1

    return {
        "module": "errors",
        "status": "ok",
        "md": str(md_file),
        "dc_summary": dc_summary,
        "cluster_count": len(clusters),
        "total": len(rows),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated 500 error analysis")
    parser.add_argument("--from",  dest="date_from", help="Start date YYYY-MM-DD")
    parser.add_argument("--to",    dest="date_to",   help="End date YYYY-MM-DD")
    parser.add_argument("--input", help="Path to errors_combined.json")
    args = parser.parse_args()
    main(start_date=args.date_from, end_date=args.date_to, input_file=args.input)
