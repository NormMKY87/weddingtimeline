import re, html, pathlib
HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent
OUT = HERE / 'consult-call-kit.html'

def smart(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'"([^"]*)"', '“\\1”', s)
    return s.replace("'", '’')

def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

def md_to_html(text, prefix='', drop_h1=True):
    out, para, lst, heads = [], [], None, []
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
            flush_p(); close_list()
            hid = f'{prefix}-{slug(line[3:])}'
            heads.append((hid, line[3:]))
            out.append(f'<h2 id="{hid}">{smart(line[3:])}</h2>'); continue
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
    return '\n'.join(out), heads

def first_para(text):
    for block in text.split('\n\n'):
        b = block.strip()
        if b and not b.startswith('#'): return b.replace('\n', ' ')
    return ''

MARK = '<span class="bleedmark">BLEEDMARK</span>'
back = '<a class="back" href="#contents">Back to contents</a>'

# num, title, file, css class, opener image (half page portrait) or None, breaker image before this section or None
sections = [
    ('01', 'The run sheet', 'run-sheet.md', 'runsheet', None, 'images/breaker-ceremony.jpg'),
    ('02', 'The timeline on the call', 'timeline-on-the-call.md', '', 'images/opener-timeline.jpg', None),
    ('03', 'The recording habit', 'recording-habit.md', '', 'images/opener-recording.jpg', None),
    ('04', 'The objections, in depth', 'objections.md', '', None, 'images/breaker-archway.jpg'),
    ('05', 'The ten questions', 'ten-questions.md', '', 'images/opener-questions.jpg', None),
    ('06', 'Make it yours', 'make-it-yours.md', 'fillin', 'images/opener-yours.jpg', None),
]

body = []
for num, title, fn, cls, opener, breaker in sections:
    text = (SRC / fn).read_text()
    lead = first_para(text)
    rest = text.replace(lead, '', 1)
    sid = 's' + num
    inner, heads = md_to_html(rest, prefix=sid)
    if breaker:
        body.append(f'<section class="breaker bleed">{MARK}<img src="{breaker}" alt=""></section>')
    if opener:
        mini = ''.join(f'<li><a href="#{h}">{smart(t)}</a></li>' for h, t in heads if not cls == 'fillin' or True)
        body.append(f'''
<section class="opener bleed" id="{sid}">{MARK}
  <div class="opener-img"><img src="{opener}" alt=""></div>
  <div class="opener-text">
    {back}
    <div class="num">{num}</div>
    <h1>{smart(title)}</h1>
    <p class="lead">{smart(lead)}</p>
    <div class="label">In this section</div>
    <ol class="mini">{mini}</ol>
  </div>
</section>
<section class="chapter {cls} continued">
  <div class="body">{inner}</div>
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
  <div class="body">{inner}</div>
</section>''')

contents_rows = '\n'.join(
    f'<a class="toc-row" href="#s{n}"><span class="toc-num">{n}</span><span class="toc-title">{smart(t)}</span></a>'
    for n, t, _, _, _, _ in sections)

intro, _ = md_to_html('''
This kit exists to kill one sentence: "I don't know what to say on a consult." Everything in it is what I actually use. The run sheet is the page I keep beside the screen. The timeline method is how I run discovery and the recommendation at the same time. The recording habit is how I got better at this faster than anything else I tried. The objections section is the long form of what I say when a couple hesitates, and the position on discounting that sits underneath it. The ten questions are how I hear the budget and the decision makers without ever asking for them.

Read the run sheet first and print it. Read the timeline section before your next call and build your day grid, even if it is a spreadsheet. Start recording on the next call. Then read the objections and the questions once each, and let them come up on their own.

Nothing here has a price in it, and nothing in it depends on my business. Wherever you see square brackets, that is where your business goes: your retainer, your range, your onboarding steps, your check-in day. The last section collects every bracket on one page so you can fill them once. Your numbers are yours.
''')

html_doc = f'''<!doctype html>
<html lang="en-AU"><head><meta charset="utf-8">
<title>The Consult Call Kit</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:opsz,wght@6..96,400;6..96,500&family=EB+Garamond:ital,wght@0,400;0,500;1,400&family=Montserrat:wght@400;500&display=swap" rel="stylesheet">
<style>
:root {{ --bg:#FFFFFF; --ink:#1F1D1A; --muted:#6B655C; --accent:#8C6A3F; --rule:#DDD6CB; }}
@page {{ size: A4; margin: 26mm 24mm 28mm 24mm; }}
@page bleed {{ margin: 0; }}
* {{ box-sizing: border-box; }}
html, body {{ margin:0; padding:0; background:var(--bg); color:var(--ink); }}
body {{ font-family: 'EB Garamond', 'Liberation Serif', serif; font-size: 11.4pt; line-height: 1.6; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
h1, h2, .num, .toc-num {{ font-family: 'Bodoni Moda', 'Liberation Serif', serif; font-weight: 400; }}
.label, .back, .kicker, .toc-hint, .footline {{ font-family: 'Montserrat', 'Liberation Sans', sans-serif; font-size: 7.6pt; letter-spacing: .22em; text-transform: uppercase; color: var(--muted); }}
a {{ color: inherit; text-decoration: none; }}
.bleed {{ page: bleed; width: 210mm; height: 297mm; overflow: hidden; page-break-before: always; page-break-after: always; position: relative; background: var(--bg); }}
.bleedmark {{ position:absolute; left:0; top:0; font-size:2px; color: rgba(255,255,255,0.01); }}
img {{ display:block; }}

/* cover, after The Portrait Experience intro page */
.cover {{ text-align:center; }}
.cover .title {{ position:absolute; left:0; right:0; top:34mm; }}
.cover h1 {{ font-size: 46pt; letter-spacing: .14em; line-height: 1; margin: 0 0 6mm; text-indent: .14em; }}
.cover .kicker {{ font-size: 9pt; letter-spacing: .4em; text-indent: .4em; color: var(--ink); }}
.cover .strip {{ position:absolute; left:0; right:0; top:72mm; height: 92mm; display:flex; gap: 2.5mm; }}
.cover .strip img {{ flex:1; width: 25%; height:100%; object-fit: cover; object-position: center 25%; }}
.cover .statement {{ position:absolute; left:30mm; right:30mm; top:182mm; }}
.cover .statement .label {{ margin-bottom: 5mm; }}
.cover .statement .line {{ font-size: 13pt; font-style: italic; margin: 0 0 12mm; }}
.cover .statement p.copy {{ text-align: justify; font-size: 10.6pt; line-height: 1.55; margin: 0 auto 4mm; max-width: 132mm; }}
.cover .footline {{ position:absolute; left:0; right:0; bottom: 20mm; color: var(--ink); letter-spacing: .3em; text-indent: .3em; }}

/* contents and intro */
.page {{ page-break-after: always; }}
.tocpage h1, .intro h1, .closing h1 {{ font-size: 30pt; letter-spacing: .04em; margin: 0 0 14mm; }}
.toc {{ border-top: 1px solid var(--ink); }}
.toc-row {{ display:flex; gap: 10mm; align-items: baseline; padding: 8.5mm 0; border-bottom: 1px solid var(--rule); }}
.toc-num {{ font-size: 13pt; color: var(--accent); width: 12mm; }}
.toc-title {{ font-size: 19pt; font-family:'Bodoni Moda', serif; }}
.toc-hint {{ margin-top: 9mm; }}
.intro .body p {{ font-size: 11.8pt; margin: 0 0 5mm; }}

/* chapters */
.chapter {{ page-break-before: always; }}
.chapter-head {{ border-top: 1px solid var(--ink); padding-top: 7mm; margin-bottom: 14mm; position: relative; }}
.chapter-head .back {{ position:absolute; right:0; top:7.5mm; }}
.back {{ color: var(--accent); }}
.num {{ font-size: 12pt; color: var(--accent); letter-spacing: .12em; }}
.chapter-head h1 {{ font-size: 32pt; line-height: 1.08; margin: 2mm 0 7mm; letter-spacing: .02em; }}
.lead {{ font-size: 14.5pt; line-height: 1.42; margin:0; max-width: 146mm; font-style: italic; }}
.body h2 {{ font-size: 16pt; margin: 12mm 0 3.5mm; line-height: 1.2; letter-spacing: .02em; page-break-after: avoid; }}
.body h2:first-child {{ margin-top: 0; }}
.body p {{ margin: 0 0 4.4mm; }}
.body ol, .body ul {{ margin: 0 0 4.6mm; padding-left: 5.5mm; }}
.body li {{ margin-bottom: 2.2mm; }}
.body li::marker {{ color: var(--accent); }}

/* openers with a half page portrait */
.opener {{ display:flex; }}
.opener-img {{ width: 105mm; height: 297mm; }}
.opener-img img {{ width:100%; height:100%; object-fit: cover; }}
.opener-text {{ width: 105mm; padding: 28mm 22mm 24mm 14mm; display:flex; flex-direction:column; }}
.opener-text .back {{ margin-bottom: 16mm; }}
.opener-text h1 {{ font-size: 28pt; line-height: 1.08; margin: 2mm 0 7mm; }}
.opener-text .lead {{ font-size: 12.5pt; }}
.opener-text .label {{ margin-top: 14mm; padding-top: 5mm; border-top: 1px solid var(--ink); }}
.mini {{ list-style:none; padding:0; margin: 4mm 0 0; font-size: 10.2pt; line-height: 1.5; }}
.mini li {{ padding: 1.6mm 0; border-bottom: 1px solid var(--rule); }}

/* breaker */
.breaker img {{ width:100%; height:297mm; object-fit: cover; object-position: center 30%; }}

/* run sheet, one page */
.runsheet .chapter-head {{ margin-bottom: 6mm; }}
.runsheet .chapter-head h1 {{ font-size: 26pt; margin-bottom: 3mm; }}
.runsheet .chapter-head .lead {{ font-size: 11.5pt; max-width: 162mm; }}
.runsheet .body {{ column-count: 2; column-gap: 9mm; column-rule: 1px solid var(--rule); font-size: 9.1pt; line-height: 1.42; }}
.runsheet .body h2 {{ font-size: 12pt; margin: 3mm 0 1.4mm; break-after: avoid; }}
.runsheet .body h2:first-child {{ margin-top: 0; }}
.runsheet .body p {{ margin: 0 0 2mm; }}
.runsheet .body ol {{ margin: 0 0 2mm; padding-left: 4.5mm; }}
.runsheet .body li {{ margin-bottom: 0.8mm; }}

/* fill-in page */
.fillin .body {{ counter-reset: fill; }}
.fillin .body ol {{ list-style: none; padding-left: 0; margin: 0; }}
.fillin .body li {{ position: relative; padding: 0 0 12mm 9mm; margin: 0 0 4mm; border-bottom: 1px solid var(--rule); font-size: 10.6pt; }}
.fillin .body li::before {{ content: counter(fill) '.'; counter-increment: fill; position: absolute; left: 0; top: 0; font-family: 'Bodoni Moda', serif; font-size: 11pt; color: var(--accent); }}
.fillin .body h2 {{ margin-top: 9mm; }}

/* closing */
.closing p {{ font-size: 11.8pt; max-width: 150mm; }}
.closingimg img {{ width:100%; height:297mm; object-fit: cover; object-position: center 20%; }}
</style></head><body>

<section class="cover bleed">{MARK}
  <div class="title">
    <h1>THE CONSULT</h1>
    <div class="kicker">Call Kit</div>
  </div>
  <div class="strip">
    <img src="images/strip-1.jpg" alt=""><img src="images/strip-2.jpg" alt=""><img src="images/strip-3.jpg" alt=""><img src="images/strip-4.jpg" alt="">
  </div>
  <div class="statement">
    <div class="label">What this kit is for</div>
    <p class="line">To walk into every consult knowing what to say, and to leave the couple better off whichever way they decide.</p>
    <p class="copy">The one page run sheet I keep beside the screen. The timeline I build on the call, which does discovery and the recommendation at the same time. The habit of recording every consult and listening back once. The five objections in depth, with my position on discounting underneath them.</p>
    <p class="copy">And the ten questions that surface budget and decision makers without ever asking for them. Nothing in here depends on my business. Wherever you see a square bracket, that is where yours goes.</p>
  </div>
  <div class="footline">Norman Yap &nbsp;&middot;&nbsp; Part-Time to Full-Time &nbsp;&middot;&nbsp; 2026</div>
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
<section class="closingimg bleed">{MARK}<img src="images/closing.jpg" alt=""></section>
</body></html>'''
OUT.write_text(html_doc)
print('wrote', OUT.name, len(html_doc))
