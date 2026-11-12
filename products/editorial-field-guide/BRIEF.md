# The Editorial Field Guide: brief

Status: rebuilt 12 Nov 2026 from my own photographs. Built, checked, not on sale. No price until Vance sets one. Not for sale until marketing consent is confirmed for every couple in it.

## What it is

An interactive A4 PDF titled **The Editorial Field Guide**, subtitle **Light. Composition. Moment.** One clickable contents page and 42 photographic studies. Each study takes one of my wedding photographs and breaks it down the way I'd teach it on the day:

- **LIGHT:** direction, quality, source and time of day
- **COMPOSITION:** framing, lines, negative space, where the eye lands
- **LENS / FOCAL LENGTH:** a "Try ..." recreation suggestion (see the note on exposure data below)
- **MOMENT:** what happened in the frame and how I'd direct it
- **BEFORE YOU SHOOT:** one practical prep check
- **THREE DIRECTIONS TO SAY OUT LOUD:** setup, small change, moment, written as words a photographer can say on the day

## Why it was rebuilt

V5 (11 Nov 2026, 43 pages) used other photographers' work taken from Instagram screenshots. It could never be sold or shown publicly. This version keeps the V5 layout and the builder SKILL.md v1.1 geometry exactly and swaps every photograph for one of mine.

## Files

| Path | Holds |
|---|---|
| `The_Editorial_Field_Guide.pdf` | The built guide. 43 pages, A4, about 15 MB |
| `studies.json` | The manifest. One record per study: id, neutral photo name, category, title, four panels, Before note, three directions |
| `build/build.js` | Generates `build/guide.html` from the manifest and renders the PDF with the pre-installed Playwright Chromium |
| `build/guide.html` | The HTML source the PDF is printed from |
| `photos/` | 42 study photographs, 1800 px long edge, neutral filenames, EXIF stripped |
| `thumbs/` | 480 px versions for the contents grid |
| `fonts/` | Lato Regular and Bold (SIL Open Font License, `OFL.txt`) |

Rebuild after any edit to `studies.json`:

```
node products/editorial-field-guide/build/build.js
```

The script refuses to build if a study has a dash or semicolon, an unknown category, or anything other than three directions. It flags any analysis panel over three lines, any Before note or direction over two lines, and any contents card title over two lines.

## Layout (locked)

Matches V5 and the builder SKILL.md v1.1, in PDF points from the top left of an A4 page:

- Warm near-white page `#FEFDFC`, ink `#252825`, accent `#9B7854`, muted `#766F68`, pale panel `#F5F3EE`, rules `#DED9D0`
- Times Roman titles (37 pt contents, 31 pt study), Lato body at 9.7 pt on 13.6 pt leading, Lato Bold labels
- Contents: seven category buttons in one row at y 146, then a 6 by 7 thumbnail grid from y 179, cards 80 by 82
- Study: photo contained in x 42 to 297, y 126 to 456. Analysis column at x 317, 236 wide, headings at y 126, 194, 262, 330. Before panel at y 469. Direction cards at y 563, 631, 699. Navigation at y 788
- Positions below the photo follow V5's measured layout, which sits about 10 pt lower than the SKILL.md table

## Categories and order

Studies are grouped in category order so each button lands on the start of a run.

| Category | Studies | Count |
|---|---|---|
| Getting Ready | 01 to 07 | 7 |
| Bridal | 08 to 16 | 9 |
| Couple | 17 to 26 | 10 |
| Party | 27 to 29 | 3 |
| Venue | 30 to 34 | 5 |
| Reception Details | 35 to 38 | 4 |
| Flash | 39 to 42 | 4 |

### Gaps to fill

Every category has at least three studies, so no button is disabled. These are the thin spots:

- **Party (3):** all three are posed or styled wedding party groups. Missing a candid party moment at the reception that doesn't fill the frame with guests' faces.
- **Reception Details (4):** missing a table setting close up, place cards or stationery without names, and centrepiece florals. Stationery frames in the folder carry the couple's names or the venue, so they were left out.
- **Flash (4):** all are reception flash. Missing off-camera flash outdoors at sunset, a shutter drag with movement, and a sparkler or confetti exit lit with flash.
- **Getting Ready:** missing hair and make-up, and the dress going on.
- **Venue:** missing a ceremony space set and empty before guests arrive.

## Source and selection

- Source: Dropbox `/ORGANIC CONTENT CREATION/SELECTED/`, listed fresh on 12 Nov 2026. 136 files.
- Exact duplicates skipped by size and Dropbox content hash: two "A" copies (21A and 23A of one set).
- Near duplicates found with a 64-bit difference hash: six more "A" pairs scored 0 to 2 bits apart, including the SP-24 pair named in the session brief (same size, but different content hashes, so not byte identical). One of each pair was used at most.
- 134 frames were opened and reviewed on contact sheets. 42 chosen.
- Left out on content: a frame with the couple's names and venue written on a card, a frame with a venue signboard listing names, a waiter wearing a logo, two frames with third-party product labels, vanity frames with branded toiletries, and every frame with crowds of guests' faces (confetti exits, ceremony aisles, first dance circles). No dogs appeared.
- Under 2 MP: three files. One 1.7 MP bow-back frame was swapped out. The 2.0 MP floral veil frame (study 11) is just on the line and only fills the half-page photo box, never a full page.
- One crop: study 32 (cathedral courtyard) was cropped at the right and bottom to remove a window edge and a sign carrying the place name.
- Venue names and couple names appear nowhere in the PDF, the manifest or the repo filenames. The mapping from neutral photo name back to the original file is kept out of the repo on purpose. To trace a study, match the photo by eye in the SELECTED folder.

## Exposure data

None of the 134 exports carry focal length, aperture, shutter or ISO. They were saved from Photoshop with that metadata stripped (no EXIF exposure fields, nothing in XMP). So every LENS / FOCAL LENGTH panel is written as a "Try ..." recreation suggestion read from the frame, which is also what the builder SKILL.md asks for when EXIF is missing. To print real settings, export the 42 originals from Lightroom with camera data kept (no serial or GPS) and I'll swap them in.

## Before anything is sold

1. **Consent.** These are client wedding images. Confirm marketing and education consent for each couple in the guide. Swap any study where consent isn't given.
2. **MOMENT check.** The MOMENT panels describe how I'd direct each frame. Read them against what actually happened and correct any that differ.
3. **Pricing.** Vance's call. Nothing in this folder carries a price.
4. **Gate.** The guide isn't on the side products list. See the decision logged in `context/part-time-to-full-time-context.md`, section 8.
