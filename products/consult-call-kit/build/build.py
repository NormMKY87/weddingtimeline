import re, html, pathlib
HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent
OUT = HERE / 'consult-call-kit.html'

def smart(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'"([^"]*)"', '“\\1”', s)
    return s.replace("'", '’')

def md_to_html(text, drop_h1=True):
    out, para, lst = [], [], None
    def flush_p():
        nonlocal para
        if para:
            out.append('<p>' + smart(' '.join(para)) + '</p>'); para = []
    def close_list():
        nonlocal lst
        if lst: out.append('</%s>' % lst); lst = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line: flush_p(); close_list(); continue
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

def first_para(text):
    for block in text.split('\n\n'):
        b = block.strip()
        if b and not b.startswith('#'): return b.replace('\n', ' ')
    return ''

# num, title, file, css class, opener image (half page portrait) or None
sections = [
    ('01', 'The run sheet', 'run-sheet.md', 'runsheet', None),
    ('02', 'The timeline on the call', 'timeline-on-the-call.md', '', 'images/opener-timeline.jpg'),
    ('03', 'The recording habit', 'recording-habit.md', '', None),
    ('04', 'The objections, in depth', 'objections.md', '', None),
    ('05', 'The ten questions', 'ten-questions.md', '', 'images/opener-questions.jpg'),
    ('06', 'Make it yours', 'make-it-yours.md', 'fillin', None),
]
BREAKER_BEFORE = '04'

back = '<a class="back" href="#contents">Back to contents</a>'
body = []
for num, title, fn, cls, opener in sections:
    text = (SRC / fn).read_text()
    lead = first_para(text)
    rest = text.replace(lead, '', 1)
    sid = 's' + num
    if num == BREAKER_BEFORE:
        body.append('<section class="breaker bleed"><img src="images/breaker.jpg" alt=""></section>')
    if opener:
        body.append(f'''
<section class="opener bleed" id="{sid}">
  <div class="opener-img"><img src="{opener}" alt=""></div>
  <div class="opener-text">
    {back}
    <div class="num">{num}</div>
    <h1>{smart(title)}</h1>
    <p class="lead">{smart(lead)}</p>
  </div>
</section>
<section class="chapter {cls} continued">
  <div class="body">{md_to_html(rest)}</div>
</section>''')
    else:
        body.append(f'''
<section class="chapter {cls}" id="{sid}">
  <header class="chapter-head">
    {back}
    <div class="num">{num}</div>
    <h1>{smart(title)}</h1>
    <p class="lead">{smart(lead)}</p>
  </header>
  <div class="body">{md_to_html(rest)}</div>
</section>''')

contents_rows = '\n'.join(
    f'<a class="toc-row" href="#s{n}"><span class="toc-num">{n}</span><span class="toc-title">{smart(t)}</span></a>'
    for n, t, _, _, _ in sections)

intro = md_to_html('''
This kit exists to kill one sentence: "I don't know what to say on a consult." Everything in it is what I actually use. The run sheet is the page I keep beside the screen. The timeline method is how I run discovery and the recommendation at the same time. The recording habit is how I got better at this faster than anything else I tried. The objections section is the long form of what I say when a couple hesitates, and the position on discounting that sits underneath it. The ten questions are how I hear the budget and the decision makers without ever asking for them.

Read the run sheet first and print it. Read the timeline section before your next call and build your day grid, even if it is a spreadsheet. Start recording on the next call. Then read the objections and the questions once each, and let them come up on their own.

Nothing here has a price in it, and nothing in it depends on my business. Wherever you see square brackets, that is where your business goes: your retainer, your range, your onboarding steps, your check-in day. The last section collects every bracket on one page so you can fill them once. Your numbers are yours.
''')

html_doc = f'''<!doctype html>
<html lang="en-AU"><head><meta charset="utf-8">
<title>The Consult Call Kit</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root {{ --bg:#F7F3EC; --ink:#26231F; --muted:#6F675C; --accent:#8C6A3F; --rule:#D9CFC0; --soft:#EFE8DC; }}
@page {{ size: A4; margin: 24mm 22mm 26mm 22mm; }}
@page bleed {{ margin: 0; }}
* {{ box-sizing: border-box; }}
html, body {{ margin:0; padding:0; background:var(--bg); color:var(--ink); }}
body {{ font-family: 'Inter', 'Liberation Sans', sans-serif; font-size: 10.6pt; line-height: 1.62; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
h1, h2, .num, .toc-num {{ font-family: 'Cormorant Garamond', 'Liberation Serif', serif; font-weight: 500; }}
a {{ color: inherit; text-decoration: none; }}
.bleed {{ page: bleed; width: 210mm; height: 297mm; overflow: hidden; page-break-before: always; page-break-after: always; position: relative; }}
img {{ display:block; }}

/* cover */
.cover {{ background: var(--ink); }}
.cover img {{ position:absolute; inset:0; width:100%; height:279mm; object-fit: cover; object-position: center 30%; }}
.cover .shade {{ position:absolute; left:0; right:0; top:0; height:279mm; background: linear-gradient(180deg, rgba(38,35,31,0) 45%, rgba(38,35,31,.78) 100%); }}
.cover .text {{ position:absolute; left:22mm; right:22mm; bottom:34mm; color: var(--bg); }}
.cover .kicker {{ font-size: 8.5pt; letter-spacing: .18em; text-transform: uppercase; color: #D9C8A4; margin-bottom: 6mm; }}
.cover h1 {{ font-size: 56pt; line-height: 1.0; margin: 0 0 8mm 0; font-weight: 400; font-family:'Cormorant Garamond', serif; }}
.cover .sub {{ font-family:'Cormorant Garamond', serif; font-size: 15.5pt; line-height: 1.35; max-width: 130mm; color: #EFE8DC; }}
.cover .band {{ position:absolute; left:0; right:0; bottom:0; height:18mm; background: var(--ink); }}
.cover .byline {{ position:absolute; left:22mm; right:22mm; bottom:22mm; display:flex; justify-content:space-between; font-size: 8.5pt; letter-spacing:.1em; text-transform: uppercase; color:#D9C8A4; }}

/* intro and contents */
.page {{ page-break-after: always; }}
.intro h1 {{ font-size: 32pt; font-weight: 400; margin: 0 0 10mm; }}
.intro .body p {{ font-size: 11pt; margin: 0 0 4.5mm; }}
.tocpage h1 {{ font-size: 32pt; font-weight: 400; margin: 0 0 14mm; }}
.toc {{ border-top: 1px solid var(--ink); }}
.toc-row {{ display:flex; gap: 10mm; align-items: baseline; padding: 8mm 0; border-bottom: 1px solid var(--rule); }}
.toc-num {{ font-size: 15pt; color: var(--accent); width: 12mm; }}
.toc-title {{ font-family:'Cormorant Garamond', serif; font-size: 21pt; }}
.toc-hint {{ margin-top: 8mm; font-size: 8.5pt; color: var(--muted); }}

/* chapters */
.chapter {{ page-break-before: always; }}
.chapter.continued {{ page-break-before: always; }}
.chapter-head {{ border-top: 2px solid var(--ink); padding-top: 6mm; margin-bottom: 14mm; position: relative; }}
.back {{ display:inline-block; font-size: 8pt; letter-spacing: .12em; text-transform: uppercase; color: var(--accent); border-bottom: 1px solid var(--rule); padding-bottom: 1mm; }}
.chapter-head .back {{ position:absolute; right:0; top:6.5mm; }}
.chapter-head .num {{ font-size: 13pt; color: var(--accent); letter-spacing: .08em; }}
.chapter-head h1 {{ font-size: 34pt; line-height: 1.05; margin: 1mm 0 7mm; font-weight: 400; }}
.chapter-head .lead {{ font-family:'Cormorant Garamond', serif; font-size: 15.5pt; line-height: 1.38; margin:0; max-width: 148mm; }}
.body h2 {{ font-size: 17.5pt; margin: 11mm 0 3.5mm; line-height: 1.15; page-break-after: avoid; }}
.body h2:first-child {{ margin-top: 0; }}
.body p {{ margin: 0 0 4.2mm; }}
.body ol, .body ul {{ margin: 0 0 4.5mm; padding-left: 5.5mm; }}
.body li {{ margin-bottom: 2.2mm; }}
.body li::marker {{ color: var(--accent); font-weight: 600; }}
.endlink {{ margin-top: 12mm; }}

/* openers with a half page portrait */
.opener {{ display:flex; }}
.opener-img {{ width: 105mm; height: 279mm; }}
.opener-img img {{ width:100%; height:100%; object-fit: cover; }}
.opener-text {{ width: 105mm; padding: 26mm 20mm 0 14mm; position: relative; }}
.opener-text .back {{ margin-bottom: 14mm; }}
.opener-text .num {{ font-size: 13pt; color: var(--accent); letter-spacing: .08em; }}
.opener-text h1 {{ font-size: 30pt; line-height: 1.05; margin: 1mm 0 7mm; font-weight: 400; }}
.opener-text .lead {{ font-family:'Cormorant Garamond', serif; font-size: 13.5pt; line-height: 1.4; margin:0; }}
.opener::after {{ content:''; position:absolute; left:0; right:0; bottom:0; height:18mm; background: var(--bg); }}

/* breaker */
.breaker img {{ width:100%; height:279mm; object-fit: cover; object-position: center 20%; }}
.breaker::after {{ content:''; position:absolute; left:0; right:0; bottom:0; height:18mm; background: var(--bg); }}

/* run sheet, one page */
.runsheet .chapter-head {{ margin-bottom: 6mm; }}
.runsheet .chapter-head h1 {{ font-size: 28pt; margin-bottom: 3mm; }}
.runsheet .chapter-head .lead {{ font-size: 12pt; max-width: 166mm; }}
.runsheet .body {{ column-count: 2; column-gap: 9mm; column-rule: 1px solid var(--rule); font-size: 8.7pt; line-height: 1.47; }}
.runsheet .body h2 {{ font-size: 12.5pt; margin: 3.2mm 0 1.4mm; break-after: avoid; }}
.runsheet .body h2:first-child {{ margin-top: 0; }}
.runsheet .body p {{ margin: 0 0 2mm; }}
.runsheet .body ol {{ margin: 0 0 2mm; padding-left: 4.5mm; }}
.runsheet .body li {{ margin-bottom: 0.8mm; }}
.runsheet .endlink {{ display:none; }}

/* fill-in page */
.fillin .body {{ counter-reset: fill; }}
.fillin .body ol {{ list-style: none; padding-left: 0; margin: 0; }}
.fillin .body li {{ position: relative; padding: 0 0 12mm 9mm; margin: 0 0 4mm; border-bottom: 1px solid var(--rule); font-size: 9.8pt; }}
.fillin .body li::before {{ content: counter(fill) '.'; counter-increment: fill; position: absolute; left: 0; top: 0; font-family: 'Cormorant Garamond', serif; font-size: 12pt; color: var(--accent); }}
.fillin .body h2 {{ margin-top: 9mm; }}

/* closing */
.closing h1 {{ font-size: 32pt; font-weight: 400; margin: 0 0 10mm; }}
.closing p {{ font-size: 11pt; max-width: 150mm; }}
</style></head><body>

<section class="cover bleed">
  <img src="images/cover.jpg" alt="">
  <div class="shade"></div>
  <div class="text">
    <div class="kicker">Part-Time to Full-Time</div>
    <h1>The Consult<br>Call Kit</h1>
    <p class="sub">The one page run sheet, the timeline I build on the call, the recording habit, the five objections in depth, and the ten questions that surface budget and decision makers without asking for them.</p>
  </div>
  <div class="band"></div>
  <div class="byline"><span>Norman Yap</span><span>2026 edition</span></div>
</section>

<section class="page tocpage" id="contents">
  <h1>Contents</h1>
  <div class="toc">{contents_rows}</div>
  <p class="toc-hint">Every title above is a link. Every section opens with a link back to this page.</p>
</section>

<section class="page intro">
  <h1>How to use this kit</h1>
  <div class="body">{intro}</div>
</section>

{''.join(body)}

<section class="chapter closing">
  <header class="chapter-head">{back}<div class="num">After</div><h1>Where this goes next</h1></header>
  <div class="body">
  <p>Run three consults with the run sheet beside you and the recorder on. Do not try to use all of it at once. The first call, get the opening and the timeline right. The second, listen back and fix one thing. The third, run the ten questions and tick what you heard. By the fourth call the structure will have disappeared into the way you talk, which is the point.</p>
  <p>Keep three logs. Consults held against bookings made, so you know which band you are in. Every price objection in the couple’s exact words, dated, so your pricing decisions come from evidence. Every question a couple asks, tallied, so you always know what to post next.</p>
  <p>This kit is the consult worksheet from Module 3 of my program, Part-Time to Full-Time, where it sits alongside the proposal template and the pipeline that feeds it. If you bought the kit on its own and later join the program, what you paid here is credited. I do not sell the same pages twice.</p>
  </div>
</section>
</body></html>'''
OUT.write_text(html_doc)
print('wrote', OUT.name, len(html_doc))
