# Quit-Number Calculator: the maths model

Status: draft for Norm's sign-off, written 8 November 2026, revised 9 November 2026 after two rulings from Norm: the calculator must work in any country, and it is not a lead magnet, so there is no email gate and the result shows on the page. The web app is built from this file and nothing else. If a rule or default changes, it changes here first.

The reference implementation is `model.py` in this folder. It runs the three worked scenarios in section 9 and is what the JavaScript gets tested against.

Not tax advice. Every rate below is quoted from the legislation in force on 8 November 2026 and dated. The app carries the same one-line disclaimer and the same dates.

---

## 1. What the calculator answers

One question: can I leave my job, and when.

It takes what the photographer earns from the job today, converts it to the full package the job pays (take-home, retirement contributions, leave, penalties), and shows the profit the photography business must make to replace that package, with a buffer, sustainably. Then it shows the gap from today's wedding profit, the bookings required at three average sale figures, and a dated path: fund the buffer, trial full time on unpaid leave, resign.

### Any country

The first dial is "Where you work": Australia, or somewhere else.

- Australia carries built-in, sourced rates (section 3) so the tool can estimate take-home from a salary. The user can still type their real take-home.
- Somewhere else carries no tax tables. The user types what their payslip and tax office already tell them: gross pay, take-home pay, the tax rate on their next dollar (including levies that scale with income), the employer's retirement contribution rate, the sales tax (GST or VAT) rate, and their currency symbol. Leave weeks come from their contract. Nothing is converted and nothing is guessed. This keeps rule 7 for every country without maintaining a table for each one.

Both paths run the same model from section 5 onward. Section 5 names the two differences. Adding another country as a sourced preset later is a data change, not a model change.

### Not a lead magnet

Norm's ruling, 9 November 2026. The result shows on the page the moment the third step is done. No email is collected and nothing leaves the browser. The earlier email gate, result email and follow-up email are withdrawn.

## 2. Vance's rules and how the model keeps them

| # | Rule | How it is kept |
|---|---|---|
| 1 | Compare net to net. Gross wedding income never sits beside a net payslip. | The job is converted to take-home (Australia: the 2026-27 resident tax table and Medicare levy, then grossed back up with the same table. Elsewhere: gross and take-home straight from the payslip). The business side is profit after direct costs and overhead, before the owner's personal tax. Both sides are therefore pre-personal-tax, same tax law, same person. The result page also shows the after-tax "in your bank" figure for both sides. The tax the side business pays today, sitting on top of a salary at the marginal rate, is computed separately (Australia: bracket arithmetic. Elsewhere: the marginal rate the user enters) so the buffer funding rate is real money. |
| 2 | The owner's wage is a fixed annual cost, never also charged per job. | No per-job line carries the owner's time. Direct costs are cash costs only: second shooter, outsourced editing, album goods, travel, card fees. The owner's hours appear once, as a capacity check in the Package Ladder. |
| 3 | Overhead is annual and divided by volume. | Overhead is entered as annual lines with switches. Overhead per wedding is shown at today's volume and at every required volume, so the user sees it fall as bookings rise. |
| 4 | Deposits are not income. Deposit cover ratio floor 1.0. | The buffer is household cash, never client money. At each required volume the result shows the client money the business will be holding on unshot weddings and says that cash at bank must at least equal it before any of it counts as buffer. |
| 5 | Revenue is ex GST. Ex equals inc divided by 1.1. Margin is net over ex GST revenue. | Every sale is entered as the couple pays it and divided by (1 plus the sales tax rate) when the business is registered. Australia: 10 percent, so divided by 1.1, default on because the quit number sits above the $75,000 registration turnover for almost every user. Elsewhere: the user's GST or VAT rate. Card fees are charged on the amount the couple pays. |
| 6 | A net margin floor, exposed as a dial with a sensible default. | Default 50 percent (NYP's own ladder floor, Norm 3 Sep 2026). The result shows the margin at each required volume and the minimum average sale that clears the floor at that volume. The Package Ladder prices every tier off the floor. |
| 7 | Never invent a figure. Rates from the ATO for the current financial year, dated, with a disclaimer. | Section 3 for Australia. The ATO website refuses automated requests from the build environment, so the rates were taken from the Acts the ATO administers, in their 1 July 2026 compilations on the Federal Register of Legislation, and cross-checked against the ATO figures reported by third parties. Each figure carries its Act, section, compilation number and date. For every other country the rule is kept by carrying no table at all: the user supplies the figures from their own payslip and tax office, and the assumptions panel says so. |

## 3. Rates and statutory defaults (Australia preset)

All figures AUD, financial year 2026-27, as at 8 November 2026. Review every July. The app shows this table on its assumptions panel when Australia is selected. Outside Australia none of 3a to 3d applies. The user's own figures take their place, and 3e's studio defaults are shown as Norm's Australian-dollar reference figures to be replaced.

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

Verified independently: Vance's cost base derived $109,982 gross for $84,000 net using the 2025-26 table (16 percent second band). The same net on the 2026-27 table is $109,588 (`model.py` prints this check). The two differ only by the 2026-27 rate cut, so the model agrees with Vance's arithmetic.

### 3b. Medicare levy

Source: Medicare Levy Act 1986, Compilation No. 53, compilation date 1 July 2026. Section 6(1): rate 2 percent of taxable income. Section 3: threshold amount $28,011, phase-in limit $35,013 (the general case, not the seniors rebate case). Section 7(2): between the threshold and the phase-in limit the levy does not exceed 10 percent of the excess over the threshold.

Model: no levy at or below $28,011. Between $28,011 and $35,013, the lesser of 2 percent of income and 10 percent of the excess over $28,011. Above $35,013, 2 percent.

Not modelled: the family threshold ($47,238 plus $4,338 per dependant, section 8), the Medicare levy surcharge, exemptions. Stated on the assumptions panel.

### 3c. Superannuation guarantee

Source: Superannuation Guarantee (Administration) Act 1992, Compilation No. 77, compilation date 27 March 2026, subsection 19(2) item 13: year starting on or after 1 July 2025, charge percentage 12.

Default 12 percent of base pay. Editable, because some employers pay above the guarantee. Applied to base salary, not to the penalties and allowances field, because overtime is not ordinary time earnings while most shift penalties are. A user whose penalties attract super adds them to the salary field instead. Stated in the field help.

### 3d. Paid leave and casual loading

These are defaults the user is expected to overwrite from their own contract or payslip. They set the shape of the employment type dial.

| Item | Default | Source and status |
|---|---|---|
| Annual leave, full time and part time | 4 weeks | National Employment Standards, Fair Work Act 2009 s 87. The Fair Work Ombudsman's Fair Work Information Statement, surfaced in search on 8 Nov 2026, states 4 weeks for full-time and part-time employees and none for casuals. The fairwork.gov.au pages themselves returned errors from the build environment on 8 Nov 2026. Verify on the live page before launch. |
| Annual leave, shiftworker | 5 weeks (switch, default off) | Fair Work Act 2009 s 87(1)(b). Same verification note. Norm's paramedic case would use this. |
| Personal and carer's leave | 2 weeks (10 days) | Fair Work Act 2009 s 96. Same verification note. |
| Long service leave | 0.8667 weeks a year (switch, default on for full time and part time) | WA Long Service Leave Act 1958 as described on wa.gov.au "Overview of long service leave in WA", page updated 2 September 2026: 8.667 weeks after 10 years of continuous employment, a further 4.333 weeks for each 5 years after. Pro rata payout possible after 7 years. Other states differ, so the field is editable and the help names WA. |
| Casual loading | 25 percent | The standard loading adopted by the Fair Work Commission's 2008 modern awards Full Bench and carried in most modern awards. Casuals receive no paid annual, personal or long service leave. The loading is paid in their place. Awards and agreements vary, so the field is editable. |
| Full-time hours | 38 a week | Fair Work Act 2009 s 62 maximum weekly hours. Used only to convert an hourly rate to an annual figure. Part time and casual users must enter their hours. |

### 3e. Studio defaults from Norm's locked standards

Direct costs per wedding, each with an on and off switch. Defaults are NYP's stated cash costs. The owner's time is never among them (rule 2).

| Line | Default | Switch default | Source |
|---|---|---|---|
| Second photographer | $70 an hour for 8 hours, $560 | on | Rate: cost-base.md section 1, Mel $70 an hour, stated 3 Sep 2026. Hours: nyp-per-job-cost-standards.md, standard 8 hours. The cost base ladder uses 6 and 10 hours by tier. Eight is the standing per-job standard. |
| Editing and culling, outsourced | $650 | on | cost-base.md 2b, stated and resolved 3 Sep 2026 as a genuine outsourced cash cost. The older per-job standard carried $850 ($600 editing plus $250 culling). The cost base supersedes it. If the user edits their own weddings the switch goes off, because their hours are not a per-job cost (rule 2). |
| Album cost of goods | $1,100 ($850 book plus $250 design) | off | cost-base.md 1f and 2c. Only on if albums are inside the package. |
| Travel and fuel | $50 | on | nyp-per-job-cost-standards.md operating block, travel and fuel $50. |
| Card fees | 1.78 percent of the inc GST sale | on | Vance associate model 29 Oct 2026, netted out of Xero sales and so invisible until named. The older standard was Stripe 1.7 percent plus 30 cents. |
| Other direct cost | $0 | | user line |

Annual overhead, each with a switch. A part-time studio does not carry NYP's full stack, so the defaults are the subset every studio must carry, at NYP's stated figures, and the NYP full figure is shown beside each as a reference.

| Line | Default (annual) | Switch default | Source |
|---|---|---|---|
| Insurance | $2,496 ($208 a month) | on | cost-base.md section 2, stated 3 Sep 2026 |
| Bookkeeping and accounting | $3,000 ($250 a month) | on | cost-base.md section 2 |
| Software stack | $2,916 ($243 a month: Pic-Time $52, Adobe $24, Dropbox $23, Photo Mechanic $20, Dubsado $61, hosting $63) | on | cost-base.md section 2, the production and client lines only. NYP's full subscriptions line is $1,628 a month and is shown as the reference. |
| Gear sinking fund | kit replacement value divided by years of life. No default value. The user must enter the kit figure. Life defaults to 5 years. | on | cost-base.md section 3: NYP carries equipment depreciation at $0 and Vance names it the most material omission in the stack. The field is required precisely because of that finding. The 5 year life is a model choice for Norm to confirm. |
| Marketing | $0 a month | off | NYP spends $1,500 to $2,000 a month (cost-base.md 1g). Most part-timers spend nothing, so the default is zero with NYP's figure as the reference. When on, the result shows cost per booking (spend over bookings) and applies Hormozi's same-CAC principle in the Package Ladder: every tier inherits the full cost per booking. |
| Other overhead | $0 | | user line (phone, vehicle, studio rent) |

Cash defaults.

| Item | Default | Source |
|---|---|---|
| Deposit at booking | 50 percent | Norm's ruling 5 Sep 2026, Vance memory.md |
| Balance due | 90 days before the wedding | Norm's ruling 5 Sep 2026 |
| Booking lead time | 11.5 months | NYP census of 237 Dubsado records, cost-base.md section 0, median lead time |
| Net margin floor | 50 percent | NYP's own ladder floor, Norm 3 Sep 2026. NYP's associate jobs use 30 percent. The dial explains both. |

## 4. Inputs

Sliders carry a typed field beside them. Every default is visible and editable. Switches are toggles.

### Step 1. Current position

| Input | Type | Default | Notes |
|---|---|---|---|
| Where you work | dial: Australia, somewhere else | Australia | Australia loads the sourced preset (section 3). Somewhere else switches to payslip mode: take-home, marginal rate, retirement rate and sales tax rate become the user's own entries, long service leave becomes "other paid leave" at zero, casual loading defaults to zero, and a currency symbol field appears. Nothing is converted. |
| Currency symbol | text, somewhere else only | $ | Display only |
| Employment type | dial: full time, part time, casual | full time | Sets leave weeks, hours and the loading logic below |
| Pay basis | toggle: annual salary or hourly rate plus hours | annual | |
| Gross annual salary | slider, $30,000 to $250,000 | none, required | Before tax, excluding super. From the payslip or contract. |
| Hourly rate and hours a week | sliders | hours: 38 for full time, required for part time and casual | Annual gross = rate times hours times 52 |
| My hourly rate already includes casual loading | switch (casual only) | on | If off, the rate is multiplied by 1.25 |
| Penalties and allowances a year | slider, $0 to $60,000 | $0 | Shift penalties, overtime, allowances. Taxed as income. No super applied (see 3c). |
| I know my take-home | switch plus field | off (Australia). Always on and required elsewhere | Annual net from the payslip. Australia: when on, it replaces the tax table for the job side and the gross is recovered by inverting the table. Elsewhere: gross and take-home are both typed and nothing is inverted. |
| Tax rate on your next dollar | slider, 0 to 60 percent, somewhere else only | none, required | The user's marginal rate including levies that scale with income, from their tax office's rate table. Taxes the side business profit while employed. A zero shows a warning on the result. |
| Employer super rate (Australia) or employer retirement contribution rate (elsewhere) | slider | 12 percent (Australia). Required elsewhere, zero allowed | 3c for Australia. Elsewhere: pension, KiwiSaver, 401(k) match, provident fund. A zero with the sustainability switch on shows a warning. |
| Paid leave weeks a year | three fields: annual, personal, long service | 4, 2, 0.87 (casual: 0, 0, 0 and locked) | 3d. Shiftworker switch sets annual leave to 5. |
| Household expenses a month | slider, $2,000 to $20,000 | none, required | What the household spends, not what the user earns. Drives the buffer. |

### Step 2. Current business

| Input | Type | Default |
|---|---|---|
| Weddings this year | slider, 0 to 60 | required |
| Weddings last year | slider, 0 to 60 | equals this year (flat trajectory) |
| Average sale per wedding, inc GST | slider, $1,000 to $25,000 | required |
| Registered for sales tax (GST or VAT), and the rate | switch plus slider | on, 10 percent (Australia). Required elsewhere | Ex revenue is the couple's payment divided by (1 plus the rate) |
| Direct costs | six lines with switches | 3e |
| Annual overhead | seven lines with switches | 3e |
| Deposit percent, balance days, lead time | sliders | 50, 90, 11.5 |

### Step 3. Targets and dials

| Input | Type | Default |
|---|---|---|
| Net margin floor | slider, 20 to 70 percent | 50 |
| Buffer, months of household expenses | slider, 0 to 12 | 3 |
| Cash already set aside for this | field | $0 |
| Other savings a month toward the buffer | field | $0 |
| Sustainability switch (my own super and a sick-leave provision) | switch | on |
| Income protection premium a year | field, counts only when above zero | $0 |
| Growth switch: hold today's average, or set a target average | switch plus slider | off |
| Unpaid leave trial length | slider, 1 to 6 months | 3 |
| Drop to part time: fraction of the job kept | slider, 0.2 to 0.8 | 0.6 (three days of five) |
| Casual bridge: shifts a month and hours a shift | sliders | 4 shifts, 10 hours |

### The result

Shown the moment step 3 is done. No email gate (Norm, 9 November 2026). Nothing leaves the browser. Inputs persist in the visitor's own browser so they can come back.

## 5. The job, converted

Let S be gross salary, P penalties and allowances, r the super rate.

```
Taxable job income        T  = S + P
Income tax                tax(T)   from 3a
Medicare levy             ml(T)    from 3b
Take-home                 N  = T - tax(T) - ml(T)
```

Australia: if the user supplies take-home N directly, T is recovered by inverting `take_home` (bisection, `model.py gross_from_net`).

Somewhere else (payslip mode): T is the gross the user typed and N is the take-home the user typed. No table is applied. The one other place tax appears, the tax the side business pays today (section 6), uses the marginal rate the user entered: tax_biz = B x marginal rate. Everything else in sections 5 to 10 is identical in both modes.

```
Employer super            U  = S x r
Paid leave weeks          L  = annual + personal + long service     (casual: 0)
Working weeks             W  = 52 - L
```

Hourly rate conversion: S = rate x hours x 52. Casual rate not yet loaded: rate x 1.25 first.

### How paid leave is treated, and why it is not added as dollars

The salary already pays for the leave weeks: an employee is paid 52 weeks and works W. Adding leave again as dollars on top of the salary would count it twice. The model carries leave in two places where it is genuinely lost on leaving the job:

1. Time. The business must earn the annual number in W working weeks, not 52. The result shows the weekly run rate as quit number divided by W, and the Package Ladder's capacity check uses W.
2. Risk. Sick leave was income insurance. The sustainability switch adds a provision of the personal leave weeks, at household expenses, to the buffer target (section 7).

Casuals have no leave and their loading already stands in for it, so L is zero and nothing is added. If Norm prefers the alternative, leave as an annual dollar add-back of L divided by 52 times N, it is a one-line change and is listed as decision D1 in section 11.

## 6. The quit number and the gap

### Quit number

The profit the business must make, after every cost of running it and before the owner's personal income tax, to replace the whole package the job paid.

```
Q = T + [sustainability on] U + [income protection premium]
```

Because T is the taxable income that produces N under the same tax table, Q replaces take-home exactly, net to net (rule 1). Shown annually and monthly, with "which lands N in your bank after tax, the same as your payslip" beneath it, also monthly.

The sustainability items are the owner's own super at the same rate the employer paid, and an optional income protection premium. Both are deductible to a sole trader, as employer super is to an employer, so they sit beside T without a gross-up.

### Current business profit

Let n be weddings this year, A the average sale inc GST, g = 1.1 when GST registered (else 1).

```
Revenue ex GST per wedding      R(A) = A / g
Direct cost per wedding         D(A) = second shooter + editing + album + travel + other + card% x A
Contribution per wedding        C(A) = R(A) - D(A)
Annual overhead                 O    = sum of the overhead lines that are on
Overhead per wedding            O / n
Business profit                 B    = n x C(A) - O
Net margin                      m(n, A) = (C(A) - O / n) / R(A)
```

Tax the side business pays today, on top of the salary:

```
tax_biz = [tax(T + B) + ml(T + B)] - [tax(T) + ml(T)]
Business take-home today        B_net = B - tax_biz
```

This is the honest after-tax figure for a side business while employed, and it is what funds the buffer.

### Gap

```
Gap = Q - B           (annual and monthly)
```

If Gap is zero or less: "On paper the business already replaces the job. The question is the buffer and the calendar."

### Bookings required

At average sale A, the bookings that make Q:

```
n*(A) = ceiling( (Q + O) / C(A) )
```

Shown at three averages: today's A, and two higher ones. Default higher averages are A x 1.25 and A x 1.5 rounded to the nearest $100 (model choice, decision D5). When the growth switch is on, the three are today's A, the target average, and target x 1.25. For each: bookings, overhead per wedding O / n*, net margin m(n*, A), whether it clears the floor, and the client money held at that volume (section 8).

### Minimum average sale that clears the margin floor at the required volume

With floor f, fixed direct cost D0 (everything in D except the card fee), card rate c:

```
A_floor = (D0 + O / n*) / ((1 - f) / g - c)
```

Shown as one line: "At n* weddings a year, anything under $A_floor fails your margin floor."

## 7. Buffer and the transition path

### Buffer target

```
Buffer = months x household expenses + [sustainability on, not casual] personal leave weeks / 52 x household expenses x 12
```

The second term is the sick-leave provision (section 5). Shown as two lines so the user sees both.

### Funding rate and dates

```
Monthly funding   F = max(B_net, 0) / 12 + other monthly savings
Months to buffer  = (Buffer - cash saved) / F
Trial threshold   = trial months x household expenses
Months to trial   = (trial threshold - cash saved) / F
```

The trial threshold is deliberately simpler than the buffer: it is enough cash to cover the household for the unpaid leave period even if the business earned nothing during it, so the trial carries no household risk.

### Trajectory

Bookings added per year, G = this year minus last year. The model projects bookings linearly at G a year from today's n, at the path average (today's A, or the target average if the growth switch is on).

```
Months until profit reaches X = ((X + O) / C(A_path) - n) / G x 12     (0 if already there, never if G <= 0)
```

When G is zero or negative and the gap is positive, the dates read "not at this trajectory" and the result page says what G would need to be to quit in 24 months. Linear growth in bookings is a model choice (decision D6). It is conservative against compounding and honest about a business that books through referrals.

### The three scenario cards

Start date is the day the calculator is used.

1. Part time to full time. Trial date = start plus months to trial. Quit date = start plus the later of months to buffer and months until profit reaches Q. Bookings needed = n*(A_path).
2. Drop to part time first. The job keeps paying a fraction phi (default 0.6). The business must cover Q_step = Q - phi x (T + U). Step-down date = start plus the later of months to trial and months until profit reaches Q_step. Bookings needed while part time = n* for Q_step. Then the full quit date as in card 1.
3. Casual bridge. Keep k shifts a month of h hours at a casual rate. Casual rate = today's hourly rate x 1.25 (or the user's casual rate as entered). Casual income Y = rate x h x k x 12. The business must cover Q_casual = Q - Y - [sustainability on] Y x r. Bridge date = start plus the later of months to trial and months until profit reaches Q_casual. Bookings needed = n* for Q_casual.

Each card shows its date, its bookings target and one sentence on what it trades.

## 8. Deposits are not your buffer

At steady state with lead time of 11.5 months, roughly one year of bookings sits on the calendar. Each has paid the deposit. Those inside the 90 day balance window have paid the rest.

```
Client money held H(n, A) = n x min(lead / 12, 1.5) x A x ( d + (1 - d) x balance_days / 365 )
```

Shown at each required volume with one line: "Cash at bank must be at least this before any of it counts as buffer. Deposit cover ratio floor 1.0 (Vance). This money belongs to couples you have not photographed yet."

## 9. Worked scenarios

Inputs in this section are hypothetical and labelled so. Scenario A is the shape of Norm's own case with stand-in figures. Norm replaces them with his payslip before the scenario is used in any lesson or on the free channel. Figures from `model.py`, start date 16 November 2026, all defaults unless stated.

### A. Full-time shift worker to full-time photographer (stand-in figures)

Inputs: salary $95,000, penalties $20,000, shiftworker (5 weeks annual leave), 12 weddings this year, 8 last year, average $5,500, kit $18,000, household $7,000 a month, buffer 3 months.

| Output | Value |
|---|---|
| Taxable job income | $115,000 |
| Income tax, Medicare levy | $25,020, $2,300 |
| Take-home | $87,680 ($7,307 a month) |
| Employer super | $11,400 |
| Paid leave | 7.87 weeks, so 44.1 working weeks |
| Quit number | $126,400 a year, $10,533 a month, landing $7,307 a month in the bank |
| Overhead | $12,012, which is $1,001 a wedding at 12 |
| Contribution per wedding | $3,642 |
| Business profit today | $31,693, taxed $10,960 on top of the salary, $20,733 after tax |
| Gap | $94,707 a year |
| Bookings required | 39 at $5,500 ($308 overhead each, 66.7% margin), 29 at $6,900, 23 at $8,200 |
| Floor check | anything under $3,590 fails the 50% floor at 39 weddings |
| Buffer | $24,231 ($21,000 plus $3,231 sick provision), funded at $1,728 a month, 14.0 months |
| Trial date | November 2027 (12.2 months) |
| Quit date, straight | May 2033 at plus 4 bookings a year |
| Drop to part time (0.6) | business needs $50,560, 18 weddings, step down March 2028 |
| Casual bridge (4 x 10 hour shifts) | casual income $28,846, business needs $94,092, 30 weddings, February 2031 |
| Client money held at 39 weddings | about $128,000 |

Reading: at a $5,500 average this person needs 39 weddings and does not get there until 2033. At $8,200 they need 23. The lever is the average sale, which is the Package Ladder's job and the thesis of Module 1.

### B. Part time, three days a week (hypothetical)

Inputs: $48 an hour, 22.8 hours, 8 weddings this year, 5 last year, average $4,200, no second shooter, kit $12,000, household $5,000, buffer 3.

Quit number $63,738 ($5,311 a month, $4,015 in the bank). Profit today $13,535 ($9,204 after tax). Gap $50,202. Bookings 25 at $4,200, 19 at $5,200, 16 at $6,300. Buffer $17,308 in 22.6 months. Trial July 2028. Straight quit May 2032 at plus 3 a year. Casual bridge covers $28,800 and needs 14 weddings, November 2028.

### C. Casual, fifteen weddings (hypothetical)

Inputs: $38 an hour loaded, 25 hours, 15 weddings this year, 11 last year, average $3,800, no second shooter, kit $15,000, household $4,500, buffer 4.

Quit number $55,328 ($4,611 a month, $3,589 in the bank). No leave, no sick provision. Profit today $28,892 ($19,646 after tax). Gap $26,436. Bookings 25 at $3,800, 19 at $4,800, 16 at $5,700. Buffer $18,000 in 11 months. Trial July 2027. Quit May 2029.

### D. Somewhere else, payslip mode (hypothetical, any currency)

Inputs: region somewhere else, gross 60,000, take-home 46,000, marginal rate 32 percent, employer retirement contribution 3 percent, sales tax 20 percent, 10 weddings this year, 7 last year, average 3,000, no second shooter, kit 9,000, household 3,200 a month, buffer 3 months, currency shown as the pound.

Quit number 61,800 (5,150 a month, 3,833 in the bank). Profit today 7,254, taxed 2,321 at the marginal rate, 4,933 after tax. Gap 54,546. Bookings 42 at 3,000. Net margin today 29 percent, under the 50 percent floor. Buffer 11,077 in 26.9 months. The result tells this user the price is the problem before the calendar is.

### Check against Vance

$84,000 net needs $109,588 gross on the 2026-27 table. Vance's cost base has $109,982 on the 2025-26 table. The difference is the 1 point rate cut in the second band. The model and Vance agree.

## 10. The Package Ladder sheet (second tab)

The calculator gives Q and n*. The ladder turns them into prices. Same inputs, same overhead per wedding at the chosen volume, same floor.

For each tier (three or four), the user enters coverage hours and inclusions (each inclusion with its cash cost and, if sold alone, its retail). The sheet computes:

```
Tier floor price (inc GST) = (D0_tier + O / n) / ((1 - f) / g - c)
```

where D0_tier is editing, travel and the cash cost of that tier's inclusions. The user sets the price at or above the floor. The sheet shows net margin, price per coverage hour, and the step multiple to the next tier.

Checks, all from Vance's ladder work (offer-architecture.md and cost-base.md 1f):

- Even hourly ramp. Price per hour must rise or hold at every step. A dip is flagged: the cheaper-per-hour tier cannibalises the one above (the P2 lesson, 3 Sep 2026).
- Floor tier clears the floor at the chosen volume, not at a hoped-for one.
- Add-ons priced with their own margin: retail against cash cost, each shown. Anything under the floor is flagged. The owner's hours are not a cost (engagement session lesson, 16 Sep 2026).
- Same CAC. When marketing is on, cost per booking is added to every tier's D0. Cheap tiers inherit the full acquisition cost.
- Hourly commodity trap. If the tiers are a flat rate per hour wearing collection names, or if add-on hours are offered on every tier, the sheet warns: quote by collection, with a finish time in the contract and a continuation rate at or above the top tier's hourly yield (C009, Money Lesson 41).
- Capacity. Owner hours per wedding (shoot plus cull at 0.35 an hour, cost-base.md 1b) times n against W working weeks. Shows hours a week.

What part-timers leave out, surfaced as named lines on the sheet: overhead, the gear sinking fund, the owner's wage (as Q), super, GST, income tax, marketing and cost per booking. The sheet is printable to A4 for Module 1 lesson 1.2.

## 11. Decisions for Norm

Each is implemented as written above unless Norm changes it.

- D1. Paid leave is carried as time (working weeks) and risk (sick provision in the buffer), not as a dollar add-back on the salary, to avoid counting it twice. Alternative: add L / 52 x N to Q.
- D2. The buffer is a separate target, not folded into the headline quit number. The result shows "Year one: quit number plus the buffer still to fund" as a second line.
- D3. The low income tax offset (up to $700 for taxable incomes under $66,667) is excluded. Its current figures live in the Income Tax Assessment Act 1997 Subdivision 61-D and could not be read from the legislation in this session. Excluding it understates take-home, and therefore the quit number, by at most $700 a year for lower earners. Add it in a PC session once verified, or leave it out and say so.
- D4. Overhead defaults are the production and compliance lines a part-timer must carry, at NYP's stated figures, with NYP's full stack shown as the reference. The gear sinking fund has no default and must be entered.
- D5. The two higher averages default to today's average times 1.25 and 1.5.
- D6. Trajectory is linear in bookings per year, from this year minus last year.
- D7. Withdrawn 9 November 2026. No email gate and no list tool. The result shows on the page.
- D8. Sole trader tax treatment is assumed for the business. A Pty Ltd structure (company tax, then a wage or dividends) is out of scope for a lead magnet and belongs in Module 5.
- D10. Country agnostic by payslip, not by tables. Australia is the only sourced preset. Other countries can be added as presets later, each with its own dated sources, but the tool never needs them to work. Decided by Norm 9 November 2026 and implemented as above.
- D11. In payslip mode the retirement contribution and marginal rate have no default and may be left at zero. The result page warns when either is zero rather than guessing a figure.
- D9. Norm's own paramedic figures. The context file says around 12 years at St John WA. The Shift Change offer design says 15. Norm to confirm the years and supply the salary, penalties and super from his last payslip so Scenario A becomes real.

## 12. Excluded, and said so on the assumptions panel

Tax tables for any country other than Australia (the user supplies the figures instead). HELP and other study loan repayments. Salary sacrifice. Tax offsets. Medicare levy surcharge and family thresholds. Deductions against the business beyond the costs entered. Company structures. Seasonality of bookings inside the year. Income from engagement sessions, commercial or other work (enter it as "other monthly savings" if it is real cash today). Interest on the buffer.

## 13. Yearly update

Every July: 3a (check the 2027-28 table is in force and switch), 3b thresholds (indexed each year, usually legislated after the Budget), 3c, 3d. Change `model.py` section 1 and the app's rates block, update the date on the assumptions panel, rerun the three scenarios, commit.
