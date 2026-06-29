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

# Allow running as `python3 modules/error_report.py` directly
_pkg_root = str(Path(__file__).parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from lib.utils import ROOT, get_week_range

SAMPLE_IDS = 5   # how many sample error IDs to show per cluster


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
    # admin console management pages
    "showPanelManagement", "showPanelDashboard", "showPanelSettings",
    "showQPointInventory", "showQPointHistory", "showImageLibrary",
    "renameUserFile", "deleteUserFile", "uploadUserFile",
    "showPanelReports", "showPanelActivityLog", "showPanelEmailLog",
}


def _extract_referer(st: str) -> str:
    """Extract referer from either JSON format or classic Referrer [...] format."""
    # AJSServlet JSON headers
    m = re.search(r'"referer"\s*:\s*"([^"]+)"', st or "")
    if m:
        return m.group(1)
    # Classic format: Referrer [https://...]
    m = re.search(r'Referrer \[([^\]]+)\]', st or "")
    return m.group(1) if m else ""


def classify_side(url: str, st: str) -> str:
    combined = (url or "") + " " + (st or "")
    # Portal signals checked against everything (url + full stacktrace)
    for sig in PORTAL_URL_SIGNALS:
        if sig.lower() in combined.lower():
            return "portal"
    # Panel signals also checked against full stacktrace (endpoint is in st body)
    for sig in PANEL_URL_SIGNALS:
        if sig.lower() in combined.lower():
            return "panel"
    # Referer-based check (catches cases where endpoint isn't in st body)
    ref = _extract_referer(st or "")
    for sig in PORTAL_URL_SIGNALS:
        if sig.lower() in ref.lower():
            return "portal"
    for sig in PANEL_URL_SIGNALS:
        if sig.lower() in ref.lower():
            return "panel"
    return "other"


# ── Error extraction ──────────────────────────────────────────────────────────

def extract_root_cause(st: str) -> str:
    """Follow Caused by: chain to get the deepest root cause exception."""
    if not st:
        return "unknown"

    # Split on <BR><BR> to get past the request context header
    exc_block = st.split("<BR><BR>", 1)[1] if "<BR><BR>" in st else st

    # Normalise line endings
    text = exc_block.replace("<BR>", "\n")

    # Walk all lines — last "Caused by:" wins (deepest root cause)
    root = None
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("at ") or line.startswith("..."):
            continue
        if line.startswith("Caused by:"):
            root = line[len("Caused by:"):].strip()
        elif root is None:
            # First non-frame line is the top-level exception (fallback)
            root = line

    return (root or exc_block[:200])[:300]


def extract_endpoint(url: str, st: str) -> str:
    """Best-effort endpoint: direct URL > request bracket > AJSServlet referer path."""
    if url:
        return url

    # [/a/something.do] format at start of st
    m = re.match(r"\[(/a/[^\]]+)\]", st or "")
    if m:
        # strip query params — keep just the path
        return m.group(1).split("?")[0]

    # AJSServlet: extract path from referer header
    m = re.search(r'"referer"\s*:\s*"https?://[^/]+(/a/[^?"]+)', st or "")
    if m:
        return m.group(1)

    # fallback: any /a/ path in the string
    m = re.search(r'(/a/[a-zA-Z0-9/_.\-]+\.do)', st or "")
    return m.group(1) if m else ""


def extract_codebase_frames(st: str, max_frames: int = 6) -> list[str]:
    """Pull com.surveyconsole / com.bhaskaran frames from the deepest Caused by: block."""
    text = st.replace("<BR>", "\n")
    lines = text.splitlines()

    # Find the last "Caused by:" block — frames there are most actionable
    last_caused_by = -1
    for idx, line in enumerate(lines):
        if line.strip().startswith("Caused by:"):
            last_caused_by = idx

    search_lines = lines[last_caused_by:] if last_caused_by >= 0 else lines

    frames = []
    for line in search_lines:
        line = line.strip()
        if line.startswith("at ") and (
            "com.surveyconsole" in line or "com.bhaskaran" in line
        ):
            frames.append(line[3:])  # strip "at "
            if len(frames) >= max_frames:
                break

    # Fallback: top-level frames if Caused by block had none
    if not frames:
        for line in lines:
            line = line.strip()
            if line.startswith("at ") and (
                "com.surveyconsole" in line or "com.bhaskaran" in line
            ):
                frames.append(line[3:])
                if len(frames) >= max_frames:
                    break

    return frames


def extract_request_context(st: str) -> dict:
    """Pull structured request info: referer, origin, IP, params."""
    ctx = {}

    ref = _extract_referer(st or "")
    if ref:
        ctx["referer"] = ref

    m = re.search(r'"cf-connecting-ip"\s*:\s*"([^"]+)"', st or "")
    if m:
        ctx["ip"] = m.group(1)

    m = re.search(r'"cf-ipcountry"\s*:\s*"([^"]+)"', st or "")
    if m:
        ctx["country"] = m.group(1)

    # Classic format: params in second bracket [endpoint][params]
    m = re.match(r'\[[^\]]+\]\[([^\]]{0,300})\]', st or "")
    if m:
        ctx["params"] = m.group(1)

    return ctx


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

        rep = rs[0]  # representative row for extraction
        root_cause  = extract_root_cause(rep.get("st", ""))
        endpoint    = extract_endpoint(rep.get("url", ""), rep.get("st", ""))
        frames      = extract_codebase_frames(rep.get("st", ""))
        req_ctx     = extract_request_context(rep.get("st", ""))
        count       = len(rs)

        # timestamps
        timestamps = sorted(r["ts"] for r in rs if r.get("ts"))
        first_seen = timestamps[0][:10] if timestamps else ""
        last_seen  = timestamps[-1][:10] if timestamps else ""

        clusters.append({
            "hash":       h,
            "count":      count,
            "root_cause": root_cause,
            "endpoint":   endpoint,
            "frames":     frames,
            "req_ctx":    req_ctx,
            "dcs":        sorted(dcs),
            "side":       side,
            "severity":   classify_severity(count, dcs, side),
            "hosts":      sorted({r["host"] for r in rs})[:6],
            "ids":        [r["id"] for r in rs[:SAMPLE_IDS]],
            "first_seen": first_seen,
            "last_seen":  last_seen,
            "st":         rep.get("st", ""),
        })

    return sorted(clusters, key=lambda c: (
        {"critical": 0, "high": 1, "medium": 2, "low": 3}[c["severity"]], -c["count"]
    ))


# ── Markdown rendering ────────────────────────────────────────────────────────

def render_report(start: str, end: str, clusters: list[dict], total: int) -> str:
    all_dcs = ["US", "EU", "QA"]

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
        "| # | sev | root cause | count | dc | side | dates |",
        "|---|-----|-----------|-------|-----|------|-------|",
    ]

    for i, c in enumerate(clusters, 1):
        rc = c["root_cause"][:80].replace("|", "\\|")
        dates = c["first_seen"] if c["first_seen"] == c["last_seen"] else f"{c['first_seen']} → {c['last_seen']}"
        lines.append(
            f"| {i} | {c['severity']} | {rc} | {c['count']} | {'+'.join(c['dcs'])} | {c['side']} | {dates} |"
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
        rc = c["root_cause"][:120]
        dates = c["first_seen"] if c["first_seen"] == c["last_seen"] else f"{c['first_seen']} → {c['last_seen']}"

        lines += [
            f"### {i}. {rc[:70]} *({c['severity']}, {c['count']} hits)*",
            "",
            f"**dc / side:** {' + '.join(dc.lower() for dc in c['dcs'])} · {c['side']}",
            f"**endpoint:** `{c['endpoint'] or '(unknown)'}`",
            f"**dates:** {dates}",
            f"**affected hosts:** {', '.join(c['hosts'])}",
            f"**error ids (sample {min(SAMPLE_IDS, c['count'])}/{c['count']}):** "
            + ", ".join(str(x) for x in c["ids"]),
            "",
        ]

        # Request context
        ctx = c["req_ctx"]
        if ctx:
            ctx_parts = []
            if ctx.get("referer"):
                ctx_parts.append(f"referer: `{ctx['referer']}`")
            if ctx.get("ip"):
                ctx_parts.append(f"ip: `{ctx['ip']}`" + (f" ({ctx['country']})" if ctx.get("country") else ""))
            if ctx.get("params"):
                ctx_parts.append(f"params: `{ctx['params'][:200]}`")
            if ctx_parts:
                lines += ["**request context:**", ""] + [f"- {p}" for p in ctx_parts] + [""]

        # Root cause (full)
        lines += [
            "**root cause:**",
            "```",
            c["root_cause"],
            "```",
            "",
        ]

        # Codebase frames
        if c["frames"]:
            lines += [
                "**codebase frames:**",
                "```",
                *[f"at {f}" for f in c["frames"]],
                "```",
                "",
            ]

        lines += ["---", ""]

    # PDM block
    us = dc_summary["US"]
    eu = dc_summary["EU"]
    qa = dc_summary["QA"]
    pdm_lines = [
        f"{total} errors logged ({start} → {end})",
        "",
        f"us dc — {us['panel']} panel, {us['portal']} portal",
        f"eu dc — {eu['panel']} panel, {eu['portal']} portal",
    ]
    if qa["panel"] + qa["portal"] + qa["other"] > 0:
        pdm_lines.append(f"qa    — {qa['panel']} panel, {qa['portal']} portal  (non-production)")

    lines += [
        "## pdm report",
        "",
        "```",
        *pdm_lines,
        "```",
        "",
        "---",
        "",
    ]

    # Engineering update — production clusters above threshold
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
        rc = c["root_cause"].lower()[:100]
        ep = c["endpoint"] or "unknown endpoint"
        dates = c["first_seen"] if c["first_seen"] == c["last_seen"] else f"{c['first_seen']}→{c['last_seen']}"
        eng_bullets.append(f"~ {c['count']:<4}: [{dates}] {rc} — {ep}")

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
        start_date, end_date = get_week_range()

    if output_dir is None:
        output_dir = ROOT / "reports" / f"{start_date}_to_{end_date}"

    if input_file is None:
        input_file = output_dir / "raw" / "errors_combined.json"

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
