"""Quit-Number Calculator: reference model (condensed, 9 November 2026).

Norm's ruling: a high level, top end planner. Few inputs, worst case
framing. This file is the arithmetic behind maths.md and the JavaScript in
app/index.html is tested against it. Every default is traced in maths.md.
Nothing here is tax advice.

Run:  python3 model.py        (prints the worked scenarios)
"""

from dataclasses import dataclass, field
from datetime import date
import math

# ---------------------------------------------------------------------------
# 1. Australia preset rates. Sourced and dated. Change once a year, here only.
# ---------------------------------------------------------------------------

RATES_AS_AT = "2026-11-08"
FINANCIAL_YEAR = "2026-27"

# Income Tax Rates Act 1986, Compilation No. 66 (1 July 2026), Schedule 7
# Part I, "Tax rates for resident taxpayers for the 2026-27 year of income".
# Section 3(1): tax-free threshold means $18,200.
TAX_BRACKETS = [(18200, 45000, 0.15), (45000, 135000, 0.30), (135000, 190000, 0.37), (190000, math.inf, 0.45)]

# Medicare Levy Act 1986, Compilation No. 53 (1 July 2026). s6(1) 2%.
# s3 threshold $28,011, phase-in limit $35,013. s7(2) 10% of the excess.
MEDICARE_RATE, MEDICARE_THRESHOLD, MEDICARE_PHASE_IN_LIMIT, MEDICARE_PHASE_IN_RATE = 0.02, 28011, 35013, 0.10

# Superannuation Guarantee (Administration) Act 1992, Compilation No. 77
# (27 March 2026), s19(2) item 13: 12% from 1 July 2025.
SUPER_GUARANTEE = 0.12
AU_SALES_TAX = 0.10

# Fixed top end assumptions (maths.md section 7). Not user inputs.
KIT_LIFE_YEARS = 5          # gear sinking fund = kit value / 5
TRIAL_MONTHS = 3            # unpaid leave trial
PART_TIME_FRACTION = 0.6    # drop to part time scenario keeps 60% of the job
CASUAL_FRACTION = 0.25      # casual bridge keeps a quarter of the job's pay
DEPOSIT_PCT, BALANCE_DAYS, LEAD_MONTHS = 0.50, 90, 11.5   # client money held estimate


def income_tax(t):
    return max(sum((min(t, hi) - lo) * r for lo, hi, r in TAX_BRACKETS if t > lo), 0.0)


def medicare_levy(t):
    if t <= MEDICARE_THRESHOLD:
        return 0.0
    full = t * MEDICARE_RATE
    return min(full, (t - MEDICARE_THRESHOLD) * MEDICARE_PHASE_IN_RATE) if t <= MEDICARE_PHASE_IN_LIMIT else full


def take_home(t):
    return t - income_tax(t) - medicare_levy(t)


def gross_from_net(net):
    lo, hi = 0.0, max(net * 3, 50000.0)
    for _ in range(200):
        mid = (lo + hi) / 2
        if take_home(mid) < net:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# ---------------------------------------------------------------------------
# 2. Inputs. Eleven of them, plus three dials.
# ---------------------------------------------------------------------------

@dataclass
class Inputs:
    region: str = "au"              # au | other
    gross: float = 90000            # everything the job pays before tax: base, penalties, allowances, overtime
    net: float | None = None        # take-home a year. Optional in au, required in other
    marginal_rate: float = 0.0      # other only: tax on the next unit of income incl. levies
    retire_rate: float = SUPER_GUARANTEE   # employer retirement contribution rate
    household: float = 6000         # household expenses a month
    weddings_now: int = 10
    weddings_last: int = 10
    average_sale: float = 5000      # as the couple pays it
    cost_per_wedding: float = 1260  # cash out per wedding incl. card fees
    overhead: float = 8412          # annual, excluding gear
    kit_value: float = 0            # replacement value of the kit
    sales_tax: float = AU_SALES_TAX
    margin_floor: float = 0.50
    buffer_months: int = 3
    cash_saved: float = 0
    sustain: bool = True
    start: date = field(default_factory=date.today)


def add_months(d, m):
    mm = d.month - 1 + int(round(m))
    return date(d.year + mm // 12, mm % 12 + 1, 1)


def run(x: Inputs):
    payslip = x.region != "au"
    T = x.gross
    if payslip:
        if x.net is None:
            raise ValueError("take-home required outside Australia")
        N = x.net
        tax_on_extra = lambda extra: max(extra, 0) * x.marginal_rate
    else:
        N = x.net if x.net is not None else take_home(T)
        T = gross_from_net(x.net) if x.net is not None else T
        tax_on_extra = lambda extra: (income_tax(T + max(extra, 0)) + medicare_levy(T + max(extra, 0))) - (income_tax(T) + medicare_levy(T))
    U = x.gross * x.retire_rate
    Q = T + (U if x.sustain else 0)

    g = 1 + x.sales_tax
    rev = lambda a: a / g
    contrib = lambda a: rev(a) - x.cost_per_wedding
    O = x.overhead + x.kit_value / KIT_LIFE_YEARS
    n, A = x.weddings_now, x.average_sale
    B = n * contrib(A) - O
    tax_biz = tax_on_extra(B)
    B_net = B - tax_biz
    gap = Q - B
    margin = lambda nn, a: (contrib(a) - O / nn) / rev(a) if nn else None
    need = lambda a, req=Q: math.ceil((req + O) / contrib(a)) if contrib(a) > 0 else math.inf
    held = lambda nn, a: nn * min(LEAD_MONTHS / 12, 1.5) * a * (DEPOSIT_PCT + (1 - DEPOSIT_PCT) * BALANCE_DAYS / 365)
    r100 = lambda v: round(v / 100) * 100
    averages = [A, r100(A * 1.25), r100(A * 1.5)]
    required = []
    for a in averages:
        nn = need(a)
        required.append(dict(a=a, n=nn, oh=O / nn if math.isfinite(nn) else None, m=margin(nn, a) if math.isfinite(nn) else None,
                             ok=(margin(nn, a) >= x.margin_floor) if math.isfinite(nn) else False, held=held(nn, a) if math.isfinite(nn) else None))
    n_star = required[0]["n"]
    floor_avg = (x.cost_per_wedding + O / n_star) / ((1 - x.margin_floor) / g) if math.isfinite(n_star) else None

    buffer = x.buffer_months * x.household
    F = max(B_net, 0) / 12
    m_buffer = max(buffer - x.cash_saved, 0) / F if F > 0 else math.inf
    m_trial = max(TRIAL_MONTHS * x.household - x.cash_saved, 0) / F if F > 0 else math.inf

    G = n - x.weddings_last
    def months_to(req):
        c = contrib(A)
        need_n = (req + O) / c if c > 0 else math.inf
        if n >= need_n:
            return 0.0
        return (need_n - n) / G * 12 if G > 0 else math.inf
    m_quit = max(months_to(Q), m_buffer)
    q_step = Q - PART_TIME_FRACTION * Q
    m_step = max(months_to(q_step), m_trial)
    q_cas = Q - CASUAL_FRACTION * Q
    m_cas = max(months_to(q_cas), m_trial)
    need24 = (Q + O) / contrib(A) if contrib(A) > 0 else math.inf
    g24 = max((need24 - n) / 2, 0) if math.isfinite(need24) else math.inf

    d = lambda m: add_months(x.start, m) if math.isfinite(m) else None
    return dict(T=T, N=N, U=U, Q=Q, O=O, B=B, tax_biz=tax_biz, B_net=B_net, gap=gap, margin_now=margin(n, A),
                required=required, floor_avg=floor_avg, buffer=buffer, F=F, m_buffer=m_buffer, m_trial=m_trial, G=G,
                full=dict(n=n_star, quit=d(m_quit), trial=d(m_trial)),
                part=dict(need=q_step, n=need(A, max(q_step, 0)), date=d(m_step)),
                casual=dict(need=q_cas, n=need(A, max(q_cas, 0)), date=d(m_cas)), g24=g24)


def fmt(v):
    if v is None or (isinstance(v, float) and not math.isfinite(v)):
        return "n/a"
    return f"{v:,.0f}" if isinstance(v, (int, float)) and abs(v) >= 100 else str(v)


def show(title, x):
    r = run(x)
    print("=" * 70); print(title); print("-" * 70)
    for k in ("T", "N", "U", "Q", "O", "B", "tax_biz", "B_net", "gap", "floor_avg", "buffer", "F"):
        print(f"  {k:<10} {fmt(r[k])}")
    print(f"  margin_now {r['margin_now']*100:.1f}%   months_to_buffer {fmt(r['m_buffer'])}   months_to_trial {fmt(r['m_trial'])}   growth {r['G']}/yr   g24 {fmt(r['g24'])}")
    for b in r["required"]:
        print(f"  at {fmt(b['a'])}: {b['n']} weddings, overhead each {fmt(b['oh'])}, margin {b['m']*100:.1f}%, floor {'ok' if b['ok'] else 'MISSED'}, client money {fmt(b['held'])}")
    print(f"  full: {r['full']}\n  part: {r['part']}\n  casual: {r['casual']}")
    return r


if __name__ == "__main__":
    s = date(2026, 11, 16)
    # A. Shape of Norm's paramedic case, STAND-IN figures until he supplies his payslip.
    show("A. Australia, full-time shift worker (stand-in figures)",
         Inputs(gross=115000, weddings_now=12, weddings_last=8, average_sale=5500, kit_value=18000, household=7000, start=s))
    # B. Australia, part-timer who knows their take-home.
    show("B. Australia, part time, take-home typed (hypothetical)",
         Inputs(gross=56900, net=48200, weddings_now=8, weddings_last=5, average_sale=4200, cost_per_wedding=700, kit_value=12000, household=5000, start=s))
    # C. Australia, casual, fifteen weddings.
    show("C. Australia, casual, fifteen weddings (hypothetical)",
         Inputs(gross=49400, weddings_now=15, weddings_last=11, average_sale=3800, cost_per_wedding=700, kit_value=15000, household=4500, buffer_months=4, start=s))
    # D. Somewhere else, payslip mode, another currency.
    show("D. Somewhere else, payslip mode (hypothetical)",
         Inputs(region="other", gross=60000, net=46000, marginal_rate=0.32, retire_rate=0.03, sales_tax=0.20,
                weddings_now=10, weddings_last=7, average_sale=3000, cost_per_wedding=700, kit_value=9000, overhead=8412, household=3200, start=s))
    print("=" * 70)
    gnet = gross_from_net(84000)
    print(f"Check against cost-base.md: $84,000 net needs ${gnet:,.0f} gross at {FINANCIAL_YEAR} rates (Vance: $109,982 on 2025-26 rates)")
