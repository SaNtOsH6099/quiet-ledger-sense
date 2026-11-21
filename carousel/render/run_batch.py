#!/usr/bin/env python3
"""Render selected Rupee Sense carousels on this machine and replace
their files on Drive in place.

Usage: run_batch.py <selection>
  selection: "65" (one post), "all" (every post in rebuild-8.json),
             or a comma list "65,79,80".
Reads carousel/rebuild-8.json for the post -> Drive folder map.
For each post:
  1. Copy carousel/specs/<slug>.json to carousel/work/<slug>/spec.json.
  2. Run build_post.py on it (HTML + PNG, 1080x1080).
  3. Verify every PNG is 1080x1080 (PIL) and >20KB.
  4. Replace .png/.html/spec.json in the post's Drive folder in place
     via pipeline.drive.video_env.upload_file (same file IDs, no dupes).
Drive auth is the repo's OAuth (DRIVE_OAUTH_JSON in the environment).
"""
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CAROUSEL = os.path.join(ROOT, "carousel")
RENDER = os.path.join(CAROUSEL, "render")
SPECS = os.path.join(CAROUSEL, "specs")
WORK = os.path.join(CAROUSEL, "work")

sys.path.insert(0, ROOT)
from pipeline.drive import video_env as env_mod


def main():
    sel = sys.argv[1]
    with open(os.path.join(CAROUSEL, "rebuild-8.json")) as f:
        posts = json.load(f)
    if sel != "all":
        wanted = {int(x) for x in sel.split(",")}
        posts = [p for p in posts if p["number"] in wanted]
        assert posts, "no matching posts for %s" % sel
    service = env_mod.drive_service()
    for post in posts:
        slug = post["slug"]
        folder_id = post["folder_id"]
        workdir = os.path.join(WORK, slug)
        os.makedirs(workdir, exist_ok=True)
        spec_src = os.path.join(SPECS, slug + ".json")
        spec_dst = os.path.join(workdir, "spec.json")
        shutil.copy(spec_src, spec_dst)
        print("=== post %s (%s) ===" % (post["number"], slug))
        r = subprocess.run(
            [sys.executable, os.path.join(RENDER, "build_post.py"), spec_dst],
            capture_output=True, text=True)
        print(r.stdout)
        if r.returncode != 0:
            print(r.stderr)
            sys.exit("build failed for %s" % slug)
        from PIL import Image  # noqa: PLC0415
        pngs = sorted(f for f in os.listdir(workdir) if f.endswith(".png"))
        assert pngs, "no PNGs built for %s" % slug
        for fn in pngs:
            p = os.path.join(workdir, fn)
            sz = os.path.getsize(p)
            assert sz > 20000, "%s too small: %d" % (fn, sz)
            with Image.open(p) as im:
                assert im.size == (1080, 1080), "%s wrong size: %s" % (fn, im.size)
            print("verified %s 1080x1080 %d bytes" % (fn, sz))
        n_rep, n_up = 0, 0
        for fn in sorted(os.listdir(workdir)):
            if not (fn.endswith(".png") or fn.endswith(".html") or fn == "spec.json"):
                continue
            existing = env_mod.find_file(service, fn, folder_id)
            env_mod.upload_file(service, folder_id, os.path.join(workdir, fn), fn)
            if existing:
                n_rep += 1
            else:
                n_up += 1
        print("POST %s DONE: %d pages, REPLACED=%d UPLOADED=%d"
              % (post["number"], len(pngs), n_rep, n_up))


if __name__ == "__main__":
    main()
