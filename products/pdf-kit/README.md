# PDF kit

Builds a designed A4 PDF from a product's markdown files. Used by The Warm List Emails and The Quiet Month Playbook.

```
pip install markdown
python products/pdf-kit/build.py                     # both
python products/pdf-kit/build.py warm-list-emails    # one
```

- Reads `products/<slug>/NN-*.md` in order. A line of `---` starts a new page.
- Writes `products/<slug>/pdf/<slug>.html` and the PDF beside the markdown.
- The cover is the photo cover from `mockups/out/covers-photo/`. Section pages use photographs from `mockups/photos/`. Fonts are the local copies in `mockups/fonts/`.
- Page size, margins, the running footer and page numbers are set in CSS (`@page`), printed with the pre-installed Playwright and Chromium.
- The markdown conventions are listed at the top of `build.py`. Product titles, cover lines and the contents page are set in `PRODUCTS` in the same file.

If a page count is one higher than the number of sections `build.py` prints, a page has spilled. Shorten it or split it with `---`.
