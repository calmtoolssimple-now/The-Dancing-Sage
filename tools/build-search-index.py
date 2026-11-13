#!/usr/bin/env python3
"""Builds search-index.json for the site search box (search.html).

Run from the top of the site folder:  python3 tools/build-search-index.py
It reads every .html page and saves its title, summary, section and text.
"""
import glob, html, json, os, re

SKIP = {"search.html", "googlef5adec181e726c68.html", "privacy.html"}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def clean(s):
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def first(pattern, s):
    m = re.search(pattern, s, re.S | re.I)
    return clean(m.group(1)) if m else ""


def section_for(name, s):
    if name in ("shop-grandmas-kitchen.html", "favourites.html"):
        return "Shop"
    if name.startswith("recipe-") or name == "easy-baking.html":
        return "Recipe"
    if name.startswith("dear-sage-") or name == "ask.html":
        return "Ask the Sage"
    if "christmas" in name:
        return "Christmas"
    if "colouring" in name:
        return "Colouring"
    if re.search(r'"@type":\s*"(Article|BlogPosting)"', s) and name not in ("about.html",):
        return "Wisdom"
    return "Site"


pages = []
for path in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
    name = os.path.basename(path)
    if name in SKIP:
        continue
    s = open(path, encoding="utf-8").read()
    if re.search(r'<meta name="robots" content="[^"]*noindex', s, re.I):
        continue
    title = first(r"<h1[^>]*>(.*?)</h1>", s) or first(r"<title>(.*?)</title>", s)
    title = re.sub(r"\s*\|\s*(The )?Dancing Sage\s*$", "", title)
    if name == "index.html":
        title = "Home: The Dancing Sage"
    desc = first(r'<meta name="description" content="([^"]*)"', s)
    body = re.search(r"<main.*?</main>", s, re.S | re.I)
    body = body.group(0) if body else s
    # Start the text after the main heading, so snippets skip labels like "Ask The Dancing Sage"
    body = re.split(r"</h1>", body, maxsplit=1, flags=re.I)[-1]
    body = re.sub(r"<(script|style|nav|footer|aside)\b.*?</\1>", " ", body, flags=re.S | re.I)
    text = clean(body)[:3000]
    pages.append({
        "url": name if name != "index.html" else "./",
        "title": title,
        "description": desc,
        "section": section_for(name, s),
        "text": text,
    })

with open(os.path.join(ROOT, "search-index.json"), "w", encoding="utf-8") as f:
    json.dump(pages, f, ensure_ascii=False, separators=(",", ":"))
print(f"search-index.json: {len(pages)} pages")
