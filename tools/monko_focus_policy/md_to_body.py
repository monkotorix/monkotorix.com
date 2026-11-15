"""Convert docs/privacy-policy.md of Monko Focus into the body HTML of /privacy/monko-focus/.

    python3 tools/monko_focus_policy/md_to_body.py ../neurocrew/docs/privacy-policy.md > /tmp/monko-focus-body.html

Step 1 of 3; README.md has all three commands.

Headings, paragraphs, lists, **bold**, the Contact block (one line each), typographic quotes.
The title and the "Last updated" line are printed first, as markers the page template uses.
"""
import html
import re
import sys

md = open(sys.argv[1], encoding="utf-8").read().rstrip("\n").split("\n")


def typo(text: str) -> str:
    # Opening/closing double quotes, then apostrophes (the policy has no single-quoted phrases).
    text = re.sub(r'"([^"]*)"', "“\\1”", text)
    if '"' in text:
        raise SystemExit(f"unpaired quote in: {text}")
    return text.replace("'", "’")


def inline(text: str) -> str:
    text = html.escape(typo(text), quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    if "*" in text:
        raise SystemExit(f"unconverted markdown in: {text}")
    text = text.replace(
        "Autoriteit Persoonsgegevens", '<span lang="nl">Autoriteit Persoonsgegevens</span>'
    ).replace(
        "(autoriteitpersoonsgegevens.nl)",
        '(<a href="https://autoriteitpersoonsgegevens.nl" rel="noopener">autoriteitpersoonsgegevens.nl</a>)',
    )
    return text


# Split into blocks on blank lines.
blocks, cur = [], []
for line in md:
    if line.strip() == "":
        if cur:
            blocks.append(cur)
            cur = []
    else:
        cur.append(line)
if cur:
    blocks.append(cur)

out = []
section = None
for block in blocks:
    first = block[0]
    if first.startswith("# "):
        out.append(f"TITLE\t{inline(first[2:])}")
        continue
    if first.startswith("Last updated: ") and len(block) == 1:
        out.append(f"UPDATED\t{inline(first)}")
        continue
    if first.startswith("## "):
        section = first[3:]
        out.append(f"    <h2>{inline(section)}</h2>")
        rest = block[1:]
        if rest:
            raise SystemExit(f"text right under a heading: {rest}")
        continue
    if section == "Contact":
        # The contact block: one line each, kept as lines.
        lines = [inline(l.strip()) for l in block]
        lines = [
            re.sub(r"Email: (\S+@\S+)$", r'Email: <a href="mailto:\1">\1</a>', l) for l in lines
        ]
        out.append("    <address>" + "<br>\n      ".join(lines) + "</address>")
        continue
    if first.startswith("- "):
        items, item = [], None
        for l in block:
            if l.startswith("- "):
                if item is not None:
                    items.append(item)
                item = l[2:].strip()
            elif l.startswith("  ") and item is not None:
                item += " " + l.strip()
            else:
                raise SystemExit(f"odd list line: {l}")
        items.append(item)
        out.append("    <ul>")
        out += [f"      <li>{inline(i)}</li>" for i in items]
        out.append("    </ul>")
        continue
    if any(l.startswith(("#", "-", "  ")) for l in block):
        raise SystemExit(f"odd paragraph: {block}")
    out.append(f"    <p>{inline(' '.join(l.strip() for l in block))}</p>")

print("\n".join(out))
