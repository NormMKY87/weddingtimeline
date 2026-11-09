# Quit-Number Calculator: the maths model

Status: draft for Norm's sign-off. Written 8 November 2026, revised 9 November 2026 after three rulings from Norm: it must work in any country, it is not a lead magnet (no email gate, the result shows on the page), and it must be a condensed, high level, top end planner rather than an itemised one. The web app is built from this file and nothing else. If a rule or default changes, it changes here first.

The reference implementation is `model.py` in this folder. It runs the four worked scenarios in section 8 and the JavaScript in `app/index.html` is tested against it to the dollar.

Not tax advice. Every Australian rate below is quoted from the legislation in force on 8 November 2026 and dated. The app carries the same disclaimer and dates.

---

## 1. What the calculator answers

One question: can I leave my job, and when.

It takes everything the job pays, converts it net to net into the profit the photography business must make to replace the whole package, and gives the top end: the number, the gap from today's wedding profit, the bookings required at three average sale figures, and a dated path (fund the buffer, trial full time on unpaid leave, resign). Plan for the top end and anything less is a bonus.

### Condensed by design

Norm's ruling, 9 November 2026: high level, not itemised. The user enters eleven figures and three dials. Shift penalties, allowances, leave weeks, casual loading, hourly rates, payment terms and itemised cost lines are gone. Where a detail used to be an input it is now either folded into one top end figure ("everything the job pays you a year, before tax") or fixed as a stated assumption (section 7). The employment type dial from the 8 November brief is dropped as an input. Its purpose, where you are now and where you are going, survives in the three dated ways out (section 6), which are the same for everyone.

### Any country

The first dial is "Where you work": Australia, or somewhere else.

- Australia carries built-in, sourced rates (section 3) so the tool can estimate take-home from gross pay. The user can still type their real take-home.
- Somewhere else carries no tax tables and guesses nothing. The user types what their payslip and tax office already tell them: gross pay, take-home, the tax rate on their next dollar, the employer's retirement contribution rate, the sales tax (GST or VAT) rate, and a currency symbol. Nothing is converted. Rule 7 holds in every country without a table for each one. Adding another country as a sourced preset later is a data change, not a model change.

### Not a lead magnet

Norm's ruling, 9 November 2026. No email is collected, nothing leaves the browser, the result shows on the page the moment step 2 is done. Inputs persist in the visitor's own browser so they can come back.

## 2. Vance's rules and how the model keeps them

| # | Rule | How it is kept |
|---|---|---|
| 1 | Compare net to net. Gross wedding income never sits beside a net payslip. | Australia: the job's gross is converted to take-home with the 2026-27 resident tax table and Medicare levy, or the typed take-home is grossed back up with the same table. Elsewhere: gross and take-home come straight from the payslip. The business side is profit after cash costs and overhead, before the owner's personal tax. Both sides therefore sit before personal tax, same tax law, same person. The tax the side business pays today, on top of the salary, is computed separately (Australia: bracket arithmetic. Elsewhere: the marginal rate the user enters) so the buffer funding rate is real money. |
| 2 | The owner's wage is a fixed annual cost, never also charged per job. | The only per wedding cost is "cash out per wedding" and the help text says the owner's hours never go in it. The owner's wage appears once, as the quit number. Owner hours appear only as a capacity check in the Package Ladder. |
| 3 | Overhead is annual and divided by volume. | Overhead is one annual figure plus a gear sinking fund (kit value over five years). Overhead per wedding is shown at today's volume and at every required volume so the user sees it fall as bookings rise. |
| 4 | Deposits are not income. Deposit cover ratio floor 1.0. | The buffer is household cash, never client money. At each required volume the result shows the client money the business will be holding on unshot weddings (section 7 assumptions) and says cash at bank must at least equal it before any of it counts as buffer. |
| 5 | Revenue is ex GST. Ex equals inc divided by 1.1. Margin is net over ex GST revenue. | Every sale is entered as the couple pays it and divided by (1 plus the sales tax rate). Australia: 10 percent, so divided by 1.1, assumed registered because the quit number sits above the $75,000 registration turnover for almost every user. Elsewhere: the user's GST or VAT rate, assumed registered for the same reason. Card fees sit inside cash out per wedding. |
| 6 | A net margin floor, exposed as a dial with a sensible default. | Default 50 percent (NYP's own ladder floor, Norm 3 Sep 2026). The result shows the margin at each required volume and the minimum average sale that clears the floor. The Package Ladder prices every tier off the floor. |
| 7 | Never invent a figure. Rates from the ATO for the current financial year, dated, with a disclaimer. | Section 3 for Australia, from the Acts the ATO administers in their 1 July 2026 compilations on the Federal Register of Legislation (the ATO website refused automated requests from the build environment), cross-checked against ATO figures reported by third parties. For every other country the rule is kept by carrying no table at all. |

## 3. Australia preset rates

All figures AUD, financial year 2026-27, as at 8 November 2026. Review every July. Shown on the app's assumptions panel when Australia is selected. Outside Australia none of this applies and the user's own figures take its place.

### 3a. Resident income tax, 2026-27

Source: Income Tax Rates Act 1986, Compilation No. 66, compilation date 1 July 2026, Schedule 7 Part I, table headed "Tax rates for resident taxpayers for the 2026-27 year of income". Section 3(1): tax-free threshold means $18,200.

| Taxable income | Rate on the part in this band | Tax at the top of the band |
|---|---|---|
| $0 to $18,200 | nil | $0 |
| $18,201 to $45,000 | 15% | $4,020 |
| $45,001 to $135,000 | 30% | $31,020 |
| $135,001 to $190,000 | 37% | $51,370 |
| over $190,000 | 45% | |

The same compilation carries the 2027-28 table, identical except the second band falls to 14 percent. The app switches to it on 1 July 2027.

Check: Vance's cost base derived $109,982 gross for $84,000 net on the 2025-26 table. The same net on the 2026-27 table is $109,588 (`model.py` prints this). The two differ only by the rate cut, so the model agrees with Vance's arithmetic.

### 3b. Medicare levy

Source: Medicare Levy Act 1986, Compilation No. 53, compilation date 1 July 2026. Section 6(1): 2 percent of taxable income. Section 3: threshold amount $28,011, phase-in limit $35,013 (general case). Section 7(2): between the two the levy does not exceed 10 percent of the excess over the threshold. Family thresholds (section 8) and the surcharge are not modelled, stated on the panel.

### 3c. Superannuation guarantee

Source: Superannuation Guarantee (Administration) Act 1992, Compilation No. 77, compilation date 27 March 2026, subsection 19(2) item 13: year starting on or after 1 July 2025, charge percentage 12. Default 12 percent of gross, editable.

### 3d. GST

10 percent, assumed registered. Revenue ex GST equals the couple's payment divided by 1.1.

### 3e. Studio defaults, from Norm's locked standards

Shown as Norm's Australian dollar reference figures beside the two cost inputs. Every one is editable and a user elsewhere replaces them in their own currency.

| Input | Default | Source |
|---|---|---|
| Cash out per wedding | $1,260 | Second photographer $70 an hour for 8 hours, $560 (cost-base.md section 1, nyp-per-job-cost-standards.md). Outsourced editing and culling $650 (cost-base.md 2b, resolved 3 Sep 2026 as a cash cost). Travel $50 (per-job operating block). Card fees at 1.78 percent (Vance, 29 Oct 2026) are mentioned in the help as sitting on top. |
| Annual overhead | $8,412 | Insurance $208 a month, bookkeeping and accounting $250 a month, production and client software $243 a month (Pic-Time, Adobe, Dropbox, Photo Mechanic, Dubsado, hosting), all stated 3 Sep 2026 in cost-base.md section 2. NYP's full stack is far larger and a part-timer does not carry it. |
| Kit replacement value | none, the user enters it | cost-base.md section 3: NYP carried equipment depreciation at $0 and Vance named it the most material omission in the stack. Spread over five years (section 7). |
| Net margin floor | 50 percent | NYP's own ladder floor, Norm 3 Sep 2026 |

## 4. Inputs

Eleven figures and three dials. Sliders carry a typed field beside them.

### Step 1. Your job and your household

| Input | Default | Notes |
|---|---|---|
| Where you work (dial) | Australia | Australia loads section 3. Somewhere else switches to payslip mode and shows the currency, take-home, marginal rate and retirement fields below. |
| Currency symbol (elsewhere only) | $ | Display only |
| Everything the job pays you a year, before tax | required | Base plus every penalty, allowance and overtime actually earned. Year-to-date gross on a payslip. The top end is the whole figure. |
| I know my take-home (Australia, switch plus field) | off | Replaces the estimate when on. |
| What lands in your bank a year (elsewhere) | required | Annual take-home from the payslip. |
| Tax rate on your next dollar (elsewhere) | required, zero allowed with a warning | Marginal rate including levies that scale with income, from the tax office rate table. |
| Employer super rate (Australia) or employer retirement contribution (elsewhere) | 12 percent (Australia). Required elsewhere, zero allowed with a warning | 3c |
| Household expenses a month | required | What the household spends. Sizes the buffer. |

### Step 2. Your business

| Input | Default | Notes |
|---|---|---|
| Weddings this year | required | |
| Weddings last year | equals this year | Sets the trajectory |
| Average sale per wedding | required | As the couple pays it |
| Cash out per wedding | $1,260 | 3e |
| What the business costs a year | $8,412 | 3e |
| Kit replacement value | required | 3e |
| Sales tax rate (elsewhere only) | required | Australia fixed at 10 percent |
| Net margin floor (dial) | 50 percent | |
| Buffer, months of household expenses (dial) | 3 | |
| Cash already set aside (dial) | $0 | |
| Top end switch | on | Adds the owner's own retirement contribution at the employer's rate |

Then the result.

## 5. The model

Let G be gross job pay, N take-home, r the retirement rate, s the sales tax rate, A the average sale, n weddings this year, c cash out per wedding, O annual overhead including the gear sinking fund.

### The job, net to net

```
Australia:   N = G - tax(G) - medicare(G)            (or the typed N, with G recovered by inverting the table)
Elsewhere:   G and N both typed from the payslip
Retirement   U = G x r
Quit number  Q = G + [top end on] U
```

Q is the profit the business must make, after every cost of running it and before the owner's personal tax, to replace the whole package. Because G is the taxable income that produces N under the same tax law, Q replaces take-home exactly (rule 1). Shown a year and a month, with "lands N a month in your bank" beneath.

### The business today

```
Revenue per wedding          R = A / (1 + s)
Contribution per wedding     C = R - c
Overhead                     O = annual overhead + kit value / 5
Profit today                 B = n x C - O
Net margin                   m(n, A) = (C - O / n) / R
Tax the business adds today  Australia: tax(G + B) + medicare(G + B) - tax(G) - medicare(G)
                             Elsewhere: B x marginal rate
After tax                    B_net = B - that tax
Gap                          Q - B
```

### Bookings required

At average sale A: n*(A) = ceiling((Q + O) / C(A)). Shown at today's A, A x 1.25 and A x 1.5 (rounded to the nearest hundred), each with overhead per wedding O / n*, margin m(n*, A), whether it clears the floor, and client money held (section 7).

Minimum average sale that clears the floor f at the required volume: A_floor = (c + O / n*) x (1 + s) / (1 - f).

## 6. Buffer and the three ways out

```
Buffer target        months x household expenses
Monthly funding      F = max(B_net, 0) / 12
Months to buffer     (buffer - cash saved) / F
Trial threshold      3 months x household expenses (section 7)
Months to trial      (trial threshold - cash saved) / F
Growth               g = weddings this year - weddings last year, per year, linear
Months to profit X   ((X + O) / C(A) - n) / g x 12     (0 if already there, never if g is 0 or less)
```

Three cards, each dated from today:

1. Straight to full time. Trial date = months to trial. Quit date = the later of months to buffer and months to profit Q. Bookings = n*(A).
2. Drop to part time first. The job keeps 60 percent of the package (section 7), so the business must cover 40 percent of Q. Date = the later of months to trial and months to that profit. Then the full quit date as in card 1.
3. Casual bridge. The job keeps a quarter of the package, so the business must cover 75 percent of Q. Date likewise.

When g is zero or less and the gap is positive, the dates read "not at this trajectory" and the result says how many bookings a year would reach Q in 24 months.

## 7. Fixed top end assumptions

Not inputs. Stated on the assumptions panel. Change here and in `FIX` in the app together.

| Assumption | Value | Why |
|---|---|---|
| Gear sinking fund | kit value over 5 years | Model choice for Norm to confirm |
| Unpaid leave trial | 3 months | Norm's transition path, 8 Nov 2026 |
| Drop to part time | job keeps 60 percent | Three days of five |
| Casual bridge | job keeps 25 percent of its pay | About one shift a week |
| Client money held | n x A x (0.5 + 0.5 x 90 / 365), with one year of bookings on the calendar | NYP terms: 50 percent at booking, balance 90 days before (Norm 5 Sep 2026), 11.5 month median lead (census 4 Sep 2026) |
| Paid leave | not added as dollars | The salary already pays for the leave weeks, so adding them again counts them twice |
| Working weeks for the ladder's capacity line | 46 | Six weeks of leave a year |
| Owner hours per wedding for the capacity line | coverage hours x 1.35 | Culling at 0.35 an hour, editing outsourced (cost-base.md 1b) |

## 8. Worked scenarios

Hypothetical inputs, labelled so. Scenario A has the shape of Norm's case with stand-in figures until he supplies his payslip. From `model.py`, start 16 November 2026.

| | A. Australia, full-time shift worker (stand-in) | B. Australia, part time, take-home typed | C. Australia, casual, fifteen weddings | D. Somewhere else, payslip mode |
|---|---|---|---|---|
| Gross | $115,000 | $56,900 (net $48,200 typed) | $49,400 | 60,000 (net 46,000, marginal 32%, retirement 3%, sales tax 20%) |
| Weddings now / last, average | 12 / 8, $5,500 | 8 / 5, $4,200 | 15 / 11, $3,800 | 10 / 7, 3,000 |
| Cash out, overhead, kit | $1,260, $8,412, $18,000 | $700, $8,412, $12,000 | $700, $8,412, $15,000 | 700, 8,412, 9,000 |
| Household, buffer months | $7,000, 3 | $5,000, 3 | $4,500, 4 | 3,200, 3 |
| Quit number | $128,800 ($10,733 a month, $7,307 in the bank) | $63,769 | $55,328 | 61,800 |
| Profit today, after tax | $32,868, $21,449 | $14,133, $9,611 | $29,906, $20,336 | 7,788, 5,296 |
| Gap | $95,932 | $49,636 | $25,422 | 54,012 |
| Bookings at today's average and at 1.5x | 38, 23 | 24, 15 | 25, 15 | 41, 24 |
| Buffer, months to fund | $21,000, 12 | $15,000, 19 | $18,000, 11 | 9,600, 22 |
| Straight quit date | April 2033 | March 2032 | March 2029 | November 2036 |

Reading: in every case the lever is the average sale, not the volume. Scenario A at $5,500 needs 38 weddings and arrives in 2033. At $8,200 it needs 23. That is the thesis of Module 1 and the reason the Package Ladder is the second tab.

## 9. The Package Ladder (second tab)

Same inputs, same overhead per wedding at the chosen volume, same floor. For each tier (three or four) the user enters coverage hours, the extra cash cost of that tier's inclusions, a price (or leaves the floor), and a share of bookings.

```
Tier floor price = (c + extra + O / n) x (1 + s) / (1 - f)
```

Default price is the floor lifted so the per hour ramp never dips below the tier beneath. Checks from Vance's ladder work (offer-architecture.md, cost-base.md 1f): even hourly ramp with a dip flagged, every tier clearing the floor at the chosen volume, add-ons with their own cash margin, the hourly commodity trap warning (no base plus add-on hours on every tier, a finish time and a continuation rate at or above the top tier's hourly yield), and the capacity line. The "backwards from the number" block weights the tiers by the booking mix and tests the ladder's profit at n weddings against Q, with the average sale that would reach Q at that volume: ((Q + O) / n + c) x (1 + s). The list of what part-timers leave out shows overhead, the sinking fund, the owner's wage as Q, the retirement contribution, sales tax and cash out per wedding. Printable to A4 for Module 1 lesson 1.2.

## 10. Decisions for Norm

Implemented as written unless Norm changes them.

- D1. Paid leave is not added as dollars (section 7). Alternative: add leave weeks over 52 times take-home to Q.
- D3. The low income tax offset (up to $700 under $66,667 taxable income) is excluded from the Australia preset. Its current figures live in Subdivision 61-D of the Income Tax Assessment Act 1997 and could not be read from the legislation in this session. Excluding it understates the quit number by at most $700 a year for lower earners.
- D7. Withdrawn 9 November 2026. No email gate and no list tool.
- D8. Sole trader tax treatment is assumed. Company structures belong in Module 5.
- D9. Norm's own paramedic figures. The context file says about 12 years at St John WA, the Shift Change design says 15. Norm to confirm the years and supply gross pay including penalties, super rate and take-home from his last payslip so scenario A becomes real.
- D10. Country agnostic by payslip, not by tables. Australia is the only sourced preset.
- D11. In payslip mode the retirement rate and marginal rate have no default and may sit at zero. The result warns rather than guesses.
- D12. Condensed to eleven inputs and three dials, 9 November 2026. Dropped as inputs: pay basis and hours, penalties as a separate line, leave weeks, casual loading, employment type dial, itemised direct costs and overhead lines, payment terms, income protection, growth target average, trial length, part time fraction, casual shifts, other savings. Each is either folded into a top end figure or fixed in section 7. The itemised version is in git history (commit 84b9c2c) if any of it is wanted back.
- D13. Fixed assumptions in section 7, especially the five year kit life and the 60 and 25 percent fractions for the two bridge scenarios.

## 11. Excluded, and said so on the assumptions panel

Tax tables for any country other than Australia (the user supplies the figures). Tax offsets and credits. Study loan repayments. Salary sacrifice. Medicare levy surcharge and family thresholds. Company structures. Seasonality inside the year. Income from other work. Interest on the buffer.

## 12. Yearly update

Every July, Australia preset only: 3a (confirm the 2027-28 table is in force and switch), 3b thresholds, 3c. Change `model.py` section 1 and `RATES` in the app, the date on the assumptions panel, rerun `python3 model.py` and `node app/test.js` with the new expected figures, commit.
