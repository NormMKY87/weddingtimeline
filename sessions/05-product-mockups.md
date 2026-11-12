# Session 5: Digital product mockups

Create the product mockup suite for the six digital products, for sales pages, the free channel, Instagram and the checkout. Asana task: see `context/asana-board.md` (Side products section, "Product mockups for the six products"). Nested under the Digital Products Build group with the four product sessions.

## Inspiration

Norm's reference is the Creative Market search for digital product PDF mockups: https://creativemarket.com/search/digital-product-pdf-mock-up?categoryIDs=0

The conventions of that genre, which the suite should match:

- Floating PDF pages fanned at a slight angle with soft drop shadows, three to seven pages visible, cover in front.
- Device scenes: an iPad or tablet showing the cover with two or three loose pages beside it, a phone showing a script or a message thread, a laptop showing the calculator.
- Stacked book or workbook sets, front cover plus spine, on a plain or textured surface.
- Bundle shots: every item in a product laid out together (cover, inner pages, the phone, the checklist) so the buyer sees the volume of what they get.
- Minimal backgrounds in one or two tones, a single light source, no busy props. Editable templates where the cover swaps in.

## The six products

Assumed from the product ladder in `context/part-time-to-full-time-context.md` section 5. Confirm with Norm before the final export.

| # | Product | Format | Mockup scene |
|---|---|---|---|
| 1 | Quit-Number Calculator | Web app, embeddable | Laptop and phone showing the result page, plus the Package Ladder sheet as a floating page |
| 2 | The Booking Pack | PDF, five parts | Fanned pages with the cover in front, plus a phone showing a DM script |
| 3 | The Follow-Up Vault | PDF, two tracks | Phone message thread beside a cadence map page |
| 4 | The Consult Call Kit | PDF, one page run sheet plus guides | Tablet with the run sheet, floating ten-questions page |
| 5 | Part-Time to Full-Time (90 day program) | Course: lessons, worksheets, community | Laptop with the lesson player, tablet with a worksheet, stacked worksheet set, bundle shot of all the tools |
| 6 | The Craft Program (phase two) | Course | Same system as 5 with its own cover, marked "coming 2027" |

Plus one bundle shot of the whole ladder together, used on the flagship sales page and as the channel banner.

## Brand

The education side runs under a separate name from NYP (open question in the context file, currently "Norman Yap the educator"). Do not reuse the NYP couple-facing brand assets. Build the mockups on a provisional, token-driven palette and type pair so the whole suite re-skins in one place when the name and brand land. Editorial, restrained, premium. No stock photography of strangers. Norm's own imagery can be pulled from Dropbox once he points to a folder.

Reference for the tone Norm already uses on his internal tools: Cormorant Garamond with Karla, cream and terracotta (the Studio Economics Calculator). Treat that as inferred direction, not the final brand.

## Build approach

1. Covers first. Design a cover for each product as HTML and CSS (or Canva if Norm prefers), one system, six variations. Titles from the product briefs in `products/` and the context file. No prices anywhere.
2. Mockup scenes as HTML and CSS with 3D transforms and real shadows, rendered to PNG with Playwright at 2x. This keeps every scene editable and re-renderable when a cover changes, instead of a one-off Photoshop file. If a scene needs a photographic device, use a licensed or self-made device frame, never a ripped product shot.
3. Export set per product: square (1080), portrait (1080 by 1350), landscape (1920 by 1080), and a transparent cutout of the hero scene for sales page use.
4. Contact sheet: one page showing all six products and the bundle, for Norm's review.

## Sources

- `products/*/BRIEF.md` and `sessions/01` to `04` for what each product contains, so the inner pages shown in the mockups are real pages, not lorem ipsum.
- `context/part-time-to-full-time-context.md` sections 3, 5 and 12 for the promise, the ladder and the voice.
- Sales page direction: `/00_COMPUTER_SYNC/10_AI_BRAIN/projects/digital-products/NYP-Digital-Products/03-landing-and-sales-motion/` in Dropbox (offer page framework, sales page wireframe) so the hero mockup fits the layout.
- Low-ticket funnel template for sizing: `/Digital Product Ideas/Ninth Avenue Studios - Low-Ticket Funnel Template/00-DESIGN-SPEC.md`.
- Canva is connected if Norm wants editable Canva versions of the covers.

## Rules

- Voice rules in `CLAUDE.md` for any copy on the covers and pages.
- No prices. No NYP client names or venues on any visible page.
- Every scene must be re-renderable from source. Commit the HTML, CSS and render script, not only the PNGs.

## Deliverables

- `mockups/covers/` six covers plus the bundle
- `mockups/scenes/` one HTML scene per product plus the bundle, with a shared `tokens.css`
- `mockups/render.js` Playwright render script and `mockups/out/` exports
- `mockups/contact-sheet.html` for review

## Done when

All six products and the bundle render cleanly at all four sizes, the contact sheet is reviewed by Norm, and the Asana task is complete with the repo path in a comment.
