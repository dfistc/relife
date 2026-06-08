"""Fetch new BMP8B/LONP1/HMGCS2 literature candidates from Europe PMC.

This script never guesses impact factors or machine-translates summaries. New
candidates are written to data/review_queue.json for the scheduled Codex task
to verify, summarize, and merge into the public dataset.
"""

from __future__ import annotations

import html
import json
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPERS_PATH = ROOT / "data" / "papers.json"
QUEUE_PATH = ROOT / "data" / "review_queue.json"
START_DATE = "2018-01-01"


def build_query(end_date: str) -> str:
    return (
        f"FIRST_PDATE:[{START_DATE} TO {end_date}] AND "
        '((TITLE_ABS:BMP8B OR TITLE_ABS:"BMP-8B") OR '
        '(TITLE_ABS:LONP1 OR TITLE_ABS:"Lon protease 1") OR '
        '(TITLE_ABS:HMGCS2 OR TITLE_ABS:"mitochondrial HMG-CoA synthase"))'
    )


def fetch_candidates(end_date: str) -> list[dict]:
    params = urllib.parse.urlencode(
        {"query": build_query(end_date), "format": "json", "pageSize": 1000, "sort": "FIRST_PDATE_D desc"}
    )
    request = urllib.request.Request(
        f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?{params}",
        headers={"User-Agent": "ThermoGene-Literature-Watch/1.0"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    return payload["resultList"]["result"]


def main() -> None:
    checked_at = datetime.now().astimezone()
    end_date = checked_at.date().isoformat()
    current = json.loads(PAPERS_PATH.read_text(encoding="utf-8"))
    known = {
        str(identifier)
        for item in current["papers"]
        for identifier in [item["id"], *item.get("aliases", [])]
    }
    queue = []
    for item in fetch_candidates(end_date):
        identifier = str(item.get("pmid") or item.get("pmcid") or item.get("id"))
        if identifier in known:
            continue
        queue.append(
            {
                "id": identifier,
                "title": html.unescape(item.get("title") or ""),
                "journal": item.get("journalTitle"),
                "date": item.get("firstPublicationDate"),
                "authors": item.get("authorString"),
                "doi": item.get("doi"),
                "discovered_date": datetime.now().astimezone().date().isoformat(),
                "needs_review": [
                    "direct or inspirational relevance to thermogenesis/PCOS",
                    "set relevance to direct or inspirational",
                    "set added_date when publishing to papers.json",
                    "verify title against PubMed/PMC and DOI before publishing",
                    "set url to DOI/publisher page and source_url to PubMed/PMC",
                    "article type and research field",
                    "latest verifiable JIF, CAS partition, and CNS classification",
                    "bilingual summaries and inspiration note",
                ],
            }
        )
    if queue:
        QUEUE_PATH.write_text(
            json.dumps(
                {
                    "checked_at": checked_at.isoformat(timespec="seconds"),
                    "search_range": {"from": START_DATE, "to": end_date},
                    "candidates": queue,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"Queued {len(queue)} new candidate(s) for review.")
    else:
        print("No new candidates; public data left unchanged.")

    current["last_checked"] = checked_at.strftime("%Y-%m-%d %H:%M")
    current["criteria"]["since"] = START_DATE
    current["criteria"]["through"] = end_date
    PAPERS_PATH.write_text(
        json.dumps(current, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
