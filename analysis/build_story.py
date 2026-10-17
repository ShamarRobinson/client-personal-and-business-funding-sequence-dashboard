"""Build the Tableau Story "Which Bureau Will They Pull" (8 dashboard cards) from the published workbook.

Input:  tableau/source/published_2026-10-08.twbx (downloaded from Tableau Public)
Output: tableau/Client_Personal_and_Business_Funding_Sequence_Dashboard.twbx

Design: an app-style dashboard in a dark "metal card" theme taken from the cover photo (near-black canvas,
charcoal cards, teal and orange edge glows). Every card has a side panel with the story navigation, a header
band with section tabs and a Help popover. Interactive pieces: formula tooltips on every number, a KPI list
that opens a detail card, share maps that open a State Detail card, a close-call explorer with the chance bars
nested inside the map tooltip, coach marks (numbered orange badges) and a guided walkthrough on card 1.
Each bureau keeps one color everywhere: Experian blue, Equifax orange, TransUnion green.
"""
import csv, html, json, re, shutil, sys, uuid, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import story_images as IMG
from titlecase import tc

SRC = ROOT / "tableau" / "source" / "published_2026-10-08.twbx"
OUT = ROOT / "tableau" / "Client_Personal_and_Business_Funding_Sequence_Dashboard.twbx"
WORK = ROOT / "tableau" / "_build"
DT = ROOT / "data" / "tableau"
ASOF = "October 7, 2026"
esc = lambda s: html.escape(str(s), quote=True)

EXP, EQ, TU = IMG.BUREAU["Experian"], IMG.BUREAU["Equifax"], IMG.BUREAU["TransUnion"]
NAVY, BODY, MUTED, LABEL = "#08306b", "#1f2937", "#4a5568", "#2e6ca8"

# ------------------------------------------------------------------ data
db = json.load(open(ROOT / "data" / "db.json"))
ss = [r for r in csv.DictReader(open(DT / "state_summary.csv")) if r["DataSet"] == "All data"]
tot = {b: sum(int(r[b]) for r in ss) for b in ("Experian", "Equifax", "TransUnion")}
TOTAL = sum(tot.values())
st = {r["State"]: r for r in ss}
top_counts = {}
for r in ss:
    top_counts[r["Top Bureau"]] = top_counts.get(r["Top Bureau"], 0) + 1
ties = sum(v for k, v in top_counts.items() if k.startswith("Tie"))
sb = [r for r in csv.DictReader(open(DT / "scorecard_bars.csv")) if r["Part"] == "Share"]
habit = {}
for r in sb:
    b = {"% EXPERIAN": "Experian", "% EQUIFAX": "Equifax", "% TRANSUNION": "TransUnion"}[r["Panel"]]
    habit.setdefault(r["Item"], {})[b] = float(r["Value"])
lenders = list(csv.DictReader(open(DT / "lenders.csv")))
conf = {k: sum(1 for l in lenders if l["Confidence"] == k) for k in ("High", "Medium", "Low")}
lowdoc = sum(1 for l in lenders if l["LowNoDoc"] == "Yes")
reg = json.load(open(DT / "regression_summary.json"))
fit = {f["Model"].split(" (")[0]: f for f in reg["fit"]}
LL_FULL, LL_BASE = fit["Full model"]["CV Log Loss"], fit["National shares only"]["CV Log Loss"]
ACC_FULL, ACC_BASE = fit["Full model"]["CV Accuracy"], fit["National shares only"]["CV Accuracy"]
rs = {r["State"]: r for r in csv.DictReader(open(DT / "regression_state.csv"))}
close_n = sum(1 for r in rs.values() if r["Close Call"] == "Yes")
status_n = {}
for r in rs.values():
    status_n[r["Close Call Status"]] = status_n.get(r["Close Call Status"], 0) + 1
tossups = sorted(r["State"] for r in rs.values() if r["Close Call Status"] == "Toss-up")
cats = {}
for r in db["states"]:
    cats[r["cat"]] = cats.get(r["cat"], 0) + 1
CONF_ROWS, PART_ROWS = cats["Confirmed by state data"], cats["Partly confirmed by state data"]
FIT_ROWS = cats["Fits national pattern"] + cats.get("Partly fits national pattern", 0)
CHECKED = CONF_ROWS + PART_ROWS + FIT_ROWS
pct = lambda a, b: f"{a / b:.0%}"
def share(state, b): return int(st[state][b]) / int(st[state]["Total Datapoints"])
tx = sorted(((share("Texas", b), b) for b in ("Experian", "Equifax", "TransUnion")), reverse=True)
TX_MARGIN = round((tx[0][0] - tx[1][0]) * 100)

CONTEXT_SOURCES = [
    ("myFICO: Do Credit Inquiries Lower Your FICO Score?", "https://www.myfico.com/crediteducation/CreditChecks.aspx", "Undated, read Oct 2026"),
    ("FTC: In FTC Study, Five Percent of Consumers Had Errors on Their Credit Reports", "https://www.ftc.gov/news-events/news/press-releases/2013/02/ftc-study-five-percent-consumers-had-errors-their-credit-reports-could-result-less-favorable-terms", "Feb 2013"),
    ("CFPB: Analysis of Differences between Consumer- and Creditor-Purchased Credit Scores", "https://files.consumerfinance.gov/f/201209_Analysis_Differences_Consumer_Credit.pdf", "Sep 2012"),
]

# ------------------------------------------------------------------ text helpers
def run(text, size=10, color=BODY, bold=False):
    b = " bold='true'" if bold else ""
    return f"<run{b} fontcolor='{color}' fontsize='{int(round(size))}'>{esc(text)}</run>"
NL = "<run>Æ&#10;</run>"
def para(*runs): return "".join(runs)
def labeled(pairs, size=9.5):
    """[(label, text)] -> runs with a bold label and body text, one pair per line."""
    out = []
    for i, (l, t) in enumerate(pairs):
        out.append((NL if i else "") + run(f"{l}: ", size, BODY, True) + run(t, size, BODY))
    return "".join(out)
def box(title, body_runs, title_color=LABEL, size=11):
    return run(title, size, title_color, True) + NL + body_runs

ZID = [100]
def nid(): ZID[0] += 1; return ZID[0]

order = ["All lenders", "American Express", "Bank of America", "Citi", "Chase", "Wells Fargo", "Capital One", "Synchrony", "U.S. Bank"]
order = ["All lenders"] + sorted(order[1:], key=lambda k: -habit[k]["Experian"])
def zstyle(margin=4, padding=4, bg=None, border=None):
    b = f"<format attr='border-color' value='{border}' /><format attr='border-style' value='solid' /><format attr='border-width' value='1' />" if border else ""
    bgx = f"<format attr='background-color' value='{bg}' />" if bg else ""
    return f"<zone-style>{b}<format attr='margin' value='{margin}' /><format attr='padding' value='{padding}' />{bgx}</zone-style>"

# ================================================================== layout: 8 dashboard cards, 1200 x 800, dark "metal card" theme
W, H = 1200, 800            # layout grid every zone is placed on
DW, DH = 1110, 740          # rendered dashboard size: the 1200 x 800 layout scaled to 92.5% so a card fits a 1080p browser without scrolling
CC = "federated.1cc5tate0ab1cd2ef3gh4ij5kl6m"
BG, CARD, CARD2, LINE_C = IMG.BG, IMG.CARD, IMG.CARD2, IMG.LINE
INK, INK2, MUT, TEAL, ORANGE = IMG.INK, IMG.INK2, IMG.MUTED, IMG.TEAL, IMG.ORANGE
TIPB = {"Experian": "#1F63B8", "Equifax": "#C4501F", "TransUnion": "#13805A"}   # darker bureau colors for white tooltips
BUREAU_COL = {"Experian": EXP, "Equifax": EQ, "TransUnion": TU}
def geo(x, y, w, h): return f"h='{int(h * 100000 / H)}' w='{int(w * 100000 / W)}' x='{int(x * 100000 / W)}' y='{int(y * 100000 / H)}'"
def izone(x, y, w, h, img):
    return f"<zone {geo(x, y, w, h)} id='{nid()}' is-scaled='1' param='Image/{img}' type-v2='bitmap'>{zstyle(0, 0)}</zone>"
def szone(x, y, w, h, sheet, title=False, bg=CARD, pad=6):
    return f"<zone {geo(x, y, w, h)} id='{nid()}' name='{esc(sheet)}' show-title='{'true' if title else 'false'}'>{zstyle(0, pad, bg)}</zone>"
def lzone(x, y, w, h, sheet, param):
    return f"<zone {geo(x, y, w, h)} id='{nid()}' name='{esc(sheet)}' pane-specification-id='0' param='{param}' type-v2='color'>{zstyle(0, 4, CARD)}</zone>"
def fzone(x, y, w, h, sheet, param):
    return f"<zone {geo(x, y, w, h)} id='{nid()}' mode='dropdown' name='{esc(sheet)}' param='{param}' type-v2='filter' values='database'>{zstyle(0, 6, CARD)}</zone>"
def dashboard(name, zones):
    return (f"<dashboard enable-sort-zone-taborder='true' name='{esc(name)}'><style /><size maxheight='{DH}' maxwidth='{DW}' minheight='{DH}' minwidth='{DW}' />"
            f"<zones><zone h='100000' id='{nid()}' type-v2='layout-basic' w='100000' x='0' y='0'>{''.join(zones)}"
            f"<zone-style><format attr='background-color' value='{BG}' /></zone-style></zone></zones>"
            f"<simple-id uuid='{{{str(uuid.uuid4()).upper()}}}' /></dashboard>")

IMG.OUT = WORK / "Image"
if WORK.exists(): shutil.rmtree(WORK)
(WORK / "Image").mkdir(parents=True)

NAV = ["Overview", "Market and KPIs", "Data and Method", "Pick a Lender", "Share Maps", "Close Calls", "Decide", "Scorecard and Moves"]
TABS = ["Overview", "Maps", "Decide"]
TAB_OF = [None, "Overview", "Overview", "Maps", "Maps", "Maps", "Decide", "Decide"]
DASH = [f"{i} {n}" for i, n in enumerate(NAV, 1)]
for i in range(1, 9):
    IMG.sidebar(172, 784, NAV, i, f"sb_{i}")
HEAD_PHOTO = {3: (ROOT / "assets" / "photo_analytics.png", (0.55, 0.6)), 7: (ROOT / "assets" / "photo_funding.png", (0.52, 0.5))}
WINUUID = {n: "{" + str(uuid.uuid4()).upper() + "}" for n in DASH}
def nav_buttons(i):
    """Clickable side-menu rows: each row is an image button (cropped from this card's side panel) that opens its card."""
    from PIL import Image as PImage
    sb = PImage.open(WORK / "Image" / f"sb_{i}.png")
    z = []
    for k in range(1, 9):
        y = 168 + 30 * (k - 1)                       # row text top inside the 172 x 784 side panel (see story_images.sidebar)
        box = (10 * IMG.S, (y - 5) * IMG.S, 158 * IMG.S, (y + 21) * IMG.S)
        sb.crop(box).save(WORK / "Image" / f"nav_{i}_{k}.png")
        z.append(f"<zone {geo(18, 8 + y - 5, 148, 26)} id='{nid()}' type-v2='dashboard-object'>"
                 f"<button action='tabdoc:goto-sheet window-id=&quot;{WINUUID[DASH[k - 1]]}&quot;'>"
                 f"<button-visual-state><image-path>Image/nav_{i}_{k}.png</image-path></button-visual-state></button>{zstyle(0, 0)}</zone>")
    return z
def shell(i, title, sub):
    """Sidebar, header band and the help popover for card i."""
    z = [izone(8, 8, 172, 784, f"sb_{i}.png")] + nav_buttons(i)
    if title:
        ph, fo = HEAD_PHOTO.get(i, (None, None))
        IMG.header_band(1000, 80, title, sub, TABS, TAB_OF[i - 1], f"hd_{i}", right_gap=96, photo=ph, focus=fo or (0.5, 0.5))
        z.append(izone(192, 8, 1000, 80, f"hd_{i}.png"))
        # clickable section tabs: Overview opens card 1, Maps card 4, Decide card 7
        from PIL import Image as PImage
        hd = PImage.open(WORK / "Image" / f"hd_{i}.png")
        for t, (x0, y0, x1, y1), target in zip(TABS, IMG.tab_boxes(1000, 80, TABS, right_gap=96), (1, 4, 7)):
            nm = f"tab_{i}_{t.lower()}"
            hd.crop((int(x0 * IMG.S), int(y0 * IMG.S), int(x1 * IMG.S), int(y1 * IMG.S))).save(WORK / "Image" / f"{nm}.png")
            z.append(f"<zone {geo(192 + x0, 8 + y0, x1 - x0, y1 - y0)} id='{nid()}' type-v2='dashboard-object'>"
                     f"<button action='tabdoc:goto-sheet window-id=&quot;{WINUUID[DASH[target - 1]]}&quot;'>"
                     f"<button-visual-state><image-path>Image/{nm}.png</image-path></button-visual-state></button>{zstyle(0, 0)}</zone>")
        z.append(szone(1096, 28, 84, 38, f"Help {i}", bg=CARD2, pad=2))
    return z

D = {}
# ------------------------------------------------------------------ card 1: overview (hero photo, tiles, context, sources and limits, walkthrough)
PHOTO = ROOT / "assets" / "cover_cards.png"
IMG.photo_hero(1000, 262, PHOTO, "hero",
               ["FP&A Credit Stacking &", "Funding Sequencing Strategy"],
               "Experian, Equifax or TransUnion: which report a lender is most likely to check, state by state, and the order to apply in so approvals stack up without piling inquiries on one report.",
               [], subhead="Which Bureau Will They Pull?")
IMG.text_card(326, 414, [
    ("Context", "Every hard inquiry lands on one of three credit reports. The same person can have a strong report at one bureau and a weak one at another, and no lender publishes which bureau it pulls by state."),
    ("Purpose", "Forecast the bureau a lender will pull in each state, then turn that into an application order for personal and business funding."),
    ("Why It Matters", [("Under 5 points", "what one more hard inquiry usually costs; it counts for a year (myFICO)."),
                        ("1 in 5", "consumers had an error on at least one report (FTC, 2013).")])], "c1_context", size=10)
IMG.text_card(326, 414, [
    ("Sources", "A 355-row inquiry table from 16 states, plus 670 outside datapoints from 56 cited sources: Doctor of Credit tables (2008 to 2019), the myFICO state grid (2023), 2025 to 2026 forum posts and lender pages."),
    ("Updates", f"As of {ASOF}. Lender minimums are reviewed quarterly; each new datapoint reruns the maps and model."),
    ("Limits", "Consumer-reported, uneven in age (most pulls are 2008 to 2016) and thin in some states. Likelihoods, not promises. Not financial advice.")], "c1_sources", size=10)
IMG.steps_card(324, 414, "How to Use This Story", [
    ("Move through 8 cards", "Use the arrows or the captions above; the side panel shows where you are."),
    ("Hover any number", "Tooltips show each formula and its source."),
    ("Click a state or KPI", "A detail panel updates beside the chart."),
    ("Open the About button", "Each card's popover explains it and its terms."),
    ("Follow the orange marks", "Numbered badges show the order to read a card."),
], "c1_steps")
D[DASH[0]] = dashboard(DASH[0], shell(1, None, None) + [
    izone(192, 8, 1000, 262, "hero.png"),
    szone(1096, 20, 84, 38, "Help 1", bg=CARD2, pad=2),
    szone(192, 278, 1000, 92, "Overview Tiles", pad=4),
    izone(192, 378, 326, 414, "c1_context.png"),
    izone(530, 378, 326, 414, "c1_sources.png"),
    izone(868, 378, 324, 414, "c1_steps.png"),
])

# ------------------------------------------------------------------ card 2: market and KPIs (tiles, KPI list + detail panel, scope)
IMG.photo_card(330, 208, ROOT / "assets" / "photo_advisors.png", "c2_who", "WHO IT SERVES", "Clients, Firms and Reviewers", [
    ("Clients", "personal and business credit clients."),
    ("Firms", "consultants, funders, advisors and brokers.")], focus=(0.4, 0.35))
IMG.text_card(324, 596, [
    ("In Scope", [("Bureau pulls", "Experian, Equifax and TransUnion, every state and DC."),
                  ("Funding types", "cards, lines, loans, SBA, auto, equipment, real estate."),
                  ("Lender facts", f"funding type, typical score and paperwork for 204 lenders ({lowdoc} low or no doc)."),
                  ("A sequence", "an application order for seven score ranges, 500 to 800+.")]),
    ("Out of Scope", [("Approval odds", "nothing here predicts approval."),
                      ("Business bureaus", "D&B and similar files are not mapped."),
                      ("Soft pulls and rates", "prequalification and live rates are left out.")])], "c2_scope", size=9.5)
D[DASH[1]] = dashboard(DASH[1], shell(2, "Market and KPIs", f"{TOTAL:,} recorded pulls. Hover a tile for its formula; click a KPI to open its detail card.") + [
    szone(192, 96, 1000, 92, "Market Tiles", pad=4),
    szone(192, 196, 330, 596, "KPI List", pad=8),
    szone(530, 196, 330, 380, "KPI Detail", pad=12),
    izone(530, 584, 330, 208, "c2_who.png"),
    izone(868, 196, 324, 596, "c2_scope.png"),
    izone(700, 204, 150, 26, "cm2_1.png"),
])
IMG.coach(1, "Click a KPI", "cm2_1", w=150, h=26)

# ------------------------------------------------------------------ card 3: data and method
IMG.flow(1000, 150, "From One Table to a Checked Database", [
    ("1. ORIGINAL TABLE", [("rows", "355"), ("states", "16"), ("columns", "State, Bank and three bureau marks")]),
    ("2. CLEAN AND MATCH", [("spellings", "229"), ("lenders", "102"), ("unknown", "11 kept and labeled")]),
    ("3. ENRICH", [("added", "funding type"), ("added", "score needed"), ("added", "paperwork level")]),
    ("4. CROSS-CHECK", [("datapoints", "670"), ("sources", "56"), ("years", "2008 to 2026")]),
    ("5. RESULT", [("confirmed", f"{CONF_ROWS} (+{PART_ROWS} partly)"), ("national fit", f"{FIT_ROWS}"), ("contradicted", "0")]),
], "c3_enrich", result_head="#1D7A72")
IMG.flow(1000, 172, "How It Was Built: Extract, Transform, Load", [
    ("1. EXTRACT", [("read", "original workbook, All States & Banks tab"), ("read", "issuer state tables, 2008 to 2017"), ("read", "myFICO grid (2023) and 2025-2026 posts"), ("read", "lender pages for scores and rules")]),
    ("2. TRANSFORM", [("match", "229 spellings to 102 lenders"), ("normalize", "x, blanks, counts to pulled or not"), ("join", "each row to outside data by lender and state"), ("reshape", "one row per state, lender and bureau")]),
    ("3. LOAD", [("excel", "six-tab workbook with live totals"), ("web", "seven-page site on GitHub Pages"), ("tableau", "maps, regression and this story"), ("model", "weighted datapoints for the regression")]),
], "c3_etl")
IMG.text_card(490, 360, [("Messy Data That Was Cleaned", [
    ("One lender, many spellings", '"Capital One", "Capital One Bank USA" and "Capital One NA" became one company; 229 spellings matched to 102 lenders.'),
    ("Mixed markers", "x marks, blanks, zeros and counts up to 211 became pulled or not pulled, with counts kept as weights."),
    ("Look-alikes", "early rules confused USAA with Apple, so every match was checked by hand."),
    ("Unknowns kept", "11 names could not be identified and are labeled, not forced."),
    ("Non-lenders", "report resellers and tenant screeners are tagged so they do not count.")])], "c3_clean", size=9.5)
IMG.hbars(502, 176, "Cross-Check: 0 of 193 Rows Contradicted", [
    ("Confirmed by state data", CONF_ROWS, TEAL), ("Partly confirmed", PART_ROWS, "#1D7A72"),
    ("Fits national pattern", FIT_ROWS, "#3B4656"), ("Contradicted", 0, ORANGE)], "c3_check")
IMG.hbars(502, 176, "Lender Confidence (204 Lenders)", [
    ("High", conf["High"], TEAL), ("Medium", conf["Medium"], "#1D7A72"), ("Low", conf["Low"], "#3B4656")], "c3_conf",
    note=f"{lowdoc} lenders are low or no doc.")
D[DASH[2]] = dashboard(DASH[2], shell(3, "Data and Method", "355 inquiries, cleaned, enriched and checked against 670 datapoints from 56 sources.") + [
    izone(192, 96, 1000, 150, "c3_enrich.png"),
    izone(192, 252, 1000, 172, "c3_etl.png"),
    izone(192, 432, 490, 360, "c3_clean.png"),
    izone(690, 432, 502, 176, "c3_check.png"),
    izone(690, 616, 502, 176, "c3_conf.png"),
])

# ------------------------------------------------------------------ card 4: pick a lender
IMG.callouts(252, 422, "Lenders by Habit", [
    (EXP, "Experian first", "Chase, Amex, Wells Fargo, Bank of America, PNC, TD."),
    (EQ, "Equifax first", "Truist, Citizens, PenFed, Huntington, KeyBank."),
    (TU, "TransUnion first", "U.S. Bank, Barclays, Synchrony, Navy Federal."),
    (ORANGE, "All three", "Capital One checks every report, so apply there last.")], "c4_groups")
IMG.coach(1, "Pick a lender", "cm4_1", w=170, h=26)
IMG.coach(2, "Hover a state for its counts", "cm4_2", w=250, h=26)
SQLP = "sqlproxy.1x5ubl100cvwz71euyvt402vty6x"
D[DASH[3]] = dashboard(DASH[3], shell(4, "Pick a Lender", "Each state shows the bureau that lender pulls most. Choose a lender on the right.") + [
    szone(192, 96, 740, 696, "Top Bureau by State, by Lender", pad=8),
    fzone(940, 96, 252, 64, "Top Bureau by State, by Lender", f"[{SQLP}].[none:Lender:nk]"),
    lzone(940, 166, 252, 196, "Top Bureau by State, by Lender", f"[{SQLP}].[none:Top Bureau:nk]"),
    izone(940, 370, 252, 422, "c4_groups.png"),
    izone(754, 104, 170, 26, "cm4_1.png"),
    izone(204, 756, 250, 26, "cm4_2.png"),
])

# ------------------------------------------------------------------ card 5: share maps with a state detail panel
IMG.callouts(664, 310, "What the Maps Show", [
    (EXP, "Florida is the most reliable Experian state", "466 of 885 pulls (53%). Big samples barely move when new data arrives."),
    (EQ, "An Equifax belt runs through the Southeast", "Virginia 39%, South Carolina 37%, North Carolina 36%. Its scale tops out near 50%."),
    (TU, "TransUnion matters in a few states", "About 1 in 3 Georgia pulls (37 of 116) landed on TransUnion."),
    (ORANGE, "Small samples look extreme", "Montana shows 0% Experian from only 2 pulls; under 10 pulls is a hint, not a finding.")], "c5_callouts")
IMG.coach(1, "Click any state", "cm5_1", w=170, h=26)
IMG.coach(2, "Its detail opens here", "cm5_2", w=190, h=26)
SHARE_CALC = {"Experian": "Calculation_0014759374798936", "Equifax": "Calculation_0014759375044698", "TransUnion": "Calculation_0014759375245404"}
MAPS = [f"{b} Share of Pulls" for b in ("Experian", "Equifax", "TransUnion")]
D[DASH[4]] = dashboard(DASH[4], shell(5, "Share Maps", "Share = pulls on one bureau in a state ÷ all bureau pulls in that state. Brighter means a bigger share.") + [
    z for i, b in enumerate(("Experian", "Equifax", "TransUnion")) for z in (
        szone(192 + i * 336, 96, 328, 330, f"{b} Share of Pulls", title=True, pad=6),
        lzone(192 + i * 336, 430, 328, 44, f"{b} Share of Pulls", f"[{SQLP}].[usr:{SHARE_CALC[b]}:qk]"))
] + [
    szone(192, 482, 328, 310, "State Detail", pad=12),
    izone(528, 482, 664, 310, "c5_callouts.png"),
    izone(200, 392, 170, 26, "cm5_1.png"),
    izone(322, 488, 190, 26, "cm5_2.png"),
])

# ------------------------------------------------------------------ card 6: close calls (existing explorer, now with viz in tooltip)
IMG.text_card(352, 178, [("How the Model Works",
    f"A multinomial logistic regression on 2,901 datapoints weighs state, lender and data era at once. It is right {ACC_FULL:.0%} of the time versus {ACC_BASE:.0%} for national shares, and is refit 150 times to test each leader.")],
    "c6_model", size=9.5)
IMG.coach(1, "Click a state", "cm6_1", w=150, h=26)
IMG.coach(2, "Hover for its chance bars", "cm6_2", w=230, h=26)
D[DASH[5]] = dashboard(DASH[5], shell(6, "Close Calls", f"In {close_n} states the top two bureaus are within 20 points. Click a state for the model's best forecast.") + [
    szone(192, 96, 640, 696, "CC Map", pad=8),
    szone(840, 96, 352, 200, "CC State Panel", pad=12),
    szone(840, 302, 352, 190, "CC Chance Bars", title=True, pad=8),
    lzone(840, 498, 352, 108, "CC Map", f"[{CC}].[none:Close Call Status:nk]"),
    izone(840, 614, 352, 178, "c6_model.png"),
    izone(204, 724, 150, 26, "cm6_1.png"),
    izone(204, 756, 230, 26, "cm6_2.png"),
])

# ------------------------------------------------------------------ card 7: decide (decision tree, what-if, ladder)
IMG.decision_tree(1000, 372, [
    ("Experian", "pulled most often, so most lenders will see it",
     "favor Experian-first issuers", [("Amex", f"{habit['American Express']['Experian']:.0%} Experian"), ("BofA", f"{habit['Bank of America']['Experian']:.0%} Experian")]),
    ("Equifax", "few lenders lead with Equifax, so choose on purpose",
     "favor Citi and Chase", [("Citi", f"{habit['Citi']['Equifax']:.0%} Equifax"), ("Chase", f"{habit['Chase']['Equifax']:.0%} Equifax")]),
    ("TransUnion", f"least-pulled bureau overall, about {tot['TransUnion'] / TOTAL:.0%}",
     "favor TransUnion-first issuers", [("Synchrony", f"{habit['Synchrony']['TransUnion']:.0%} TransUnion"), ("U.S. Bank", f"{habit['U.S. Bank']['TransUnion']:.0%} TransUnion")]),
], [("you live in a close-call state", "check card 6 first"),
    ("your score is under 650", "start low on the funding ladder"),
    ("one report already has new inquiries", "switch to issuers that pull another bureau")], name="c7_tree")
IMG.whatif_table(490, 316, [
    ("American Express in Kansas", "Experian", {"Experian": .84, "Equifax": .05, "TransUnion": .11}, ""),
    ("Chase in Florida", "Experian", {"Experian": .43, "Equifax": .37, "TransUnion": .21}, ""),
    ("Capital One in Virginia", "Equifax", {"Experian": .29, "Equifax": .45, "TransUnion": .26}, ""),
    ("Synchrony in Ohio", "TransUnion", {"Experian": .26, "Equifax": .09, "TransUnion": .65}, ""),
], compact=True, name="c7_whatif")
IMG.ladder(502, 316, [
    ("500-549", "Repair", "Fix errors, builder loan."), ("550-599", "Start small", "Prequalify, starter card."),
    ("600-649", "Unsecured", "Mainstream cards."), ("650-699", "Majors", "Chase, then Amex."),
    ("700-749", "Stack", "0% business cards."), ("750-799", "Banks", "Bank lines, SBA."),
    ("800+", "Biggest first", "Largest facilities.")], name="c7_ladder")
D[DASH[6]] = dashboard(DASH[6], shell(7, "Decide: Tree, Forecast and Ladder", "Start from your strongest report, check a real forecast, then find your step on the funding ladder.") + [
    izone(192, 96, 1000, 372, "c7_tree.png"),
    izone(192, 476, 490, 316, "c7_whatif.png"),
    izone(690, 476, 502, 316, "c7_ladder.png"),
])

# ------------------------------------------------------------------ card 8: scorecard, recommendations, sources
IMG.text_card(502, 538, [
    ("Personal Credit Clients", "Pull all three reports, then apply where your strongest report gets pulled in your state. Prequalify before any hard inquiry."),
    ("Business Credit Clients", f"Most business cards check the owner's personal report. Build the business file in parallel and review the {lowdoc} low or no doc lenders."),
    ("Credit Consulting Companies", "Fix the report the client's target lenders pull first; one in five consumers has an error on at least one report (FTC)."),
    ("Business Funding Companies", "Stack in strictest-rule order (Chase, Amex, U.S. Bank, Wells Fargo, Bank of America) and leave Capital One last."),
    ("Funding Advisors and Brokers", f"Run the close-call check first. Experian is the best forecast in all {close_n} close calls, but {len(tossups)} are toss-ups ({', '.join(tossups[:-1])} and {tossups[-1]})."),
], "c8_recs", title="The Best Move for Each Stakeholder", size=10.5)
IMG.photo_card(502, 150, ROOT / "assets" / "photo_approved.png", "c8_photo", "RECOMMENDATIONS", "Approvals That Stack Up", [], focus=(0.5, 0.55))
D[DASH[7]] = dashboard(DASH[7], shell(8, "Scorecard, Moves and Sources", "Each issuer's bureau habit, the best move for each stakeholder, and every source (click to open).") + [
    szone(192, 96, 490, 340, "Issuer Habits", title=True, pad=8),
    szone(192, 444, 490, 348, "Sources List", title=True, pad=8),
    izone(690, 96, 502, 150, "c8_photo.png"),
    izone(690, 254, 502, 538, "c8_recs.png"),
])

# ================================================================== KPI definitions (used by the KPI list, detail panel and tooltips)
K1 = [(1, "Bureau share of pulls", "how likely a pull in one state is to land on one bureau, all lenders combined.",
       "pulls on one bureau in a state ÷ all bureau pulls in that state.", f"Florida, Experian: 466 ÷ 885 = {466 / 885:.0%}."),
      (2, "National share of pulls", "which bureau lenders use most across the country.",
       f"one bureau's pulls ÷ all {TOTAL:,} recorded pulls.", f"Experian {tot['Experian']:,} ÷ {TOTAL:,} = {tot['Experian'] / TOTAL:.0%}; Equifax {tot['Equifax'] / TOTAL:.0%}; TransUnion {tot['TransUnion'] / TOTAL:.0%}."),
      (3, "Lead margin", "how far the top bureau is ahead in a state.",
       "top bureau share − second bureau share, in percentage points.", f"Texas: Experian {tx[0][0]:.0%} − {tx[1][1]} {tx[1][0]:.0%} = {TX_MARGIN} points."),
      (4, "Close call", "where the map alone cannot decide.",
       "a state whose lead margin is under 20 points in the recorded pulls.", f"{close_n} of 49 states. In Alabama, Experian and Equifax are tied at {share('Alabama', 'Experian'):.0%} (0 points)."),
      (5, "Issuer bureau habit", "how predictable one lender is.",
       "an issuer's pulls on one bureau ÷ that issuer's recorded pulls.",
       f"American Express {habit['American Express']['Experian']:.0%} Experian; Synchrony {habit['Synchrony']['TransUnion']:.0%} TransUnion; Capital One splits {habit['Capital One']['Experian']:.0%} / {habit['Capital One']['Equifax']:.0%} / {habit['Capital One']['TransUnion']:.0%}.")]
K2 = [(6, "Predicted likelihood", "the chance each bureau is pulled for a typical application, after weighing state, lender and data era together.",
       "multinomial logistic regression probability; the three chances add up to 100%.",
       f"Alabama: Experian {float(rs['Alabama']['P_Experian']):.0%}, Equifax {float(rs['Alabama']['P_Equifax']):.0%}, TransUnion {float(rs['Alabama']['P_TransUnion']):.0%}."),
      (7, "Leader stability", "how sure the model is about the top bureau.",
       "refits (out of 150) where the same bureau stays on top; at least 90% is a clear lean, at least 70% a moderate lean.",
       f"Connecticut {float(rs['Connecticut']['Leader Holds in Resamples']):.0%} (clear lean); Alabama {float(rs['Alabama']['Leader Holds in Resamples']):.0%} (moderate lean)."),
      (8, "Model lift", "how much better the model is than national shares alone.",
       "1 − (model log loss ÷ baseline log loss), from 5-fold cross-validation.",
       f"1 − ({LL_FULL:.3f} ÷ {LL_BASE:.3f}) = {1 - LL_FULL / LL_BASE:.0%} lower error; accuracy {ACC_FULL:.0%} versus {ACC_BASE:.0%}."),
      (9, "Cross-check result", "how much of the original table outside data supports.",
       "rows confirmed, partly confirmed or fitting the national pattern ÷ rows that had outside data to check.",
       f"{CHECKED} of 355 rows could be checked ({CONF_ROWS} + {PART_ROWS} + {FIT_ROWS}), and 0 were contradicted."),
      (10, "Lender confidence mix", "how much evidence stands behind each lender profile.",
       "lenders at each confidence level ÷ 204 lenders.",
       f"{conf['High']} High ({conf['High'] / 204:.0%}), {conf['Medium']} Medium ({conf['Medium'] / 204:.0%}), {conf['Low']} Low ({conf['Low'] / 204:.0%}).")]

# Every number in a worked example says what it is, in parentheses.
WORKED = {
    1: (f"Florida, Experian: 466 (Experian pulls in Florida) ÷ 885 (all bureau pulls in Florida) = {466 / 885:.0%} (Experian's share of Florida pulls).",
        f"Florida: 466 (Experian pulls) ÷ 885 (all pulls) = {466 / 885:.0%} (share)"),
    2: (f"{tot['Experian']:,} (Experian pulls nationwide) ÷ {TOTAL:,} (all recorded pulls) = {tot['Experian'] / TOTAL:.0%} (Experian's national share). "
        f"Equifax: {tot['Equifax']:,} (pulls) = {tot['Equifax'] / TOTAL:.0%} (share); TransUnion: {tot['TransUnion']:,} (pulls) = {tot['TransUnion'] / TOTAL:.0%} (share).",
        f"{tot['Experian']:,} (Experian pulls) ÷ {TOTAL:,} (all pulls) = {tot['Experian'] / TOTAL:.0%} (share)"),
    3: (f"Texas: {tx[0][0]:.0%} (Experian's share of Texas pulls) − {tx[1][0]:.0%} ({tx[1][1]}'s share, the runner-up) = {TX_MARGIN} points (Experian's lead in Texas).",
        f"Texas: {tx[0][0]:.0%} (Experian) − {tx[1][0]:.0%} ({tx[1][1]}) = {TX_MARGIN} pts (lead)"),
    4: (f"{close_n} (close-call states) of 49 (states with data). Alabama: {share('Alabama', 'Experian'):.0%} (Experian's share) and {share('Alabama', 'Equifax'):.0%} (Equifax's share) = 0 points (lead, a tie).",
        f"{close_n} (close-call states) of 49 (states with data)"),
    5: (f"American Express: {habit['American Express']['Experian']:.0%} (share of its pulls on Experian). Synchrony: {habit['Synchrony']['TransUnion']:.0%} (share on TransUnion). "
        f"Capital One: {habit['Capital One']['Experian']:.0%} (Experian), {habit['Capital One']['Equifax']:.0%} (Equifax), {habit['Capital One']['TransUnion']:.0%} (TransUnion).",
        f"American Express: {habit['American Express']['Experian']:.0%} (of its pulls on Experian)"),
    6: (f"Alabama: {float(rs['Alabama']['P_Experian']):.0%} (chance of Experian), {float(rs['Alabama']['P_Equifax']):.0%} (chance of Equifax), "
        f"{float(rs['Alabama']['P_TransUnion']):.0%} (chance of TransUnion); the three add to 100%.",
        f"Alabama: {float(rs['Alabama']['P_Experian']):.0%} (chance the pull is Experian)"),
    7: (f"Connecticut: {float(rs['Connecticut']['Leader Holds in Resamples']):.0%} (of 150 refits keep its leader, a clear lean). "
        f"Alabama: {float(rs['Alabama']['Leader Holds in Resamples']):.0%} (of refits keep its leader, a moderate lean).",
        f"Connecticut: {float(rs['Connecticut']['Leader Holds in Resamples']):.0%} (of 150 refits keep the leader)"),
    8: (f"1 − ({LL_FULL:.3f} (model log loss) ÷ {LL_BASE:.3f} (national-shares log loss)) = {1 - LL_FULL / LL_BASE:.0%} (lower error). "
        f"Accuracy: {ACC_FULL:.0%} (model) versus {ACC_BASE:.0%} (national shares alone).",
        f"{1 - LL_FULL / LL_BASE:.0%} (lower error than national shares)"),
    9: (f"{CHECKED} (rows that could be checked) = {CONF_ROWS} (confirmed) + {PART_ROWS} (partly confirmed) + {FIT_ROWS} (fit the national pattern); 0 (contradicted).",
        f"{CHECKED} (rows checked), 0 (contradicted)"),
    10: (f"{conf['High']} (High-confidence lenders, {conf['High'] / 204:.0%}), {conf['Medium']} (Medium, {conf['Medium'] / 204:.0%}), {conf['Low']} (Low, {conf['Low'] / 204:.0%}) of 204 (lenders profiled).",
         f"{conf['High']} High, {conf['Medium']} Medium, {conf['Low']} Low (lenders by confidence)"),
}
K1 = [(n, nm, t, f, WORKED[n][0]) for n, nm, t, f, _ in K1]
K2 = [(n, nm, t, f, WORKED[n][0]) for n, nm, t, f, _ in K2]

# ------------------------------------------------------------------ worksheets and datasources for the interactive and source cards
from tableauhyperapi import HyperProcess, Telemetry, Connection, CreateMode, TableDefinition, SqlType, TableName, Inserter
def hyper(fname, cols, rows):
    p = WORK / "Data" / "Extracts" / fname
    p.parent.mkdir(parents=True, exist_ok=True)
    stp = {"string": SqlType.text(), "integer": SqlType.big_int(), "real": SqlType.double()}
    with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hp:
        with Connection(hp.endpoint, str(p), CreateMode.CREATE_AND_REPLACE) as cx:
            cx.catalog.create_schema("Extract")
            td = TableDefinition(TableName("Extract", "Extract"), [TableDefinition.Column(c, stp[t]) for c, t in cols])
            cx.catalog.create_table(td)
            cv = {"string": lambda v: v, "integer": lambda v: int(float(v)) if v not in ("", None) else None, "real": lambda v: float(v) if v not in ("", None) else None}
            with Inserter(cx, td) as ins:
                ins.add_rows([[cv[t](r[c]) for c, t in cols] for r in rows]); ins.execute()

def datasource(key, caption, fname, cols, rows, extra_cols="", dsname=None):
    (WORK / "Data" / "data").mkdir(parents=True, exist_ok=True)
    with open(WORK / "Data" / "data" / fname, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=[c for c, _ in cols]); w.writeheader(); [w.writerow({c: r[c] for c, _ in cols}) for r in rows]
    hyp = fname.replace(".csv", ".hyper"); hyper(hyp, cols, rows)
    tcode = {"string": 129, "integer": 20, "real": 5}
    oid = f"{fname}_{uuid.uuid4().hex.upper()}"
    colxml = "".join(f"<column datatype='{t}' name='{esc(c)}' ordinal='{i}' />" for i, (c, t) in enumerate(cols))
    fam = fname.replace(".csv", "#csv")
    rel = f"<relation connection='textscan.{key}' name='{fname}' table='[{fam}]' type='table'><columns character-set='UTF-8' header='yes' locale='en_US' separator=','>{colxml}</columns></relation>"
    def rec(c, t, i, ext):
        coll = "<collation flag='0' name='LEN_RUS' />" if t == "string" else ""
        if ext:
            return (f"<metadata-record class='column'><remote-name>{esc(c)}</remote-name><remote-type>{tcode[t]}</remote-type><local-name>[{esc(c)}]</local-name>"
                    f"<parent-name>[Extract]</parent-name><remote-alias>{esc(c)}</remote-alias><ordinal>{i}</ordinal><family>{fname}</family><local-type>{t}</local-type>"
                    f"<aggregation>{'Count' if t == 'string' else 'Sum'}</aggregation><approx-count>{len(rows)}</approx-count><contains-null>true</contains-null>{coll}<object-id>[{oid}]</object-id></metadata-record>")
        return (f"<metadata-record class='column'><remote-name>{esc(c)}</remote-name><remote-type>{tcode[t]}</remote-type><local-name>[{esc(c)}]</local-name>"
                f"<parent-name>[{fname}]</parent-name><remote-alias>{esc(c)}</remote-alias><ordinal>{i}</ordinal><local-type>{t}</local-type>"
                f"<aggregation>{'Count' if t == 'string' else 'Sum'}</aggregation>{'<scale>1</scale><width>1073741823</width>' if t == 'string' else ''}<contains-null>true</contains-null>{coll}<object-id>[{oid}]</object-id></metadata-record>")
    meta = "".join(rec(c, t, i, False) for i, (c, t) in enumerate(cols))
    emeta = "".join(rec(c, t, i, True) for i, (c, t) in enumerate(cols))
    fields = ""
    for c, t in cols:
        if t == "string":
            sem = " semantic-role='[State].[Name]'" if c == "State" else ""
            fields += f"<column datatype='string' name='[{esc(c)}]' role='dimension'{sem} type='nominal' />"
        else:
            fmt = " default-format='p0%'" if c in ("Predicted Likelihood", "Observed Share", "Leader Holds in Resamples") else ""
            fields += f"<column datatype='{t}'{fmt} name='[{esc(c)}]' role='measure' type='quantitative' />"
    fields += f"<column caption='{fname}' datatype='table' name='[__tableau_internal_object_id__].[{oid}]' role='measure' type='quantitative' />"
    extract = (f"<extract count='-1' enabled='true' object-id='{oid}' units='records' user-specific='false'><connection authentication='auth-none' author-locale='en_US' class='hyper' "
               f"dbname='Data/Extracts/{hyp}' default-settings='yes' schema='Extract' tablename='Extract' update-time='10/17/2026 06:30:00 AM'>"
               f"<relation name='Extract' table='[Extract].[Extract]' type='table' /><refresh><refresh-event add-from-file-path='{caption}' increment-value='%null%' "
               f"refresh-type='create' rows-inserted='{len(rows)}' timestamp-start='2026-10-17 06:30:00.000' /></refresh>"
               f"<metadata-records>{emeta}</metadata-records></connection></extract>")
    graph = (f"<object-graph><objects><object caption='{fname}' id='{oid}'><properties context=''>{rel}</properties>"
             f"<properties context='extract'><relation name='Extract' table='[Extract].[Extract]' type='table' /></properties></object></objects></object-graph>")
    return (f"<datasource caption='{esc(caption)}' inline='true' name='{dsname or 'federated.' + key}' version='18.1'><connection class='federated'><named-connections>"
            f"<named-connection caption='{esc(caption)}' name='textscan.{key}'><connection class='textscan' directory='Data/data' /></named-connection>"
            f"</named-connections>{rel}<metadata-records>{meta}</metadata-records></connection><aliases enabled='yes' />{fields}{extra_cols}{extract}"
            f"<layout dim-ordering='alphabetic' measure-ordering='alphabetic' show-structure='true' />"
            f"<semantic-values><semantic-value key='[Country].[Name]' value='&quot;United States&quot;' /></semantic-values>{graph}</datasource>")

cc_rows = list(csv.DictReader(open(DT / "regression_state_long.csv")))
for r in cc_rows:
    r["Result"] = rs[r["State"]]["Summary"]
    r["Sample Note"] = rs[r["State"]]["Sample Note"]
cc_cols = [("State", "string"), ("StateAbbr", "string"), ("Bureau", "string"), ("Predicted Likelihood", "real"), ("Observed Share", "real"),
           ("Close Call", "string"), ("Close Call Status", "string"), ("Datapoints", "integer"), ("Pct Label", "string"), ("Result", "string"), ("Sample Note", "string")]
CC = "federated.1cc5tate0ab1cd2ef3gh4ij5kl6m"
cc_calc = ("<column caption='Map Label' datatype='string' name='[Calc_cc_label]' role='dimension' type='nominal'>"
           "<calculation class='tableau' formula='IF [Close Call] = &quot;Yes&quot; THEN [StateAbbr] END' /></column>")
PANEL = {"Calc_p_title": f"IF COUNTD([State]) &gt; 1 THEN &quot;Pick a State&quot; ELSE ATTR([State]) END",
         "Calc_p_status": f"IF COUNTD([State]) &gt; 1 THEN &quot;All 49 states with data&quot; ELSE ATTR([Close Call Status]) END",
         "Calc_p_result": f"IF COUNTD([State]) &gt; 1 THEN &quot;The map is colored by verdict. Click a state to see its result; the bars show the average chance across all states until you do.&quot; ELSE ATTR([Result]) END",
         "Calc_p_note": f"IF COUNTD([State]) &gt; 1 THEN &quot;&quot; ELSE &quot;Based on &quot; + STR(INT(AVG([Datapoints]))) + &quot; recorded pulls; sample: &quot; + ATTR([Sample Note]) END"}
cc_calc += "".join(f"<column caption='{k}' datatype='string' name='[{k}]' role='measure' type='nominal'><calculation class='tableau' formula='{v}' /></column>" for k, v in PANEL.items())
STATUS_COL = {"Clear lean": "#5B3FA8", "Moderate lean": "#A796DC", "Toss-up": "#E0B43A", "Thin data (national pattern)": "#C3C8D1", "Not a close call": "#EEF0F3"}
BUREAU_COL = {"Experian": EXP, "Equifax": EQ, "TransUnion": TU}
ds_cc = datasource("0cc5tate0ab1cd2ef3gh4ij5kl6m", "Close Calls by State", "close_calls_state.csv", cc_cols, cc_rows, cc_calc, dsname=CC)
ds_cc = ds_cc.replace("<semantic-values>", "<style><style-rule element='mark'>"
    + "<encoding attr='color' field='[none:Close Call Status:nk]' type='palette'>" + "".join(f"<map to='{c}'><bucket>&quot;{esc(k)}&quot;</bucket></map>" for k, c in STATUS_COL.items()) + "</encoding>"
    + "<encoding attr='color' field='[none:Bureau:nk]' type='palette'>" + "".join(f"<map to='{c}'><bucket>&quot;{k}&quot;</bucket></map>" for k, c in BUREAU_COL.items()) + "</encoding>"
    + "</style-rule></style><semantic-values>", 1)
ds_cc = ds_cc.replace("<extract ", "<column-instance column='[Close Call Status]' derivation='None' name='[none:Close Call Status:nk]' pivot='key' type='nominal' />"
                      "<column-instance column='[Bureau]' derivation='None' name='[none:Bureau:nk]' pivot='key' type='nominal' /><extract ", 1)

src_rows = []
for i, s in enumerate(db["sources"], 1):
    if s[4]:
        src_rows.append({"n": str(len(src_rows) + 1), "Source": s[1], "Dated": s[3], "url": s[4]})
for name, url, dated in CONTEXT_SOURCES:
    src_rows.append({"n": str(len(src_rows) + 1), "Source": name, "Dated": dated, "url": url})
SR = "federated.1st0rysrc0ab1cd2ef3gh4ij5kl6"
ds_src = datasource("0st0rysrc0ab1cd2ef3gh4ij5kl6", "Story Sources", "story_sources.csv", [("n", "integer"), ("Source", "string"), ("Dated", "string"), ("url", "string")], src_rows, dsname=SR)

def deps(ds, cols, instances, extra=""):
    used = set(re.findall(r"column='\[([^\]]+)\]'", "".join(instances)))
    cols = [(n, t) for n, t in cols if n in used]
    if extra:  # only the calculated columns this sheet uses
        keep = [m.group(0) for m in re.finditer(r"<column caption='[^']*' datatype='[^']*' name='\[([^\]]+)\]'.*?</column>", extra) if m.group(1) in used]
        extra = "".join(keep)
    c = "".join(f"<column datatype='{t}' name='[{esc(n)}]' role='{'dimension' if t == 'string' else 'measure'}'{' semantic-role=&apos;[State].[Name]&apos;' if n == 'State' else ''} type='{'nominal' if t == 'string' else 'quantitative'}' />" for n, t in cols)
    c = c.replace("&apos;", "'")
    return f"<datasource-dependencies datasource='{ds}'>{c}{extra}{''.join(instances)}</datasource-dependencies>"
def inst(col, kind):
    if kind == "nk": return f"<column-instance column='[{esc(col)}]' derivation='None' name='[none:{esc(col)}:nk]' pivot='key' type='nominal' />"
    if kind == "attr": return f"<column-instance column='[{esc(col)}]' derivation='Attribute' name='[attr:{esc(col)}:nk]' pivot='key' type='nominal' />"
    if kind == "ok": return f"<column-instance column='[{esc(col)}]' derivation='None' name='[none:{esc(col)}:ok]' pivot='key' type='ordinal' />"
    d = {"sum": "Sum", "avg": "Avg"}[kind]
    return f"<column-instance column='[{esc(col)}]' derivation='{d}' name='[{kind}:{esc(col)}:qk]' pivot='key' type='quantitative' />"
def worksheet(name, title_runs, ds, caption, dep, body, rows_, cols_, style="", show_title=True):
    t = f"<layout-options><title><formatted-text>{title_runs or '<run> </run>'}</formatted-text></title></layout-options>"
    return (f"<worksheet name='{esc(name)}'>{t}<table><view><datasources><datasource caption='{esc(caption)}' name='{ds}' /></datasources>"
            f"{"<mapsources><mapsource name='Tableau' /></mapsources>" if 'Geometry' in body else ''}{dep}<aggregation value='true' /></view>"
            + (f"<style>{style}</style>" if style else "<style />") + f"<panes>{body}</panes>" + (f"<rows>{rows_}</rows>" if rows_ else "<rows />") + (f"<cols>{cols_}</cols>" if cols_ else "<cols />") + "</table>"
            +
            f"<simple-id uuid='{{{str(uuid.uuid4()).upper()}}}' /></worksheet>")


def rid(): return "1" + uuid.uuid4().hex[:27]
def palette_style(ds_xml, maps):
    """maps: {column: {value: color}} -> datasource-level color encodings plus column-instances."""
    enc = "".join(f"<encoding attr='color' field='[none:{c}:nk]' type='palette'>" + "".join(f"<map to='{col}'><bucket>&quot;{esc(k)}&quot;</bucket></map>" for k, col in m.items()) + "</encoding>" for c, m in maps.items())
    ds_xml = ds_xml.replace("<semantic-values>", f"<style><style-rule element='mark'>{enc}</style-rule></style><semantic-values>", 1)
    ci = "".join(f"<column-instance column='[{c}]' derivation='None' name='[none:{c}:nk]' pivot='key' type='nominal' />" for c in maps)
    return ds_xml.replace("<extract ", ci + "<extract ", 1)
def cf(name, formula, role="measure"):
    return f"<column caption='{name}' datatype='string' name='[{name}]' role='{role}' type='nominal'><calculation class='tableau' formula='{formula}' /></column>"
def F(t): return esc(t)  # escape a Tableau formula for XML
def ref(ds, c, kind="nk"):
    return f"[{ds}].[none:{c}:{kind}]"
def T(ds, c, kind="nk", pre="none"):   # field token inside formatted text
    return f"&lt;[{ds}].[{pre}:{c}:{kind}]&gt;"
def tiprun(t, color="#1F2937", size=9, bold=False):
    b = " bold='true'" if bold else ""
    return f"<run{b} fontcolor='{color}' fontsize='{size}'>{t}</run>"
def tooltip(runs): return f"<customized-tooltip show-buttons='false'><formatted-text>{runs}</formatted-text></customized-tooltip>"
def label(runs): return f"<customized-label><formatted-text>{runs}</formatted-text></customized-label>"
NLR = "<run>Æ&#10;</run>"
def catfilter(ds, col, val):
    return (f"<filter class='categorical' column='[{ds}].[none:{col}:nk]'><groupfilter function='member' level='[none:{col}:nk]' member='&quot;{esc(val)}&quot;' "
            f"user:ui-domain='database' user:ui-enumeration='inclusive' user:ui-marker='enumerate' /></filter>")
def bgstyle(extra=""):
    return (f"<style-rule element='table'><format attr='background-color' value='{CARD}' /><format attr='band-size' scope='rows' value='0' /><format attr='band-size' scope='cols' value='0' /></style-rule>"
            f"<style-rule element='pane'><format attr='background-color' value='{CARD}' /><format attr='border-width' value='0' /></style-rule>"
            f"<style-rule element='label'><format attr='color' value='{INK2}' /></style-rule>"
            f"<style-rule element='worksheet'><format attr='color' value='{INK2}' /></style-rule>"
            f"<style-rule element='legend'><format attr='color' value='{INK2}' /></style-rule>"
            f"<style-rule element='legend-title'><format attr='color' value='{INK}' /></style-rule>"
            f"<style-rule element='gridline'><format attr='stroke-size' value='0' /><format attr='line-visibility' value='off' /></style-rule>"
            f"<style-rule element='zeroline'><format attr='stroke-size' value='0' /><format attr='line-visibility' value='off' /></style-rule>"
            f"<style-rule element='table-div'><format attr='stroke-size' value='0' /><format attr='line-visibility' value='off' /></style-rule>"
            + extra)

# ------------------------------------------------------------------ tiles (BANs with formula tooltips)
TILES = [
    ("1", 1, "355", "original rows", "Ink", "The inquiry table this project started from: 355 rows from 16 states, every one cross-checked."),
    ("1", 2, "670", "outside datapoints", "Ink", "State-level datapoints added from 56 cited sources, 2008 to 2026."),
    ("1", 3, "204", "lenders profiled", "Ink", f"Each with funding type, typical score and paperwork level; {conf['High']} High, {conf['Medium']} Medium and {conf['Low']} Low confidence."),
    ("1", 4, "56", "cited sources", "Ink", "Doctor of Credit, myFICO, MyBankTracker, CardRight, StackEasy and lender pages. Every link is on card 8."),
    ("1", 5, f"{TOTAL:,}", "recorded pulls", "Teal", f"{tot['Experian']:,} (Experian pulls) + {tot['Equifax']:,} (Equifax pulls) + {tot['TransUnion']:,} (TransUnion pulls) = {TOTAL:,} (all recorded bureau pulls, all lenders combined)."),
    ("2", 1, f"{tot['Experian'] / TOTAL:.0%}", "Experian share", "Experian", f"KPI 2. {tot['Experian']:,} (Experian pulls) ÷ {TOTAL:,} (all recorded pulls) = {tot['Experian'] / TOTAL:.0%} (Experian share of all pulls)."),
    ("2", 2, f"{tot['Equifax'] / TOTAL:.0%}", "Equifax share", "Equifax", f"KPI 2. {tot['Equifax']:,} (Equifax pulls) ÷ {TOTAL:,} (all recorded pulls) = {tot['Equifax'] / TOTAL:.0%} (Equifax share of all pulls)."),
    ("2", 3, f"{tot['TransUnion'] / TOTAL:.0%}", "TransUnion share", "TransUnion", f"KPI 2. {tot['TransUnion']:,} (TransUnion pulls) ÷ {TOTAL:,} (all recorded pulls) = {tot['TransUnion'] / TOTAL:.0%} (TransUnion share of all pulls)."),
    ("2", 4, f"{top_counts.get('Experian', 0)} of 49", "states led by Experian", "Ink", f"{top_counts.get('Experian', 0)} (states Experian leads) + {top_counts.get('Equifax', 0)} (Equifax leads) + {top_counts.get('TransUnion', 0)} (TransUnion leads) + {ties} (ties) = 49 (states and DC with data)."),
    ("2", 5, f"{close_n}", "close-call states", "Teal", f"KPI 4. {close_n} (states where the top two bureaus are within 20 points) = {status_n.get('Clear lean', 0)} (clear leans) + {status_n.get('Moderate lean', 0)} (moderate leans) + {len(tossups)} (toss-ups) + {status_n.get('Thin data (national pattern)', 0)} (thin data)."),
]
TILE_MORE = {  # (what it means, how to use it) for each tile, in order
    ("1", 1): ("Each row is one consumer-reported hard inquiry: a lender, a state and the bureau or bureaus it pulled.",
               "This is the starting dataset; every other number in the story was built from it or checked against it."),
    ("1", 2): ("Each datapoint is an outside record of a lender pulling a bureau in a state, from issuer tables, forums and lender pages.",
               "They confirm or correct the original rows; 0 rows were contradicted (card 3)."),
    ("1", 3): ("Every lender in the database has a profile: what it funds, the score it typically needs and how much paperwork it asks for.",
               "Use the lender map (card 4) to see which bureau a lender pulls in each state."),
    ("1", 4): ("Every number traces to a named, dated source.",
               "Open any source from the clickable list on card 8."),
    ("1", 5): ("A pull is one bureau checked for one application. Counts are weighted so one large report cannot dominate.",
               "Shares on the maps and KPIs are calculated from these pulls."),
    ("2", 1): ("More than half of all recorded pulls landed on Experian.",
               "If your Experian report is your strongest, most lenders will see your best file."),
    ("2", 2): ("About one pull in four landed on Equifax; it is often the second report a lender checks.",
               "Citi and Chase lean Equifax more than most issuers (card 8)."),
    ("2", 3): ("About one pull in five landed on TransUnion, the least-pulled bureau overall.",
               "Synchrony and U.S. Bank lean TransUnion, so they suit a strong TransUnion report."),
    ("2", 4): ("In most states Experian receives the largest share of pulls.",
               "Check the share maps (card 5) for the states where Equifax or TransUnion leads or ties."),
    ("2", 5): ("In these states the map alone cannot settle the bureau, so the regression model gives its best forecast.",
               "Open card 6 and click your state to see the chance of each bureau."),
}
tile_rows = [dict(Card=c, Order=str(o), Value=v, Label=l, Tone=t, Tip=tp, Means=TILE_MORE[(c, o)][0], Use=TILE_MORE[(c, o)][1]) for c, o, v, l, t, tp in TILES]
TL = "federated." + rid()
tile_cols = [("Card", "string"), ("Order", "integer"), ("Value", "string"), ("Label", "string"), ("Tone", "string"), ("Tip", "string"), ("Means", "string"), ("Use", "string")]
ds_tiles = palette_style(datasource(TL[10:], "Story Tiles", "story_tiles.csv", tile_cols, tile_rows, dsname=TL),
                         {"Tone": {"Ink": INK, "Teal": TEAL, "Experian": EXP, "Equifax": EQ, "TransUnion": TU}})

# ------------------------------------------------------------------ KPIs (list + dynamic detail card)
kpi_rows = []
for n, name, tells, formula, ex in K1 + K2:
    kpi_rows.append(dict(KPI=str(n), Name=tc(name), Tells=tells[0].upper() + tells[1:], Formula=formula[0].upper() + formula[1:], Worked=ex, Short=WORKED[n][1], Code=f"KPI {n}"))
KP = "federated." + rid()
kpi_cols = [("KPI", "integer"), ("Name", "string"), ("Tells", "string"), ("Formula", "string"), ("Worked", "string"), ("Short", "string"), ("Code", "string")]
KCALC = {"Calc_k_title": 'IF COUNTD([Name]) > 1 THEN "Pick a KPI" ELSE "KPI " + STR(ATTR([KPI])) + ". " + ATTR([Name]) END',
         "Calc_k_tells": 'IF COUNTD([Name]) > 1 THEN "Click any KPI on the left. This card then shows what it tells you, its formula and a worked example with the October 2026 numbers." ELSE ATTR([Tells]) END',
         "Calc_k_formula": 'IF COUNTD([Name]) > 1 THEN "" ELSE ATTR([Formula]) END',
         "Calc_k_worked": 'IF COUNTD([Name]) > 1 THEN "" ELSE ATTR([Worked]) END',
         "Calc_k_h1": 'IF COUNTD([Name]) > 1 THEN "" ELSE "WHAT IT TELLS YOU" END',
         "Calc_k_h2": 'IF COUNTD([Name]) > 1 THEN "" ELSE "FORMULA" END',
         "Calc_k_h3": 'IF COUNTD([Name]) > 1 THEN "" ELSE "WORKED EXAMPLE" END'}
kcalc_xml = "".join(cf(k, F(v)) for k, v in KCALC.items())
ds_kpi = datasource(KP[10:], "Story KPIs", "story_kpis.csv", kpi_cols, kpi_rows, kcalc_xml, dsname=KP)

# ------------------------------------------------------------------ issuer habits (stacked bars)
HB = "federated." + rid()
habit_rows = []
for k in order:
    for b in ("Experian", "Equifax", "TransUnion"):
        v = habit[k].get(b, 0)
        habit_rows.append(dict(Issuer=k, Bureau=b, Share=f"{v:.4f}", Pct=f"{v:.0%}" if v >= 0.12 else ""))
habit_cols = [("Issuer", "string"), ("Bureau", "string"), ("Share", "real"), ("Pct", "string")]
ds_habit = palette_style(datasource(HB[10:], "Issuer Habits", "issuer_habits.csv", habit_cols, habit_rows, dsname=HB), {"Bureau": BUREAU_COL})
ds_habit = ds_habit.replace("<column datatype='real' name='[Share]'", "<column datatype='real' default-format='p0%' name='[Share]'")

# ------------------------------------------------------------------ help popovers (one per card)
HELP = [
    ("1", "About This Story", "Eight cards move from context to a decision. Card 1 holds the context, purpose, sources, update cadence and data limits. Key terms: a hard inquiry (hard pull) is a lender's check of one report when you apply; a soft pull, such as prequalification, does not affect the score."),
    ("2", "Reading the KPIs", "The tiles are the headline shares (KPI 2) and the close-call count (KPI 4). Click a KPI in the list to open its detail card with the formula and a worked example. A close call is a state where the top two bureaus are within 20 points."),
    ("3", "How the Data Was Built", "Read each row left to right: the original table was cleaned, matched to 102 lenders, enriched with funding facts, then cross-checked against 670 outside datapoints. 0 rows were contradicted."),
    ("4", "Using the Lender Map", "Pick a lender in the drop-down list. Each state is colored by the bureau that lender pulled most in the recorded data. Gray means a tie. Hover a state to see the Experian, Equifax and TransUnion counts behind it."),
    ("5", "Reading a Share Map", "A share is a part out of a whole: pulls on one bureau ÷ all bureau pulls in the state. Click any state and the State Detail panel shows all three shares with mini bars. States with under 10 pulls are hints, not findings."),
    ("6", "Using the Close-Call Explorer", "Colors show the model's verdict. Click a state to load its forecast in the side panel; hover a state to see its chance bars inside the tooltip. Clear lean: the leader holds in at least 90% of 150 refits; moderate: at least 70%."),
    ("7", "Reading the Decision Tree", "Start at the top with your strongest report and follow its branch. Check the override rules first. The forecast table shows the model's chance of each bureau for four real lender and state cases (KPI 6)."),
    ("8", "Scorecard and Sources", "Each bar shows the share of an issuer's recorded pulls that landed on each bureau (KPI 5). Click a source name to open it. Every recommendation traces back to a KPI or an earlier card. Not financial advice."),
]
HP = "federated." + rid()
help_rows = [dict(Card=c, Icon="ⓘ  About", Title=t, Tip=tp) for c, t, tp in HELP]
help_cols = [("Card", "string"), ("Icon", "string"), ("Title", "string"), ("Tip", "string")]
ds_help = datasource(HP[10:], "Story Help", "story_help.csv", help_cols, help_rows, dsname=HP)

# ------------------------------------------------------------------ close calls (dark theme colors)
STATUS_COL = {"Clear lean": "#9A7BFF", "Moderate lean": "#5E4BA8", "Toss-up": "#E0B43A", "Thin data (national pattern)": "#4A5260", "Not a close call": "#252B34"}
ds_cc = datasource("0cc5tate0ab1cd2ef3gh4ij5kl6m", "Close Calls by State", "close_calls_state.csv", cc_cols, cc_rows, cc_calc, dsname=CC)
ds_cc = palette_style(ds_cc, {"Close Call Status": STATUS_COL, "Bureau": BUREAU_COL})

# ================================================================== worksheets
WS = {}
txt_pane = lambda enc, tip, lab, extra="": (f"<pane selection-relaxation-option='selection-relaxation-allow'><view><breakdown value='auto' /></view><mark class='Text' /><encodings>{enc}</encodings>"
                                            f"{tooltip(tip) if tip else ''}{label(lab)}<style><style-rule element='mark'><format attr='mark-labels-show' value='true' /></style-rule>{extra}</style></pane>")
for card, nm in (("1", "Overview Tiles"), ("2", "Market Tiles")):
    dep = deps(TL, tile_cols, [inst("Card", "nk"), inst("Order", "ok"), inst("Value", "nk"), inst("Label", "nk"), inst("Tone", "nk"), inst("Tip", "attr"), inst("Means", "attr"), inst("Use", "attr")]) + catfilter(TL, "Card", card)
    WS[nm] = worksheet(nm, "", TL, "Story Tiles", dep,
        txt_pane(f"<color column='{ref(TL, 'Tone')}' /><text column='{ref(TL, 'Value')}' /><text column='{ref(TL, 'Label')}' /><tooltip column='[{TL}].[attr:Tip:nk]' /><tooltip column='[{TL}].[attr:Means:nk]' /><tooltip column='[{TL}].[attr:Use:nk]' />",
                 tiprun(T(TL, "Value") + " (" + T(TL, "Label") + ")", "#0E1115", 11, True) + NLR + NLR
                 + tiprun("How it is calculated: ", "#0E1115", 9, True) + tiprun(T(TL, "Tip", "nk", "attr"), "#1F2937", 9) + NLR
                 + tiprun("What it means: ", "#0E1115", 9, True) + tiprun(T(TL, "Means", "nk", "attr"), "#1F2937", 9) + NLR
                 + tiprun("How to use it: ", "#0E1115", 9, True) + tiprun(T(TL, "Use", "nk", "attr"), "#1F2937", 9),
                 f"<run bold='true' fontalignment='1' fontsize='22'>{T(TL, 'Value')}</run>{NLR}<run fontalignment='1' fontcolor='{INK2}' fontsize='9'>{T(TL, 'Label')}</run>",
                 "<style-rule element='cell'><format attr='text-align' value='center' /><format attr='vertical-align' value='center' /></style-rule>"),
        "", ref(TL, "Order", "ok"),
        style=bgstyle(f"<style-rule element='header'><format attr='display' class='0' field='{ref(TL, 'Order', 'ok')}' scope='cols' value='false' /></style-rule>"
                      f"<style-rule element='label'><format attr='display' field='{ref(TL, 'Order', 'ok')}' value='false' /></style-rule>"
                      f"<style-rule element='worksheet'><format attr='display-field-labels' scope='cols' value='false' /></style-rule>"))

dep = deps(KP, kpi_cols, [inst("KPI", "ok"), inst("Name", "nk"), inst("Short", "nk"), inst("Code", "nk"), inst("Tells", "attr"), inst("Formula", "attr"), inst("Worked", "attr")])
WS["KPI List"] = worksheet("KPI List", "", KP, "Story KPIs", dep,
    txt_pane(f"<text column='{ref(KP, 'Code')}' /><text column='{ref(KP, 'Name')}' /><text column='{ref(KP, 'Short')}' /><tooltip column='[{KP}].[attr:Tells:nk]' /><tooltip column='[{KP}].[attr:Formula:nk]' /><tooltip column='[{KP}].[attr:Worked:nk]' />",
             tiprun(T(KP, "Code") + ". " + T(KP, "Name"), "#0E1115", 10, True) + NLR + tiprun(T(KP, "Tells", "nk", "attr")) + NLR + NLR
             + tiprun("Formula: ", "#0E1115", 9, True) + tiprun(T(KP, "Formula", "nk", "attr")) + NLR + tiprun("Example: ", "#0E1115", 9, True) + tiprun(T(KP, "Worked", "nk", "attr")),
             f"<run bold='true' fontcolor='{TEAL}' fontsize='9'>{T(KP, 'Code')}  </run><run bold='true' fontcolor='{INK}' fontsize='10'>{T(KP, 'Name')}</run>{NLR}<run fontcolor='{MUT}' fontsize='8'>{T(KP, 'Short')}</run>",
             "<style-rule element='cell'><format attr='text-align' value='left' /><format attr='vertical-align' value='center' /></style-rule>"),
    ref(KP, "KPI", "ok"), "",
    style=bgstyle(f"<style-rule element='header'><format attr='display' class='0' field='{ref(KP, 'KPI', 'ok')}' scope='rows' value='false' /></style-rule>"
                  f"<style-rule element='label'><format attr='display' field='{ref(KP, 'KPI', 'ok')}' value='false' /></style-rule>"
                  f"<style-rule element='worksheet'><format attr='display-field-labels' scope='rows' value='false' /></style-rule>"))
uk = lambda k: f"<column-instance column='[{k}]' derivation='User' name='[usr:{k}:nk]' pivot='key' type='nominal' />"
WS["KPI Detail"] = worksheet("KPI Detail", "", KP, "Story KPIs", deps(KP, kpi_cols, [uk(k) for k in KCALC], kcalc_xml),
    txt_pane("".join(f"<text column='[{KP}].[usr:{k}:nk]' />" for k in KCALC), "",
             f"<run bold='true' fontcolor='{INK}' fontsize='15'>{T(KP, 'Calc_k_title', 'nk', 'usr')}</run>{NLR}{NLR}"
             f"<run bold='true' fontcolor='{TEAL}' fontsize='8'>{T(KP, 'Calc_k_h1', 'nk', 'usr')}</run>{NLR}<run fontcolor='{INK2}' fontsize='10'>{T(KP, 'Calc_k_tells', 'nk', 'usr')}</run>{NLR}{NLR}"
             f"<run bold='true' fontcolor='{TEAL}' fontsize='8'>{T(KP, 'Calc_k_h2', 'nk', 'usr')}</run>{NLR}<run fontcolor='{INK}' fontsize='10'>{T(KP, 'Calc_k_formula', 'nk', 'usr')}</run>{NLR}{NLR}"
             f"<run bold='true' fontcolor='{ORANGE}' fontsize='8'>{T(KP, 'Calc_k_h3', 'nk', 'usr')}</run>{NLR}<run fontcolor='{INK2}' fontsize='10'>{T(KP, 'Calc_k_worked', 'nk', 'usr')}</run>",
             "<style-rule element='cell'><format attr='text-align' value='left' /><format attr='vertical-align' value='top' /></style-rule>"),
    "", "", style=bgstyle())

for card, *_ in HELP:
    dep = deps(HP, help_cols, [inst("Card", "nk"), inst("Icon", "nk"), inst("Title", "attr"), inst("Tip", "attr")]) + catfilter(HP, "Card", card)
    WS[f"Help {card}"] = worksheet(f"Help {card}", "", HP, "Story Help", dep,
        txt_pane(f"<text column='{ref(HP, 'Icon')}' /><tooltip column='[{HP}].[attr:Title:nk]' /><tooltip column='[{HP}].[attr:Tip:nk]' />",
                 tiprun(T(HP, "Title", "nk", "attr"), "#0E1115", 11, True) + NLR + tiprun(T(HP, "Tip", "nk", "attr"), "#1F2937", 9),
                 f"<run bold='true' fontalignment='1' fontcolor='{TEAL}' fontsize='11'>{T(HP, 'Icon')}</run>",
                 "<style-rule element='cell'><format attr='text-align' value='center' /><format attr='vertical-align' value='center' /></style-rule>"),
        "", "", style=bgstyle().replace(CARD, CARD2))

hb_sort = (f"<sort class='manual' column='{ref(HB, 'Issuer')}' direction='ASC'><dictionary>" + "".join(f"<bucket>&quot;{esc(k)}&quot;</bucket>" for k in order) + "</dictionary></sort>"
           f"<sort class='manual' column='{ref(HB, 'Bureau')}' direction='ASC'><dictionary><bucket>&quot;TransUnion&quot;</bucket><bucket>&quot;Equifax&quot;</bucket><bucket>&quot;Experian&quot;</bucket></dictionary></sort>")
WS["Issuer Habits"] = worksheet("Issuer Habits", f"<run bold='true' fontcolor='{INK}' fontsize='12'>Issuer Bureau Habits (Share of Each Issuer's Pulls)</run>", HB, "Issuer Habits",
    deps(HB, habit_cols, [inst("Issuer", "nk"), inst("Bureau", "nk"), inst("Share", "sum"), inst("Pct", "nk")]) + hb_sort,
    f"<pane selection-relaxation-option='selection-relaxation-allow'><view><breakdown value='auto' /></view><mark class='Bar' /><encodings>"
    f"<color column='{ref(HB, 'Bureau')}' /><text column='{ref(HB, 'Pct')}' /></encodings>"
    + tooltip(tiprun(T(HB, "Issuer"), "#0E1115", 10, True) + NLR + tiprun(T(HB, "Bureau"), "#1F2937", 9, True) + tiprun(" got ") + tiprun(f"&lt;[{HB}].[sum:Share:qk]&gt;", "#0E1115", 9, True)
              + tiprun(" of this issuer's recorded pulls (KPI 5).") + NLR + tiprun("Plan applications around the issuer's habit, not only the state.", "#4A5568", 8))
    + label(f"<run bold='true' fontcolor='#FFFFFF' fontsize='9'>{T(HB, 'Pct')}</run>")
    + "<style><style-rule element='mark'><format attr='mark-labels-show' value='true' /><format attr='mark-labels-cull' value='true' /><format attr='size' value='0.7' /></style-rule></style></pane>",
    ref(HB, "Issuer"), f"[{HB}].[sum:Share:qk]",
    style=bgstyle(f"<style-rule element='axis'><encoding attr='space' class='0' field='[{HB}].[sum:Share:qk]' field-type='quantitative' max='1' min='0' range-type='fixed' scope='cols' type='space' />"
                  f"<format attr='display' class='0' field='[{HB}].[sum:Share:qk]' scope='cols' value='false' /></style-rule>"
                  f"<style-rule element='header'><format attr='width' field='{ref(HB, 'Issuer')}' value='130' /></style-rule>"
                  f"<style-rule element='worksheet'><format attr='display-field-labels' scope='rows' value='false' /></style-rule>"))

# close-call sheets (map gets a viz in tooltip: the chance bars for the hovered state)
ccdeps = lambda inst_list, extra="": deps(CC, cc_cols, inst_list, extra)
WS["CC Map"] = worksheet("CC Map", "", CC, "Close Calls by State",
    ccdeps([inst("State", "nk"), inst("Close Call Status", "nk"), "<column-instance column='[Calc_cc_label]' derivation='None' name='[none:Calc_cc_label:nk]' pivot='key' type='nominal' />"], cc_calc),
    f"<pane selection-relaxation-option='selection-relaxation-allow'><view><breakdown value='auto' /></view><mark class='Multipolygon' /><encodings>"
    f"<color column='[{CC}].[none:Close Call Status:nk]' /><lod column='[{CC}].[none:State:nk]' /><text column='[{CC}].[none:Calc_cc_label:nk]' />"
    f"<geometry column='[{CC}].[Geometry (generated)]' /></encodings>"
    + tooltip(tiprun(T(CC, "State"), "#0E1115", 11, True) + NLR + tiprun(T(CC, "Close Call Status"), "#5B3FA8", 9, True) + NLR
              + "<run>&lt;Sheet name=&quot;CC Chance Bars&quot; maxwidth=&quot;300&quot; maxheight=&quot;150&quot; filter=&quot;&lt;All Fields&gt;&quot;&gt;</run>"
              + NLR + tiprun("Click to pin this state in the side panel.", "#4A5568", 8))
    + f"<customized-label><formatted-text><run bold='true' fontalignment='1' fontcolor='{INK}' fontsize='8'>&lt;[{CC}].[none:Calc_cc_label:nk]&gt;</run></formatted-text></customized-label>"
    f"<style><style-rule element='mark'><format attr='mark-labels-show' value='true' /><format attr='mark-labels-cull' value='false' /></style-rule></style></pane>",
    f"[{CC}].[Latitude (generated)]", f"[{CC}].[Longitude (generated)]",
    style=bgstyle(f"<style-rule element='axis'><encoding attr='space' class='0' field='[{CC}].[Longitude (generated)]' field-type='quantitative' max='-7300000' min='-13950000' projection='EPSG:3857' range-type='fixed' scope='cols' type='space' />"
                  f"<encoding attr='space' class='0' field='[{CC}].[Latitude (generated)]' field-type='quantitative' max='6500000' min='2750000' projection='EPSG:3857' range-type='fixed' scope='rows' type='space' /></style-rule>"
                  f"<style-rule element='map'><format attr='washout' value='0.0' /><format attr='map-style' value='dark' /></style-rule>"))
WS["CC State Panel"] = worksheet("CC State Panel", "", CC, "Close Calls by State",
    ccdeps([uk(k) for k in PANEL], cc_calc),
    txt_pane("".join(f"<text column='[{CC}].[usr:{k}:nk]' />" for k in PANEL), "",
             f"<run bold='true' fontcolor='{INK}' fontsize='17'>{T(CC, 'Calc_p_title', 'nk', 'usr')}</run>{NLR}"
             f"<run bold='true' fontcolor='#9A7BFF' fontsize='11'>{T(CC, 'Calc_p_status', 'nk', 'usr')}</run>{NLR}"
             f"<run fontcolor='{INK2}' fontsize='10'>{T(CC, 'Calc_p_result', 'nk', 'usr')}</run>{NLR}"
             f"<run fontcolor='{MUT}' fontsize='9'>{T(CC, 'Calc_p_note', 'nk', 'usr')}</run>",
             "<style-rule element='cell'><format attr='text-align' value='left' /><format attr='vertical-align' value='top' /></style-rule>"),
    "", "", style=bgstyle())
WS["CC Chance Bars"] = worksheet("CC Chance Bars", f"<run bold='true' fontcolor='{INK}' fontsize='11'>Chance of Each Bureau (Typical Application)</run>", CC, "Close Calls by State",
    ccdeps([inst("Bureau", "nk"), inst("Predicted Likelihood", "avg")]) +
        f"<sort class='manual' column='[{CC}].[none:Bureau:nk]' direction='ASC'><dictionary><bucket>&quot;Experian&quot;</bucket><bucket>&quot;Equifax&quot;</bucket><bucket>&quot;TransUnion&quot;</bucket></dictionary></sort>",
    f"<pane selection-relaxation-option='selection-relaxation-allow'><view><breakdown value='auto' /></view><mark class='Bar' /><encodings>"
    f"<color column='[{CC}].[none:Bureau:nk]' /><text column='[{CC}].[avg:Predicted Likelihood:qk]' /></encodings>"
    + tooltip(tiprun(T(CC, "Bureau"), "#0E1115", 10, True) + tiprun(": ") + tiprun(f"&lt;[{CC}].[avg:Predicted Likelihood:qk]&gt;", "#0E1115", 10, True) + NLR
              + tiprun("Predicted chance this bureau is pulled for a typical application (KPI 6). The three chances add to 100%.", "#4A5568", 8))
    + f"<customized-label><formatted-text><run bold='true' fontcolor='{INK}' fontsize='10'>&lt;[{CC}].[avg:Predicted Likelihood:qk]&gt;</run></formatted-text></customized-label>"
    f"<style><style-rule element='mark'><format attr='mark-labels-show' value='true' /><format attr='size' value='0.75' /></style-rule></style></pane>",
    f"[{CC}].[none:Bureau:nk]", f"[{CC}].[avg:Predicted Likelihood:qk]",
    style=bgstyle(f"<style-rule element='axis'><encoding attr='space' class='0' field='[{CC}].[avg:Predicted Likelihood:qk]' field-type='quantitative' max='1' min='0' range-type='fixed' scope='cols' type='space' />"
                  f"<format attr='display' class='0' field='[{CC}].[avg:Predicted Likelihood:qk]' scope='cols' value='false' /></style-rule>"
                  f"<style-rule element='header'><format attr='width' field='[{CC}].[none:Bureau:nk]' value='90' /></style-rule>"
                  f"<style-rule element='worksheet'><format attr='display-field-labels' scope='rows' value='false' /></style-rule>"))
WS["Sources List"] = worksheet("Sources List", f"<run bold='true' fontcolor='{INK}' fontsize='12'>Sources (Click a Name to Open It)</run>", SR, "Story Sources",
    deps(SR, [("n", "integer"), ("Source", "string"), ("Dated", "string"), ("url", "string")], [inst("n", "ok"), inst("Source", "nk"), inst("Dated", "nk"), inst("url", "nk")]),
    f"<pane selection-relaxation-option='selection-relaxation-allow'><view><breakdown value='auto' /></view><mark class='Text' /><encodings>"
    f"<text column='[{SR}].[none:Dated:nk]' /><lod column='[{SR}].[none:url:nk]' /></encodings>"
    + tooltip(tiprun(T(SR, "Source"), "#0E1115", 10, True) + NLR + tiprun("Dated " + T(SR, "Dated")) + NLR + tiprun("Click to open the source.", "#4A5568", 8))
    + label(f"<run fontcolor='{MUT}' fontsize='8'>{T(SR, 'Dated')}</run>")
    + "<style><style-rule element='mark'><format attr='mark-labels-show' value='true' /></style-rule></style></pane>",
    f"([{SR}].[none:n:ok] / [{SR}].[none:Source:nk])", "",
    style=bgstyle(f"<style-rule element='header'><format attr='display' class='0' field='[{SR}].[none:n:ok]' scope='rows' value='false' /><format attr='width' field='[{SR}].[none:Source:nk]' value='330' /></style-rule>"
                  f"<style-rule element='label'><format attr='display' field='[{SR}].[none:n:ok]' value='false' /></style-rule>"
                  f"<style-rule element='worksheet'><format attr='display-field-labels' scope='rows' value='false' /></style-rule>"
                  f"<style-rule element='label'><format attr='color' field='[{SR}].[none:Source:nk]' value='{TEAL}' /><format attr='font-size' field='[{SR}].[none:Source:nk]' value='8' /></style-rule>"))

ACTIONS = (f"<action caption='Pick a state' name='[Action_ccpick]'><activation auto-clear='true' type='on-select' />"
           f"<source dashboard='{DASH[5]}' type='sheet' worksheet='CC Map' /><command command='tsc:tsl-filter'>"
           f"<param name='special-fields' value='all' /><param name='target' value='{DASH[5]}' /></command></action>"
           f"<action caption='Pick a KPI' name='[Action_kpipick]'><activation auto-clear='true' type='on-select' />"
           f"<source dashboard='{DASH[1]}' type='sheet' worksheet='KPI List' /><command command='tsc:tsl-filter'>"
           f"<param name='exclude' value='Market Tiles,Help 2' /><param name='special-fields' value='all' /><param name='target' value='{DASH[1]}' /></command></action>"
           + "".join(f"<action caption='State detail {i}' name='[Action_sd{i}]'><activation auto-clear='true' type='on-select' />"
                     f"<source dashboard='{DASH[4]}' type='sheet' worksheet='{m}' /><command command='tsc:tsl-filter'>"
                     f"<param name='exclude' value='{','.join(x for x in MAPS if x != m)},Help 5' /><param name='special-fields' value='all' /><param name='target' value='{DASH[4]}' /></command></action>"
                     for i, m in enumerate(MAPS))
           + f"<action caption='Open source' name='[Action_srcurl]'><activation auto-clear='true' type='on-select' />"
           f"<source dashboard='{DASH[7]}' type='sheet' worksheet='Sources List' />"
           f"<link caption='' delimiter=',' escape='\\' expression='&lt;url&gt;' include-null='true' multi-select='false' url-escape='false' /></action>")

# ================================================================== assemble
zin = zipfile.ZipFile(SRC)
twb_name = [n for n in zin.namelist() if n.endswith(".twb")][0]
s = zin.read(twb_name).decode("utf-8")
# navigation buttons need these document-format flags
if "<BasicButtonObject />" not in s:
    s = s.replace("<document-format-change-manifest>", "<document-format-change-manifest>\n    <BasicButtonObject />\n    <BasicButtonObjectTextSupport />", 1)
def remove_block(s, tag, name):
    i = s.find(f"<{tag} name='{name}'")
    if i < 0:
        i = s.find(f"<{tag} enable-sort-zone-taborder='true' name='{name}'")
    if i < 0: return s
    j = s.find(f"</{tag}>", i) + len(f"</{tag}>")
    k = s.rfind("\n", 0, i)
    return s[:k] + s[j:]
OLD_DASH = ["1 Start Here", "2 Data and Method", "4 Reading the Maps", "5 Experian and Equifax", "7 Close Calls", "8 If Then", "9 Funding Ladder", "10 Scorecard"]
OLD_WS = ["D1 Stakeholders", "D2 Scope", "D3 Enrichment", "D4 ETL", "D5 Equation", "D6 Regression", "D7 Ladder", "D8 KPIs", "D9 Decision Tree", "D10 What If", "Scorecard Bars", "Regression Close Calls"]
for n in OLD_DASH: s = remove_block(s, "dashboard", n)
for n in OLD_WS: s = remove_block(s, "worksheet", n)
for n in OLD_DASH + OLD_WS:
    s = re.sub(r"\s*<window class='(?:dashboard|worksheet)'[^>]*name='" + re.escape(n) + r"'(?: [^>]*)?>.*?</window>", "", s, flags=re.S)
s = re.sub(r"\s*<actions>.*?</actions>", "", s, flags=re.S)
for cap in ("Story Diagrams", "Scorecard Bars", "Regression Bars"):
    s = re.sub(r"\s*<datasource caption='" + cap + r"' inline='true'.*?</datasource>", "", s, count=1, flags=re.S)

# embed the pulls table (Tableau Public cannot open the published server source), plus the State Detail calcs
m = re.search(r"<datasource caption='Funding Lender State Bureau Pulls' inline='true' name='(sqlproxy[^']*)'.*?\n    </datasource>", s, re.S)
SQLNAME = m.group(1)
calcs = {}
for c in re.finditer(r"<column caption='[^']*' datatype='[^']*' name='(\[Calculation_\d+\])'[^>]*>\s*<calculation[^>]*/>\s*</column>", s):
    calcs.setdefault(c.group(1), re.sub(r"\s*\n\s*", "", c.group(0)))
for key_, xml_ in list(calcs.items()):
    for bb in ("Experian", "Equifax", "TransUnion"):
        if f"caption='{bb} Tooltip'" in xml_:
            xml_ = xml_.replace("&quot; / &quot; + STR(INT(SUM([Total Datapoints]))) + &quot; = &quot;",
                                f"&quot; ({bb} pulls) / &quot; + STR(INT(SUM([Total Datapoints]))) + &quot; (all bureau pulls) = &quot;")
            xml_ = xml_.replace("&quot;%&quot; + CHAR(10) + CHAR(10) +&#10;&quot;All bureau pulls",
                                f"&quot;% ({bb} share)&quot; + CHAR(10) + CHAR(10) +&#10;&quot;All bureau pulls")
            calcs[key_] = xml_
ls_rows = list(csv.DictReader(open(DT / "lender_state.csv")))
ls_cols = [("State", "string"), ("StateAbbr", "string"), ("Lender", "string"), ("Industry", "string"), ("Experian", "integer"), ("Equifax", "integer"),
           ("TransUnion", "integer"), ("Top Bureau", "string"), ("Total Datapoints", "integer"), ("Bureaus Reported", "string")]
def sd_line(b):
    sh = f"SUM([{b}])/SUM([Total Datapoints])"
    return (f'"{b}  " + STR(INT(ROUND(100*{sh}))) + "% (share)  " + LEFT("████████████████████", INT(ROUND(20*{sh}))) + '
            f'"  " + STR(INT(SUM([{b}]))) + " ({b} pulls) of " + STR(INT(SUM([Total Datapoints]))) + " (all pulls)"')
SDCALC = {"Calc_sd_title": 'IF COUNTD([State]) > 1 THEN "All States" ELSE ATTR([State]) END',
          "Calc_sd_sub": 'IF COUNTD([State]) > 1 THEN "Click any state on a map to open its detail card." ELSE "Share of this state\'s recorded pulls, all lenders" END',
          "Calc_sd_exp": sd_line("Experian"), "Calc_sd_eq": sd_line("Equifax"), "Calc_sd_tu": sd_line("TransUnion"),
          "Calc_sd_note": 'IF SUM([Total Datapoints]) < 10 THEN "Under 10 pulls: treat this as a hint, not a finding." ELSE "Based on " + STR(INT(SUM([Total Datapoints]))) + " recorded pulls." END'}
sd_xml = "".join(cf(k, F(v)) for k, v in SDCALC.items())
ds_pulls = datasource("lenderstate", "Funding Lender State Bureau Pulls", "lender_state.csv", ls_cols, ls_rows,
                      "".join(calcs.values()) + sd_xml + "<column-instance column='[Top Bureau]' derivation='None' name='[none:Top Bureau:nk]' pivot='key' type='nominal' />", dsname=SQLNAME)
s = s[:m.start()] + ds_pulls + s[m.end():]
s = re.sub(r"\s*<datasource [^>]*formatted-name='Funding Lender State Bureau Pulls'.*?</datasource>", "", s, flags=re.S)
WS["State Detail"] = worksheet("State Detail", "", SQLNAME, "Funding Lender State Bureau Pulls", deps(SQLNAME, ls_cols, [uk(k) for k in SDCALC], sd_xml),
    txt_pane("".join(f"<text column='[{SQLNAME}].[usr:{k}:nk]' />" for k in SDCALC), "",
             f"<run bold='true' fontcolor='{INK}' fontsize='17'>{T(SQLNAME, 'Calc_sd_title', 'nk', 'usr')}</run>{NLR}"
             f"<run fontcolor='{MUT}' fontsize='9'>{T(SQLNAME, 'Calc_sd_sub', 'nk', 'usr')}</run>{NLR}{NLR}"
             f"<run bold='true' fontcolor='{EXP}' fontsize='11'>{T(SQLNAME, 'Calc_sd_exp', 'nk', 'usr')}</run>{NLR}{NLR}"
             f"<run bold='true' fontcolor='{EQ}' fontsize='11'>{T(SQLNAME, 'Calc_sd_eq', 'nk', 'usr')}</run>{NLR}{NLR}"
             f"<run bold='true' fontcolor='{TU}' fontsize='11'>{T(SQLNAME, 'Calc_sd_tu', 'nk', 'usr')}</run>{NLR}{NLR}"
             f"<run fontcolor='{ORANGE}' fontsize='9'>{T(SQLNAME, 'Calc_sd_note', 'nk', 'usr')}</run>",
             "<style-rule element='cell'><format attr='text-align' value='left' /><format attr='vertical-align' value='top' /></style-rule>"),
    "", "", style=bgstyle())

NOBASE = ("<style-rule element='map-layer'>" + "".join(f"<format attr='enabled' id='{l}' value='false' />" for l in
          ("tab_base", "um_lcover", "tab_coastline", "tab_streets", "tab_country_name", "tab_state_name", "tab_state_border", "tab_county_border", "tab_terrain")) + "</style-rule>")
DARKMAP = "<format attr='washout' value='0.0' /><format attr='map-style' value='dark' />"
MAPSTYLE = {b_: DARKMAP for b_ in ("Experian", "Equifax", "TransUnion")}
# share maps: dark-to-bright ramps in each bureau's color, light labels, dark panes
def ramp(c):
    a = tuple(int(IMG.CARD2[i:i + 2], 16) for i in (1, 3, 5)); b = tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)); w_ = (235, 240, 250)
    out = []
    for k in range(11):
        t = k / 10
        src, dst, tt = (a, b, t / 0.7) if t <= 0.7 else (b, w_, (t - 0.7) / 0.3 * 0.55)
        out.append("#" + "".join(f"{int(src[j] + (dst[j] - src[j]) * tt):02x}" for j in range(3)))
    return out
for b in ("Experian", "Equifax", "TransUnion"):
    i = s.find(f"<worksheet name='{b} Share of Pulls'"); j = s.find("</worksheet>", i)
    x = s[i:j]
    x = re.sub(r"<color-palette custom='true' name='' type='ordered-sequential'>.*?</color-palette>",
               "<color-palette custom='true' name='' type='ordered-sequential'>" + "".join(f"<color>{c}</color>" for c in ramp(BUREAU_COL[b])) + "</color-palette>", x, flags=re.S)
    x = re.sub(r"<run><!\[CDATA\[<Sheet Name>(.*?)\]\]></run>", lambda mm: f"<run bold='true' fontcolor='{BUREAU_COL[b]}' fontsize='11'>{b}</run><run fontcolor='{INK2}' fontsize='9'><![CDATA[ Share{mm.group(1)}]]></run>", x)
    x = x.replace("fontcolor='#ffffff'", "fontcolor='#0E1115'").replace("fontcolor='#1f2937'", f"fontcolor='{INK}'")
    x = x.replace("<format attr='washout' value='0.0' />", MAPSTYLE[b])
    x = x.replace("<style>", "<style>" + bgstyle(), 1)
    s = s[:i] + x + s[j:]
# lender map: dark pane, washed-out base map, rich tooltip
i = s.find("<worksheet name='Top Bureau by State, by Lender'"); j = s.find("</worksheet>", i)
x = s[i:j]
x = x.replace("<format attr='washout' value='0.0' />", DARKMAP).replace("<style>", "<style>" + bgstyle(
    f"<style-rule element='axis'><encoding attr='space' class='0' field='[{SQLNAME}].[Longitude (generated)]' field-type='quantitative' max='-7300000' min='-13950000' projection='EPSG:3857' range-type='fixed' scope='cols' type='space' />"
    f"<encoding attr='space' class='0' field='[{SQLNAME}].[Latitude (generated)]' field-type='quantitative' max='6500000' min='2750000' projection='EPSG:3857' range-type='fixed' scope='rows' type='space' /></style-rule>"), 1)
x = x.replace("</encodings>", "</encodings>" + tooltip(
    tiprun(T(SQLNAME, "State"), "#0E1115", 11, True) + NLR + tiprun(T(SQLNAME, "Lender"), "#4A5568", 9) + NLR + NLR
    + tiprun("Pulled most: ", "#1F2937", 9) + tiprun(T(SQLNAME, "Top Bureau"), "#0E1115", 9, True) + NLR
    + tiprun("Experian ", TIPB["Experian"], 9, True) + tiprun(f"&lt;[{SQLNAME}].[sum:Experian:qk]&gt;") + tiprun("   Equifax ", TIPB["Equifax"], 9, True)
    + tiprun(f"&lt;[{SQLNAME}].[sum:Equifax:qk]&gt;") + tiprun("   TransUnion ", TIPB["TransUnion"], 9, True) + tiprun(f"&lt;[{SQLNAME}].[sum:TransUnion:qk]&gt;") + NLR
    + tiprun("Counts are recorded pulls for this lender in this state.", "#4A5568", 8)), 1)
s = s[:i] + x + s[j:]
TOPMAP = {"Experian": EXP, "Equifax": EQ, "TransUnion": TU, "Tie: Experian / Equifax": "#6B6F86", "Tie: Experian / TransUnion": "#4F7C77",
          "Tie: Equifax / TransUnion": "#7F6E58", "Tie: Experian / Equifax / TransUnion": "#5A6270"}
s = re.sub(r"(<encoding attr='color' field='\[none:Top Bureau:nk\]' type='palette'>).*?(</encoding>)",
           lambda mm: mm.group(1) + "".join(f"<map to='{c}'><bucket>&quot;{esc(k)}&quot;</bucket></map>" for k, c in TOPMAP.items()) + mm.group(2), s, flags=re.S)
if "field='[none:Top Bureau:nk]' type='palette'" not in s:
    s = s.replace(ds_pulls, ds_pulls.replace("<semantic-values>", "<style><style-rule element='mark'><encoding attr='color' field='[none:Top Bureau:nk]' type='palette'>"
        + "".join(f"<map to='{c}'><bucket>&quot;{esc(k)}&quot;</bucket></map>" for k, c in TOPMAP.items()) + "</encoding></style-rule></style><semantic-values>", 1))
for b in ("Experian", "Equifax", "TransUnion"):
    s = s.replace(f"caption='SUM([{b}])/SUM([Total Datapoints])'", f"caption='{b} Share of Pulls'")
s = s.replace("caption='SUM([Trans Union])/SUM([Total Datapoints])'", "caption='TransUnion Share of Pulls'")

NEW_DS = ds_cc + ds_src + ds_tiles + ds_kpi + ds_habit + ds_help
s = s.replace("</datasources>\n  <worksheets>", NEW_DS + "</datasources>\n  <worksheets>", 1) if "</datasources>\n  <worksheets>" in s else s.replace("</datasources>", NEW_DS + "</datasources>", 1)
s = s.replace("</worksheets>", "".join(WS.values()) + "</worksheets>", 1)
s = s.replace("<dashboards>", "<dashboards>" + "".join(D.values()), 1)
s = s.replace("<worksheets>", f"<actions>{ACTIONS}</actions><worksheets>", 1)

STORY = [(DASH[0], "Overview: context, purpose, sources and limits"),
         (DASH[1], f"Market and KPIs: Experian gets {tot['Experian'] / TOTAL:.0%} of pulls"),
         (DASH[2], "Data and method: 355 rows, 0 contradicted"),
         (DASH[3], "Pick a lender: its top bureau by state"),
         (DASH[4], "Share maps: click a state for its detail"),
         (DASH[5], f"Close calls: the forecast in {close_n} states"),
         (DASH[6], "Decide: tree, forecast and funding ladder"),
         (DASH[7], "Scorecard, moves for each stakeholder and sources")]
pts = "".join(f"<story-point caption='{i}. {esc(tc(c))}' captured-sheet='{esc(n)}' id='{100 + i}' />" for i, (n, c) in enumerate(STORY, 1))
s = re.sub(r"<story-points>.*?</story-points>", f"<story-points>{pts}</story-points>", s, flags=re.S)
s = re.sub(r"<flipboard active-id='\d+'", "<flipboard active-id='101'", s)
SW, SH = DW + 24, 880
s = s.replace("<size maxheight='964' maxwidth='1016' minheight='964' minwidth='1016' />", f"<size maxheight='{SH}' maxwidth='{SW}' minheight='{SH}' minwidth='{SW}' />", 1)
s = s.replace("<zone h='3527' id='3' type-v2='title' w='98426' x='787' y='830' />",
              "<zone h='3527' id='3' type-v2='title' w='98426' x='787' y='830'><zone-style><format attr='border-style' value='none' /><format attr='border-width' value='0' /></zone-style></zone>")
s = s.replace("<dashboard name='Which Bureau Will They Pull' type='storyboard'>",
              "<dashboard name='Which Bureau Will They Pull' type='storyboard'><layout-options><title><formatted-text>"
              "<run bold='true' fontcolor='#14213D' fontsize='18'>FP&amp;A Credit Stacking &amp; Funding Sequencing Strategy</run>"
              "<run fontcolor='#4A5568' fontsize='13'>   Which Bureau Will They Pull?</run></formatted-text></title></layout-options>", 1)
# dark story frame
s = re.sub(r"(<dashboard name='Which Bureau Will They Pull' type='storyboard'>.*?<zone h='100000' id='2' type-v2='layout-basic' w='100000' x='0' y='0'>)",
           r"\1", s, flags=re.S)

VIEWS = {DASH[0]: ["Help 1", "Overview Tiles"], DASH[1]: ["Help 2", "Market Tiles", "KPI List", "KPI Detail"], DASH[2]: ["Help 3"],
         DASH[3]: ["Help 4", "Top Bureau by State, by Lender"], DASH[4]: ["Help 5", "State Detail"] + MAPS,
         DASH[5]: ["Help 6", "CC Map", "CC State Panel", "CC Chance Bars"], DASH[6]: ["Help 7"], DASH[7]: ["Help 8", "Issuer Habits", "Sources List"]}
ZOOM = {"Sources List": "fit-width"}
new_windows = "".join(f"<window class='dashboard' name='{esc(n)}'><viewpoints>{''.join(f'<viewpoint name={chr(39)}{esc(v)}{chr(39)}><zoom type={chr(39)}{ZOOM.get(v, chr(101)+'ntire-view')}{chr(39)} /></viewpoint>' for v in VIEWS.get(n, []))}</viewpoints>"
                      f"<active id='-1' /><simple-id uuid='{WINUUID[n]}' /></window>" for n in D)
new_windows += "".join(f"<window class='worksheet' name='{esc(n)}'><cards><edge name='left'><strip size='160'><card type='pages' /><card type='filters' /><card type='marks' /></strip></edge>"
                       f"<edge name='top'><strip size='31'><card type='columns' /></strip><strip size='31'><card type='rows' /></strip><strip size='31'><card type='title' /></strip></edge></cards>"
                       f"<simple-id uuid='{{{str(uuid.uuid4()).upper()}}}' /></window>" for n in WS)
s = s.replace("</windows>", new_windows + "</windows>", 1)
s = re.sub(r"<window class='worksheet'(?! hidden)", "<window class='worksheet' hidden='true'", s)

# bureau names: bold, in their color, in every text run outside tooltips
BW = re.compile(r"(Experian|Equifax|TransUnion)")
def color_runs(block):
    def fix(m):
        attrs, body = m.group(1), m.group(2)
        cdata = body.startswith("<![CDATA[")
        text = body[9:-3] if cdata else body
        if "<[" in text or "&lt;[" in text or not BW.search(text):
            return m.group(0)
        if re.search(r"fontcolor='(" + "|".join(re.escape(c) for c in BUREAU_COL.values()) + ")'", attrs):
            return m.group(0)
        a = dict(re.findall(r"(\w+)='([^']*)'", attrs))
        out = []
        for part in BW.split(text):
            if not part: continue
            aa = dict(a)
            if part in BUREAU_COL:
                aa["bold"] = "true"; aa["fontcolor"] = BUREAU_COL[part]
            at = "".join(f" {k}='{v}'" for k, v in sorted(aa.items()))
            out.append(f"<run{at}>" + (f"<![CDATA[{part}]]>" if cdata else part) + "</run>")
        return "".join(out)
    return re.sub(r"<run((?: \w+='[^']*')*)>(.*?)</run>", fix, block, flags=re.S)
s = re.sub(r"<customized-tooltip>.*?</customized-tooltip>|<formatted-text>.*?</formatted-text>",
           lambda mm: mm.group(0) if mm.group(0).startswith("<customized-tooltip>") else color_runs(mm.group(0)), s, flags=re.S)

OUT.parent.mkdir(exist_ok=True)
drop = ("Story Diagrams.csv", "Scorecard Bars.csv", "Regression Bars.csv")
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr(twb_name, s)
    for n in zin.namelist():
        if n == twb_name or any(n.endswith(d) for d in drop): continue
        if n.startswith("Data/Extracts/"):
            if n.split("/")[-1].replace(".hyper", "") not in s: continue
        z.writestr(n, zin.read(n))
    for p in (WORK / "Data").rglob("*"):
        if p.is_file(): z.write(p, str(p.relative_to(WORK)))
    for p in (WORK / "Image").glob("*.png"):
        z.write(p, f"Image/{p.name}")
(ROOT / "tableau" / "story_points.md").write_text("# Tableau Story Points\n\n" + "\n".join(f"{i}. {tc(c)}" for i, (n, c) in enumerate(STORY, 1)) + "\n")
print("wrote", OUT, OUT.stat().st_size, "bytes;", len(STORY), "story points")
