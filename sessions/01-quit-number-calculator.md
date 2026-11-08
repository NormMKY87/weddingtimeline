# Session 1: Quit-Number Calculator and Package Ladder

Build the Quit-Number Calculator as an embeddable web app, and the Package Ladder sheet that turns the number into prices. Due live 16 November 2026. Asana task 1220327478129069 (calculator) and 1220327362286790 (Package Ladder worksheet).

## What Norm asked for (8 Nov 2026)

- A dynamic calculator that works from what the photographer currently earns. Sliding scale design with switches that turn on and off.
- Target is not plain income replacement. Replace the income, build in a buffer, be sustainable.
- Work situation dial: full time, part time, casual. The photographer sets where they are now and where they are going.
- Transition path built in: build the buffer first, then trial full time by taking unpaid leave before resigning.
- Embeddable on a website. Email required for the result.
- Draw on everything Vance has already built: the margin calculator, the studio calculator, the offer and collections calculators, the cost base and the finance books.

## The maths model (write this first, as `products/quit-number-calculator/maths.md`)

Vance's rules that govern the model. Each one came out of real mistakes in the NYP model and must hold here.

1. Compare net to net. Gross wedding income never sits beside a net payslip. Convert the salary to take-home after tax, then add back what the job also paid: employer super, paid leave (annual, sick, long service), and any penalties or allowances. That full figure is what the business must produce after its own costs and after tax.
2. The owner's wage is a fixed annual cost. It is never also charged per job. Double-counting the wage was the error that made every NYP package look thin until 3 Sep 2026.
3. Overhead is annual and divided by volume. Overhead per wedding falls as volume rises, which is why the calculator must show overhead per wedding at the photographer's chosen volume, not a flat number.
4. Deposits are not income. A wedding studio collects up to 18 months before it delivers. The transition plan must run on cash collected and work delivered side by side. Deposit cover ratio (cash at bank divided by deposits held on unshot weddings) has a floor of 1.0.
5. Revenue is ex GST. Ex equals inc divided by 1.1. Every margin is net divided by ex GST revenue.
6. A set net margin floor. NYP uses 50 percent on its own ladder and 30 percent on associate jobs. The calculator exposes the floor as a dial with a sensible default and explains it.
7. Never invent a figure. Tax rates, super guarantee and Medicare levy must be sourced from the ATO for the current financial year, dated inside the app, with a one-line disclaimer that it is not tax advice. Do not type rates from memory.

### Inputs (sliders and switches)

Current position
- Employment type switch: full time, part time, casual. Drives hours, leave and super assumptions.
- Gross salary (annual) or hourly rate plus hours, with a toggle.
- Employer super rate (default from ATO, editable).
- Paid leave weeks per year (default by employment type, editable). Casual gets loading instead of leave.
- Household expenses per month (for the buffer).

Current business
- Weddings per year now.
- Average sale per wedding inc GST.
- Direct cost per wedding: second shooter, editing and culling, albums, travel, card fees. Defaults from Norm's locked standards, each editable and each with an on/off switch.
- Annual overhead: software, insurance, gear sinking fund, accounting, marketing. Defaults from the NYP cost base, editable.
- Marketing spend and client acquisition cost. Hormozi's same-CAC principle: cheap offers inherit the full CAC.

Targets and dials
- Net margin floor (default 50 percent).
- Buffer in months of household expenses (default 3, range 0 to 12).
- Sustainability switch: include the owner's own super and leave in the target or not. Default on.
- Growth switch: hold current average sale, or set a target average sale.

### Outputs

- Quit number: annual net the business must produce to replace the job plus the chosen buffer and sustainability items. Shown monthly as well.
- Gap: quit number minus current net wedding profit.
- Bookings required at the current average sale and at two higher averages.
- Overhead per wedding at the chosen volume.
- Buffer target in dollars and months to fund it at the current trajectory.
- Provisional quit date, plus the trial date: when the buffer is funded enough to take unpaid leave and trial full time.
- Three scenario cards: part time to full time, drop to part time first, casual bridge. Each shows the date and the bookings needed.

## Sources to read, in order

Vance and the NYP model (Dropbox)
- `/00_COMPUTER_SYNC/10_AI_BRAIN/wiki/projects/vance-cfo-agent.md` (the full design history, the wage double-count correction, the ladder findings, breakeven weddings for a $7,000 net month)
- `/00_COMPUTER_SYNC/09_VANCE OS/cost-base.md` (locked cost base, every line labelled stated or derived)
- `/00_COMPUTER_SYNC/09_VANCE OS/offer-architecture.md` (package ladder, margins, deposit schedule logic)
- `/00_COMPUTER_SYNC/09_VANCE OS/metrics-spec.md` (what to track and why, the contribution needed for $7,000 net)
- `/00_COMPUTER_SYNC/09_VANCE OS/04_MODEL/nyp-studio-model.html` (the live studio calculator with sliders for volume, price, costs, overhead, target net. Closest existing ancestor of this app)
- `/00_COMPUTER_SYNC/09_VANCE OS/04_MODEL/nyp-collections-pnl.html` and `compute_pnl.py`
- `/00_COMPUTER_SYNC/09_VANCE OS/rulebook/money-model-doctrine.md` and `decision-rules.md` (30 day cash, CAC, LTGP, calibration meta-rule)
- `/00_COMPUTER_SYNC/10_AI_BRAIN/bots/Vance/memory.md` and `associate-model-2026-10.md` (current pricing, the 30 percent floor, overhead per wedding at 40)
- `/00_COMPUTER_SYNC/08_CLAUDE_CODE_MEMORY/nyp-per-job-cost-standards.md` (per-job cost standards, the $1,200 operating block)
- `/00_COMPUTER_SYNC/11_CONSULTATION COMPANION/margin-calculator.html` (the margin calculator: brand, collection, add-ons, contractor pay, overheads, saved quotes)
- `/00_COMPUTER_SYNC/12_P + L Audit/CONTINUATION-BRIEF.md` and `NYP-Subscriptions-PL-Dashboard.html` (the Studio Economics Calculator: recurring costs with on/off toggles, per-job margins, booking presets)

Finance books (Dropbox `/FOUNDERS LIBRARY/Founders Library V1/`)
- Simple Numbers, Straight Talk, Big Profits (Crabtree): market-based owner wage, labour efficiency, the profit target. Also the reference in the founders-library-2 skill.
- Profit First (Michalowicz): allocation percentages, the buffer and tax accounts.
- Financial Intelligence (Berman): cash versus profit, the language for the explainer copy.
- $100M Money Models and $100M Lost Chapters (Hormozi): 30 day cash, CAC, LTGP, the five-step ladder. `money-models-reference.md` is the distilled version.

Avatar and offer thinking
- `/Digital Product Ideas/The Shift Change - Shift Worker to Paid Photographer/01-full-offer-design.md` and `02-hormozi-critical-evaluation.md`
- `/00_COMPUTER_SYNC/10_AI_BRAIN/projects/digital-products/digital-products-ideas-and-avatar-2026-10-31.md`
- `context/part-time-to-full-time-context.md` in this repo, sections 2, 3 and 6 (Module 1)

## Build

- Single page app, no framework required. Static HTML, CSS and JS so it embeds in an iframe or a page section. Mobile first.
- Steps: current position, current business, targets, email gate, result. Sliders with typed inputs beside them. Switches as toggles. Every default visible and editable.
- Result page shows the headline number, the gap, the dates, the three scenarios, and one paragraph in Norm's voice explaining what to do next.
- Email capture posts to the educator list tool (decide with Norm, separate from NYP). Result also emailed.
- Assumptions panel: every rate with its source and date.
- Copy in first person singular, Australian English, no dashes, no semicolons. See `CLAUDE.md`.

## Package Ladder sheet (second deliverable)

The calculator gives the number. The ladder sheet turns it into prices. Build it as the second tab or a companion page, and as a printable worksheet for Module 1 lesson 1.2.

It must make gross profit realistic by surfacing what part-timers leave out: overhead, capital costs and a gear sinking fund, the owner's wage, super, GST, income tax, marketing cost and client acquisition cost per booking. Structure follows Vance's ladder work: three or four tiers, even hourly ramp (no dip between tiers, the P2 lesson), add-ons priced with their own margin, a floor tier that clears the net margin floor at the chosen volume, and the warning that base plus add-on hours pricing recreates the hourly commodity trap.

## Done when

- `maths.md` signed off by Norm before the UI is built.
- Three real scenarios produce sensible results, including Norm's own paramedic to photographer numbers.
- Email arrives with the result.
- Published, embeddable, linked from the free channel on 16 Nov.
- Package Ladder sheet exports as PDF and reads cleanly to a stranger.
