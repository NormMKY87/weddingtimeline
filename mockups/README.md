# Product mockups

Mockup suite for the six digital products and the bundle shot. Session brief: `sessions/05-product-mockups.md`.

## Re-render

```
node mockups/render.js            # everything, about two minutes
node mockups/render.js covers     # covers only
node mockups/render.js screens    # device screens (calculator, lesson player, worksheets, phone threads)
node mockups/render.js scenes 03  # one scene, all four sizes
node mockups/render.js sheet      # contact-sheet.png
```

Uses the pre-installed Playwright and Chromium. Do not run `playwright install`. Order matters on a clean checkout: covers, then screens, then scenes, which is what the default does.

## Re-skin

Everything reads from `tokens.css`: the palette, the type pair, the brand wordmark (`--brand-name`), the series name and the per-product cover colourways. Change the tokens, re-render, done. The fonts are local copies in `fonts/` (Cormorant Garamond and Karla, SIL Open Font License) so renders are identical offline.

## What is where

| Path | Holds |
|---|---|
| `covers/` | Seven covers as HTML, one system, `cover.css` shared |
| `screens/` | Lesson player, worksheets and worksheet covers, phone threads. Every `[data-shot]` element becomes a PNG |
| `pages/` | Real inner pages rasterised from the product PDFs in `products/` (`bp` Booking Pack, `fv` Follow-Up Vault, `cck` Consult Call Kit, `pl` Package Ladder) |
| `scenes/` | One scene per product plus the bundle. `scene.css` holds the device frames, page and shadow primitives and the per-size switch |
| `out/` | Exports. `out/<product>/{landscape,square,portrait,hero}.png` plus `out/covers/`, `out/screens/` and `contact-sheet.png` |
| `contact-sheet.html` | Review page showing all 28 exports and the cover system |

Export sizes: landscape 1920 by 1080, square 1080, portrait 1080 by 1350, hero 1600 by 1200 with a transparent background. All rendered at 2x.

## Rules kept

No prices on any visible surface. No NYP client names or venues. Inner pages are the real product pages. Calculator screens are screenshots of the live app on its result page. Device frames are drawn in CSS, no ripped product shots. Copy on the covers and screens follows the voice rules in `CLAUDE.md`.

## Open for Norm

- Confirm the six products and the bundle (listed in the session brief table).
- The brand name and palette are provisional. Swap `tokens.css` when the education brand lands.
- Norm's own photographs can replace the plain backgrounds once a Dropbox folder is nominated.

## Reference-inspired scenes (12 Nov 2026)

Norm asked for the scenes in six Creative Market listings to be recreated as closely as possible. Eleven scene types were rebuilt in `ref-scenes/`, one HTML file each, sharing `lib.js` (3D book boxes, curved pages, shadows) and `lib.css`. Every scene renders for all six products from the same source: `?p=<product>` picks the product.

```
node mockups/ref-scenes/render.js            # all 66, about two minutes
node mockups/ref-scenes/render.js r05        # one scene, all six products
node mockups/ref-scenes/render.js --cutout   # transparent PNG versions
```

Exports: `out/ref/<scene>/<product>.jpg` at 2400 by 1600. Scene surfaces live in `tokens.css` under the `--surf-*` tokens.

How each scene was matched, round by round, is in `iteration-log.md`. The reference images were studied in a scratch folder and are not in the repo: they are paid, licensed products.

Review gallery (private until shared): https://claude.ai/artifact/YEAjFkhQxeBNFoTeiqbFFn

## Products 08 and 09 (13 and 14 Nov 2026)

The Warm List Emails (`warm-list-emails`) and The Quiet Month Playbook (`quiet-month-playbook`), both working titles. Briefs, copy and PDFs are in `products/`.

- Each has a photo cover, a magazine edition, print assets, a reader page and all twelve photoreal scenes in `out/ref/`.
- Inside pages are real pages rasterised from the two PDFs: `pages/wle-*.jpg` and `pages/qmp-*.jpg`.
- To rename one, change its title in `covers-photo/cover.html`, `covers-photo/magazine.html`, `blender/assets.html`, `ref-scenes/lib.js` and `products/pdf-kit/build.py`, then re-render and rebuild the PDF.

```
node mockups/render.js photocovers && node mockups/render.js screens
node mockups/mag-render.js && node mockups/blender/assets.js
python products/pdf-kit/build.py
python mockups/blender/mock.py all warm-list-emails,quiet-month-playbook --samples 48
```

Review sheet for the two: `out/review-08-09.jpg`.
