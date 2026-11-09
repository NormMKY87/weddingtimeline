# Rebuilding the PDF

Run from this folder. Needs Python 3 with Pillow and pypdf, Node with Playwright and Chromium, and poppler-utils.

```
python3 build.py && node print.js && python3 stamp.py
```

build.py reads the six markdown files in the parent folder and writes consult-call-kit.html as one document. print.js prints it with Chromium to main.pdf with no footer, then prints footers.pdf, one footer per page. stamp.py lays the footer onto every page except the full bleed image pages (marked in the HTML) and writes ../consult-call-kit.pdf. Keeping it one document is what keeps the contents links and the back links working.

Design follows The Portrait Experience intro page: white, Bodoni Moda display, Montserrat tracked labels, EB Garamond body. Fonts load from Google Fonts at print time.

`images/` holds the photographs: four in the cover strip, two full page breakers, four half page section openers and the closing page. All are Norm's own work, resized to 2200px on the long side. Swap a file to swap a picture. Edit the markdown, never the HTML.
