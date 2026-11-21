#!/usr/bin/env python3
"""Build Rupee Sense carousel drafts. Theme C: pages alternate cream/green.
1080x1080, Montserrat, Direction A palette. Pages built in code for exact text.
No em dashes anywhere. All numbers verified in code before building.

The Montserrat font URL comes from CAROUSEL_FONT_URL when set (the
GitHub Actions runner downloads the font and points here); otherwise it
defaults to the local VM path, so local builds work unchanged.
"""
import os

DIR = os.path.dirname(os.path.abspath(__file__))
FONT_URL = os.environ.get(
    "CAROUSEL_FONT_URL",
    "file:///home/hatch/workspace/rupee-sense/fonts/Montserrat-VF.ttf",
)
GREEN = "#0E4D3A"
CREAM = "#FFF6E8"
GOLD = "#E8A90C"
GOLD2 = "#F5B301"

SCHEMES = {
    "cream": {
        "bg": "radial-gradient(circle at 50% 38%, #FFF9EB 0%, #FFF3D6 60%, #FBEEC8 100%)",
        "fg": GREEN, "body": "#33473C", "muted": "#5A6B5E", "eyebrow": "#B07E00",
        "card_bg": "#FFFFFF", "card_border": "rgba(14,77,58,0.18)",
        "row_line": "rgba(14,77,58,0.14)", "num": GREEN,
    },
    "green": {
        "bg": "linear-gradient(150deg, #0E4D3A 0%, #0A3527 100%)",
        "fg": CREAM, "body": "#E4EFE8", "muted": "#C9D8CE", "eyebrow": GOLD,
        "card_bg": "rgba(255,246,232,0.08)", "card_border": "rgba(255,246,232,0.25)",
        "row_line": "rgba(255,246,232,0.18)", "num": GOLD2,
    },
}

COIN_LIGHT = """
<svg class="coin" viewBox="0 0 320 380">
  <path d="M160 92 V52" stroke="#1B5E20" stroke-width="7" stroke-linecap="round" fill="none"/>
  <path d="M160 58 C136 58 120 42 118 14 C144 16 158 34 160 58 Z" fill="#2E7D32"/>
  <path d="M160 58 C184 58 200 42 202 14 C176 16 162 34 160 58 Z" fill="#43A047"/>
  <circle cx="160" cy="235" r="132" fill="#F5B301"/>
  <circle cx="160" cy="235" r="132" fill="none" stroke="#D99A00" stroke-width="7"/>
  <circle cx="160" cy="235" r="106" fill="none" stroke="#D99A00" stroke-width="3" stroke-dasharray="4 9"/>
  <text x="160" y="282" text-anchor="middle" font-family="Montserrat" font-weight="800" font-size="150" fill="#0E4D3A">&#8377;</text>
</svg>
"""

COIN_DARK = """
<svg class="coin" viewBox="0 0 320 380">
  <path d="M160 92 V52" stroke="#7CB87F" stroke-width="7" stroke-linecap="round" fill="none"/>
  <path d="M160 58 C136 58 120 42 118 14 C144 16 158 34 160 58 Z" fill="#66BB6A"/>
  <path d="M160 58 C184 58 200 42 202 14 C176 16 162 34 160 58 Z" fill="#81C784"/>
  <circle cx="160" cy="235" r="132" fill="#F5B301"/>
  <circle cx="160" cy="235" r="132" fill="none" stroke="#D99A00" stroke-width="7"/>
  <circle cx="160" cy="235" r="106" fill="none" stroke="#D99A00" stroke-width="3" stroke-dasharray="4 9"/>
  <text x="160" y="282" text-anchor="middle" font-family="Montserrat" font-weight="800" font-size="150" fill="#0E4D3A">&#8377;</text>
</svg>
"""


def base_css(s):
    return f"""
  @font-face {{
    font-family: 'Montserrat';
    src: url('{FONT_URL}') format('truetype');
    font-weight: 100 900;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    width: 1080px; height: 1080px;
    background: {s['bg']};
    font-family: 'Montserrat', sans-serif;
    overflow: hidden;
    position: relative;
    color: {s['fg']};
  }}
  .footer {{
    position: absolute;
    bottom: 54px; left: 90px; right: 90px;
    display: flex; justify-content: space-between; align-items: center;
    font-weight: 700; font-size: 28px; letter-spacing: 0.28em;
  }}
  .footer .page {{ letter-spacing: 0.1em; font-weight: 600; }}
  .rule {{
    width: 130px; height: 7px; background: {GOLD};
    border-radius: 4px; margin: 32px 0 30px 0;
  }}
  .card {{
    background: {s['card_bg']};
    border: 2px solid {s['card_border']};
    border-radius: 28px;
    padding: 34px 44px 22px 44px;
  }}
  .card-title {{
    font-weight: 700; font-size: 34px; letter-spacing: 0.04em;
    margin-bottom: 22px;
  }}
"""


PAGE_TOTAL = 6


def footer(page_no, total=None):
    t = total if total is not None else PAGE_TOTAL
    return f'<div class="footer"><span>RUPEE SENSE</span><span class="page">{page_no} / {t}</span></div>'


def cover(scheme, eyebrow, title, sub, title_size=118):
    s = SCHEMES[scheme]
    coin = COIN_LIGHT if scheme == "cream" else COIN_DARK
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
{base_css(s)}
  .wrap {{
    height: 100%;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    text-align: center;
    padding: 0 90px 60px 90px;
  }}
  .eyebrow {{
    font-weight: 700; font-size: 32px; letter-spacing: 0.34em; text-indent: 0.34em;
    color: {s['eyebrow']};
    margin-bottom: 36px;
  }}
  .title {{
    font-weight: 800; font-size: {title_size}px; line-height: 1.04; letter-spacing: 0.01em;
  }}
  .rule {{ margin: 40px 0 34px 0; width: 150px; }}
  .sub {{
    font-weight: 500; font-size: 46px; line-height: 1.35;
    color: {s['muted'] if scheme == 'cream' else s['body']};
  }}
  .coin {{ width: 260px; margin-top: 56px; }}
</style>
</head>
<body>
  <div class="wrap">
    <div class="eyebrow">{eyebrow}</div>
    <div class="title">{title}</div>
    <div class="rule"></div>
    <div class="sub">{sub}</div>
    {coin}
  </div>
  {footer(1)}
</body>
</html>
"""


def standard(scheme, eyebrow, heading, body, inner, page_no, note=None, heading_size=82, total=6):
    s = SCHEMES[scheme]
    note_html = f'<div class="note">{note}</div>' if note else ""
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
{base_css(s)}
  .wrap {{
    height: 100%;
    display: flex; flex-direction: column;
    justify-content: center;
    padding: 0 90px 70px 90px;
  }}
  .eyebrow {{
    font-weight: 700; font-size: 30px; letter-spacing: 0.3em;
    color: {s['eyebrow']};
    margin-bottom: 28px;
  }}
  h1 {{
    font-weight: 800; font-size: {heading_size}px; line-height: 1.05;
  }}
  .body {{
    font-weight: 500; font-size: 42px; line-height: 1.45;
    color: {s['body']};
  }}
  .inner {{ margin-top: 40px; }}
  .note {{
    margin-top: 22px;
    font-weight: 500; font-size: 28px; line-height: 1.4;
    color: {s['muted']};
  }}
  .row {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 16px 0;
    border-top: 2px solid {s['row_line']};
    font-size: 42px;
  }}
  .row .yr {{ font-weight: 600; color: {s['body']}; }}
  .row .yr small {{ display: block; font-size: 29px; font-weight: 500; color: {s['muted']}; margin-top: 4px; }}
  .row .amt {{ font-weight: 800; color: {s['num']}; white-space: nowrap; padding-left: 20px; }}
  .check-row {{
    display: flex; align-items: center; gap: 22px;
    padding: 20px 0;
    border-top: 2px solid {s['row_line']};
    font-size: 42px; font-weight: 600; color: {s['body']};
  }}
  .check {{
    flex: 0 0 auto;
    width: 52px; height: 52px; border-radius: 50%;
    background: {GOLD2}; color: {GREEN};
    display: flex; align-items: center; justify-content: center;
    font-size: 32px; font-weight: 800;
  }}
  .card-foot {{
    padding-top: 22px;
    border-top: 2px solid {s['row_line']};
    font-size: 32px; font-weight: 600; color: {s['fg']};
  }}
</style>
</head>
<body>
  <div class="wrap">
    <div class="eyebrow">{eyebrow}</div>
    <h1>{heading}</h1>
    <div class="rule"></div>
    <div class="body">{body}</div>
    <div class="inner">{inner}</div>
    {note_html}
  </div>
  {footer(page_no)}
</body>
</html>
"""


def rows_card(title, rows):
    items = ""
    for r in rows:
        if len(r) == 3:
            items += f'<div class="row"><span class="yr">{r[0]}<small>{r[1]}</small></span><span class="amt">{r[2]}</span></div>'
        else:
            items += f'<div class="row"><span class="yr">{r[0]}</span><span class="amt">{r[1]}</span></div>'
    return f'<div class="card"><div class="card-title">{title}</div>{items}</div>'


def rows_card_foot(title, rows, foot):
    items = ""
    for r in rows:
        items += f'<div class="row"><span class="yr">{r[0]}</span><span class="amt">{r[1]}</span></div>'
    return f'<div class="card"><div class="card-title">{title}</div>{items}<div class="card-foot">{foot}</div></div>'


def checklist_card(title, items):
    rows = "".join(
        f'<div class="check-row"><span class="check">&#10003;</span><span>{t}</span></div>'
        for t in items
    )
    return f'<div class="card"><div class="card-title">{title}</div>{rows}</div>'


def bars_page(scheme, eyebrow, heading, body, bars, page_no):
    s = SCHEMES[scheme]
    bars_html = ""
    for label, pct, color in bars:
        bars_html += f"""
    <div class="bar-block">
      <div class="bar-label"><span>{label}</span><span class="bar-pct">{pct}%</span></div>
      <div class="track"><div class="fill" style="width: {pct * 2}%; background: {color};"></div></div>
    </div>"""
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
{base_css(s)}
  .wrap {{
    height: 100%;
    display: flex; flex-direction: column;
    justify-content: center;
    padding: 0 90px 70px 90px;
  }}
  .eyebrow {{
    font-weight: 700; font-size: 30px; letter-spacing: 0.3em;
    color: {s['eyebrow']};
    margin-bottom: 28px;
  }}
  h1 {{ font-weight: 800; font-size: 88px; line-height: 1.05; }}
  .body {{
    font-weight: 500; font-size: 45px; line-height: 1.45;
    color: {s['body']};
  }}
  .bars {{ margin-top: 56px; }}
  .bar-block {{ margin-bottom: 44px; }}
  .bar-label {{
    display: flex; justify-content: space-between; align-items: baseline;
    font-weight: 700; font-size: 38px; letter-spacing: 0.06em;
    margin-bottom: 16px;
  }}
  .bar-pct {{ font-weight: 800; font-size: 46px; color: {s['num']}; }}
  .track {{
    height: 44px; border-radius: 22px;
    background: rgba(255,246,232,0.16);
    overflow: hidden;
  }}
  .fill {{ height: 100%; border-radius: 22px; }}
</style>
</head>
<body>
  <div class="wrap">
    <div class="eyebrow">{eyebrow}</div>
    <h1>{heading}</h1>
    <div class="rule"></div>
    <div class="body">{body}</div>
    <div class="bars">{bars_html}
    </div>
  </div>
  {footer(page_no)}
</body>
</html>
"""


def compare_page(scheme, eyebrow, heading, body, groups, page_no):
    s = SCHEMES[scheme]
    groups_html = ""
    for title, items in groups:
        groups_html += f"""
    <div class="mini">
      <div class="mini-title">{title}</div>
      <div class="mini-items">{items}</div>
    </div>"""
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
{base_css(s)}
  .wrap {{
    height: 100%;
    display: flex; flex-direction: column;
    justify-content: center;
    padding: 0 90px 70px 90px;
  }}
  .eyebrow {{
    font-weight: 700; font-size: 30px; letter-spacing: 0.3em;
    color: {s['eyebrow']};
    margin-bottom: 28px;
  }}
  h1 {{ font-weight: 800; font-size: 88px; line-height: 1.05; }}
  .body {{
    font-weight: 500; font-size: 45px; line-height: 1.45;
    color: {s['body']};
  }}
  .minis {{ margin-top: 52px; }}
  .mini {{
    background: {s['card_bg']};
    border: 2px solid {s['card_border']};
    border-radius: 28px;
    padding: 34px 44px;
    margin-bottom: 28px;
  }}
  .mini-title {{
    font-weight: 800; font-size: 36px; letter-spacing: 0.12em;
    color: {s['num']};
    margin-bottom: 12px;
  }}
  .mini-items {{
    font-weight: 500; font-size: 40px; line-height: 1.4;
    color: {s['body']};
  }}
</style>
</head>
<body>
  <div class="wrap">
    <div class="eyebrow">{eyebrow}</div>
    <h1>{heading}</h1>
    <div class="rule"></div>
    <div class="body">{body}</div>
    <div class="minis">{groups_html}
    </div>
  </div>
  {footer(page_no)}
</body>
</html>
"""


def list_page(scheme, eyebrow, heading, body, items, page_no):
    s = SCHEMES[scheme]
    items_html = ""
    for num, title, line in items:
        items_html += f"""
    <div class="item">
      <div class="num">{num}</div>
      <div class="item-text"><div class="item-title">{title}</div><div class="item-line">{line}</div></div>
    </div>"""
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
{base_css(s)}
  .wrap {{
    height: 100%;
    display: flex; flex-direction: column;
    justify-content: center;
    padding: 0 90px 70px 90px;
  }}
  .eyebrow {{
    font-weight: 700; font-size: 30px; letter-spacing: 0.3em;
    color: {s['eyebrow']};
    margin-bottom: 28px;
  }}
  h1 {{ font-weight: 800; font-size: 88px; line-height: 1.05; }}
  .body {{
    font-weight: 500; font-size: 45px; line-height: 1.45;
    color: {s['body']};
  }}
  .items {{ margin-top: 52px; }}
  .item {{ display: flex; gap: 32px; margin-bottom: 40px; align-items: flex-start; }}
  .num {{
    flex: 0 0 auto;
    width: 84px; height: 84px; border-radius: 50%;
    background: {GOLD2}; color: {GREEN};
    display: flex; align-items: center; justify-content: center;
    font-size: 46px; font-weight: 800;
  }}
  .item-title {{ font-weight: 800; font-size: 44px; line-height: 1.2; }}
  .item-line {{ font-weight: 500; font-size: 38px; line-height: 1.35; color: {s['body']}; margin-top: 6px; }}
</style>
</head>
<body>
  <div class="wrap">
    <div class="eyebrow">{eyebrow}</div>
    <h1>{heading}</h1>
    <div class="rule"></div>
    <div class="body">{body}</div>
    <div class="items">{items_html}
    </div>
  </div>
  {footer(page_no)}
</body>
</html>
"""


def closing(scheme, big, sub):
    s = SCHEMES[scheme]
    coin = COIN_DARK if scheme == "green" else COIN_LIGHT
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
{base_css(s)}
  .wrap {{
    height: 100%;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    text-align: center;
    padding: 0 90px 60px 90px;
  }}
  .eyebrow {{
    font-weight: 700; font-size: 32px; letter-spacing: 0.34em; text-indent: 0.34em;
    color: {s['eyebrow']};
    margin-bottom: 36px;
  }}
  .big {{
    font-weight: 800; font-size: 92px; line-height: 1.12;
  }}
  .rule {{ margin: 40px 0 34px 0; width: 150px; }}
  .sub {{
    font-weight: 500; font-size: 44px; line-height: 1.4;
    color: {s['body']};
  }}
  .coin {{ width: 220px; margin-top: 56px; }}
</style>
</head>
<body>
  <div class="wrap">
    <div class="eyebrow">RUPEE SENSE</div>
    <div class="big">{big}</div>
    <div class="rule"></div>
    <div class="sub">{sub}</div>
    {coin}
  </div>
  {footer(PAGE_TOTAL)}
</body>
</html>
"""
