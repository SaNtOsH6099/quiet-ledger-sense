#!/usr/bin/env python3
"""Fetch evidence for review claims, cheaply, on the local machine.

Takes a prompts file (one entry per claim: the claim, search queries,
preferred domains, keywords), searches the web with DuckDuckGo's HTML
endpoint (no API key), fetches the top pages, extracts the main text
with Trafilatura, and returns only the sentences matching each claim.

The reviewer reads the evidence file, never a raw page. A lookup that
used to cost a full page read (5,000-15,000 tokens in context) costs
one snippet (100-300 tokens).

Run with the pipeline venv python:
    venv/bin/python scrape_evidence.py prompts/test.json evidence/out

Inputs: prompts JSON {"claims": [{"id", "claim", "queries": [...],
"urls": [direct source URLs, used first when present],
"prefer": [domain substrings], "keywords": [...]}]}
Outputs: <out>.json (machine-readable) and <out>.md (readable).

Search note: free search-engine HTML endpoints (DuckDuckGo, DDG Lite,
Bing, Mojeek, public SearXNG) all block or starve requests from this
VM's datacenter IP, so search is best-effort only. The reliable path
is direct URLs in the prompts file (Muse supplies authoritative
sources), with Brave Search API (free tier, needs a key) as the
planned search layer. See README.md.
"""
import json
import os
import re
import sys
import time
import urllib.parse
from datetime import datetime

import httpx
from bs4 import BeautifulSoup

try:
    import trafilatura
except ImportError:
    trafilatura = None

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
SEARCH_URL = "https://html.duckduckgo.com/html/?q="
PAUSE = 1.0            # seconds between requests (polite, avoids blocks)
MAX_RESULTS = 5        # search results kept per query
MAX_FETCHES = 4        # pages fetched per claim
MAX_SNIPPETS = 3       # snippets returned per claim


def search(query, client):
    """Top result URLs for a query via DuckDuckGo HTML. No API key."""
    try:
        r = client.get(SEARCH_URL + urllib.parse.quote(query), timeout=20)
        if r.status_code != 200:
            return [], f"HTTP {r.status_code}"
    except Exception as e:
        return [], str(e)
    soup = BeautifulSoup(r.text, "html.parser")
    urls = []
    for a in soup.select("a.result__a"):
        href = a.get("href", "")
        if href.startswith("//duckduckgo.com/l/?"):
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
            href = qs.get("uddg", [""])[0]
        if href.startswith("http") and href not in urls:
            urls.append(href)
        if len(urls) >= MAX_RESULTS:
            break
    return urls, ""


def fetch_text(url, client):
    """Main text of a page. Trafilatura first, plain text fallback.
    One retry on transient failures (some hosts drop the first request)."""
    html, err = "", ""
    for attempt in range(2):
        try:
            r = client.get(url, timeout=20, follow_redirects=True)
            if r.status_code != 200:
                err = f"HTTP {r.status_code}"
                break
            html = r.text
            err = ""
            break
        except Exception as e:
            err = str(e)
            time.sleep(2)
    if err:
        return "", err
    text = ""
    if trafilatura:
        try:
            text = trafilatura.extract(html, include_tables=True) or ""
        except Exception:
            text = ""
    if not text.strip():
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer"]):
            tag.decompose()
        text = soup.get_text("\n")
    return text, ""


def sentences(text):
    """Split text into sentences, keeping decimals and Rs figures intact."""
    parts = re.split(r"\n+", text)
    out = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # split on sentence ends followed by a capital or digit, but
        # not inside decimals (8.2) or Indian digit groups (1,00,000)
        for s in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])", part):
            s = s.strip()
            if len(s) > 20:
                out.append(s)
    return out


def numbers(text):
    """Numbers mentioned in the claim, normalised for matching."""
    found = set()
    for m in re.finditer(r"\d[\d,]*(?:\.\d+)?\s?%?", text):
        found.add(m.group(0).replace(",", "").replace(" ", "").rstrip("%"))
        found.add(m.group(0))
    return found


def score_sentence(sent, keywords, claim_numbers):
    score = 0
    low = sent.lower()
    for kw in keywords:
        if kw.lower() in low:
            score += 2
    for num in claim_numbers:
        if num and num in sent.replace(",", ""):
            score += 3
    return score


def run_claim(claim, client):
    cid = claim.get("id", "?")
    text = claim.get("claim", "")
    queries = claim.get("queries", [])[:2]
    prefer = claim.get("prefer", [])
    keywords = claim.get("keywords", []) or []
    claim_numbers = numbers(text)
    if not keywords:
        keywords = [w for w in re.findall(r"[A-Za-z]{4,}", text)][:6]

    urls, errors = [], []
    direct = claim.get("urls", [])
    if direct:
        urls.extend(direct)
    else:
        for q in queries:
            found, err = search(q, client)
            if err:
                errors.append(f"search '{q[:40]}': {err}")
            urls.extend(found)
            time.sleep(PAUSE)
    # dedupe, preferred domains first
    seen, ordered = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            ordered.append(u)
    ordered.sort(key=lambda u: 0 if any(p in u for p in prefer) else 1)

    snippets = []
    for url in ordered[:MAX_FETCHES]:
        page_text, err = fetch_text(url, client)
        if err:
            errors.append(f"fetch {url[:60]}: {err}")
            continue
        sents = sentences(page_text)
        scored = [(score_sentence(s, keywords, claim_numbers), i, s)
                  for i, s in enumerate(sents)]
        scored = [x for x in scored if x[0] > 0]
        scored.sort(reverse=True)
        for score, i, s in scored[:2]:
            before = sents[i - 1] if i > 0 else ""
            after = sents[i + 1] if i + 1 < len(sents) else ""
            snippets.append({
                "score": score,
                "text": " ".join(x for x in (before, s, after) if x),
                "source": url,
            })
        time.sleep(PAUSE)
    snippets.sort(key=lambda s: -s["score"])
    snippets = snippets[:MAX_SNIPPETS]
    status = "FOUND" if snippets else "NOT_FOUND"
    return {
        "id": cid, "claim": text, "status": status,
        "snippets": snippets, "errors": errors,
        "urls_tried": ordered[:MAX_FETCHES],
    }


def main():
    if len(sys.argv) != 3:
        print("Usage: scrape_evidence.py <prompts.json> <out-prefix>")
        sys.exit(2)
    with open(sys.argv[1]) as f:
        prompts = json.load(f)
    claims = prompts.get("claims", [])
    out_prefix = sys.argv[2]
    results = []
    # Proxy/CA handling that works both on this VM and on a GitHub
    # runner. This VM needs the egress proxy (HTTPS_PROXY) and its CA
    # bundle (SSL_CERT_FILE); trust_env=False avoids httpx choking on
    # the bracketed IPv6 entries in this machine's no_proxy. A runner
    # has neither env var, so it connects directly with certifi.
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    cafile = os.environ.get("SSL_CERT_FILE")
    verify = cafile if cafile and os.path.exists(cafile) else True
    with httpx.Client(headers={"User-Agent": UA}, trust_env=False,
                      proxy=proxy, verify=verify) as client:
        for claim in claims:
            print(f"claim {claim.get('id', '?')}: {claim.get('claim', '')[:60]}")
            results.append(run_claim(claim, client))
    found = sum(1 for r in results if r["status"] == "FOUND")
    payload = {
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "claims": results,
        "summary": {"total": len(results), "found": found,
                    "not_found": len(results) - found},
    }
    with open(out_prefix + ".json", "w") as f:
        json.dump(payload, f, indent=1, ensure_ascii=False)
    lines = [f"# Evidence: {len(results)} claims, {found} found",
             f"Generated {payload['generated']}.", ""]
    for r in results:
        lines.append(f"## {r['id']}: {r['claim']}")
        lines.append(f"Status: {r['status']}")
        for s in r["snippets"]:
            lines.append(f"- (score {s['score']}) {s['text']}")
            lines.append(f"  Source: {s['source']}")
        for e in r["errors"]:
            lines.append(f"- ERROR: {e}")
        lines.append("")
    with open(out_prefix + ".md", "w") as f:
        f.write("\n".join(lines))
    print(f"wrote {out_prefix}.json + .md: {found}/{len(results)} found")


if __name__ == "__main__":
    main()
