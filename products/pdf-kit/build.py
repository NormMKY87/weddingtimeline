"""Builds a product PDF from its markdown files.

    python products/pdf-kit/build.py warm-list-emails
    python products/pdf-kit/build.py quiet-month-playbook

Reads products/<slug>/NN-*.md in order, writes products/<slug>/pdf/<slug>.html and
products/<slug>/<pdf name>.pdf. One page per section: sections are split on a line of ---.

Markdown conventions the kit understands:
  ###### text            kicker above a page title
  # Title                page title
  **A:** x | **B:** y    a line of labelled facts under the title
  **Email** then a > blockquote   a message card (also SMS, Instagram DM)
  Skip it when: ...      the skip note
  The email: ...         a pointer to another product
  :::grid ... :::        three columns, one paragraph each
  :::opener <photo> ... :::   a full bleed photograph page (photo from mockups/photos)
"""
import re, sys, subprocess, pathlib
import markdown

ROOT = pathlib.Path(__file__).resolve().parents[2]
PRODUCTS = {
    'warm-list-emails': dict(
        title='The Warm List Emails', pdf='the-warm-list-emails.pdf', cover='08-warm-list-emails.png',
        kicker='A companion to the Booking Pack',
        lede='Eleven emails for the people who already know your work. Past couples, their families, and the venues and vendors you have stood beside.',
        contents=[('Start here', 'How this works, and the three rules behind every email'),
                  ('Build your list', 'Thirty minutes, six groups, and the map of all eleven emails'),
                  ('Part one: past couples', 'Emails 1 to 7, from the gallery follow-up to the newly engaged guest'),
                  ('Part two: venues and vendors', 'Emails 8 to 11, from the venue gallery to the open dates swap'),
                  ('The sending plan', 'Two weeks, one group a day, then the routine after every wedding')],
        close='Open this, find the person, change the line in brackets, press send.'),
    'quiet-month-playbook': dict(
        title='The Quiet Month Playbook', pdf='the-quiet-month-playbook.pdf', cover='09-quiet-month-playbook.png',
        kicker='A bonus with the Booking Pack',
        lede='Twenty one plays for the month the calendar has a gap. Sorted so the fastest come first.',
        contents=[('Start here', 'How this works, and the check to run before play one'),
                  ('List one: people who know you', 'Plays 1 to 7. These can pay back in days'),
                  ('List two: people who send you work', 'Plays 8 to 14. These can pay back in weeks'),
                  ('List three: people who have never heard of you', 'Plays 15 to 21. These can pay back in months'),
                  ('The scorecard', 'One line a play, so you know which five are yours')],
        close='Pick one play from the first list. Finish it before you read the rest.'),
}

CSS = r"""
@font-face { font-family: "Cormorant Garamond"; font-style: normal; font-weight: 300 700; src: url("FONTS/cormorant-garamond-latin.woff2") format("woff2"); }
@font-face { font-family: "Cormorant Garamond"; font-style: italic; font-weight: 300 700; src: url("FONTS/cormorant-garamond-italic-latin.woff2") format("woff2"); }
@font-face { font-family: "Karla"; font-style: normal; font-weight: 200 800; src: url("FONTS/karla-latin.woff2") format("woff2"); }
@page { size: A4; margin: 20mm 18mm 22mm;
  @bottom-left { content: "TITLE"; font: 400 7pt "Karla", sans-serif; letter-spacing: .14em; text-transform: uppercase; color: #7C7268; }
  @bottom-right { content: counter(page); font: 400 7.5pt "Karla", sans-serif; color: #7C7268; } }
@page bleed { margin: 0; @bottom-left { content: none; } @bottom-right { content: none; } }
:root { --ink: #221E1A; --ink-2: #3D3631; --mute: #7C7268; --rule: #D9D1C7; --clay: #B5603B; --clay-deep: #8E4A2D; --card: #F6F1E8; --white: #FBF8F2; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body { font-family: "Karla", "Helvetica Neue", Arial, sans-serif; color: var(--ink); font-size: 11pt; line-height: 1.58; -webkit-font-smoothing: antialiased; }
.page { break-after: page; }
.page:last-child { break-after: auto; }
.bleed { page: bleed; position: relative; width: 210mm; height: 297mm; overflow: hidden; }
.bleed img.full { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.kicker { font-size: 7.5pt; letter-spacing: .22em; text-transform: uppercase; color: var(--clay-deep); font-weight: 600; margin: 0 0 9pt; }
h2.title { font-family: "Cormorant Garamond", Georgia, serif; font-weight: 500; font-size: 36pt; line-height: 1.04; letter-spacing: -.005em; margin: 0 0 16pt; }
h3 { font-family: "Cormorant Garamond", Georgia, serif; font-weight: 500; font-size: 19pt; line-height: 1.15; margin: 20pt 0 7pt; break-after: avoid; }
p { margin: 0 0 8pt; max-width: 158mm; }
h2.title + p, .facts + p { font-size: 12.2pt; line-height: 1.52; color: var(--ink-2); margin-bottom: 12pt; }
strong { font-weight: 600; }
.v { color: var(--clay-deep); }
ul, ol { margin: 4pt 0 10pt; padding: 0; list-style: none; max-width: 158mm; }
ul li { position: relative; padding-left: 14pt; margin-bottom: 5pt; }
ul li::before { content: ""; position: absolute; left: 1pt; top: .68em; width: 5pt; height: 1px; background: var(--clay); }
ol { counter-reset: n; margin-top: 10pt; }
ol li { counter-increment: n; position: relative; padding: 10pt 0 10pt 30pt; border-top: 1px solid var(--rule); margin: 0; }
ol li:last-child { border-bottom: 1px solid var(--rule); }
ol li::before { content: counter(n); position: absolute; left: 2pt; top: 6pt; font-family: "Cormorant Garamond", Georgia, serif; font-size: 18pt; color: var(--clay-deep); }
/* facts under a title */
.facts { display: grid; grid-auto-flow: column; grid-auto-columns: 1fr; gap: 0 8mm; border-top: 1px solid var(--ink); border-bottom: 1px solid var(--rule); margin: 0 0 16pt; padding: 10pt 0 11pt; }
.facts div { font-size: 10.2pt; line-height: 1.4; }
.facts b { display: block; font-size: 6.8pt; letter-spacing: .18em; text-transform: uppercase; font-weight: 600; color: var(--mute); margin-bottom: 3pt; }
/* message cards */
.msg { background: var(--card); border-left: 2px solid var(--clay); padding: 15pt 19pt 8pt; margin: 12pt 0 12pt; break-inside: avoid; }
.msg .ch { display: block; text-transform: uppercase; letter-spacing: .18em; font-size: 6.8pt; color: var(--clay-deep); font-weight: 600; margin-bottom: 4pt; }
.msg .subj { font-size: 10.4pt; font-weight: 600; border-bottom: 1px solid rgb(34 30 26 / .14); padding-bottom: 7pt; margin-bottom: 8pt; }
.msg p { margin: 0 0 9pt; font-size: 10.8pt; line-height: 1.58; max-width: none; }
.pl { font-size: 6.6pt; letter-spacing: .16em; font-weight: 600; color: var(--clay-deep); margin-right: 3pt; }
.skip { font-size: 10.2pt; margin: 14pt 0 0; padding: 1pt 0 1pt 12pt; border-left: 2px solid var(--rule); color: var(--ink-2); }
.goes { font-size: 10.2pt; color: var(--ink-2); margin: 10pt 0 0; }
.goes b, .skip b { font-weight: 600; color: var(--ink); }
/* three columns */
.grid3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 7mm; margin: 6pt 0 12pt; }
.grid3 > div { border-top: 1px solid var(--ink); padding-top: 8pt; }
.grid3 h4 { font-family: "Cormorant Garamond", Georgia, serif; font-weight: 500; font-size: 14pt; line-height: 1.15; margin: 0 0 5pt; }
.grid3 p { font-size: 10pt; line-height: 1.5; margin: 0; }
/* tables */
table { width: 100%; border-collapse: collapse; font-size: 10pt; line-height: 1.4; margin: 8pt 0 12pt; break-inside: avoid; }
th { text-align: left; font-weight: 600; text-transform: uppercase; letter-spacing: .14em; font-size: 6.6pt; color: var(--mute); padding: 0 8pt 6pt 0; border-bottom: 1px solid var(--ink); }
td { padding: 8.5pt 8pt 8.5pt 0; border-bottom: 1px solid var(--rule); vertical-align: top; }
td:first-child:not(:empty) { white-space: nowrap; }
table.num td:first-child { font-family: "Cormorant Garamond", Georgia, serif; font-size: 13pt; line-height: 1; padding-top: 6pt; width: 9mm; color: var(--clay-deep); }
table.fill td { padding-top: 8.2pt; padding-bottom: 8.2pt; }
table.long td { padding-top: 4.6pt; padding-bottom: 4.6pt; }
table.long.num td:first-child { padding-top: 3pt; }
table.fill td:nth-child(n+3) { width: 27mm; border-left: 1px solid var(--rule); }
/* contents page */
.contents .top { display: flex; justify-content: space-between; font-size: 7.5pt; letter-spacing: .22em; text-transform: uppercase; color: var(--mute); border-bottom: 1px solid var(--ink); padding-bottom: 8pt; margin-bottom: 30mm; }
.contents h1 { font-family: "Cormorant Garamond", Georgia, serif; font-weight: 500; font-size: 46pt; line-height: 1; margin: 0 0 14pt; max-width: 150mm; }
.contents .lede { font-size: 12.5pt; line-height: 1.5; color: var(--ink-2); max-width: 135mm; margin-bottom: 22mm; }
.contents table td { padding: 9pt 10pt 9pt 0; font-size: 10pt; }
.contents table td:nth-child(2) { font-family: "Cormorant Garamond", Georgia, serif; font-size: 14.5pt; line-height: 1.1; white-space: nowrap; }
.contents table td:nth-child(3) { color: var(--mute); }
.contents .close { font-family: "Cormorant Garamond", Georgia, serif; font-style: italic; font-size: 15pt; line-height: 1.3; margin-top: 18mm; max-width: 120mm; }
/* photograph pages */
.opener::after { content: ""; position: absolute; inset: 0; background: linear-gradient(180deg, rgb(0 0 0 / .3), rgb(0 0 0 / 0) 24%, rgb(0 0 0 / 0) 40%, rgb(0 0 0 / .62) 66%, rgb(0 0 0 / .88)); }
.opener .txt { position: absolute; z-index: 2; left: 18mm; right: 18mm; bottom: 20mm; color: #fff; }
.opener .kicker { color: #fff; opacity: .9; }
.opener h2.title { font-size: 50pt; margin-bottom: 10pt; color: #fff; }
.opener .txt p { font-size: 13pt; line-height: 1.45; max-width: 120mm; color: #fff; }
/* play pages: a log pinned to the foot */
.page.play { min-height: 253mm; display: flex; flex-direction: column; }
.log { margin-top: auto; display: grid; grid-template-columns: 1fr 1fr 2.4fr; gap: 0 8mm; border-top: 1px solid var(--ink); padding-top: 8pt; }
.log div { font-size: 6.8pt; letter-spacing: .18em; text-transform: uppercase; font-weight: 600; color: var(--mute); height: 15mm; border-bottom: 1px solid var(--rule); }
.opener .series { position: absolute; z-index: 2; left: 18mm; right: 18mm; top: 16mm; display: flex; justify-content: space-between; color: #fff; font-size: 7.5pt; letter-spacing: .22em; text-transform: uppercase; }
"""

def md(text):
    return markdown.markdown(text, extensions=['tables', 'nl2br', 'sane_lists'])

def facts(m):
    cells = re.findall(r'<strong>(.*?):</strong>\s*(.*?)(?=\s*\|\s*<strong>|$)', m.group(1), flags=re.S)
    return '<div class="facts">' + ''.join(f'<div><b>{k}</b>{v}</div>' for k, v in cells) + '</div>'

def page_html(src, title):
    src = src.strip()
    op = re.match(r':::opener (\S+)\n(.*?)\n:::', src, flags=re.S)
    if op:
        inner = md(op.group(2))
        inner = re.sub(r'<h6>(.*?)</h6>', r'<div class="kicker">\1</div>', inner)
        inner = re.sub(r'<h1>(.*?)</h1>', r'<h2 class="title">\1</h2>', inner)
        return (f'<section class="page bleed opener"><img class="full" src="PHOTOS/{op.group(1)}.jpg" alt="">'
                f'<div class="series"><span>{title}</span><span>Part-Time to Full-Time</span></div><div class="txt">{inner}</div></section>')
    def grid(m):
        cells = [c for c in re.split(r'\n\s*\n', m.group(1).strip()) if c.strip()]
        out = ''
        for c in cells:
            h, body = re.match(r'\*\*(.*?)\*\*\s*(.*)', c.strip(), flags=re.S).groups()
            out += f'<div><h4>{h.rstrip(".")}</h4><p>{body}</p></div>'
        return f'\n\n<div class="grid3">{out}</div>\n\n'
    src = re.sub(r':::grid\n(.*?)\n:::', grid, src, flags=re.S)
    h = md(src)
    h = re.sub(r'<h6>(.*?)</h6>', r'<div class="kicker">\1</div>', h)
    h = re.sub(r'<h1>(.*?)</h1>', r'<h2 class="title">\1</h2>', h)
    h = re.sub(r'<h2>(.*?)</h2>', r'<h3>\1</h3>', h)
    h = re.sub(r'<p>(<strong>[^<]*:</strong>[^\n]*?\|[^\n]*?)</p>', facts, h)
    h = re.sub(r'<p><strong>(Email|SMS|Instagram DM)</strong></p>\s*(?:<p>Subject: (.*?)</p>\s*)?<blockquote>',
               lambda m: f'<div class="msg"><span class="ch">{m.group(1)}</span>' + (f'<div class="subj">Subject: {m.group(2)}</div>' if m.group(2) else ''), h, flags=re.S)
    h = h.replace('</blockquote>', '</div>')
    h = h.replace('PERSONAL:', '<span class="pl">PERSONAL</span>')
    h = re.sub(r'<p>(Skip it when):\s*(.*?)</p>', r'<p class="skip"><b>\1:</b> \2</p>', h, flags=re.S)
    h = re.sub(r'<p>(The (?:email|replies)[^:<]*):\s*(.*?)</p>', r'<p class="goes"><b>\1:</b> \2</p>', h, flags=re.S)
    # numbered and fill-in tables
    def table(m):
        t = m.group(0)
        cls = []
        if re.search(r'<td>\d+</td>\s*<td>', t): cls.append('num')
        if t.count('<td></td>') > 12: cls.append('fill')
        if t.count('<tr>') > 11: cls.append('long')
        return t.replace('<table>', f'<table class="{" ".join(cls)}">', 1) if cls else t
    h = re.sub(r'<table>.*?</table>', table, h, flags=re.S)
    if re.search(r'<div class="kicker">(Play \d|Before play)', h):
        return f'<section class="page play">{h}<div class="log"><div>Date run</div><div>First enquiry</div><div>What came of it</div></div></section>'
    return f'<section class="page">{h}</section>'

def build(slug):
    p = PRODUCTS[slug]
    d = ROOT / 'products' / slug
    pages = []
    for f in sorted(d.glob('[0-9][0-9]-*.md')):
        pages += [s for s in re.split(r'\n---\n', f.read_text()) if s.strip()]
    body = ''.join(page_html(s, p['title']) for s in pages)
    body = re.sub(r'\[([^\[\]<>]{1,200})\]', r'<span class="v">[\1]</span>', body)
    rows = ''.join(f'<tr><td>{i}</td><td>{a}</td><td>{b}</td></tr>' for i, (a, b) in enumerate(p['contents'], 1))
    front = (f'<section class="page bleed"><img class="full" src="COVERS/{p["cover"]}" alt=""></section>'
             f'<section class="page contents"><div class="top"><span>Part-Time to Full-Time</span><span>First edition</span></div>'
             f'<div class="kicker">{p["kicker"]}</div><h1>{p["title"]}</h1><p class="lede">{p["lede"]}</p>'
             f'<div class="kicker">Inside</div><table class="num">{rows}</table><p class="close">{p["close"]}</p></section>')
    css = CSS.replace('TITLE', p['title']).replace('FONTS', '../../../mockups/fonts')
    html = (f'<!doctype html><html lang="en-AU"><head><meta charset="utf-8"><title>{p["title"]}</title><style>{css}</style></head><body>'
            + front + body + '</body></html>')
    html = html.replace('PHOTOS/', '../../../mockups/photos/').replace('COVERS/', '../../../mockups/out/covers-photo/')
    out = d / 'pdf'; out.mkdir(exist_ok=True)
    (out / f'{slug}.html').write_text(html)
    subprocess.run(['node', str(ROOT / 'products/pdf-kit/print.js'), str(out / f'{slug}.html'), str(d / p['pdf'])], check=True)
    print('built', d / p['pdf'], 'sections:', len(pages) + 2)

if __name__ == '__main__':
    for s in (sys.argv[1:] or PRODUCTS):
        build(s)
