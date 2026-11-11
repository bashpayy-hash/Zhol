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
    # addresses the companies gave us themselves (an auto-reply naming a new address) stay out of the repository:
    # outreach/private/contact_overrides.csv (id,email,note) goes only into the copy that is published privately
    # and the WhatsApp numbers companies publish on their own sites (outreach/private/whatsapp.csv: id, whatsapp,
    # source, how): often the owner's own mobile at a small haulier, so they too stay in the private copy only
    over, wa = OUT / "private" / "contact_overrides.csv", OUT / "private" / "whatsapp.csv"
    if over.exists() or wa.exists():
        import csv
        fix = {r["id"]: r for r in csv.DictReader(open(over, encoding="utf-8")) if r.get("email")} if over.exists() else {}
        was = {r["id"]: r for r in csv.DictReader(open(wa, encoding="utf-8")) if r.get("whatsapp")} if wa.exists() else {}
        rows = json.loads((OUT / "survey_send_list.json").read_text(encoding="utf-8"))
        for r in rows:
            if r["id"] in fix:
                r["to"], r["to_src"] = fix[r["id"]]["email"], ""
                r["where"] = "адрес из автоответа самой компании: старый ящик отключён"
            if r["id"] in was:
                r["wa"], r["wa_src"] = was[r["id"]]["whatsapp"], was[r["id"]]["source"]
        data = json.dumps(rows, ensure_ascii=False).replace("</", "<\\/")
        private = (OUT / "console" / "template.html").read_text(encoding="utf-8")
        private = private.replace("__DATA__", data).replace("__POSTS__", enc(OUT / "console" / "posts.json"))
        (OUT / "private" / "send-console.html").write_text(private, encoding="utf-8")
        print(f"wrote outreach/private/send-console.html ({len(fix)} address(es) from the companies' own replies, "
              f"{len(was)} WhatsApp number(s) from their sites)")


if __name__ == "__main__":
    main()
