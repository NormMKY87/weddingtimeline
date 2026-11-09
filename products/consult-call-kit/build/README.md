# Rebuilding the PDF

Run from this folder. Needs Python 3 with Pillow, Node with Playwright and Chromium, and poppler-utils for checking.

```
python3 build.py && node print.js
```

build.py reads the six markdown files in the parent folder and writes consult-call-kit.html as one document. print.js prints it with Chromium to ../consult-call-kit.pdf. The contents page links to every section and every section opens with a link back to the contents, so the document must stay a single print (no merging, which breaks the links). Fonts: Cormorant Garamond from Google Fonts, Inter local. Edit the markdown, never the HTML.

`images/` holds the four photographs used: cover, breaker, and the two half page openers. All are Norm's own work, resized to 2200px on the long side. Swap a file to swap a picture.
