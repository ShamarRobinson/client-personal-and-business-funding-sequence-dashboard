"""Build data/generator.json for the Funding Plan Generator page.

Reads the same files as the dashboard, website and Tableau story so every number matches:
  data/db.json                                   lender records, funding ladder by score tier, rules, sources
  data/tableau/regression_lender_state_wide.csv  likely bureau per state x major lender (logistic regression)
  data/tableau/regression_state.csv              likely bureau per state, all lenders
"""
import csv, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from update_schedule import ASOF, NEXT_UPDATE

ROOT = Path(__file__).resolve().parents[1]
DT = ROOT / "data" / "tableau"
db = json.load(open(ROOT / "data" / "db.json"))

lenders = []
for l in db["lenders"]:
    lenders.append({
        "name": l["name"], "ind": l["ind"][3:], "ftype": l["ftype"], "prim": l["prim"],
        "avg": l["avg"], "min": l["mn"], "doc": l["ld"], "conf": l["conf"], "notes": l["notes"],
    })

ls = {}
for r in csv.DictReader(open(DT / "regression_lender_state_wide.csv")):
    ls.setdefault(r["StateAbbr"], {})[r["Lender"]] = {
        "b": r["Most Likely Bureau"], "p": round(float(r["Lead Probability"]), 3),
        "ex": round(float(r["P_Experian"]), 3), "eq": round(float(r["P_Equifax"]), 3), "tu": round(float(r["P_TransUnion"]), 3),
        "n": int(r["Lender Datapoints in State"]), "ev": r["Evidence"]}

states = {}
for r in csv.DictReader(open(DT / "regression_state.csv")):
    states[r["StateAbbr"]] = {"name": r["State"], "b": r["Most Likely Bureau"], "p": round(float(r["Lead Probability"]), 3),
                              "ex": round(float(r["P_Experian"]), 3), "eq": round(float(r["P_Equifax"]), 3),
                              "tu": round(float(r["P_TransUnion"]), 3), "n": int(r["Datapoints"]), "status": r["Close Call Status"]}

seq = {}
for s in db["seq"]:
    tier, step, when, action, link, product, bureau, amount, note = (s + [""] * 9)[:9]
    seq.setdefault(tier, []).append({"step": step, "when": when, "action": action, "product": product, "bureau": bureau, "amount": amount, "note": note})

out = {"asof": ASOF, "next": NEXT_UPDATE, "lenders": lenders, "lenderState": ls, "states": states, "seq": seq,
       "rules": db["rules"], "sources": db["sources"]}
p = ROOT / "data" / "generator.json"
p.write_text(json.dumps(out, separators=(",", ":")))
print(f"wrote {p} {p.stat().st_size:,} bytes; {len(lenders)} lenders, {len(states)} states, {len(seq)} tiers")
