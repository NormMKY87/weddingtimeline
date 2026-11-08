import re, html, pathlib
SRC = pathlib.Path(__file__).resolve().parent.parent
OUT = pathlib.Path(__file__).parent / 'consult-call-kit.html'

def smart(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'"([^"]*)"', '“\\1”', s)
    s = s.replace("'", '’')
    return s

def md_to_html(text, drop_h1=True):
    out, para, lst = [], [], None
    def flush_p():
        nonlocal para
        if para:
            out.append('<p>' + smart(' '.join(para)) + '</p>')
            para = []
    def close_list():
        nonlocal lst
        if lst:
            out.append('</%s>' % lst)
            lst = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line:
            flush_p(); close_list(); continue
        if line.startswith('# '):
            flush_p(); close_list()
            if not drop_h1: out.append('<h1>%s</h1>' % smart(line[2:]))
            continue
        if line.startswith('## '):
            flush_p(); close_list(); out.append('<h2>%s</h2>' % smart(line[3:])); continue
        m = re.match(r'^(\d+)\. (.*)', line)
        if m:
            flush_p()
            if lst != 'ol': close_list(); out.append('<ol>'); lst = 'ol'
            out.append('<li>%s</li>' % smart(m.group(2))); continue
        if line.startswith('- '):
            flush_p()
            if lst != 'ul': close_list(); out.append('<ul>'); lst = 'ul'
            out.append('<li>%s</li>' % smart(line[2:])); continue
        if lst and raw.startswith('  '):
            out[-1] = out[-1][:-5] + ' ' + smart(line.strip()) + '</li>'; continue
        close_list(); para.append(line)
    flush_p(); close_list()
    return '\n'.join(out)

sections = [
    ('01', 'The run sheet', 'run-sheet.md', 'runsheet'),
    ('02', 'The timeline on the call', 'timeline-on-the-call.md', ''),
    ('03', 'The recording habit', 'recording-habit.md', ''),
    ('04', 'The objections, in depth', 'objections.md', ''),
    ('05', 'The ten questions', 'ten-questions.md', ''),
]

def first_para(text):
    for block in text.split('\n\n'):
        b = block.strip()
        if b and not b.startswith('#'):
            return b.replace('\n', ' ')
    return ''

body = []
for num, title, fn, cls in sections:
    text = (SRC / fn).read_text()
    lead = first_para(text)
    rest = text.replace(lead, '', 1)
    body.append(f'''
<section class="chapter {cls}">
  <header class="chapter-head">
    <div class="num">{num}</div>
    <h1>{smart(title)}</h1>
    <p class="lead">{smart(lead)}</p>
  </header>
  <div class="body">{md_to_html(rest)}</div>
</section>''')

contents_rows = '\n'.join(
    f'<div class="toc-row"><span class="toc-num">{n}</span><span class="toc-title">{smart(t)}</span></div>'
    for n, t, _, _ in sections)

intro = md_to_html('''
This kit exists to kill one sentence: "I don't know what to say on a consult." Everything in it is what I actually use. The run sheet is the page I keep beside the screen. The timeline method is how I run discovery and the recommendation at the same time. The recording habit is how I got better at this faster than anything else I tried. The objections section is the long form of what I say when a couple hesitates, and the position on discounting that sits underneath it. The ten questions are how I hear the budget and the decision makers without ever asking for them.

Read the run sheet first and print it. Read the timeline section before your next call and build your day grid, even if it is a spreadsheet. Start recording on the next call. Then read the objections and the questions once each, and let them come up on their own.

Nothing here has a price in it. Your numbers are yours. What this kit gives you is the shape of a call that earns the booking and leaves the couple better off whichever way they decide.
''')

html_doc = f'''<!doctype html>
<html lang="en-AU"><head><meta charset="utf-8">
<title>The Consult Call Kit</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root {{
  --bg:#F7F3EC; --ink:#26231F; --muted:#6F675C; --accent:#8C6A3F; --rule:#D9CFC0; --soft:#EFE8DC;
}}
@page {{ size: A4; margin: 20mm 20mm 24mm 20mm; }}
* {{ box-sizing: border-box; }}
html, body {{ margin:0; padding:0; background:var(--bg); color:var(--ink); }}
body {{ font-family: 'Inter', 'Liberation Sans', sans-serif; font-size: 10.4pt; line-height: 1.55; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
h1, h2, .num, .toc-num, .cover h1, .cover .sub {{ font-family: 'Cormorant Garamond', 'Liberation Serif', serif; font-weight: 500; }}
.page {{ page-break-after: always; }}
.chapter {{ page-break-before: always; }}
/* cover */
.cover {{ display:flex; flex-direction:column; justify-content:space-between; background: var(--ink); color: var(--bg); width:210mm; height:297mm; padding: 22mm 20mm; }}
.coverdoc {{ background: var(--ink); }}
.coverdoc @page {{ margin:0; }}
.cover .kicker {{ font-size: 8.5pt; letter-spacing: .18em; text-transform: uppercase; color: #C9B894; }}
.cover h1 {{ font-size: 54pt; line-height: 1.02; margin: 0 0 10mm 0; font-weight: 400; }}
.cover .sub {{ font-size: 16pt; line-height: 1.35; max-width: 140mm; color: #E9E1D2; font-weight: 400; }}
.cover .foot {{ display:flex; justify-content:space-between; font-size: 9pt; color:#C9B894; letter-spacing:.06em; border-top: 1px solid #5a5248; padding-top: 6mm; }}
/* intro + contents */
.intro h1 {{ font-size: 30pt; font-weight: 400; margin: 0 0 8mm; }}
.intro .body p {{ font-size: 11pt; }}
.toc {{ margin-top: 12mm; border-top: 1px solid var(--rule); }}
.toc-row {{ display:flex; gap: 8mm; align-items: baseline; padding: 4.2mm 0; border-bottom: 1px solid var(--rule); }}
.toc-num {{ font-size: 15pt; color: var(--accent); width: 12mm; }}
.toc-title {{ font-family:'Cormorant Garamond', serif; font-size: 17pt; }}
/* chapters */
.chapter-head {{ border-top: 2px solid var(--ink); padding-top: 5mm; margin-bottom: 8mm; }}
.chapter-head .num {{ font-size: 13pt; color: var(--accent); letter-spacing: .08em; }}
.chapter-head h1 {{ font-size: 32pt; line-height: 1.05; margin: 1mm 0 5mm; font-weight: 400; }}
.chapter-head .lead {{ font-family:'Cormorant Garamond', serif; font-size: 15pt; line-height: 1.35; color: var(--ink); margin:0; max-width: 150mm; }}
.body h2 {{ font-size: 17pt; margin: 8mm 0 2.5mm; line-height: 1.15; page-break-after: avoid; }}
.body p {{ margin: 0 0 3.2mm; }}
.body ol, .body ul {{ margin: 0 0 3.5mm; padding-left: 5.5mm; }}
.body li {{ margin-bottom: 1.6mm; }}
.body li::marker {{ color: var(--accent); font-weight: 600; }}
/* run sheet, one page */
.runsheet .chapter-head {{ margin-bottom: 5mm; }}
.runsheet .chapter-head h1 {{ font-size: 28pt; margin-bottom: 3mm; }}
.runsheet .chapter-head .lead {{ font-size: 12.5pt; max-width: 170mm; }}
.runsheet .body {{ column-count: 2; column-gap: 9mm; column-rule: 1px solid var(--rule); font-size: 8.9pt; line-height: 1.45; }}
.runsheet .body h2 {{ font-size: 13pt; margin: 3.2mm 0 1.4mm; break-after: avoid; }}
.runsheet .body h2:first-child {{ margin-top: 0; }}
.runsheet .body p {{ margin: 0 0 2mm; }}
.runsheet .body ol {{ margin: 0 0 2mm; padding-left: 4.5mm; }}
.runsheet .body li {{ margin-bottom: 0.8mm; }}
/* closing */
.closing h1 {{ font-size: 30pt; font-weight: 400; margin: 0 0 8mm; }}
.closing p {{ font-size: 11pt; max-width: 150mm; }}
</style></head><body>

<section class="page cover">
  <div class="kicker">Part-Time to Full-Time &nbsp;&middot;&nbsp; The Consult Call Kit</div>
  <div>
    <h1>The Consult<br>Call Kit</h1>
    <p class="sub">The one page run sheet, the timeline I build on the call, the recording habit, the five objections in depth, and the ten questions that surface budget and decision makers without asking for them.</p>
  </div>
  <div class="foot"><span>Norman Yap</span><span>2026 edition</span></div>
</section>

<section class="page intro">
  <h1>How to use this kit</h1>
  <div class="body">{intro}</div>
  <div class="toc">{contents_rows}</div>
</section>

{''.join(body)}

<section class="chapter closing">
  <header class="chapter-head"><div class="num">After</div><h1>Where this goes next</h1></header>
  <div class="body">
  <p>Run three consults with the run sheet beside you and the recorder on. Do not try to use all of it at once. The first call, get the opening and the timeline right. The second, listen back and fix one thing. The third, run the ten questions and tick what you heard. By the fourth call the structure will have disappeared into the way you talk, which is the point.</p>
  <p>Keep three logs. Consults held against bookings made, so you know which band you are in. Every price objection in the couple’s exact words, dated, so your pricing decisions come from evidence. Every question a couple asks, tallied, so you always know what to post next.</p>
  <p>This kit is the consult worksheet from Module 3 of my program, Part-Time to Full-Time, where it sits alongside the proposal template and the pipeline that feeds it. If you bought the kit on its own and later join the program, what you paid here is credited. I do not sell the same pages twice.</p>
  </div>
</section>
</body></html>'''

head, rest = html_doc.split('<body>', 1)
cover_html, body_html = rest.split('<section class="page intro">', 1)
cover_doc = head.replace('@page {{ size: A4; margin: 20mm 20mm 24mm 20mm; }}', '@page { size: A4; margin: 0; }').replace('@page { size: A4; margin: 20mm 20mm 24mm 20mm; }', '@page { size: A4; margin: 0; }') + '<body class="coverdoc">' + cover_html + '</body></html>'
body_doc = head + '<body><section class="page intro">' + body_html
pathlib.Path(OUT.parent / 'cover.html').write_text(cover_doc)
pathlib.Path(OUT.parent / 'body.html').write_text(body_doc)
print('wrote cover.html and body.html')
