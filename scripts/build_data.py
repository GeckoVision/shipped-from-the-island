"""Build data/site.json for the page from three inputs.

1. Attendance: Gecko's dataset ``islanddao-v5-attendance`` (one row per day, aggregates only,
   small cells withheld). Fetched with a read-only key limited to that dataset when
   GECKO_READER_KEY is set; otherwise the committed snapshot data/attendance-raw.json is used.
2. data/ledger.csv: the milestones ledger, one row per public, dated, sourced milestone.
3. data/editions.json: edition totals and the V4 to V5 comeback, counts only.

Standard library only. Prints counts, never a key.
"""

from __future__ import annotations

import csv
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
URL = "https://mcp.geckovision.tech/d/islanddao-v5-attendance.json"
DAY_FIELDS = ("day_status", "check_ins", "unique_attendees", "new_attendees", "returning_attendees", "cumulative_unique")


def fetch_attendance() -> dict:
    key = os.environ.get("GECKO_READER_KEY", "").strip()
    if not key:
        return json.loads((DATA / "attendance-raw.json").read_text())
    req = urllib.request.Request(URL, headers={"Authorization": f"Bearer {key}", "User-Agent": "shipped-from-the-island"})
    with urllib.request.urlopen(req, timeout=120) as resp:  # noqa: S310 - fixed https URL
        doc = json.load(resp)
    rows = doc["rows"]
    if rows and isinstance(rows[0], list):
        rows = [dict(zip(doc["columns"], row)) for row in rows]
    snapshot = {"version": doc.get("version"), "columns": doc.get("columns"), "rows": rows}
    (DATA / "attendance-raw.json").write_text(json.dumps(snapshot))
    return snapshot


def as_int(value: object) -> int | None:
    try:
        return int(float(value))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def days_of(snapshot: dict) -> list[dict]:
    by_day: dict[str, dict] = {}
    fetched: dict[str, str] = {}
    for row in snapshot["rows"]:
        if row.get("item") or row["field"] not in DAY_FIELDS:
            continue
        day = by_day.setdefault(row["subject"], {"date": row["subject"]})
        day[row["field"]] = row["value"] if row["field"] == "day_status" else as_int(row["value"])
        if row.get("fetched_at"):
            fetched[row["subject"]] = row["fetched_at"]
    days = [by_day[d] for d in sorted(by_day)]
    return days, (max(fetched.values()) if fetched else None)


def ledger() -> list[dict]:
    with (DATA / "ledger.csv").open(newline="") as f:
        return list(csv.DictReader(f))


def main() -> int:
    snapshot = fetch_attendance()
    days, fetched_at = days_of(snapshot)
    rows = ledger()
    projects = [r for r in rows if not r["project"].startswith("IslandDAO")]
    editions = json.loads((DATA / "editions.json").read_text())
    active = [d for d in days if (d.get("unique_attendees") or 0) > 0]
    site = {
        "built_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "attendance": {
            "dataset": "islanddao-v5-attendance",
            "version": snapshot.get("version"),
            "fetched_at": fetched_at,
            "days": days,
            "check_ins": sum(d.get("check_ins") or 0 for d in days),
            "cumulative_unique": max((d.get("cumulative_unique") or 0) for d in days) if days else 0,
            "peak": max(active, key=lambda d: d["unique_attendees"]) if active else None,
        },
        "editions": editions,
        "ledger": {
            "rows": rows,
            "entries": len(projects),
            "projects": len({r["project"] for r in projects}),
            "outcomes": sum(r["kind"] == "outcome" for r in projects),
            "projects_with_outcome": len({r["project"] for r in projects if r["kind"] == "outcome"}),
        },
    }
    (DATA / "site.json").write_text(json.dumps(site, indent=1, ensure_ascii=False))
    a = site["attendance"]
    print(f"attendance v{a['version']}: {len(days)} days, {a['check_ins']} check-ins, {a['cumulative_unique']} unique")
    print(f"ledger: {site['ledger']['entries']} entries, {site['ledger']['projects']} projects")
    return 0


if __name__ == "__main__":
    sys.exit(main())
