# Stamp the running footer onto every page that is not a full bleed image page, keep links intact.
import pathlib
from pypdf import PdfReader, PdfWriter
HERE = pathlib.Path(__file__).resolve().parent
main = PdfReader(HERE / 'main.pdf'); foot = PdfReader(HERE / 'footers.pdf')
w = PdfWriter(clone_from=main)
stamped = 0
for i, p in enumerate(w.pages):
    if 'BLEEDMARK' in (main.pages[i].extract_text() or ''): continue
    p.merge_page(foot.pages[i]); stamped += 1
w.write(HERE.parent / 'consult-call-kit.pdf')
print('stamped', stamped, 'of', len(w.pages))
