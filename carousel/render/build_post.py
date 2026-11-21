#!/usr/bin/env python3
"""Build one Rupee Sense carousel from a JSON spec.

Usage: build_post.py <spec.json>
The spec lives in the post folder; HTML + PNG land in the same folder.
Theme C: odd pages cream, even pages green, alternating for any count.
Page count is flexible (2026-11-21 user redirect): the topic decides how
many pages it needs, minimum 3 solid pages of real value. No padding to
reach a count, no cutting real content to fit one.
No em/en dashes anywhere (asserted). All numbers must already be verified
by the author before writing the spec; this script does not check facts.

NODE_PATH comes from the environment when set (the GitHub Actions
workflow points it at this folder's node_modules); otherwise it defaults
to the local VM path, so local builds work unchanged.
"""
import json
import os
import shutil
import subprocess
import sys

RENDER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RENDER)
import carousel_lib as L

def scheme_for(page_no):
    return "cream" if page_no % 2 == 1 else "green"


def no_dashes(obj, path="spec"):
    if isinstance(obj, str):
        assert "\u2014" not in obj and "\u2013" not in obj, "dash in %s: %s" % (path, obj[:60])
    elif isinstance(obj, dict):
        for k, v in obj.items():
            no_dashes(v, "%s.%s" % (path, k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            no_dashes(v, "%s[%d]" % (path, i))


def build_inner(inner):
    if not inner:
        return ""
    kind = inner["kind"]
    if kind == "rows":
        return L.rows_card(inner["title"], [tuple(r) for r in inner["rows"]])
    if kind == "rows_foot":
        return L.rows_card_foot(inner["title"], [tuple(r) for r in inner["rows"]], inner["foot"])
    if kind == "checklist":
        return L.checklist_card(inner["title"], inner["items"])
    raise ValueError("unknown inner kind %s" % kind)


def build_page(page, page_no):
    scheme = page.get("scheme", scheme_for(page_no))
    t = page["type"]
    if t == "cover":
        return L.cover(scheme, page["eyebrow"], page["title"], page["sub"],
                       page.get("title_size", 118))
    if t == "standard":
        return L.standard(scheme, page["eyebrow"], page["heading"], page["body"],
                          build_inner(page.get("inner")), page_no,
                          note=page.get("note"), heading_size=page.get("heading_size", 82))
    if t == "bars":
        return L.bars_page(scheme, page["eyebrow"], page["heading"], page["body"],
                           [tuple(b) for b in page["bars"]], page_no)
    if t == "compare":
        return L.compare_page(scheme, page["eyebrow"], page["heading"], page["body"],
                              [(g["title"], g["items"]) for g in page["groups"]], page_no)
    if t == "list":
        return L.list_page(scheme, page["eyebrow"], page["heading"], page["body"],
                           [tuple(i) for i in page["items"]], page_no)
    if t == "closing":
        return L.closing(scheme, page["big"], page["sub"])
    raise ValueError("unknown page type %s" % t)


def main():
    spec_path = sys.argv[1]
    folder = os.path.dirname(os.path.abspath(spec_path))
    with open(spec_path) as f:
        spec = json.load(f)
    no_dashes(spec)
    pages = spec["pages"]
    assert len(pages) >= 3, "need at least 3 pages, got %d" % len(pages)
    L.PAGE_TOTAL = len(pages)
    names = []
    for i, page in enumerate(pages, 1):
        html = build_page(page, i)
        name = "p%d-%s" % (i, page["name"])
        names.append(name)
        with open(os.path.join(folder, name + ".html"), "w") as f:
            f.write(html)
        print("wrote", name + ".html")
    env = dict(os.environ)
    if "NODE_PATH" not in env:
        env["NODE_PATH"] = "/home/hatch/workspace/chrome-test/node_modules"
    r = subprocess.run(["node", os.path.join(RENDER, "shot-post.js"), folder],
                       env=env, capture_output=True, text=True)
    print(r.stdout)
    if r.returncode != 0:
        print(r.stderr)
        sys.exit(1)
    shutil.rmtree(os.path.join(folder, ".profile-shot"), ignore_errors=True)
    for n in names:
        p = os.path.join(folder, n + ".png")
        assert os.path.exists(p), "missing %s" % p
        sz = os.path.getsize(p)
        assert sz > 20000, "%s.png too small: %d" % (n, sz)
        print("OK %s.png %d bytes" % (n, sz))


if __name__ == "__main__":
    main()
