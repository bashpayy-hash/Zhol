"""Build the send console (outreach/send-console.html) from its template, the send list and the posts.

    python scripts/professor_letters.py   # if the professors' letters changed
    python scripts/survey_targets.py      # refreshes outreach/survey_send_list.json
    python scripts/build_console.py

The page is published as a private claude.ai artifact (https://claude.ai/artifact/9uv2W3txr1GgrJAf6VJh3J), where the
"sent / answered" status is shared through the artifact's database. Opened as a local file it keeps the status in this
browser only.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outreach"


def enc(path: Path) -> str:
    return json.dumps(json.loads(path.read_text(encoding="utf-8")), ensure_ascii=False).replace("</", "<\\/")


def main() -> None:
    page = (OUT / "console" / "template.html").read_text(encoding="utf-8")
    page = page.replace("__DATA__", enc(OUT / "survey_send_list.json")).replace("__POSTS__", enc(OUT / "console" / "posts.json"))
    (OUT / "send-console.html").write_text(page, encoding="utf-8")
    print("wrote outreach/send-console.html")


if __name__ == "__main__":
    main()
