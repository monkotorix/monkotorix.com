"""Assemble site/privacy/monko-focus/index.html from the body HTML (md_to_body.py) in the layout of /privacy/.

    python3 tools/monko_focus_policy/make_page.py /tmp/monko-focus-body.html site/privacy/index.html site/privacy/monko-focus/index.html

Step 2 of 3. The styles, the emblem and the Content-Security-Policy come from site/privacy/index.html,
so run this again after changing those there too.
"""
import re
import sys

body_lines = open(sys.argv[1], encoding="utf-8").read().rstrip("\n").split("\n")
privacy = open(sys.argv[2], encoding="utf-8").read()
out_path = sys.argv[3]

title = body_lines[0].split("\t", 1)[1]
updated = body_lines[1].split("\t", 1)[1]
assert title == "Privacy policy for Monko Focus", title
assert updated.startswith("Last updated: "), updated

# A blank line before each section, as on /privacy/.
body = []
for line in body_lines[2:]:
    if line.startswith("    <h2>"):
        body.append("")
    body.append(line)

# Shared pieces, taken from /privacy/ so they stay the same.
emblem = re.search(r'(<a class="back" href="/">.*?</a>)', privacy).group(1)
style = re.search(r"(  <style>\n.*?\n  </style>)", privacy, re.S).group(1)
# This page has no Dutch twin, so no language link; the contact block is an <address>.
style = style.replace("    .lang{font-size:.95rem;font-weight:600}\n", "")
style = style.replace(
    "    p,ul{margin:0 0 1rem}\n", "    p,ul,address{margin:0 0 1rem}\n    address{font-style:normal}\n"
)
assert "address{font-style:normal}" in style
csp = re.search(r'(  <meta http-equiv="Content-Security-Policy"[^>]*>)', privacy).group(1)

page = f"""<!doctype html>
<!-- Generated from docs/privacy-policy.md in the Monko Focus repository (monkotorix/monkofocus), word for word,
     by tools/monko_focus_policy/. Change the policy there first, then rebuild this page (see README.md). -->
<html lang="en-GB">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} — Monkotorix</title>
  <meta name="description" content="The privacy policy for the Monko Focus app for phones and tablets: no accounts, no ads, no tracking, and what the app keeps stays on the device.">
  <link rel="canonical" href="https://monkotorix.com/privacy/monko-focus/">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Monkotorix">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="The Monko Focus app for phones and tablets: no accounts, no ads, no tracking.">
  <meta property="og:url" content="https://monkotorix.com/privacy/monko-focus/">
  <meta property="og:image" content="https://monkotorix.com/assets/og.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
{csp}
  <meta name="color-scheme" content="light dark">
  <meta name="theme-color" content="#f5edda" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#0c1124" media="(prefers-color-scheme: dark)">
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
  <link rel="icon" type="image/png" sizes="48x48" href="/assets/favicon-48.png">
  <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
  <script src="/assets/site.js"></script>
{style}
</head>
<body>
  <main class="wrap">
    <div class="top">
      {emblem}
    </div>

    <p class="eyebrow">The Monko Focus app for phones and tablets</p>
    <h1>{title}</h1>
    <p class="muted">{updated}</p>

{chr(10).join(body)}

    <footer>
      <p>For this website and the games you play in a browser, see the <a href="/privacy/">privacy notice</a>.</p>
      <p><a href="/">Back to Monkotorix</a> · <a href="mailto:hello@monkotorix.com">hello@monkotorix.com</a></p>
      <p>© 2026 Sofmon B.V. All rights reserved.</p>
    </footer>
  </main>
</body>
</html>
"""
open(out_path, "w", encoding="utf-8").write(page)
print(f"wrote {out_path}")
