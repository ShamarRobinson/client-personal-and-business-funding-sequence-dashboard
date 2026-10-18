"""Condensed 10-slide deck in the dark 'metal card' theme (sharp-edged panels, teal/orange edge glow)."""
import csv, json, shutil
from pathlib import Path
from PIL import Image, ImageEnhance

REPO = Path("/home/claude/funding-inquiry-dashboard")
P = Path(__file__).parent / "project"
SL = P / "slides"; AS = P / "assets"
AS.mkdir(exist_ok=True)
DT = REPO / "data" / "tableau"
import sys; sys.path.insert(0, str(REPO / "analysis"))
from update_schedule import ASOF, NEXT_UPDATE

# ---------------------------------------------------------------- photos (compressed)
def jpg(src, name, w):
    im = Image.open(src).convert("RGB")
    if im.width > w: im = im.resize((w, int(im.height * w / im.width)))
    im.save(AS / name, quality=82, optimize=True)
for src, name, w in [("cover_cards.png", "cover_cards.jpg", 1600), ("photo_analytics.png", "photo_analytics.jpg", 1400),
                     ("photo_funding.png", "photo_funding.jpg", 1000), ("photo_advisors.png", "photo_advisors.jpg", 1200),
                     ("photo_approved.png", "photo_approved.jpg", 900)]:
    jpg(REPO / "assets" / src, name, w)
for img in ("c7_tree.png", "c7_ladder.png", "c3_enrich.png", "c3_etl.png", "c7_whatif.png", "c7_ladder_big.png", "c7_tiers.png", "c7_rules.png", "c9_photo.png", "c7_tiers_wide.png", "c7_ladder_wide.png", "c7_tree_wide.png"):
    shutil.copy(REPO / "tableau" / "_build" / "Image" / img, AS / img)

# ---------------------------------------------------------------- theme
BG, CARD, CARD2, LINE = "#07090C", "#161A20", "#1C2129", "#2E3540"
INK, INK2, MUT, TEAL, ORANGE = "#F2EFE8", "#C3C8D0", "#8C94A1", "#2FD4C4", "#FF8A2A"
EXP, EQ, TU = "#4C8DF0", "#F07A3A", "#2EBF86"
BC = {"Experian": EXP, "Equifax": EQ, "TransUnion": TU}
SANS = "'IBM Plex Sans', Arial, sans-serif"; MONO = "'IBM Plex Mono', Menlo, monospace"
GLOW = f"linear-gradient(90deg,{TEAL},{ORANGE})"
def b(t):  # bold bureau names in their color
    for k, c in BC.items():
        t = t.replace(k, f"<span style=\"font-weight:700;color:{c}\">{k}</span>")
    return t
def kicker(t, c=TEAL): return f'<div style="font-family:{MONO};font-size:20px;letter-spacing:.14em;color:{c};text-transform:uppercase">{t}</div>'
def card(inner, style=""):
    return (f'<div style="position:relative;background:{CARD};border:1px solid {LINE};padding:28px 32px;{style}">'
            f'<div style="position:absolute;left:0;right:0;top:-1px;height:3px;background:{GLOW}"></div>{inner}</div>')
def h3(t, c=INK): return f'<div style="font-size:32px;font-weight:600;color:{c};margin-bottom:12px">{t}</div>'
def p(t, size=26, c=INK2): return f'<div style="font-size:{size}px;line-height:1.42;color:{c}">{b(t)}</div>'
def lead(l, t, size=25): return f'<div style="font-size:{size}px;line-height:1.4;color:{INK2};margin-bottom:10px"><span style="font-weight:700;color:{INK}">{l}:</span> {b(t)}</div>'
def ban(v, l, c=INK): return (f'<div style="flex:1;background:{CARD};border:1px solid {LINE};padding:20px 24px;position:relative">'
                              f'<div style="position:absolute;left:0;right:0;top:-1px;height:3px;background:{GLOW}"></div>'
                              f'<div style="font-size:56px;font-weight:600;color:{c};line-height:1">{v}</div><div style="font-size:19px;color:{INK2};margin-top:10px">{b(l)}</div></div>')
def tabs(cur):
    out = ""
    for t in ("Overview", "Maps", "Decide"):
        on = t == cur
        out += f'<span style="padding:8px 22px;font-family:{MONO};font-size:17px;letter-spacing:.1em;{"background:"+TEAL+";color:"+BG if on else "color:"+INK2}">{t.upper()}</span>'
    return f'<div style="display:flex;gap:4px;border:1px solid {LINE};padding:4px;background:{CARD2}">{out}</div>'
def header(n, title, sub, tab, photo=None):
    ph = (f'<div style="position:absolute;right:0;top:0;bottom:0;width:46%;background:url(assets/{photo}) center 40%/cover;opacity:.55;'
          f'-webkit-mask-image:linear-gradient(90deg,transparent,#000 60%);mask-image:linear-gradient(90deg,transparent,#000 60%)"></div>') if photo else ""
    return (f'<div style="position:relative;display:flex;align-items:center;justify-content:space-between;background:#0F1217;border:1px solid {LINE};padding:26px 36px;overflow:hidden">{ph}'
            f'<div style="position:absolute;left:0;right:0;bottom:-1px;height:3px;background:{GLOW}"></div>'
            f'<div style="position:relative"><div style="font-family:{MONO};font-size:18px;color:{TEAL};letter-spacing:.14em">{n:02d} / 12</div>'
            f'<h2 style="font-size:54px;font-weight:600;color:{INK};margin:6px 0 6px;line-height:1.08">{title}</h2>'
            f'<div style="font-size:22px;color:{INK2}">{b(sub)}</div></div><div style="position:relative">{tabs(tab)}</div></div>')
def coach(n, t): return (f'<span style="display:inline-flex;align-items:center;gap:10px;background:{INK};color:{BG};font-size:18px;font-weight:600;padding:4px 16px 4px 4px">'
                         f'<span style="width:30px;height:30px;border-radius:50%;background:{ORANGE};display:inline-flex;align-items:center;justify-content:center;font-weight:700">{n}</span>{t}</span>')
def section(sid, body, notes):
    return (f'<section id="{sid}" data-transition="fade" style="background:{BG};color:{INK};font-family:{SANS};padding:48px 64px;display:flex;flex-direction:column;gap:24px">'
            f'{body}<aside>{notes}</aside></section>\n')

ss = {r["StateAbbr"]: r for r in csv.DictReader(open(DT / "state_summary.csv")) if r["DataSet"] == "All data"}
rs = {r["StateAbbr"]: r for r in csv.DictReader(open(DT / "regression_state.csv"))}
TOTAL = 3003
S = {}

# 1 cover --------------------------------------------------------------
S["cover"] = (f'<section id="cover" data-transition="fade" style="background:{BG};color:{INK};font-family:{SANS};padding:0;position:relative;overflow:hidden">'
    f'<div style="position:absolute;right:0;top:0;bottom:0;width:66%;background:url(assets/cover_cards.jpg) center/cover;'
    f'-webkit-mask-image:linear-gradient(90deg,transparent 0%,#000 45%);mask-image:linear-gradient(90deg,transparent 0%,#000 45%)"></div>'
    f'<div style="position:absolute;left:0;right:0;bottom:0;height:4px;background:{GLOW}"></div>'
    f'<div style="position:relative;padding:120px 96px;display:flex;flex-direction:column;gap:30px;width:980px">'
    f'{kicker("Client Personal and Business Funding Sequence")}'
    f'<h1 style="font-size:92px;font-weight:700;line-height:1.02;margin:0">FP&amp;A: Credit Stacking &amp; Funding Sequencing Strategy</h1>'
    f'<div style="font-size:40px;font-weight:600;color:{TEAL};margin-top:-6px">Which Bureau Will They Pull?</div>'
    f'<div style="font-size:30px;line-height:1.4;color:{INK2}">{b("Experian, Equifax or TransUnion: the report a lender is most likely to check, state by state, and the order to apply in so approvals stack up.")}</div>'
    f'<div style="display:flex;gap:14px;margin-top:30px">{ban("355", "original rows")}{ban("670", "outside datapoints")}{ban("204", "lenders")}{ban("3,003", "recorded pulls", TEAL)}</div>'
    f'<div style="font-size:20px;color:{MUT};margin-top:10px">As of {ASOF} &middot; Next update {NEXT_UPDATE} &middot; Designed by Shamar Robinson</div></div>'
    f'<aside>Open with the one-line purpose: this replaces guesses about which bureau a lender will pull with recorded datapoints. Each bureau keeps one color throughout: Experian blue, Equifax orange, TransUnion green.</aside></section>\n')

# 2 overview: context, purpose, sources, updates, limits ---------------
S["overview"] = section("overview", header(2, "Overview: Context, Sources and Limits", "What this answers, where the data comes from, how it is updated and what it cannot tell you.", "Overview", "photo_analytics.jpg") +
    f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:24px;flex:1">'
    + card(h3("Context") + p("Every hard inquiry lands on one of three credit reports. The same person can have a strong report at one bureau and a weak one at another, and no lender publishes which bureau it pulls by state.")
           + '<div style="height:18px"></div>' + h3("Purpose") + p("Forecast the bureau a lender will pull in each state, then turn that into an application order for personal and business funding."))
    + card(h3("Sources and Updates") + lead("Sources", "a 355-row inquiry table from 16 states plus 670 outside datapoints from 56 cited sources: Doctor of Credit tables (2008 to 2019), the myFICO state grid (2023), 2025 to 2026 forum posts, MyBankTracker, CardRight, StackEasy and lender pages.")
           + lead("As of", f"{ASOF}. Next update: {NEXT_UPDATE}.") + lead("Updates", "lender minimums are reviewed every quarter; each new datapoint reruns the cleaning, maps and model from the same scripts."))
    + card(h3("Data Limits", ORANGE) + lead("Consumer-reported", "no lender publishes its bureau by state.") + lead("Uneven in age", "most pulls are from 2008 to 2016; the newest are 2025 and 2026.")
           + lead("Thin states", "under 10 pulls is a hint, not a finding.") + lead("Not a promise", "income, utilization and recent inquiries decide approvals. Not financial advice."))
    + '</div>', "Slide 2 keeps the sources, update cadence and limits up front, as the Tableau Story does on card 1.")

# 3 market, scope, who it serves ---------------------------------------
S["ladder"] = section("ladder", header(3, "The Funding Ladder: One Score Step at a Time", "Find your step by credit score, finish its moves, let the score rise, then climb. 57 (steps) across 7 (score ranges).", "Overview", "photo_funding.jpg") +
    f'<div style="display:flex;gap:20px;justify-content:space-between"><img src="assets/c7_ladder_wide.png" style="height:314px;display:block"><img src="assets/c7_rules.png" style="height:314px;display:block"></div>'
    f'<img src="assets/c7_tiers_wide.png" style="width:100%;height:auto;display:block">',
    "Each step is a credit score range with its own moves, example lenders, bureau pulled and typical limit, taken from the 57-step funding sequence.")

S["market"] = section("market", header(4, "Market, Scope and Who It Serves", "3,003 recorded bureau pulls, all lenders combined.", "Overview") +
    f'<div style="display:flex;gap:16px">{ban("54%", "Experian share of pulls", EXP)}{ban("25%", "Equifax share", EQ)}{ban("21%", "TransUnion share", TU)}{ban("38 of 49", "states led by Experian")}{ban("24", "close-call states", TEAL)}</div>'
    f'<div style="display:grid;grid-template-columns:1.1fr 1fr 1fr;gap:24px;flex:1">'
    + card(h3("In Scope") + lead("Bureau pulls", "Experian, Equifax and TransUnion, every state and DC.") + lead("Funding types", "cards, lines, loans, SBA, auto, equipment and real estate.")
           + lead("Lender facts", "funding type, typical score and paperwork for 204 lenders (47 low or no doc).") + lead("A sequence", "an application order for seven score ranges, 500 to 800+."))
    + card(h3("Out of Scope", MUT) + lead("Business bureaus", "D&amp;B and similar files are not mapped.")
           + lead("Soft pulls and rates", "prequalification and live rates are left out.") + lead("Advice", "nothing here is legal, tax or investment advice."))
    + (f'<div style="position:relative;border:1px solid {LINE};background:url(assets/photo_advisors.jpg) 35% 30%/cover;display:flex;align-items:flex-end">'
       f'<div style="position:absolute;left:0;right:0;top:-1px;height:3px;background:{GLOW}"></div>'
       f'<div style="width:100%;padding:28px 30px;background:linear-gradient(transparent,rgba(7,9,12,.95) 40%)">{kicker("Who It Serves")}'
       f'<div style="font-size:21px;line-height:1.45;color:{INK};margin-top:10px"><span style="font-weight:700">Clients:</span> personal and business credit clients.<br><span style="font-weight:700">Firms:</span> credit consultants, funding companies, advisors and brokers.<br><span style="font-weight:700">Reviewers:</span> analysts and partners tracing each number.</div></div></div>')
    + '</div>', "Experian dominates nationally, but Equifax leads 2 states and TransUnion 3, with 6 ties. Hover the tiles in the Tableau Story for each formula.")

# 4 KPIs (table with inline data bars) ---------------------------------
KPIS = [("Bureau Share of Pulls", "pulls on one bureau in a state ÷ all bureau pulls there", "Florida: 466 (Experian pulls) ÷ 885 (all pulls) = 53% (share)", .53, EXP),
        ("National Share of Pulls", "one bureau's pulls ÷ all 3,003 pulls", "1,616 (Experian pulls) ÷ 3,003 (all pulls) = 54% (share)", .54, EXP),
        ("Lead Margin", "top share − second share, in points", "Texas: 66% (Experian) − 17% (TransUnion) = 49 pts (lead)", .49, TEAL),
        ("Close Call", "a state whose lead margin is under 20 points", "24 (close-call states) of 49 (states with data)", 24 / 49, TEAL),
        ("Issuer Bureau Habit", "an issuer's pulls on one bureau ÷ its pulls", "American Express: 87% (of its pulls on Experian)", .87, EXP),
        ("Predicted Likelihood", "multinomial logistic regression probability", "Alabama: 43% (chance the pull is Experian)", .43, EXP),
        ("Leader Stability", "refits of 150 where the leader holds", "Connecticut: 95% (of 150 refits keep the leader)", .95, TEAL),
        ("Model Lift", "1 − model log loss ÷ baseline log loss", "1 − 0.903 (model log loss) ÷ 1.041 (baseline) = 13% (lower error)", .13, TEAL),
        ("Cross-Check Result", "rows supported ÷ rows checkable", "193 (rows checked), 0 (contradicted)", 1.0, TEAL),
        ("Lender Confidence Mix", "lenders at each level ÷ 204", "39 (High), 104 (Medium), 61 (Low) of 204 (lenders)", .19, TEAL)]
rows = "".join(f'<tr style="background:{CARD if i % 2 == 0 else CARD2}"><td style="padding:11px 16px;color:{TEAL};font-family:{MONO};font-size:18px">KPI {i + 1}</td>'
               f'<td style="padding:11px 16px;font-weight:600;color:{INK}">{n}</td><td style="padding:11px 16px;color:{INK2}">{f}</td><td style="padding:11px 16px;color:{INK2}">{b(e)}</td>'
               f'<td style="padding:11px 16px;color:{c};font-weight:700">{v:.0%}</td></tr>'
               for i, (n, f, e, v, c) in enumerate(KPIS))
S["kpis"] = section("kpis", header(5, "Ten KPIs With Formulas", f"Each formula worked with the {ASOF} numbers. The bar shows the worked value.", "Overview") +
    f'<table style="width:100%;border-collapse:collapse;font-size:21px;line-height:1.3;border:1px solid {LINE}"><tr style="background:#0F1217;text-align:left;font-family:{MONO};font-size:16px;color:{MUT};letter-spacing:.08em">'
    f'<th style="padding:12px 16px;width:8%">#</th><th style="padding:12px 16px;width:20%">KPI</th><th style="padding:12px 16px;width:29%">FORMULA</th><th style="padding:12px 16px;width:33%">WORKED EXAMPLE</th><th style="padding:12px 16px;width:10%">VALUE</th></tr>{rows}</table>',
    "In the Tableau Story, click any KPI to open its detail card with what it tells you, the formula and the worked example.")

# 5 data and method ----------------------------------------------------
def hbar(label, v, mx, c): return (f'<div style="display:flex;align-items:center;gap:14px;margin-bottom:12px"><div style="width:240px;font-size:21px;color:{INK2}">{label}</div>'
                                   f'<div style="flex:1;background:#262C35;height:22px"><div style="width:{v / mx * 100:.0f}%;height:22px;background:{c}"></div></div><div style="width:50px;font-size:22px;font-weight:600">{v}</div></div>')
S["data"] = section("data", header(6, "Data and Method", "355 inquiries, cleaned, enriched and checked against 670 datapoints from 56 sources.", "Overview", "photo_analytics.jpg") +
    f'<div style="display:grid;grid-template-columns:2.7fr 1fr;gap:24px;flex:1"><div style="display:flex;flex-direction:column;gap:20px;justify-content:center">'
    f'<img src="assets/c3_enrich.png" style="width:100%;display:block"><img src="assets/c3_etl.png" style="width:100%;display:block"></div>'
    f'<div style="display:flex;flex-direction:column;gap:20px">'
    + card(h3("Messy Data That Was Cleaned") + lead("Many spellings", "229 names matched to 102 lenders.", 23) + lead("Mixed markers", "x marks, blanks and counts up to 211 became pulled or not, with counts kept as weights.", 23)
           + lead("Unknowns kept", "11 names are labeled, not forced into a match.", 23), "flex:1")
    + card(h3("Cross-Check: 0 Contradicted") + hbar("Confirmed", 84, 103, TEAL) + hbar("Partly confirmed", 6, 103, "#1D7A72") + hbar("Fits national pattern", 103, 103, "#3B4656") + hbar("Contradicted", 0, 103, ORANGE))
    + '</div></div>', "Read the two flows left to right. Every row could be traced back to a source or the national pattern; none were contradicted.")

# 6 maps: tile-grid share maps + state detail --------------------------
GRID = {"AK": (0, 0), "ME": (11, 0), "VT": (10, 1), "NH": (11, 1), "WA": (1, 2), "ID": (2, 2), "MT": (3, 2), "ND": (4, 2), "MN": (5, 2), "IL": (6, 2), "WI": (7, 2), "MI": (8, 2), "NY": (9, 2), "RI": (10, 2), "MA": (11, 2),
        "OR": (1, 3), "NV": (2, 3), "WY": (3, 3), "SD": (4, 3), "IA": (5, 3), "IN": (6, 3), "OH": (7, 3), "PA": (8, 3), "NJ": (9, 3), "CT": (10, 3),
        "CA": (1, 4), "UT": (2, 4), "CO": (3, 4), "NE": (4, 4), "MO": (5, 4), "KY": (6, 4), "WV": (7, 4), "VA": (8, 4), "MD": (9, 4), "DE": (10, 4),
        "AZ": (2, 5), "NM": (3, 5), "KS": (4, 5), "AR": (5, 5), "TN": (6, 5), "NC": (7, 5), "SC": (8, 5), "DC": (9, 5),
        "OK": (4, 6), "LA": (5, 6), "MS": (6, 6), "AL": (7, 6), "GA": (8, 6), "HI": (0, 7), "TX": (4, 7), "FL": (9, 7)}
def mix(c, t):
    a = (0x1C, 0x21, 0x29); bb = tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))
    return "#" + "".join(f"{int(a[k] + (bb[k] - a[k]) * t):02x}" for k in range(3))
def tilemap(bureau, mx):
    cells = ""
    for ab, (x, y) in GRID.items():
        r = ss.get(ab)
        if not r or int(r["Total Datapoints"]) == 0:
            bg, lab = "#14181E", ""
        else:
            sh = int(r[bureau]) / int(r["Total Datapoints"]); bg = mix(BC[bureau], min(sh / mx, 1) ** .8); lab = f"{sh:.0%}"
        cells += (f'<div style="position:absolute;left:{x * 44}px;top:{y * 44}px;width:41px;height:41px;background:{bg};font-size:11px;line-height:1.1;color:{INK};'
                  f'display:flex;flex-direction:column;align-items:center;justify-content:center"><span style="font-weight:700">{ab}</span><span style="font-size:10px;color:{INK2}">{lab}</span></div>')
    return f'<div data-snap="map_{bureau}" style="position:relative;width:528px;height:352px;background:{CARD}">{cells}</div>'
maps = "".join(card(f'<div style="font-size:24px;font-weight:600;margin-bottom:14px">{b(k)} <span style="color:{INK2};font-weight:400">Share of Pulls</span></div>{tilemap(k, mx)}', "padding:22px 24px")
               for k, mx in (("Experian", 1.0), ("Equifax", .5), ("TransUnion", .5)))
S["maps"] = section("maps", header(7, "Share Maps: Where Each Bureau Is Pulled", "Share = pulls on one bureau in a state ÷ all bureau pulls in that state. Brighter means a bigger share.", "Maps") +
    f'<div style="display:flex;gap:20px">{maps}</div>'
    f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:20px">'
    + card(h3(b("Florida, Experian")) + p("466 of 885 pulls (53%); big samples barely move.", 22))
    + card(h3(b("Equifax belt")) + p("Virginia 39%, South Carolina 37%, North Carolina 36%.", 22))
    + card(h3(b("TransUnion in Georgia")) + p("About 1 in 3 pulls (37 of 116).", 22))
    + card(h3("Small Samples", ORANGE) + p("Montana shows 0% Experian from only 2 pulls.", 22))
    + f'</div><div style="display:flex;gap:16px"><a href="https://public.tableau.com/app/profile/shamar.robinson/viz/ClientPersonalandBusinessFundingSequenceDashboard/WhichBureauWillTheyPull" target="_blank" rel="noopener" title="Open the interactive maps on Tableau Public" style="text-decoration:none;display:inline-flex">{coach(1, "In Tableau, click a state  &#8599;")}</a>{coach(2, "Its detail card opens beside the maps")}</div>',
    "The Equifax and TransUnion maps use a 0 to 50% scale, so a bright Equifax state is still about half as strong as a bright Experian state. The live maps and the State Detail panel are on Tableau Public, card 5.")

# 7 close calls -------------------------------------------------------
groups = {}
for ab, r in rs.items():
    groups.setdefault(r["Close Call Status"], []).append((ab, float(r["P_Experian"])))
GCOL = {"Clear lean": "#ECE6D6", "Moderate lean": "#A69F8E", "Toss-up": "#F2B634", "Thin data (national pattern)": "#6B7380"}
GDESC = {"Clear lean": "leader holds in 90%+ of 150 refits", "Moderate lean": "leader holds in 70%+ of refits", "Toss-up": "leader holds in under 70% of refits", "Thin data (national pattern)": "under 10 datapoints; national pattern shown"}
gcards = ""
for g, col in GCOL.items():
    chips = "".join(f'<span style="display:inline-block;border:1px solid {LINE};background:{CARD2};padding:8px 12px;margin:0 10px 10px 0;font-size:24px"><span style="font-weight:700">{ab}</span> <span style="color:{EXP}">{v:.0%}</span></span>' for ab, v in sorted(groups.get(g, [])))
    gcards += card(f'<div style="display:flex;align-items:baseline;gap:14px"><span style="font-size:64px;font-weight:700;color:{col}">{len(groups.get(g, []))}</span><span style="font-size:26px;font-weight:600">{g.replace(" (national pattern)", "")}</span></div>'
                   f'<div style="font-size:22px;color:{MUT};margin:4px 0 18px">{GDESC[g]}</div>{chips}', f"border-top:0")
S["close"] = section("close", header(8, "Close Calls: The Model's Best Forecast", "In 24 states the top two bureaus are within 20 points. Chips show Experian's predicted likelihood for a typical application.", "Maps") +
    f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:20px;flex:1">{gcards}</div>'
    f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px">{ban("55%", "held-out accuracy vs 50% for national shares")}{ban("13%", "lower error (log loss 0.903 vs 1.041)", TEAL)}{ban("150", "refits to test each leader")}</div>',
    "Multinomial logistic regression on 2,901 datapoints from 862 reports, with five-fold cross-validation that holds out whole reports. In Tableau, hover a state to see its chance bars inside the tooltip.")

# 8 decide -------------------------------------------------------------
S["decide"] = section("decide", header(9, "Decision Tree: Which Lender, in What Order", "Check the five overrides, follow your strongest report's branch, then apply in the Step 3 order.", "Decide", "photo_funding.jpg") +
    f'<div style="display:flex;gap:20px;flex:1;min-height:0"><img src="assets/c7_tree_wide.png" style="height:786px;display:block">'
    f'<div style="display:flex;flex-direction:column;gap:20px;flex:1;min-width:0"><img src="assets/c7_whatif.png" style="width:100%;display:block">'
    + card(p("Every number says what it is in parentheses. Overrides come first; then the branch for your strongest report; then the order in Step 3.", 21), "flex:1") + '</div></div>',
    "Walk the tree top to bottom: five override checks, three bureau branches with three if/then cases each, then four ordering rules.")

# 9 scorecard and recommendations --------------------------------------
HAB = [("All lenders", 54, 25, 21), ("American Express", 87, 5, 8), ("Bank of America", 56, 12, 32), ("Citi", 50, 39, 11), ("Chase", 44, 36, 21),
       ("Wells Fargo", 43, 28, 29), ("Capital One", 37, 35, 28), ("Synchrony", 26, 12, 62), ("U.S. Bank", 25, 28, 47)]
bars = "".join(f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:18px"><div style="width:220px;font-size:22px;color:{INK2};text-align:right">{n}</div><div style="flex:1;display:flex;height:40px">'
               + "".join(f'<div style="width:{v}%;background:{c};font-size:18px;font-weight:600;color:#fff;display:flex;align-items:center;padding-left:6px">{str(v) + "%" if v >= 12 else ""}</div>' for v, c in ((e, EXP), (q, EQ), (t, TU)))
               + '</div></div>' for n, e, q, t in HAB)
bars = f'<div data-snap="habits" style="width:860px;background:{CARD};padding:4px 0">{bars}</div>'
NOTES = [("Sources", "56 (cited sources) plus the original 355-row (inquiry) table."),
         ("Clean", "229 (spellings) matched to 102 (lenders); every mark normalized."),
         ("Check", "193 (rows checked), 0 (contradicted)."),
         ("Model", "multinomial logistic regression, 5-fold cross-validation, 150 (refits)."),
         ("Limits", "consumer-reported; most pulls from 2008 to 2016; likelihoods, not promises.")]
S["scorecard"] = section("scorecard", header(10, "Scorecard: Issuer Habits and Where the Numbers Come From", "Each issuer's bureau habit (KPI 5), how every number was built and what the data cannot tell you.", "Decide") +
    f'<div style="display:grid;grid-template-columns:1.2fr 1fr;gap:24px;flex:1">'
    + card(h3("Issuer Bureau Habits") + f'<div style="font-size:18px;color:{MUT};margin-bottom:16px">{b("Share of each issuer's recorded pulls: Experian, Equifax, TransUnion")}</div>' + bars)
    + card(h3("Where the Numbers Come From") + "".join(lead(r, t, 24) for r, t in NOTES)) + '</div>',
    "Every number in the deck and the Story comes from the same files on GitHub.")
RECS = [("Personal Credit Clients", "Pull all three reports, then apply where your strongest report gets pulled in your state.", "one report is clearly stronger or cleaner.", "check your lender on Tableau card 5; prequalify first."),
        ("Business Credit Clients", "Treat business card applications as personal inquiries.", "you apply for business cards as an owner.", "build the business file in parallel; review the 47 (low or no doc) lenders."),
        ("Credit Consulting Companies", "Plan disputes and inquiry spacing bureau by bureau.", "a client's three reports disagree or carry errors.", "fix the report target lenders pull first, then apply."),
        ("Business Funding Companies", "Stack in strictest-rule order; spread each round across bureaus.", "a client is at 700+ (credit score).", "use the funding ladder and one lender per bureau group per round."),
        ("Funding Advisors and Brokers", "Run the close-call check before advising.", "the client lives in one of the 24 (close-call states).", "in the 4 (toss-up states), plan for any bureau.")]
S["recs"] = section("recs", header(11, "Recommendations: The Best Move for Each Stakeholder", "Best move, when to choose it and the next move, for five stakeholder types.", "Decide") +
    f'<div style="position:relative;height:170px;border:1px solid {LINE};background:url(assets/photo_approved.jpg) center 55%/cover;display:flex;align-items:flex-end">'
    f'<div style="position:absolute;left:0;right:0;top:-1px;height:3px;background:{GLOW}"></div><div style="width:100%;padding:18px 28px;background:linear-gradient(transparent,rgba(7,9,12,.92) 45%)">{kicker("Recommendations")}<div style="font-size:34px;font-weight:600">Approvals That Stack Up</div></div></div>'
    + '<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:18px;flex:1">'
    + "".join(card(h3(w) + lead("Best move", m, 22) + lead("Choose this when", c, 22) + lead("Next move", n, 22)) for w, m, c, n in RECS) + '</div>',
    "Every recommendation traces back to a KPI or an earlier slide. A planning guide, not financial advice.")

# 10 sources, limits, next ---------------------------------------------
def link(t, u): return f'<a href="{u}" style="color:{TEAL};text-decoration:none">{t}</a>'
SRC = [("Doctor of Credit: Which Credit Bureau Does Each Card Issuer Pull?", "https://www.doctorofcredit.com/which-credit-bureau-does-each-card-issuer-pull/"),
       ("myFICO Forums: Which Report Will They Pull, Part 2 (state grid)", "https://ficoforums.myfico.com/t5/General-Credit-Topics/Which-Report-Will-They-Pull-Part-2/td-p/6379773"),
       ("MyBankTracker: Bank of America credit pull", "https://mybanktracker.com/credit-cards/credit-score/credit-report-bank-of-america-pull-273"),
       ("CardRight: Which credit report each bank pulls", "https://cardright.com/list-of-which-credit-report-each-bank-pulls/"),
       ("StackEasy: Credit bureau pull database 2026", "https://www.stackeasy.ai/blog/credit-bureau-pull-database-2026"),
       ("myFICO: Do credit inquiries lower your FICO Score?", "https://www.myfico.com/crediteducation/CreditChecks.aspx"),
       ("FTC: Five percent of consumers had errors (2013)", "https://www.ftc.gov/news-events/news/press-releases/2013/02/ftc-study-five-percent-consumers-had-errors-their-credit-reports-could-result-less-favorable-terms"),
       ("All 56 sources, cited by row", "https://shamarrobinson.github.io/Client-Personal-and-Business-Funding-Sequence-Dashboard/sources.html")]
S["sources"] = section("sources", header(12, "FP&amp;A: Credit Stacking &amp; Funding Sequencing Strategy", f"Which Bureau Will They Pull? Sources, as of {ASOF}; next update {NEXT_UPDATE}.", "Decide") +
    f'<div style="display:grid;grid-template-columns:1.3fr 1fr;gap:24px;flex:1">'
    + card(h3("Key Sources") + "".join(f'<div style="font-size:25px;line-height:1.35;margin-bottom:18px">{link(t, u)}</div>' for t, u in SRC))
    + '<div style="display:flex;flex-direction:column;gap:24px">'
    + card(h3("Live Now") + f'<div style="font-size:25px;line-height:1.7">{link("Tableau Story: Which Bureau Will They Pull", "https://public.tableau.com/views/ClientPersonalandBusinessFundingSequenceDashboard/WhichBureauWillTheyPull?:showVizHome=no")}<br>'
           f'{link("Dashboard website", "https://shamarrobinson.github.io/Client-Personal-and-Business-Funding-Sequence-Dashboard/")}<br>{link("Code and data on GitHub", "https://github.com/ShamarRobinson/client-personal-and-business-funding-sequence-dashboard")}</div>')
    + card(h3("Next Steps", ORANGE) + p("Log new inquiry datapoints and refit the model; resolve the 11 unidentified names; refresh lender minimums each quarter.", 20))
    + '</div></div>', "Close by pointing to the live Story and the sources page; every source opens from Tableau card 11.")

ORDER = ["cover", "overview", "ladder", "market", "kpis", "data", "maps", "close", "decide", "scorecard", "recs", "sources"]
old = [f.stem for f in SL.glob("*.html")]
for f in SL.glob("*.html"): f.unlink()
for k in ORDER: (SL / f"{k}.html").write_text(S[k])
deck = json.load(open(P / "deck.json"))
deck["order"] = ORDER; deck["cover"] = "cover"
deck["sections"] = {"s1": {"description": "Overview: context, sources, limits, market, scope and KPIs.", "start": "cover"},
                    "s2": {"description": "Data, maps and close calls.", "start": "data"},
                    "s3": {"description": "Decide: tree, scorecard, recommendations and sources.", "start": "decide"}}
deck["faces"] = {"ibm-plex-sans": {"family": "IBM Plex Sans", "href": "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap"},
                 "ibm-plex-mono": {"family": "IBM Plex Mono", "href": "https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&display=swap"}}
json.dump(deck, open(P / "deck.json", "w"))
pass
print("slides:", ORDER, "removed:", sorted(set(old) - set(ORDER)))
