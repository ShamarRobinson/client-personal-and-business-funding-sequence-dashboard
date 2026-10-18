"""Data for the Tableau Story infographics: diagram grids, scorecard bars and regression bars.

Diagram engine: each diagram is a grid of cells (Col x Row). Tableau draws each cell as a
square mark filling the cell (highlight-table style), coloured by [Tone] with the "Tableau 20"
palette, with up to three text lines. Colours carry meaning: Experian blue, Equifax orange,
TransUnion green, in scope green, out of scope red, and a red-to-blue funding ladder. Only the
darkest fills (blue, gray, brown) carry light text fields (*L); all others carry dark text (*D).

Outputs (data/tableau/):
  story_diagrams.csv   Diagram, Col, Row, Kind, Shade, Tone, TitleD, TitleL, L1D, L1L, L2D, L2L
  scorecard_bars.csv   Panel, Item, ItemOrder, Part, Value, Shade, Tone, LabelL, LabelD
  regression_bars.csv  StateLabel, StateOrder, Bureau, Value, Shade, Tone, LabelL, LabelD, Verdict
"""
from pathlib import Path

import pandas as pd

OUT = Path(__file__).resolve().parents[1] / "data" / "tableau"
rows = []


# Tone keys sort into the order of Tableau's "Tableau 20" palette, so assigning that palette
# to [Tone] gives each key its colour with no manual mapping. Every key appears at least once
# in every data source (padding rows), so the sort positions never shift.
TONES = ["01 Blue", "02 Blue light", "03 Orange", "04 Orange light", "05 Green", "06 Green light",
         "07 Olive", "08 Yellow", "09 Teal", "10 Teal light", "11 Red", "12 Red light",
         "13 Gray", "14 Gray light", "15 Pink", "16 Pink light", "17 Purple", "18 Purple light",
         "19 Brown", "20 Brown light"]
T = {k.split(" ", 1)[1].lower().replace(" ", "_"): k for k in TONES}   # e.g. T["blue_light"]
DARK_FILLS = {"01 Blue", "13 Gray", "19 Brown"}                       # white text only on these


def cell(diagram, col, row, title="", l1="", l2="", tone="gray_light", kind="Box"):
    tone = T[tone]
    dark = tone in DARK_FILLS
    # Tableau treats an empty string as NULL, and NULL + text = NULL, so a one-line body
    # would vanish. A non-breaking space keeps the second line present but blank.
    if l1 and not l2:
        l2 = "\u00a0"
    rows.append({
        "Diagram": diagram, "Col": col, "Row": row, "Kind": kind, "Shade": 1.0 if dark else 0.2,
        "Tone": tone,
        "TitleD": "" if dark else title, "TitleL": title if dark else "",
        "L1D": "" if dark else l1, "L1L": l1 if dark else "",
        "L2D": "" if dark else l2, "L2L": l2 if dark else "",
    })


def arrow(diagram, col, row, glyph="\u2794"):
    cell(diagram, col, row, glyph, "", "", "gray_light", "Arrow")


# Every card body is one or two full sentences, split across two lines (L1, L2) and written
# for a general audience (readable by a high school student). Flow diagrams put the arrow in
# the title so every column is wide enough for a sentence.

# 1. Stakeholders ---------------------------------------------------------------
D = "1 Stakeholders"
for c, (t, a, b) in enumerate([
    ("Personal credit clients", "They can apply where their", "strongest report gets pulled."),
    ("Business credit clients", "Many business cards still check", "the owner's personal report."),
    ("Credit consulting companies", "They use it to plan disputes", "and to space out inquiries."),
    ("Business funding companies", "They can line up approvals without", "piling inquiries on one report."),
], start=1):
    cell(D, c, 1, t, a, b, ["blue", "orange", "green", "purple"][c - 1])
for c, (t, a, b) in enumerate([
    ("Funding advisors and brokers", "They look up the likely bureau", "before each client applies."),
    ("Analysts and reviewers", "They can trace every number", "back to the source it came from."),
    ("Lenders and partners", "They get applications from people", "who are a better fit."),
    ("Everyone", "It is a planning guide.", "It is not financial advice."),
], start=1):
    cell(D, c, 2, t, a, b, ["blue_light", "orange_light", "green_light", "purple_light"][c - 1])

# 2. Scope ----------------------------------------------------------------------
D = "2 Scope"
cell(D, 1, 1, "IN SCOPE", "These are the questions this story answers.", "", "green")
cell(D, 2, 1, "OUT OF SCOPE", "These are the questions it does not try to answer.", "", "red")
ins = [("Which bureau a lender pulls", "It covers Experian, Equifax and TransUnion", "in every U.S. state and Washington, DC."),
       ("Personal and business funding", "It includes cards, credit lines, loans, SBA loans,", "auto, equipment and real estate financing."),
       ("Facts about each lender", "Each lender has a funding type, a typical score", "and whether low or no paperwork options exist."),
       ("A funding sequence", "It suggests an application order for seven", "score ranges, from 500-549 up to 800+."),
       ("The evidence used", "It starts from a 355-row inquiry table and adds", "public datapoints dated 2008 to 2026.")]
outs = [("Business credit bureaus", "Business files like D&B are not", "mapped by state in this project."),
        ("Soft pulls", "Prequalification checks and account reviews", "do not affect scores, so they are left out."),
        ("Live rates and terms", "Minimum scores and terms are a snapshot", "from October 2026 and can change."),
        ("Advice", "Nothing here is legal, tax", "or investment advice.")]
for r, (a, b) in enumerate(zip(ins, outs), start=2):
    cell(D, 1, r, *a, "green_light")
    cell(D, 2, r, *b, "red_light")

# 3. Enrichment flow --------------------------------------------------------------
D = "3 Enrichment"
steps = [("1. ORIGINAL TABLE \u2794", "The starting table had 355 rows", "from 16 states."),
         ("2. CLEAN AND MATCH \u2794", "229 messy spellings were", "matched to 102 real lenders."),
         ("3. ENRICH \u2794", "Each lender got a funding type,", "a typical score and a paperwork level."),
         ("4. CROSS-CHECK \u2794", "670 outside datapoints from 56 sources", "were compared state by state."),
         ("5. RESULT", "84 rows were confirmed and", "none were contradicted.")]
for i, (t, a, b) in enumerate(steps):
    cell(D, i + 1, 1, t, a, b, ["gray_light", "blue_light", "purple_light", "teal_light", "green"][i])

# 4. ETL flow ----------------------------------------------------------------------
D = "4 ETL"
cell(D, 1, 1, "1. EXTRACT \u2794", "First, every source is read in.", "", "teal")
cell(D, 2, 1, "2. TRANSFORM \u2794", "Next, the data is cleaned and joined.", "", "purple")
cell(D, 3, 1, "3. LOAD", "Last, it is published to every output.", "", "green")
ext = [("Original workbook", "The All States & Banks tab", "is read exactly as it was."),
       ("Issuer state tables", "Tables from Doctor of Credit and", "MyBankTracker cover 2008 to 2017."),
       ("myFICO forum grid", "A 2023 grid and 2025-2026 posts", "add newer datapoints."),
       ("Lender pages", "Lender websites give minimum scores,", "products and paperwork rules.")]
trf = [("Name matching", "Ordered rules turn 229 spellings", "into 102 lenders, and each is reviewed."),
       ("Normalize markers", "Marks like x, blanks and counts", "become pulled or not pulled."),
       ("Join and compare", "Each row is checked against outside", "data for the same lender and state."),
       ("Reshape", "Data is turned into one row per state,", "lender and bureau for maps and models.")]
lod = [("Excel workbook", "A six-tab workbook keeps", "totals that update themselves."),
       ("Website", "A seven-page site on GitHub Pages", "shows the database."),
       ("Tableau Public", "The maps, the regression", "and this story live here."),
       ("Regression inputs", "Weighted datapoints feed", "the prediction model.")]
for r, (a, b, c) in enumerate(zip(ext, trf, lod), start=2):
    cell(D, 1, r, *a, "teal_light")
    cell(D, 2, r, *b, "purple_light")
    cell(D, 3, r, *c, "green_light")

# 5. Share equation ------------------------------------------------------------------
D = "5 Equation"
cell(D, 1, 1, "Pulls on one bureau", "Count the pulls on one bureau", "in a state, all lenders combined.", "blue")
arrow(D, 2, 1, "\u00f7")
cell(D, 3, 1, "All pulls in the state", "Add up the pulls on Experian,", "Equifax and TransUnion there.", "gray_light")
arrow(D, 4, 1, "=")
cell(D, 5, 1, "Bureau share", "The result is the share of recorded", "pulls that landed on that bureau.", "teal")
for r, (st, n, tot, pct, note) in enumerate([
        ("Utah: Experian pulls", 4, 7, "57%", "Only 7 pulls, so treat it as a hint."),
        ("Florida: Experian pulls", 466, 885, "53%", "885 pulls make this very reliable."),
        ("Georgia: TransUnion pulls", 37, 116, "32%", "About 1 in 3 Georgia pulls.")], start=2):
    cell(D, 1, r, f"{n}", st, "", "green_light" if "TransUnion" in st else "blue_light")
    arrow(D, 2, r, "\u00f7")
    cell(D, 3, r, f"{tot}", "all pulls in the state", "", "gray_light")
    arrow(D, 4, r, "=")
    cell(D, 5, r, pct, note, "", "teal_light")

# 6. Regression flow ----------------------------------------------------------------
D = "6 Regression"
cell(D, 1, 1, "1. INPUTS \u2794", "2,901 datapoints from 862 reports", "go into the model.", "teal")
cell(D, 2, 1, "2. MODEL \u2794", "A multinomial logistic regression", "weighs each factor at once.", "purple")
cell(D, 3, 1, "3. OUTPUT \u2794", "It gives each bureau a chance", "of being pulled in each state.", "blue")
cell(D, 4, 1, "4. VERDICT", "24 states were close calls,", "with the top two within 20 points.", "green")
inp = [("State", "Where the person lives", "is one factor."), ("Lender", "Who they apply to is the", "factor that matters most."),
       ("Data era", "Older and newer datapoints", "are kept apart."), ("Lender in state", "Some lenders switch bureaus", "from one state to another.")]
mod = [("Shrinkage", "States with little data are pulled", "toward the national pattern."), ("Tested on held-out data", "It is right 55% of the time,", "compared with 50% by guessing."),
       ("Capped weights", "No single report counts for", "more than 10 datapoints."), ("150 refits", "The model is refit 150 times", "to see how stable the leader is.")]
outp = [("Chance of Experian", "This is for a typical application", "with the usual mix of lenders."), ("Chance of Equifax", "Each chance comes with", "a 90% range."),
        ("Chance of TransUnion", "The three chances", "always add up to 100%."), ("Lender by state", "Each major lender gets", "its own chance in each state.")]
ver = [("10 clear leans", "Experian stayed on top", "in at least 90% of refits.", "green"), ("5 moderate leans", "Experian stayed on top", "in at least 70% of refits.", "green_light"),
       ("4 toss-ups", "Hawaii, Kansas, South Carolina", "and Virginia are still too close.", "orange_light"), ("5 thin-data states", "These have under 10 datapoints,", "so they follow the national pattern.", "gray_light")]
for r in range(4):
    cell(D, 1, r + 2, *inp[r], "teal_light")
    cell(D, 2, r + 2, *mod[r], "purple_light")
    cell(D, 3, r + 2, *outp[r], ["blue_light", "orange_light", "green_light", "gray_light"][r])
    t, a, b, s = ver[r]
    cell(D, 4, r + 2, t, a, b, s)

# 7. Funding ladder ---------------------------------------------------------------
D = "7 Ladder"
tiers = [("500-549", "Repair first.", "Fix errors, then use", "a builder loan."),
         ("550-599", "Start small.", "Prequalify, then open", "a starter card."),
         ("600-649", "Go unsecured.", "Add mainstream cards", "and a low-doc line."),
         ("650-699", "Enter the majors.", "Apply to Chase first,", "then to Amex."),
         ("700-749", "Build the stack.", "Open 0% business cards", "over six rounds."),
         ("750-799", "Add the banks.", "Add bank lines", "and SBA loans."),
         ("800+", "Go biggest first.", "Lead with the largest", "bank facilities.")]
for c, (t, head, a, b) in enumerate(tiers, start=1):
    s = ["red_light", "orange_light", "yellow", "green_light", "green", "teal", "blue"][c - 1]
    top = 8 - c                      # higher tiers climb higher: a staircase
    cell(D, c, top, t, head, "", s)
    for r in range(top + 1, 8):      # the step's riser, same shade, no text
        cell(D, c, r, "", "", "", s, "Step")
    cell(D, c, 8, "", a, b, "gray_light")

# 8. Scorecard KPIs -----------------------------------------------------------------
D = "8 KPIs"
for c, (n, a, b) in enumerate([("355", "The original rows", "were all cross-checked."), ("0", "No rows were contradicted", "by published data."),
                               ("670", "Outside datapoints were", "added state by state."), ("204", "Lenders are profiled,", "102 of them newly added."),
                               ("54%", "Over half of all pulls", "landed on Experian."), ("24", "Close-call states were", "sorted out by the model.")], start=1):
    cell(D, c, 1, n, a, b, ["gray", "green", "teal", "purple", "blue", "orange"][c - 1])

# 9. Decision tree (if / then) -------------------------------------------------------
D = "9 Decision Tree"
cell(D, 2, 1, "START: WHICH REPORT IS STRONGEST? ▼", "Check all three reports first.", "Then follow the branch for your best one.", "gray")
for c, (t, a, b, s) in enumerate([
        ("IF EXPERIAN IS STRONGEST ▼", "Experian is pulled most often,", "so most lenders will see it.", "blue"),
        ("IF EQUIFAX IS STRONGEST ▼", "Few lenders lead with Equifax,", "so choose them on purpose.", "orange"),
        ("IF TRANSUNION IS STRONGEST ▼", "TransUnion is the least-pulled", "bureau overall, at about 21%.", "green")], start=1):
    cell(D, c, 2, t, a, b, s)
for c, (t, a, b) in enumerate([
        ("THEN favor Experian-first issuers", "American Express pulls Experian 87% of the time,", "and Bank of America pulls it 56% of the time."),
        ("THEN favor Citi and Chase", "Citi pulls Equifax 39% of the time and Chase 36%,", "the highest Equifax shares of the big issuers."),
        ("THEN favor TransUnion-first issuers", "Synchrony pulls TransUnion 62% of the time", "and U.S. Bank pulls it 47% of the time.")], start=1):
    cell(D, c, 3, t, a, b, ["blue_light", "orange_light", "green_light"][c - 1])
for c, (t, a, b) in enumerate([
        ("IF you live in a close-call state", "THEN check the Close Calls card first, because", "the bureau there is nearly a coin flip."),
        ("IF your score is under 650", "THEN start on the lower steps of the ladder", "before applying to the major banks."),
        ("IF one report already has new inquiries", "THEN switch to issuers that pull a different", "bureau so no single report stacks up.")], start=1):
    cell(D, c, 4, t, a, b, "purple_light")

# 10. What-if table: lender + state -> most likely bureau (from the regression) -------
D = "10 What If"
cell(D, 1, 1, "IF YOU APPLY TO...", "Pick a lender and a state.", "", "gray")
cell(D, 2, 1, "THEN THE LIKELY BUREAU IS...", "This is the model's best guess.", "", "gray")
cell(D, 3, 1, "WHY IT MATTERS", "The chance shows how sure", "the model is.", "gray")
w = pd.read_csv(OUT / "regression_lender_state_wide.csv")
for r, (lender, state, why) in enumerate([
        ("American Express", "Kansas", "Amex picks Experian almost everywhere, even in a toss-up state."),
        ("Chase", "Florida", "Florida has 189 Chase datapoints, and Equifax is a close second."),
        ("Capital One", "Virginia", "Capital One leans Equifax here, but only 3 datapoints back it up."),
        ("Synchrony", "Ohio", "Synchrony is a rare lender, one that leads with TransUnion.")], start=2):
    x = w[(w.Lender == lender) & (w.State == state)].iloc[0]
    probs = {b: x[f"P_{b}"] for b in ["Experian", "Equifax", "TransUnion"]}
    top = max(probs, key=probs.get)
    cell(D, 1, r, f"{lender} in {state}", "", "", "purple_light")
    cell(D, 2, r, f"{top}: {round(100 * probs[top])}% chance",
         f"The chances are Experian {round(100 * probs['Experian'])}%,",
         f"Equifax {round(100 * probs['Equifax'])}% and TransUnion {round(100 * probs['TransUnion'])}%.",
         {"Experian": "blue_light", "Equifax": "orange_light", "TransUnion": "green_light"}[top])
    a, b = why.split(", ", 1) if ", " in why else (why, "")
    cell(D, 3, r, "", a + ("," if b else ""), b, "gray_light")

# Palette padding: one hidden cell per tone so every key exists in the data source.
for i, k in enumerate(TONES, start=1):
    rows.append({"Diagram": "0 Palette", "Col": i, "Row": 1, "Kind": "Pad", "Shade": 0.0, "Tone": k,
                 "TitleD": "", "TitleL": "", "L1D": "", "L1L": "", "L2D": "", "L2L": ""})
diag = pd.DataFrame(rows)
diag.to_csv(OUT / "story_diagrams.csv", index=False)

# Scorecard bars: share of pulls by bureau, overall and for the busiest lenders -------
p = pd.read_csv(OUT / "pulls_long.csv")
p = p[p.Industry != "Credit Report Resellers & Screening (Not Lenders)"]
short = {"American Express": "American Express", "Citibank (Citi Cards / CBNA)": "Citi",
         "JPMorgan Chase (Chase Card Services)": "Chase", "Bank of America": "Bank of America",
         "U.S. Bank": "U.S. Bank", "Wells Fargo (Card Services)": "Wells Fargo", "Capital One": "Capital One",
         "Synchrony Bank (Amazon, PayPal, Lowe's, Old Navy, HSN, CareCredit and others)": "Synchrony"}
BUREAU_TONE = {"Experian": T["blue"], "Equifax": T["orange"], "TransUnion": T["green"]}
tab = p.groupby(["Lender", "Bureau"]).Datapoints.sum().unstack(fill_value=0)
items = [("All lenders", tab.sum())] + [(short[k], tab.loc[k]) for k in short]
bars = []
for order, (name, s) in enumerate(items, start=1):
    tot = s.sum()
    for b in ["Experian", "Equifax", "TransUnion"]:
        v = s[b] / tot
        lab = f"{round(100 * v)}%"
        white = b == "Experian" and v >= 0.12        # white text only on the dark blue bar
        bars.append({"Panel": f"% {b.upper()}", "Item": name, "ItemOrder": order, "Part": "Share", "Value": v, "Shade": 1.0,
                     "Tone": BUREAU_TONE[b], "LabelL": lab if white else "", "LabelD": "" if white else lab})
        bars.append({"Panel": f"% {b.upper()}", "Item": name, "ItemOrder": order, "Part": "Rest", "Value": 1 - v, "Shade": 0.08,
                     "Tone": T["gray_light"], "LabelL": "", "LabelD": ""})
# zero-length padding segments so every tone key exists (keeps the palette order fixed)
for k in TONES:
    bars.append({"Panel": "% EXPERIAN", "Item": "All lenders", "ItemOrder": 1, "Part": "Pad", "Value": 0.0, "Shade": 0.0,
                 "Tone": k, "LabelL": "", "LabelD": ""})
pd.DataFrame(bars).to_csv(OUT / "scorecard_bars.csv", index=False)

# The same scorecard for the website's Bureau Likelihood page
import json
site_path = OUT.parent / "regression.json"
if site_path.exists():
    site = json.loads(site_path.read_text())
    site["scorecard"] = [{"l": name, "n": int(s.sum()),
                          "p": [round(float(s[b] / s.sum()), 3) for b in ["Experian", "Equifax", "TransUnion"]]}
                         for name, s in items]
    site_path.write_text(json.dumps(site, separators=(",", ":")))

# Regression bars: predicted likelihood in the close-call states ----------------------
st = pd.read_csv(OUT / "regression_state.csv")
c = st[st["Close Call"] == "Yes"].copy()
rank = {"Clear lean": 1, "Moderate lean": 2, "Toss-up": 3, "Thin data (national pattern)": 4}
c["r"] = c["Model Confidence"].map(rank)
c = c.sort_values(["r", "Lead Margin (pts)"], ascending=[True, False]).reset_index(drop=True)
rb = []
shade = {"Experian": 1.0, "Equifax": 0.55, "TransUnion": 0.2}
for i, r in c.iterrows():
    verdict = r["Model Confidence"].replace(" (national pattern)", "")
    for b in ["Experian", "Equifax", "TransUnion"]:
        v = r[f"P_{b}"]
        lab = f"{b[:2].upper() if b != 'TransUnion' else 'TU'} {round(100 * v)}%"
        lab = lab.replace("EX", "EX").replace("EQ", "EQ")
        rb.append({"StateLabel": f"{r.State} ({verdict})", "StateOrder": i + 1, "Bureau": b, "Value": v,
                   "Shade": shade[b], "Tone": BUREAU_TONE[b],
                   "LabelL": lab if b == "Experian" else "", "LabelD": "" if b == "Experian" else lab,
                   "Verdict": verdict})
for k in TONES:
    first = rb[0]
    rb.append({**first, "Bureau": "Pad", "Value": 0.0, "Shade": 0.0, "Tone": k, "LabelL": "", "LabelD": ""})
pd.DataFrame(rb).to_csv(OUT / "regression_bars.csv", index=False)
print(diag.groupby("Diagram").size(), len(bars), len(rb))
