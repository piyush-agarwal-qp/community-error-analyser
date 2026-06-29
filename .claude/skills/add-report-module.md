---
name: add-report-module
description: >
  Step-by-step guide for adding a new report module to the Communities weekly
  report pipeline. Covers creating the script, wiring into run_all.py,
  adding to assemble_report.py, and updating config files.
---

## Trigger phrases

- "add a new report module for X"
- "add [metric/report] to the weekly report"
- "wire up [new Metabase question] into the pipeline"

---

## Step 1 — Clarify what the module does

Before writing any code, confirm:

1. **Data source** — which Metabase question ID(s)? Or a different API?
2. **Output** — what does the copy-paste block look like? (ask user to show example)
3. **Module name** — short snake_case name, e.g. `nps_report`, `ticket_report`
4. **Frequency** — weekly (standard) or different cadence?

---

## Step 2 — Create the script `{name}_report.py`

Follow the pattern of existing modules. Required structure:

```python
#!/usr/bin/env python3
SCRIPT_DIR = Path(__file__).parent
load_dotenv(SCRIPT_DIR / ".env")

def main(start_date=None, end_date=None, dry_run=False, output_dir=None) -> dict:
    # 1. authenticate (reuse SESSION_TOKEN pattern from other modules)
    # 2. fetch data from Metabase
    # 3. format into markdown with a ## Copy-paste block section
    # 4. write to output_dir / "{name}_report.md"
    # 5. return {"module": "{name}", "status": "ok", "md": str(md_file)}

if __name__ == "__main__":
    # argparse with --start, --end, --dry-run
```

Key rules:
- `main()` must be **importable** (no top-level side effects)
- Always return `{"module": "...", "status": "ok"|"error", "md": path}`
- Write output to `output_dir / "{name}_report.md"`
- Include a `## Copy-paste block` section with a fenced ` ``` ` block — `assemble_report.py` extracts from there
- Use `METABASE_SESSION_TOKEN` from `.env` for auth
- For Metabase saved questions: `POST /api/card/{id}/query` with template-tag parameters
- For per-day heavy queries: use `daily_splits()` pattern + `ThreadPoolExecutor` (see `performance_report.py`)

---

## Step 3 — Add environment variables to `.env.example`

```bash
# {MODULE NAME}
METABASE_QUESTION_ID_{NAME}=XXXX
```

Also add to the actual `.env` file.

---

## Step 4 — Wire into `run_all.py`

Add a `run_{name}()` function:

```python
def run_{name}(start: str, end: str, output_dir: Path, dry_run: bool) -> dict:
    from {name}_report import main as {name}_main
    print("[{name}] starting...")
    result = {name}_main(start_date=start, end_date=end, dry_run=dry_run, output_dir=output_dir)
    print("[{name}] done")
    return result
```

Then add to the `MODULES` list:

```python
MODULES = [
    ("metrics",     run_metrics),
    ("errors",      run_errors),
    ("radar",       run_radar),
    ("performance", run_performance),
    ("{name}",      run_{name}),   # ← add here
]
```

`ThreadPoolExecutor` picks it up automatically — no other changes needed.

---

## Step 5 — Wire into `assemble_report.py`

1. Add a parser function `parse_{name}()` that reads `{name}_report.md` and extracts the copy-paste block
2. Call it in `main()` and insert the result into the assembled `weekly_report.md` at the right position

Pattern used by existing modules:
```python
def extract_copy_paste_block(md_path: Path) -> str:
    """Finds content inside ``` after ## Copy-paste block."""
    ...
```

Check `assemble_report.py` for the existing pattern and follow it.

---

## Step 6 — Update `config.yaml` (if needed)

If the module needs database IDs, question IDs, or other config beyond `.env`:

```yaml
{name}_report:
  question_id: XXXX
  # other config...
```

---

## Step 7 — Update `CLAUDE.md`

Add the new module to the **Report modules** table:

```markdown
| {Module name} | `{name}_report.py` | ✓ |
```

And add the standalone run command to the **Quick reference** section:

```bash
python3 {name}_report.py --start YYYY-MM-DD --end YYYY-MM-DD
```

---

## Step 8 — Validate

```bash
# Test standalone
python3 {name}_report.py --start 2026-06-19 --end 2026-06-25 --dry-run

# Test wired into pipeline
python3 run_all.py --from 2026-06-19 --to 2026-06-25 --dry-run

# Full live run on a single day (fast)
python3 {name}_report.py --start 2026-06-25 --end 2026-06-25
```

Check that:
- `reports/{START}_to_{END}/{name}_report.md` is created
- Copy-paste block is present and well-formatted
- `weekly_report.md` includes the new section after reassembly

---

## Step 9 — Commit

```bash
git add {name}_report.py assemble_report.py run_all.py .env.example CLAUDE.md config.yaml
git commit -m "add {name} report module to weekly pipeline"
```
