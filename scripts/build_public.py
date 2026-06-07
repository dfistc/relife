"""Build the static public website for GitHub Pages."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"


def main() -> None:
    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)
    (PUBLIC / "data").mkdir(parents=True)
    (PUBLIC / "downloads").mkdir()

    for name in ("index.html", "app.js", "styles.css"):
        shutil.copy2(ROOT / name, PUBLIC / name)
    shutil.copy2(ROOT / "data" / "papers.json", PUBLIC / "data" / "papers.json")
    for pdf in (ROOT / "downloads").glob("*.pdf"):
        shutil.copy2(pdf, PUBLIC / "downloads" / pdf.name)
    (PUBLIC / ".nojekyll").touch()
    print(f"Built public site at {PUBLIC}")


if __name__ == "__main__":
    main()
