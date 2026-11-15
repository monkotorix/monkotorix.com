"""Check that the page says the policy word for word.

    python3 tools/monko_focus_policy/check_same_text.py ../neurocrew/docs/privacy-policy.md site/privacy/monko-focus/index.html

Step 3 of 3.

Takes the text of the page from the <h1> to the <footer>, drops the tags and the eyebrow,
turns typographic quotes back into straight ones, and compares it word by word with the
markdown without its markup. Prints the first difference, or OK.
"""
import html
import re
import sys

md = open(sys.argv[1], encoding="utf-8").read()
page = open(sys.argv[2], encoding="utf-8").read()

md_text = re.sub(r"^#+ ", "", md, flags=re.M)
md_text = re.sub(r"^- ", "", md_text, flags=re.M)
md_text = md_text.replace("**", "")
md_words = md_text.split()

body = page[page.index("<h1>"): page.index("<footer>")]
body = re.sub(r"<br>", " ", body)
body = re.sub(r"</?(?:strong|a|span)\b[^>]*>", "", body)  # inline: no word break
body = re.sub(r"<[^>]+>", " ", body)
body = html.unescape(body)
body = body.replace("“", '"').replace("”", '"').replace("’", "'")
page_words = body.split()

if md_words == page_words:
    print(f"OK: {len(md_words)} words, identical")
    sys.exit(0)
for i, (a, b) in enumerate(zip(md_words, page_words)):
    if a != b:
        print(f"differs at word {i}: md {md_words[max(0, i-6):i+6]}\n               page {page_words[max(0, i-6):i+6]}")
        sys.exit(1)
print(f"length differs: md {len(md_words)} words, page {len(page_words)} words")
print("md tail:  ", md_words[min(len(md_words), len(page_words)) - 5:][:20])
print("page tail:", page_words[min(len(md_words), len(page_words)) - 5:][:20])
sys.exit(1)
