"""Quit-Number Calculator: reference model.

This file is the arithmetic behind maths.md, written once in Python so the
numbers in that document can be checked, and so the JavaScript in the web app
has something to be tested against. Every default here is traced to a source
in maths.md. Nothing in this file is tax advice.

Run:  python3 model.py        (prints the three worked scenarios)
"""

from dataclasses import dataclass, field, asdict
from datetime import date
import math

# ---------------------------------------------------------------------------
# 1. Rates. Sourced and dated. Change these once a year and nowhere else.
# ---------------------------------------------------------------------------

RATES_AS_AT = "2026-11-08"
FINANCIAL_YEAR = "2026-27"

# Income Tax Rates Act 1986, Compilation No. 66 (1 July 2026), Schedule 7
# Part I, "Tax rates for resident taxpayers for the 2026-27 year of income".
# Section 3(1): tax-free threshold means $18,200.
TAX_FREE_THRESHOLD = 18200
TAX_BRACKETS = [  # (lower bound exclusive, upper bound inclusive, rate)
    (18200, 45000, 0.15),
    (45000, 135000, 0.30),
    (135000, 190000, 0.37),
    (190000, math.inf, 0.45),
]

# Medicare Levy Act 1986, Compilation No. 53 (1 July 2026).
# s6(1) rate 2%. s3 threshold amount $28,011 and phase-in limit $35,013
# (the "any other case" figures, not the seniors rebate case).
# s7(2): within the phase-in band the levy does not exceed 10% of the excess
# over the threshold. Family thresholds (s8) are not modelled.
MEDICARE_RATE = 0.02
MEDICARE_THRESHOLD = 28011
MEDICARE_PHASE_IN_LIMIT = 35013
MEDICARE_PHASE_IN_RATE = 0.10

# Superannuation Guarantee (Administration) Act 1992, Compilation No. 77
# (27 March 2026), s19(2) item 13: year starting on or after 1 July 2025,
# charge percentage 12.
SUPER_GUARANTEE = 0.12

GST_FACTOR = 1.1  # Australia preset: revenue ex GST = inc GST / 1.1 (Vance rule 5)

# Country agnostic design (Norm, 9 Nov 2026). The tables above belong to the
# Australia preset only. Everywhere else the user's own payslip and tax office
# supply the figures: gross, take-home, marginal rate, employer retirement
# contribution rate, sales tax rate. Nothing is typed from memory for any
# other country (rule 7).


def income_tax(taxable):
    """Resident income tax before offsets. No LITO, no HELP, no offsets."""
    t = 0.0
    for lo, hi, rate in TAX_BRACKETS:
        if taxable > lo:
            t += (min(taxable, hi) - lo) * rate
    return max(t, 0.0)


def medicare_levy(taxable):
    if taxable <= MEDICARE_THRESHOLD:
        return 0.0
    full = taxable * MEDICARE_RATE
    if taxable <= MEDICARE_PHASE_IN_LIMIT:
        return min(full, (taxable - MEDICARE_THRESHOLD) * MEDICARE_PHASE_IN_RATE)
    return full


def take_home(taxable):
    return taxable - income_tax(taxable) - medicare_levy(taxable)


def gross_from_net(net):
    """Invert take_home by bisection. Used when the user types their payslip net."""
    lo, hi = 0.0, max(net * 3, 50000.0)
    for _ in range(200):
        mid = (lo + hi) / 2
        if take_home(mid) < net:
            lo = mid
        else:
            hi = mid
    return round((lo + hi) / 2, 2)


# ---------------------------------------------------------------------------
# 2. Inputs. Every default carries a source tag in maths.md.
# ---------------------------------------------------------------------------

@dataclass
class Job:
    region: str = "au"                # au (sourced preset) | other (payslip mode)
    tax_mode: str = "table"           # table (Australia preset) | payslip (any country)
    marginal_rate: float = 0.0        # payslip mode: tax on the next dollar incl. levies, as a fraction
    employment: str = "full"          # full | part | casual
    pay_basis: str = "annual"         # annual | hourly
    gross_salary: float = 0.0         # annual gross, before tax, excluding super
    hourly_rate: float = 0.0
    hours_per_week: float = 38.0      # full time default 38; part time and casual: user enters
    rate_includes_loading: bool = True  # casual only: is the 25% loading already in the hourly rate
    casual_loading: float = 0.25      # modern awards standard loading
    penalties_allowances: float = 0.0  # annual, taxed as income (shift penalties, overtime, allowances)
    super_rate: float = SUPER_GUARANTEE
    known_take_home: float | None = None  # annual net from the payslip; overrides the tax table
    annual_leave_weeks: float = 4.0   # NES; shiftworkers 5
    personal_leave_weeks: float = 2.0  # NES 10 days
    long_service_weeks: float = 0.8667  # WA Long Service Leave Act: 8.667 weeks per 10 years
    include_long_service: bool = True

    def gross(self):
        if self.pay_basis == "hourly":
            rate = self.hourly_rate
            if self.employment == "casual" and not self.rate_includes_loading:
                rate *= 1 + self.casual_loading
            base = rate * self.hours_per_week * 52
        else:
            base = self.gross_salary
        return base

    def taxable(self):
        return self.gross() + self.penalties_allowances

    def net(self):
        if self.known_take_home is not None:
            return self.known_take_home
        if self.tax_mode == "payslip":
            raise ValueError("payslip mode needs known_take_home")
        return take_home(self.taxable())

    def gross_equivalent(self):
        """Taxable income that produces the net. In table mode with a payslip
        override, recovered by inverting the table. In payslip mode the gross
        is what the user typed."""
        if self.tax_mode == "payslip":
            return self.taxable()
        if self.known_take_home is not None:
            return gross_from_net(self.known_take_home)
        return self.taxable()

    def tax_on_extra(self, base, extra):
        """Tax the side business adds on top of the job. Table mode: the real
        bracket arithmetic. Payslip mode: the marginal rate the user entered."""
        if extra <= 0:
            return 0.0
        if self.tax_mode == "payslip":
            return extra * self.marginal_rate
        return (income_tax(base + extra) + medicare_levy(base + extra)) - (income_tax(base) + medicare_levy(base))

    def employer_super(self):
        # SG is paid on ordinary time earnings. Shift penalties count, overtime
        # does not. The model applies the rate to base pay only and lets the
        # user add the rest by editing the rate or the salary.
        return self.gross() * self.super_rate

    def paid_leave_weeks(self):
        if self.employment == "casual":
            return 0.0
        w = self.annual_leave_weeks + self.personal_leave_weeks
        if self.include_long_service:
            w += self.long_service_weeks
        return w


@dataclass
class Business:
    weddings_now: int = 10
    weddings_last_year: int | None = None   # for the trajectory; defaults to weddings_now
    average_sale_inc: float = 5000.0
    gst_registered: bool = True             # registered for sales tax (GST or VAT)
    sales_tax_rate: float = 0.10            # Australia preset 10%. Elsewhere the user enters it
    # Direct cost per wedding, each with a switch
    second_shooter_on: bool = True
    second_shooter_rate: float = 70.0       # $/hr, NYP cost base
    second_shooter_hours: float = 8.0       # NYP per-job standard
    editing_on: bool = True
    editing_cost: float = 650.0             # NYP cost base 2b, stated 3 Sep 2026
    album_on: bool = False
    album_cost: float = 1100.0              # $850 album + $250 design, cost base 1f
    travel_on: bool = True
    travel_cost: float = 50.0               # NYP operating block, travel and fuel
    card_fee_on: bool = True
    card_fee_rate: float = 0.0178           # 1.78% of the inc GST amount, Vance 29 Oct 2026
    other_direct: float = 0.0
    # Annual overhead, each with a switch. Defaults are NYP stated lines.
    insurance_on: bool = True
    insurance: float = 208 * 12
    accounting_on: bool = True
    accounting: float = 250 * 12
    software_on: bool = True
    software: float = (52 + 24 + 23 + 20 + 61 + 63) * 12   # Pic-Time, Adobe, Dropbox, Photo Mechanic, Dubsado, hosting
    gear_on: bool = True
    kit_replacement_value: float = 0.0      # no default: the user must enter it
    kit_life_years: float = 5.0
    marketing_on: bool = False
    marketing_monthly: float = 0.0          # NYP runs $1,500 to $2,000; part-timer default is zero
    other_overhead: float = 0.0
    # Cash
    deposit_pct: float = 0.50               # Norm's ruling 5 Sep 2026
    balance_days_before: int = 90           # Norm's ruling 5 Sep 2026
    booking_lead_months: float = 11.5       # NYP census median, 4 Sep 2026

    def gst_factor(self):
        return 1 + self.sales_tax_rate if self.gst_registered else 1.0

    def revenue_ex(self, sale_inc):
        return sale_inc / self.gst_factor()

    def direct_cost(self, sale_inc):
        c = 0.0
        if self.second_shooter_on:
            c += self.second_shooter_rate * self.second_shooter_hours
        if self.editing_on:
            c += self.editing_cost
        if self.album_on:
            c += self.album_cost
        if self.travel_on:
            c += self.travel_cost
        if self.card_fee_on:
            c += self.card_fee_rate * sale_inc
        c += self.other_direct
        return c

    def contribution(self, sale_inc):
        return self.revenue_ex(sale_inc) - self.direct_cost(sale_inc)

    def overhead(self):
        o = 0.0
        if self.insurance_on:
            o += self.insurance
        if self.accounting_on:
            o += self.accounting
        if self.software_on:
            o += self.software
        if self.gear_on and self.kit_life_years > 0:
            o += self.kit_replacement_value / self.kit_life_years
        if self.marketing_on:
            o += self.marketing_monthly * 12
        o += self.other_overhead
        return o

    def profit(self, weddings=None, sale_inc=None):
        n = self.weddings_now if weddings is None else weddings
        a = self.average_sale_inc if sale_inc is None else sale_inc
        return n * self.contribution(a) - self.overhead()

    def overhead_per_wedding(self, weddings=None):
        n = self.weddings_now if weddings is None else weddings
        return self.overhead() / n if n else math.inf

    def net_margin(self, weddings, sale_inc):
        rev = self.revenue_ex(sale_inc)
        return (self.contribution(sale_inc) - self.overhead() / weddings) / rev

    def client_money_held(self, weddings, sale_inc):
        """Deposits and balances sitting on unshot weddings at steady state.
        About one year of bookings sits on the calendar (lead time 11.5
        months). All have paid the deposit. The share inside the balance
        window has paid the rest."""
        on_books = weddings * min(self.booking_lead_months / 12, 1.5)
        balance_share = self.balance_days_before / 365
        return on_books * sale_inc * (self.deposit_pct + (1 - self.deposit_pct) * balance_share)

    def cac(self):
        if not self.marketing_on or self.weddings_now == 0:
            return 0.0
        return self.marketing_monthly * 12 / self.weddings_now


@dataclass
class Targets:
    net_margin_floor: float = 0.50          # NYP ladder floor, Norm 3 Sep 2026
    buffer_months: int = 3
    household_monthly: float = 6000.0       # user input, no source
    cash_saved: float = 0.0
    other_monthly_savings: float = 0.0
    sustainability_on: bool = True          # owner super and sick leave provision
    income_protection_annual: float = 0.0   # optional, off at zero
    growth_on: bool = False
    target_average_sale: float | None = None
    trial_months_unpaid_leave: int = 3
    part_time_fraction: float = 0.6         # drop-to-part-time scenario, 3 days of 5
    casual_shifts_per_month: int = 4
    casual_shift_hours: float = 10.0
    start: date = field(default_factory=date.today)


# ---------------------------------------------------------------------------
# 3. The model
# ---------------------------------------------------------------------------

def add_months(d, months):
    m = d.month - 1 + int(round(months))
    y = d.year + m // 12
    m = m % 12 + 1
    return date(y, m, 1)


def run(job: Job, biz: Business, tg: Targets):
    out = {}

    # A. The job, net to net
    net_job = job.net()
    gross_eq = job.gross_equivalent()
    out["job_net"] = net_job
    out["job_gross_equivalent"] = gross_eq
    out["job_income_tax"] = income_tax(gross_eq) if job.tax_mode == "table" else (gross_eq - net_job)
    out["job_medicare"] = medicare_levy(gross_eq) if job.tax_mode == "table" else 0.0
    out["job_super"] = job.employer_super()
    out["job_leave_weeks"] = job.paid_leave_weeks()
    out["working_weeks"] = 52 - job.paid_leave_weeks()

    # B. Quit number: profit the business must make after all its own costs,
    # before the owner's personal tax, to replace the whole package.
    q = gross_eq
    sustain = 0.0
    if tg.sustainability_on:
        sustain += job.employer_super()
    sustain += tg.income_protection_annual
    q += sustain
    out["quit_number"] = q
    out["quit_number_monthly"] = q / 12
    out["quit_number_in_bank"] = net_job
    out["quit_number_in_bank_monthly"] = net_job / 12
    out["sustainability_items"] = sustain

    # C. Current business
    profit0 = biz.profit()
    out["business_profit_now"] = profit0
    out["overhead"] = biz.overhead()
    out["overhead_per_wedding_now"] = biz.overhead_per_wedding()
    out["contribution_per_wedding_now"] = biz.contribution(biz.average_sale_inc)
    out["net_margin_now"] = biz.net_margin(biz.weddings_now, biz.average_sale_inc) if biz.weddings_now else None
    # Tax the side business pays today, on top of the salary
    tax_on_business_now = job.tax_on_extra(gross_eq, profit0)
    out["business_tax_now"] = tax_on_business_now
    out["business_net_now"] = profit0 - tax_on_business_now

    # D. Gap and bookings required
    gap = q - profit0
    out["gap"] = gap
    out["gap_monthly"] = gap / 12

    def bookings_needed(sale_inc, required=q):
        c = biz.contribution(sale_inc)
        if c <= 0:
            return math.inf
        return math.ceil((required + biz.overhead()) / c)

    averages = [biz.average_sale_inc, round(biz.average_sale_inc * 1.25, -2), round(biz.average_sale_inc * 1.5, -2)]
    if tg.growth_on and tg.target_average_sale:
        averages = [biz.average_sale_inc, tg.target_average_sale, round(tg.target_average_sale * 1.25, -2)]
    out["bookings_required"] = []
    for a in averages:
        n = bookings_needed(a)
        out["bookings_required"].append({
            "average_sale_inc": a,
            "bookings": n,
            "overhead_per_wedding": biz.overhead() / n if n not in (0, math.inf) else None,
            "net_margin": biz.net_margin(n, a) if n not in (0, math.inf) else None,
            "clears_floor": (biz.net_margin(n, a) >= tg.net_margin_floor) if n not in (0, math.inf) else False,
            "client_money_held": biz.client_money_held(n, a) if n != math.inf else None,
        })

    # Minimum average sale that clears the margin floor at the required volume
    # Solve for A: (A/g)(1-f) = fixed_direct + card*A + OH/n  where g = GST factor
    g = biz.gst_factor()
    f = tg.net_margin_floor
    n_now = out["bookings_required"][0]["bookings"]
    fixed_direct = biz.direct_cost(0.0)
    card = biz.card_fee_rate if biz.card_fee_on else 0.0
    if n_now not in (0, math.inf):
        denom = (1 - f) / g - card
        out["floor_average_sale_at_required_volume"] = (fixed_direct + biz.overhead() / n_now) / denom if denom > 0 else None
    else:
        out["floor_average_sale_at_required_volume"] = None

    # E. Buffer
    buffer_target = tg.buffer_months * tg.household_monthly
    sick_provision = 0.0
    if tg.sustainability_on and job.employment != "casual":
        sick_provision = job.personal_leave_weeks / 52 * tg.household_monthly * 12
    buffer_target += sick_provision
    out["buffer_target"] = buffer_target
    out["buffer_sick_provision"] = sick_provision
    monthly_funding = max(out["business_net_now"], 0) / 12 + tg.other_monthly_savings
    out["buffer_monthly_funding"] = monthly_funding
    shortfall = max(buffer_target - tg.cash_saved, 0)
    months_to_buffer = shortfall / monthly_funding if monthly_funding > 0 else math.inf
    out["months_to_buffer"] = months_to_buffer
    trial_need = tg.trial_months_unpaid_leave * tg.household_monthly
    months_to_trial = max(trial_need - tg.cash_saved, 0) / monthly_funding if monthly_funding > 0 else math.inf
    out["months_to_trial"] = months_to_trial

    # F. Trajectory. Bookings added per year = this year minus last year.
    last = biz.weddings_last_year if biz.weddings_last_year is not None else biz.weddings_now
    growth = biz.weddings_now - last
    out["bookings_growth_per_year"] = growth

    def months_until_profit_reaches(required, sale_inc=biz.average_sale_inc):
        """Months until n(t) * contribution - overhead >= required, with n
        growing linearly at `growth` per year from weddings_now."""
        c = biz.contribution(sale_inc)
        need_n = (required + biz.overhead()) / c if c > 0 else math.inf
        if biz.weddings_now >= need_n:
            return 0.0
        if growth <= 0:
            return math.inf
        return (need_n - biz.weddings_now) / growth * 12

    sale_for_path = tg.target_average_sale if (tg.growth_on and tg.target_average_sale) else biz.average_sale_inc

    # Scenario 1: part time to full time, straight
    m_profit = months_until_profit_reaches(q, sale_for_path)
    m_quit = max(m_profit, months_to_buffer)
    out["scenario_full"] = {
        "label": "Part time to full time",
        "bookings_needed": bookings_needed(sale_for_path),
        "months_to_trial": months_to_trial,
        "months_to_quit": m_quit,
        "trial_date": add_months(tg.start, months_to_trial) if months_to_trial != math.inf else None,
        "quit_date": add_months(tg.start, m_quit) if m_quit != math.inf else None,
    }

    # Scenario 2: drop to part time first. The job keeps paying a fraction.
    phi = tg.part_time_fraction
    q_step = q - phi * (gross_eq + (job.employer_super() if tg.sustainability_on else 0))
    m_step = max(months_until_profit_reaches(q_step, sale_for_path), months_to_trial)
    out["scenario_part"] = {
        "label": "Drop to part time first",
        "job_fraction": phi,
        "business_profit_needed_while_part_time": q_step,
        "bookings_needed_while_part_time": bookings_needed(sale_for_path, q_step),
        "months_to_step_down": m_step,
        "step_down_date": add_months(tg.start, m_step) if m_step != math.inf else None,
        "months_to_quit": m_quit,
        "quit_date": add_months(tg.start, m_quit) if m_quit != math.inf else None,
    }

    # Scenario 3: casual bridge. Keep some shifts at a casual rate.
    hourly_now = job.gross() / (job.hours_per_week * 52) if job.hours_per_week else 0
    casual_rate = hourly_now * (1 + job.casual_loading) if job.employment != "casual" else hourly_now
    casual_income = casual_rate * tg.casual_shift_hours * tg.casual_shifts_per_month * 12
    q_casual = q - casual_income - (casual_income * job.super_rate if tg.sustainability_on else 0)
    m_casual = max(months_until_profit_reaches(q_casual, sale_for_path), months_to_trial)
    out["scenario_casual"] = {
        "label": "Casual bridge",
        "casual_income_annual": casual_income,
        "business_profit_needed": q_casual,
        "bookings_needed": bookings_needed(sale_for_path, max(q_casual, 0)),
        "months_to_bridge": m_casual,
        "bridge_date": add_months(tg.start, m_casual) if m_casual != math.inf else None,
    }

    out["cac"] = biz.cac()
    return out


# ---------------------------------------------------------------------------
# 4. Package Ladder (second tab)
# ---------------------------------------------------------------------------

def ladder(biz: Business, tg: Targets, weddings: int, tiers):
    """tiers: list of dicts with name, hours, inclusions (list of (name, cost, retail)).
    Returns each tier's floor price at the margin floor and the hourly ramp."""
    g = biz.gst_factor()
    f = tg.net_margin_floor
    card = biz.card_fee_rate if biz.card_fee_on else 0.0
    oh = biz.overhead() / weddings if weddings else math.inf
    rows = []
    prev_per_hour = None
    for t in tiers:
        fixed = (biz.editing_cost if biz.editing_on else 0) + (biz.travel_cost if biz.travel_on else 0) + biz.other_direct
        fixed += sum(c for _, c, _ in t["inclusions"])
        denom = (1 - f) / g - card
        floor_price = (fixed + oh) / denom if denom > 0 else math.inf
        price = t.get("price") or floor_price
        rev = price / g
        direct = fixed + card * price
        net = rev - direct - oh
        per_hour = price / t["hours"] if t["hours"] else None
        rows.append({
            "name": t["name"],
            "hours": t["hours"],
            "floor_price_inc": floor_price,
            "price_inc": price,
            "net_margin": net / rev if rev else None,
            "per_hour_inc": per_hour,
            "dip": (prev_per_hour is not None and per_hour is not None and per_hour < prev_per_hour),
        })
        prev_per_hour = per_hour
    return rows


# ---------------------------------------------------------------------------
# 5. Worked scenarios (hypothetical inputs, see maths.md section 9)
# ---------------------------------------------------------------------------

def fmt(v):
    if v is None:
        return "n/a"
    if v == math.inf:
        return "never at this trajectory"
    if isinstance(v, float):
        return f"${v:,.0f}" if abs(v) >= 100 else f"{v:,.2f}"
    return str(v)


def show(title, job, biz, tg):
    r = run(job, biz, tg)
    print("=" * 72)
    print(title)
    print("-" * 72)
    keys = ["job_gross_equivalent", "job_income_tax", "job_medicare", "job_net", "job_super",
            "job_leave_weeks", "quit_number", "quit_number_monthly", "quit_number_in_bank_monthly",
            "overhead", "overhead_per_wedding_now", "contribution_per_wedding_now",
            "business_profit_now", "business_tax_now", "business_net_now", "net_margin_now",
            "gap", "gap_monthly", "floor_average_sale_at_required_volume",
            "buffer_target", "buffer_sick_provision", "buffer_monthly_funding",
            "months_to_trial", "months_to_buffer", "bookings_growth_per_year", "cac"]
    for k in keys:
        v = r[k]
        if k.startswith("net_margin") and v is not None:
            v = f"{v*100:.1f}%"
        elif k.startswith("months") and v != math.inf:
            v = f"{v:.1f} months"
        else:
            v = fmt(v)
        print(f"  {k:<42} {v}")
    print("  bookings required:")
    for b in r["bookings_required"]:
        nm = f"{b['net_margin']*100:.1f}%" if b["net_margin"] is not None else "n/a"
        print(f"    at {fmt(b['average_sale_inc'])}: {b['bookings']} weddings, overhead/wedding {fmt(b['overhead_per_wedding'])}, net margin {nm}, floor {'ok' if b['clears_floor'] else 'MISSED'}, client money held {fmt(b['client_money_held'])}")
    for s in ("scenario_full", "scenario_part", "scenario_casual"):
        print(f"  {s}:")
        for k, v in r[s].items():
            if isinstance(v, float) and k.startswith("months"):
                v = f"{v:.1f} months" if v != math.inf else "never at this trajectory"
            else:
                v = fmt(v) if not isinstance(v, (str, date)) else str(v)
            print(f"    {k:<40} {v}")
    return r


if __name__ == "__main__":
    start = date(2026, 11, 16)

    # Scenario A: full-time shift worker, salary plus penalties. STAND-IN
    # figures for the shape of Norm's own paramedic case. Norm replaces them
    # with his payslip before this is quoted anywhere.
    show("A. Full-time shift worker to full-time photographer (stand-in figures)",
         Job(employment="full", gross_salary=95000, penalties_allowances=20000, annual_leave_weeks=5),
         Business(weddings_now=12, weddings_last_year=8, average_sale_inc=5500, kit_replacement_value=18000),
         Targets(household_monthly=7000, buffer_months=3, start=start))

    # Scenario B: part-time nurse, three days a week, eight weddings
    show("B. Part-time, three days a week (hypothetical)",
         Job(employment="part", pay_basis="hourly", hourly_rate=48, hours_per_week=22.8),
         Business(weddings_now=8, weddings_last_year=5, average_sale_inc=4200, second_shooter_on=False, kit_replacement_value=12000),
         Targets(household_monthly=5000, buffer_months=3, start=start))

    # Scenario C: casual, hourly rate includes loading, fifteen weddings
    show("C. Casual retail, fifteen weddings (hypothetical)",
         Job(employment="casual", pay_basis="hourly", hourly_rate=38, hours_per_week=25),
         Business(weddings_now=15, weddings_last_year=11, average_sale_inc=3800, second_shooter_on=False, kit_replacement_value=15000),
         Targets(household_monthly=4500, buffer_months=4, start=start))

    # Scenario D: somewhere else, payslip mode. Hypothetical figures in a
    # currency that is not dollars. Gross 60,000, take-home 46,000, marginal
    # rate 32% incl. levies, employer retirement contribution 3%, sales tax 20%.
    show("D. Somewhere else, payslip mode (hypothetical, any currency)",
         Job(region="other", tax_mode="payslip", gross_salary=60000, known_take_home=46000, marginal_rate=0.32,
             super_rate=0.03, casual_loading=0.0, include_long_service=False),
         Business(weddings_now=10, weddings_last_year=7, average_sale_inc=3000, sales_tax_rate=0.20, second_shooter_on=False, kit_replacement_value=9000),
         Targets(household_monthly=3200, buffer_months=3, start=start))

    # Vance's own check from cost-base.md section 1: $84,000 net
    print("=" * 72)
    print("Check against cost-base.md: $84,000 net")
    g = gross_from_net(84000)
    print(f"  gross for $84,000 net at {FINANCIAL_YEAR} rates: ${g:,.0f} (Vance had $109,982 on 2025-26 rates)")
    print(f"  income tax ${income_tax(g):,.0f}, Medicare ${medicare_levy(g):,.0f}, super at 12% ${g*0.12:,.0f}")
