# Reference scene iteration log

Norm asked for the six Creative Market listings to be used as inspiration and the scenes rebuilt as close as possible, iterating until they match. This log records each round.

## Method

- The preview images from the six listings were downloaded to a scratch folder for study only. They are paid, licensed products, so no reference pixels are committed, embedded or shipped. Only the compositions, angles and lighting were studied.
- Eleven scene types were picked across the six listings. Each was rebuilt in HTML and CSS in `mockups/ref-scenes/`, with real product pages and the token-driven covers.
- Each round renders the Booking Pack version at the reference size (1200 by 800), places it beside the reference in one image, lists the differences, fixes them and renders again.
- Final exports are 2400 by 1600 for every product in `out/ref/<scene>/`.

## Scenes and their references

| Scene | Inspired by | What was taken from it |
|---|---|---|
| r01 Paperback lying flat | Minimalist book mockup, preview 3 | Three quarter top view, spine and page block visible, pale grey surface |
| r02 Open paperback | Minimalist book mockup, preview 7 | Open book at an angle, pages curving up from the gutter |
| r03 Standing hardcover | Matte hardcover book mockup, preview 2 | Front-on standing hardcover with a sliver of spine, soft floor shadow, white |
| r04 Banded stack | Newspaper mock-up set, preview 10 | Three copies fanned in a stack, paper band, sage vignette |
| r05 Cover in window light | Magazine mockup kit, preview 1 | Flat cover from above, long drop shadow, raking window light |
| r06 Leaning against a wall | Magazine mockup kit, preview 17 | Cover leaning on a wall, marble ledge, leaf shadow across the wall |
| r07 E-reader | Magazine mockup kit, preview 14 | Tablet from above, cropped at the bottom, olive surface |
| r08 Diagonal tile | Magazine mockup kit, preview 26 | Covers tiled on the diagonal, edge to edge, cream surface |
| r09 Cover on the spread | US Letter magazine mockup, preview 2 | Cover lying over the open spread, top down, stone surface |
| r10 Page turning | US Letter magazine mockup, preview 8 | Open spread top down with a page lifting and curling over |
| r11 Leaning stack | Book mockup set (Renderteam), preview 9 | Standing books spine out with two leaning, hard sun shadow, white |

## Rounds

### r01 Paperback lying flat

1. Book about 40 percent too small, too far right, tilt too steep, spine reads as a sliver.
2. Scale and position match. Long axis five degrees short of the reference rotation. Spine too thin.
3. Rotation and outline line up. Spine still a hairline.
4. Moved the camera vantage left to expose the spine. Wrong cause: perspective over-distorted the book and the spine still did not read. The spine was present, it shared the cover colour.
5. Camera restored. Spine shaded darker than the cover and thickened to the reference proportion. Spine title now legible, page block shows on the bottom edge. Accepted.

### r02 Open paperback

1. Pages floated well above the page stack. The curve rose higher than the block was thick.
2. Block thickness computed from the strip angles. Now the pages sat inside the block, hidden under its top face.
3. Removed the block's top face so the pages are the top surface. Head and tail edges clipped to the page profile so they taper into the gutter. Reads as an open book. About 10 percent too large, sitting low and right.
4. Scaled and moved. Accepted. Limit: CSS bends a page from flat strips, so the long rolling curve of the reference's left page is approximated, not continuous.

### r03 Standing hardcover

1. Stance, spine sliver and proportions already close. Book 5 percent small. Floor shadow too faint.
2. Larger book. Shadow from a rotated floor plane landed to the right and read as a hard ledge.
3. Replaced the floor plane with a soft elliptical contact shadow drawn under the base. Right shape, but it floated 30 pixels below the book.
4. Shadow raised to touch the base, moved left away from the light, layered behind the book. Accepted.

### r04 Banded stack

The reference is a folded newspaper. The composition was kept (three copies fanned down and right, a kraft band, a sage vignette) with the products as A4 portrait pieces.

1. Blank render. A script variable named `top` collides with a browser global. Renamed.
2. Stack and shadow right. The band showed only its label, with no paper.
3. The band was sized top to bottom inside a parent with no height, so it collapsed. Given the cover's height. Band now reads as kraft paper with edge shadows, but it covered the cover title.
4. Band moved to the right third and narrowed, as in the reference. Label type tightened to stop the issue number wrapping. Accepted.

### r05 Cover in window light

The reference preview carries the seller's title card on the left. That card was left out.

1. Window shadow drawn as a full grid of mullions across the cover, too busy. Drop shadow too light.
2. Window reduced to one dark corner and a single parallel bar, as in the reference. Drop shadow longer and heavier to the lower left. The light had slid almost out of frame.
3. Light pulled back into the top right. Nudged a further 40 pixels so it grazes the cover corner. Accepted.

### r06 Leaning against a wall

1. Cover 15 percent small. Leaf shadow too crisp and sparse, where the reference has a dense, very soft canopy. Book's wall shadow on the wrong side, since the reference light comes from the right.
2. Cover enlarged. Leaves bigger, denser and blurrier, shadow moved to the left of the book. Overcorrected: the canopy covered the cover and a solid strip along the top read as a flat band.
3. Canopy thinned to the top quarter with gaps, kept off the cover. Accepted after pushing the book's side shadow further out. Limit: the marble ledge is generated noise, so it shows soft clouding rather than the reference's crisp veins. A photographed marble texture would close that gap.

### r07 E-reader

The reference has the seller's caption strip across the bottom. That strip was left out.

1. Tablet about 18 percent small and right of centre. Bezel too thick. Screen too cold. Shadow to the left too faint.
2. Resized and centred, thinner bezel, warm paper tint on the screen, deeper left shadow. Matches. The screen now shows each product's fuller right-hand page, because the reference fills its screen. Accepted.

### r08 Diagonal tile

1. Angle and arrangement right. Gaps between covers wider than the reference, and no visible board edge.
2. Grid tightened, a two-tone edge added to every cover. Accepted.

### r09 Cover on the spread

1. Layout, scale, gutter shading and page edges matched on the first render. Accepted. The reference cover shadow is slightly crisper on its left edge, which is a fine-tuning difference only.

### r10 Page turning

The hardest scene. CSS can only bend a sheet by chaining flat strips around one straight axis.

1. Spread right. The sheet curled from the gutter itself, so mostly its reverse side showed.
2. Bend profile changed to flat for the first third then lifting. Read as a lift, but the roll was too tight and the strips showed as separate bands.
3. Rebuilt as a half-turn roll with the sheet lying back face up beside it, as in the reference. Strips stacked into visible steps.
4. Same half turn spread over more, narrower strips for a wider roll. The reversed band became too long and repeated the left page's text.
5. Longer flat front, shorter band, plain paper on the reverse. Shape now matches the reference. Faint seams between strips.
6. Strips overlapped slightly to hide the seams. Accepted. Limits: the reference curls on a diagonal with a continuous bend and shows a printed reverse side. Strips can only curl along one straight axis, so this version curls straight and the reverse is plain paper. This is the scene furthest from its reference.

### r11 Leaning stack

The reference carries the seller's logo and a "transparent background" label. Both were left out.

1. Far off. Camera on the wrong side, so a whole back cover faced the viewer. Leaning copies stood edge-on. Shadow floated.
2. Camera moved, spines to camera with the band across each. Floor shadow computed as the cast of the row's footprint, so it starts at the bases. Leaning copies tipped the wrong way and stood apart.
3. Pivot moved, but the group had no size, so the pivot sat at its top-left corner. Copies leaned the right way but stood 270 pixels clear of the row.
4. Group given the book's size. Copies sat on the wrong corner and sank into the floor.
5. Slid toward the row. Still sinking: a book leaning back to the left stands on its bottom-left corner, not its bottom-right.
6. Pivot on the bottom-left corner. Bottom edges now rise to the right as in the reference. Still clear of the row.
7. Slid onto the row. Accepted. The reference row recedes further with more copies, a detail that does not change the read.

## r12 US Letter magazine (added after the photo pass)

Reference: US Letter magazine mockup, preview 2, the full screen hero. Straight down on warm grey, light from the top right, the closed issue over the left page of an open copy.

- Round 1. Built a white magazine edition per product in `covers-photo/magazine.html` (letterspaced masthead, framed photograph, coverlines, a two page editorial spread with four photographs). Set the cover and spread to the reference positions. Close on layout, shadows too light.
- Round 2. Deepened the cover's down-left shadow into three layers and strengthened the left page's gutter roll. Verdict: closest.

## Photo pass

Every cover in r01 to r12 is now a photo cover from `out/covers-photo/` (`covers-photo/cover.html`). Add `?cover=type` to any scene to bring back the typographic covers.

## 3D rebuild (Blender Cycles)

Norm's verdict on the CSS scenes: still artificial, not close enough. All twelve scenes were rebuilt as real 3D geometry in `blender/mock.py` and rendered with Cycles: a sun, sky fill and a shadow catcher, composited over each reference's ground colour. Covers switched to the white magazine cover, because most references use light covers with a framed photograph.

- Round 1. Geometry and framing for all twelve at low resolution. Objects too small, light too hot.
- Round 2. One exposure dial for every light, reference sizes for each object, spine turned to the correct side on the hardcover.
- Round 3, side by side with the references at full size:
  - r01: 2:3 paperback cover (`out/assets/*-cover-pb.png`), new rotation and placement, softer shadow.
  - r02: narrower pages, deeper gutter curve.
  - r03: thick hardcover, wide spine, 86 mm lens up close so the edges converge.
  - r04: folded copies showing the top of the cover, fanned down and right, wider band.
  - r05: cover lifted 22 mm for the deep soft shadow, darker taupe ground.
  - r06: magazine centred, 22 leaf clusters, darker wall.
  - r07: rounded tablet built from a bevelled plane, centred.
  - r08: tile angle flipped to match the reference lean.
- Verdicts. Closest: r01 to r05, r07, r08, r09, r12. Close: r10. Close with a limit: r06 (generated marble), r11 (fewer, thicker copies than the reference).

Renders are 1800 by 1200 at 48 samples with denoising, about 85 seconds each on four cores. `ref-scenes/` keeps the earlier CSS versions.
