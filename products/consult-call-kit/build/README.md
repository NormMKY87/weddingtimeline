# Rebuilding the PDF

Run from this folder. Needs Python 3, Node with Playwright and Chromium, and poppler-utils for pdfunite.

```
python3 build.py && node print.js
```

build.py reads the five markdown files in the parent folder and writes cover.html and body.html. print.js prints both with Chromium and merges them into ../consult-call-kit.pdf. Fonts: Cormorant Garamond from Google Fonts, Inter local. Edit the markdown, never the HTML.
