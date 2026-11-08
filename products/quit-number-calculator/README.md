# Quit-Number Calculator: build notes

| File | What it is |
|---|---|
| `maths.md` | The model. Norm signs this off. Every rule, input, default and output with its source. |
| `model.py` | Reference implementation of the model. `python3 model.py` prints the three worked scenarios. |
| `app/index.html` | The embeddable app. One file, no build step, no framework. Both tabs: the calculator and the Package Ladder. |
| `app/test.js` | Checks the app's JavaScript against `model.py` for the three scenarios, checks the visible text for dashes and semicolons, checks phone width, takes screenshots. `node app/test.js`. |
| `app/render-worksheet.js` | Renders the Package Ladder tab to `package-ladder-worksheet.pdf` for Module 1 lesson 1.2. |
| `copy.md` | Page copy, opt-in, result email, follow-up email, launch piece notes. |
| `BRIEF.md` | The original product brief. |

## Embedding

The app is a single HTML file with inline CSS and JavaScript. It loads two Google Fonts and nothing else.

- As a page section: paste the contents of `<body>` and the `<style>` and `<script>` blocks into the page, or host `index.html` and embed it in an iframe:

```html
<iframe src="https://YOUR-HOST/quit-number-calculator/" title="Quit-Number Calculator" style="width:100%;min-height:1400px;border:0"></iframe>
```

- The page is mobile first and has no horizontal scroll at 390px.
- Inputs persist in the visitor's browser (localStorage) so they can come back to their numbers.
- `#ladder` in the URL opens the Package Ladder tab directly.

## Email capture

`CONFIG.emailEndpoint` at the top of the script is empty. When set, the form posts JSON to it on submit:

```json
{ "firstName": "...", "email": "...", "source": "quit-number-calculator", "result": { "quitNumberAnnual": 126400, "quitNumberMonthly": 10533, "...": "..." }, "inputs": { "...": "..." } }
```

The `result` object carries every figure the result email in `copy.md` needs, so the list tool's automation can merge them. Until the endpoint is set the result still shows on screen and the payload is logged to the console. Decision D7 in `maths.md`: the list must be separate from NYP. A separate GoHighLevel sub-account, ConvertKit or MailerLite all work with a webhook or inbound form endpoint.

## Yearly update

Every July, in this order: `model.py` section 1, `RATES` in `app/index.html`, the assumptions text in the result page and the footer, `maths.md` section 3, then `node app/test.js` and update the expected figures from `python3 model.py`.

## Checks run on 8 November 2026

- JavaScript matches `model.py` to the dollar on all three scenarios.
- No em dashes, en dashes or semicolons in any visible text.
- No horizontal scroll at phone width. No console errors.
- Worksheet renders to three A4 pages.
