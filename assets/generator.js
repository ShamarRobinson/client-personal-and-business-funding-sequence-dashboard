/* Credit Stack and Funding Generator
   Turns a client's personal and business credit profile into a funding tier, a state-specific bureau plan,
   an ordered application sequence and a dated benchmark timeline, then exports the result as a PDF.
   Data: data/generator.json (built by analysis/build_generator_data.py from the same files as the dashboard).
   Everything runs in the browser; nothing is uploaded or stored. */
(function () {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const esc = s => String(s == null ? "" : s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const money = n => n == null || isNaN(n) ? "N/A" : "$" + Math.round(n).toLocaleString("en-US");
  const pct = n => n == null || isNaN(n) ? "N/A" : Math.round(n * 100) + "%";
  const B = { ex: "Experian", eq: "Equifax", tu: "TransUnion" };
  const BK = { Experian: "ex", Equifax: "eq", TransUnion: "tu" };
  const TIERS = ["500-549", "550-599", "600-649", "650-699", "700-749", "750-799", "800+"];
  const TIER_LOW = [500, 550, 600, 650, 700, 750, 800];
  // Strictest rule first: Chase (5/24), Amex (2 cards per 90 days), U.S. Bank (new-account sensitive), Wells Fargo, BofA, then the rest; Capital One last (pulls all three).
  const ORDER = ["Chase", "American Express", "U.S. Bank", "Wells Fargo", "Bank of America", "Citi", "Barclays", "Elan", "Navy Federal", "Discover", "Synchrony", "Comenity / Bread", "Apple Card", "Capital One"];
  const CANDIDATES = {
    low: ["Capital One", "Discover", "Navy Federal"],
    fair: ["Capital One", "Discover", "Synchrony", "Comenity / Bread", "Navy Federal"],
    mid: ["Chase", "American Express", "Wells Fargo", "Discover", "Navy Federal", "Capital One"],
    high: ["Chase", "American Express", "U.S. Bank", "Wells Fargo", "Bank of America", "Citi", "Barclays", "Elan", "Capital One"]
  };
  const RULE_NOTE = {
    "Chase": "5/24 rule: denied with 5+ new personal accounts in 24 months. One business card per 30 days.",
    "American Express": "Up to 2 cards per 90 days. Existing customers are often approved on a soft pull.",
    "U.S. Bank": "Sensitive to 5+ new accounts in 12 months. Banking relationship helps.",
    "Wells Fargo": "Possible double pull if new to the bank.",
    "Bank of America": "Experian for personal; relationship banking helps limits.",
    "Capital One": "Pulls all three bureaus; most business cards report to personal credit. Apply last.",
    "Navy Federal": "Membership required. TransUnion, sometimes a double pull."
  };
  const BANKS = ["Chase", "American Express", "U.S. Bank", "Wells Fargo", "Bank of America", "Citi", "Capital One", "PNC", "Truist", "TD Bank", "Navy Federal", "PenFed", "Credit union (other)", "Online bank"];
  const NAICS_SECTORS = {
    "11": "Agriculture, Forestry, Fishing and Hunting", "21": "Mining, Quarrying, and Oil and Gas Extraction", "22": "Utilities", "23": "Construction",
    "31": "Manufacturing", "32": "Manufacturing", "33": "Manufacturing", "42": "Wholesale Trade", "44": "Retail Trade", "45": "Retail Trade",
    "48": "Transportation and Warehousing", "49": "Transportation and Warehousing", "51": "Information", "52": "Finance and Insurance",
    "53": "Real Estate and Rental and Leasing", "54": "Professional, Scientific, and Technical Services", "55": "Management of Companies and Enterprises",
    "56": "Administrative and Support and Waste Management", "61": "Educational Services", "62": "Health Care and Social Assistance",
    "71": "Arts, Entertainment, and Recreation", "72": "Accommodation and Food Services", "81": "Other Services (except Public Administration)", "92": "Public Administration"
  };
  let D = null, lastPlan = null;

  // ------------------------------------------------------------------ form setup
  const f = $("#f");
  const today = new Date();
  const localISO = d => new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
  f.start.value = localISO(today);
  $("#banks").innerHTML = BANKS.map(b => `<label><input type="checkbox" name="bank" value="${esc(b)}">${esc(b)}</label>`).join("");
  const addCard = (c = {}) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td><input name="c_name" value="${esc(c.name || "")}" placeholder="e.g. Chase Freedom"></td>
      <td><input name="c_limit" type="number" min="0" value="${c.limit ?? ""}"></td>
      <td><input name="c_bal" type="number" min="0" value="${c.bal ?? ""}"></td>
      <td><select name="c_type"><option>Personal</option><option${c.type === "Business" ? " selected" : ""}>Business</option></select></td>
      <td><button type="button" class="btn ghost small" aria-label="Remove card">Remove</button></td>`;
    tr.querySelector("button").onclick = () => tr.remove();
    $("#cardrows").appendChild(tr);
  };
  $("#addcard").onclick = () => addCard();
  addCard(); addCard();
  f.addEventListener("reset", () => setTimeout(() => { $("#cardrows").innerHTML = ""; addCard(); addCard(); f.start.value = localISO(today); $("#out").style.display = "none"; }, 0));

  fetch("data/generator.json").then(r => r.json()).then(d => {
    D = d;
    const opts = Object.entries(d.states).sort((a, b) => a[1].name.localeCompare(b[1].name)).map(([k, v]) => `<option value="${k}">${esc(v.name)}</option>`);
    f.state.innerHTML = `<option value="">Select a state</option>` + opts.join("");
  }).catch(e => { $("#msg").textContent = "Lender data could not be loaded. Reload the page."; console.error(e); });

  $("#sample").onclick = () => {
    f.reset();
    setTimeout(() => {
      const v = { client: "Sample Client", preparer: "Funding Consultant", state: "FL", goal: 100000, purpose: "Working capital", urgency: "normal", income: 95000,
        entity: "LLC", bizname: "Sample Logistics LLC", naics: "484121", employees: "3", revenue: 240000, deposits: 20000, ein: "Yes", duns: "Yes", bizbank: "Yes",
        s_ex: 712, s_eq: 688, s_tu: 701, i6_ex: 1, i6_eq: 3, i6_tu: 0, i24_ex: 3, i24_eq: 5, i24_tu: 2, d_ex: 0, d_eq: 1, d_tu: 0, new24: 3, oldest: 9,
        paydex: "72", intelliscore: "N/A", eqbiz: "", creditsafe: "", tradelines: 2, banktenure: 6, otherbanks: "", notes: "" };
      const dt = new Date(today); dt.setMonth(dt.getMonth() - 20); v.formed = localISO(dt);
      Object.entries(v).forEach(([k, val]) => { if (f[k]) f[k].value = val; });
      $("#cardrows").innerHTML = "";
      [{ name: "Chase Freedom Unlimited", limit: 8000, bal: 3100 }, { name: "Discover it", limit: 5000, bal: 900 }, { name: "Amex Blue Business Plus", limit: 10000, bal: 4200, type: "Business" }].forEach(addCard);
      f.querySelectorAll("input[name=bank]").forEach(c => { c.checked = ["Chase", "Navy Federal"].includes(c.value); });
    }, 10);
  };

  // ------------------------------------------------------------------ read inputs
  const num = v => { if (v == null) return null; const s = String(v).trim(); if (!s || /^n\/?a$/i.test(s)) return null; const n = Number(s.replace(/[$,]/g, "")); return isNaN(n) ? null : n; };
  const txt = v => { const s = String(v || "").trim(); return s || "N/A"; };
  function read() {
    const g = n => f[n] ? f[n].value : "";
    const cards = [...$("#cardrows").querySelectorAll("tr")].map(tr => ({
      name: tr.querySelector("[name=c_name]").value.trim(), limit: num(tr.querySelector("[name=c_limit]").value),
      bal: num(tr.querySelector("[name=c_bal]").value), type: tr.querySelector("[name=c_type]").value
    })).filter(c => c.name || c.limit || c.bal);
    const files = n => [...(f[n].files || [])].map(x => x.name);
    const banks = [...f.querySelectorAll("input[name=bank]:checked")].map(c => c.value)
      .concat(String(g("otherbanks")).split(",").map(s => s.trim()).filter(Boolean));
    const bureau = p => ({ ex: num(g(p + "_ex")), eq: num(g(p + "_eq")), tu: num(g(p + "_tu")) });
    return {
      client: g("client").trim(), preparer: txt(g("preparer")), start: g("start") || localISO(today), state: g("state"),
      goal: num(g("goal")), purpose: txt(g("purpose")), urgency: g("urgency"), income: num(g("income")),
      entity: g("entity"), bizname: txt(g("bizname")), naics: String(g("naics")).trim(), formed: g("formed"), employees: txt(g("employees")),
      revenue: num(g("revenue")), deposits: num(g("deposits")), ein: g("ein") === "Yes", duns: g("duns") === "Yes", bizbank: g("bizbank") === "Yes",
      score: bureau("s"), inq6: bureau("i6"), inq24: bureau("i24"), derog: bureau("d"), new24: num(g("new24")), oldest: num(g("oldest")), pubrec: g("pubrec"),
      cards, banks, banktenure: num(g("banktenure")),
      paydex: num(g("paydex")), intelliscore: num(g("intelliscore")), eqbiz: num(g("eqbiz")), creditsafe: num(g("creditsafe")), tradelines: num(g("tradelines")),
      notes: g("notes").trim(), docs: files("rpt_personal").concat(files("rpt_business"))
    };
  }

  // ------------------------------------------------------------------ strategy engine
  const addDays = (iso, n) => { const d = new Date(iso + "T12:00:00"); d.setDate(d.getDate() + n); return d; };
  const fmtDate = d => d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
  const minScore = s => { const m = String(s || "").match(/\b([3-8]\d\d)\b/); return m ? +m[1] : null; };
  const monthsBetween = (a, b) => (b.getFullYear() - a.getFullYear()) * 12 + (b.getMonth() - a.getMonth()) - (b.getDate() < a.getDate() ? 1 : 0);

  function plan(x) {
    const P = { x, flags: [], timeline: [], bench: [] };
    // scores and tier
    const sc = Object.entries(x.score).filter(([, v]) => v != null);
    const vals = sc.map(([, v]) => v).sort((a, b) => a - b);
    P.mid = vals.length === 3 ? vals[1] : vals.length ? Math.round(vals.reduce((a, b) => a + b, 0) / vals.length) : null;
    let ti = 0; if (P.mid != null) TIER_LOW.forEach((lo, i) => { if (P.mid >= lo) ti = i; });
    P.tierIdx = P.mid == null || P.mid < 500 ? 0 : ti; P.tier = TIERS[P.tierIdx];
    // bureau health: score, minus recent inquiries and derogatory marks
    P.health = {};
    for (const k of ["ex", "eq", "tu"]) {
      const s = x.score[k];
      P.health[k] = s == null ? null : s - 12 * (x.inq6[k] || 0) - 4 * (x.inq24[k] || 0) - 30 * (x.derog[k] || 0);
    }
    const ranked = Object.entries(P.health).filter(([, v]) => v != null).sort((a, b) => b[1] - a[1]);
    P.best = ranked.length ? ranked[0][0] : null; P.worst = ranked.length > 1 ? ranked[ranked.length - 1][0] : null;
    if (ranked.length > 1 && ranked[0][1] - ranked[ranked.length - 1][1] < 10) P.worst = null; // reports roughly even
    // utilization
    const pc = x.cards.filter(c => c.type === "Personal" && c.limit), allc = x.cards.filter(c => c.limit);
    const sum = (a, k) => a.reduce((t, c) => t + (c[k] || 0), 0);
    P.util = pc.length ? sum(pc, "bal") / sum(pc, "limit") : null;
    P.utilAll = allc.length ? sum(allc, "bal") / sum(allc, "limit") : null;
    P.totalLimit = sum(allc, "limit"); P.totalBal = sum(allc, "bal");
    P.payTo10 = pc.length ? Math.max(0, sum(pc, "bal") - 0.09 * sum(pc, "limit")) : 0;
    // business stage
    P.tib = x.formed ? Math.max(0, monthsBetween(new Date(x.formed + "T12:00:00"), new Date(x.start + "T12:00:00"))) : null;
    P.hasEntity = x.entity !== "N/A";
    P.sector = x.naics && /^\d{2}/.test(x.naics) ? NAICS_SECTORS[x.naics.slice(0, 2)] || "Unrecognized sector" : null;
    P.stateName = D.states[x.state] ? D.states[x.state].name : x.state;
    P.stateBureau = D.states[x.state];
    const inqMax = Math.max(...["ex", "eq", "tu"].map(k => x.inq6[k] || 0));
    const derogTotal = ["ex", "eq", "tu"].reduce((t, k) => t + (x.derog[k] || 0), 0);
    P.over524 = x.new24 != null && x.new24 >= 5;

    // readiness flags
    const F = (lvl, t) => P.flags.push({ lvl, t });
    if (P.mid == null) F("bad", "No personal credit scores entered. Pull a 3-bureau report before applying for anything.");
    if (P.util != null && P.util > 0.3) F("bad", `Personal utilization is ${pct(P.util)}. Paying ${money(P.payTo10)} to bring it under 10% before statement dates is the fastest score lift available.`);
    else if (P.util != null && P.util > 0.1) F("warn", `Personal utilization is ${pct(P.util)}. Get it under 10% (pay ${money(P.payTo10)}) before the first application round.`);
    else if (P.util != null) F("good", `Personal utilization is ${pct(P.util)}, inside the under 10% target.`);
    for (const k of ["ex", "eq", "tu"]) if ((x.inq6[k] || 0) >= 3) F("warn", `${B[k]} has ${x.inq6[k]} hard inquiries in 6 months. Avoid lenders likely to pull ${B[k]} until it drops under 3.`);
    if (derogTotal) F("bad", `${derogTotal} late payment or collection item(s) reported. Dispute errors and bring accounts current; these weigh more than any new account.`);
    if (x.pubrec === "Yes, within 2 years") F("bad", "Public record within 2 years. Most prime card and bank lenders will decline; lead with secured and asset-based products.");
    if (P.over524) F("warn", `${x.new24} new personal accounts in 24 months: Chase business cards are out until the count drops under 5.`);
    if (P.worst) F("warn", `${B[P.worst]} is the weakest report and ${B[P.best]} the strongest. The sequence below favors lenders likely to pull ${B[P.best]} in ${P.stateName}.`);
    if (!P.hasEntity) F("warn", "No business entity yet. Form an LLC (or corporation), get an EIN and open a business checking account before business applications.");
    else { if (!x.ein) F("warn", "No EIN on file. Get one free from the IRS before any business application."); if (!x.duns) F("warn", "No D-U-N-S number. Request one free from Dun & Bradstreet so vendor payments build a Paydex score."); if (!x.bizbank) F("warn", "No business bank account. Lenders and vendors look for one; open it 30 days before applying."); }
    if (P.tib != null && P.tib < 12) F("warn", `Business is ${P.tib} months old. Most online lenders want 6 to 12 months and banks want 24; lean on personal-credit-based business cards first.`);
    const naics2 = (x.naics || "").slice(0, 4);
    if (["5221", "5222", "5223", "5239", "7132"].includes(naics2)) F("warn", "This NAICS code covers lending, investment or gambling activity, which SBA programs and many lenders restrict. Confirm eligibility with each lender.");
    if (x.urgency === "urgent" && (P.util > 0.3 || inqMax >= 3 || derogTotal)) F("warn", "Funding is needed within 30 days but the profile has open issues. Use revenue-based or asset-backed options now and run the card stack after the fixes post.");

    // bureau plan: likely bureau per major lender in the client's state
    const group = P.tierIdx <= 1 ? "low" : P.tierIdx === 2 ? "fair" : P.tierIdx === 3 ? "mid" : "high";
    const ls = D.lenderState[x.state] || {};
    P.lenders = ORDER.filter(n => CANDIDATES[group].includes(n)).map(n => {
      const r = ls[n]; if (!r) return null;
      const bk = BK[r.b]; let fit = "good", why = `Likely ${r.b} (${pct(r.p)}) in ${P.stateName}.`;
      const bScore = x.score[bk];
      if (n === "Chase" && P.over524) { fit = "bad"; why = "Over 5/24. Skip until under 5 new accounts in 24 months."; }
      else if (bk === P.worst) { fit = "warn"; why += ` That is the weakest report; apply later or after it improves.`; }
      else if ((x.inq6[bk] || 0) >= 3) { fit = "warn"; why += ` ${r.b} already has ${x.inq6[bk]} recent inquiries.`; }
      else if (n === "Capital One") { fit = "warn"; why = "Pulls all three bureaus. Keep it for last."; }
      else if (bk === P.best) why += " Matches the strongest report.";
      if (r.p < 0.5 && fit === "good") why += " Close call; another bureau is possible.";
      return { name: n, bureau: r.b, p: r.p, fit, why, rule: RULE_NOTE[n] || "", score: bScore, n: r.n };
    }).filter(Boolean);
    // move warn lenders after good ones, keep strict-first order within each group
    const rank = { good: 0, warn: 1, bad: 2 };
    P.lenders.sort((a, b) => rank[a.fit] - rank[b.fit] || ORDER.indexOf(a.name) - ORDER.indexOf(b.name));
    if (P.lenders.length) { const cap = P.lenders.findIndex(l => l.name === "Capital One"); if (cap > -1) P.lenders.push(P.lenders.splice(cap, 1)[0]); }

    // dated timeline
    const T = (day, phase, action, detail, bureau, amount) => P.timeline.push({ day, date: fmtDate(addDays(x.start, day)), phase, action, detail: detail || "", bureau: bureau || "", amount: amount || "" });
    let prep = 0;
    T(0, "Prepare", "Pull all three credit reports and dispute any errors", "annualcreditreport.com. Note which bureau is cleanest.", "None", "");
    if (P.util != null && P.util > 0.1) { T(0, "Prepare", `Pay personal card balances down by ${money(P.payTo10)}`, "Pay before each statement closes so the lower balance reports.", "None", ""); prep = Math.max(prep, 35); }
    if (derogTotal) { T(7, "Prepare", "Bring past-due accounts current; dispute inaccurate late payments and collections", "Ask for goodwill adjustments on one-time lates.", "None", ""); prep = Math.max(prep, 45); }
    if (inqMax >= 3) prep = Math.max(prep, 60);
    if (!P.hasEntity || !x.ein || !x.duns || !x.bizbank) T(3, "Business Setup", [!P.hasEntity && "Form the entity", !x.ein && "get an EIN", !x.duns && "get a D-U-N-S number", !x.bizbank && "open business checking"].filter(Boolean).join(", ").replace(/^./, c => c.toUpperCase()), "None of this touches personal credit.", "None", "");
    const vendors = D.lenders.filter(l => l.ind.startsWith("Vendor") && /no personal pull/i.test(l.min)).slice(0, 4).map(l => l.name.split(" (")[0]);
    if ((x.tradelines || 0) < 5) T(7, "Business Setup", `Open ${Math.max(1, 5 - (x.tradelines || 0))} net-30 vendor account(s) that report to business bureaus`, vendors.join(", ") + ".", "No personal pull", "$500 to $2,000 per vendor");
    const relBanks = ["Chase", "U.S. Bank"].filter(b => !x.banks.includes(b));
    if (P.tierIdx >= 4 && relBanks.length) T(0, "Prepare", `Open business checking at ${relBanks.join(" and ")} 30 days before applying`, "A deposit relationship improves approval odds and limits.", "None", "");
    const start1 = Math.max(prep, P.tierIdx >= 4 && relBanks.length ? 30 : 0, 14);

    if (P.tierIdx >= 3) {
      let day = start1; let i = 0;
      const ALIAS = { "American Express": "Amex", "Comenity / Bread": "Comenity" };
      const seqRows = D.seq[P.tier].filter(r => r.product && r.product !== "Checkpoint" && r.product !== "Setup");
      const amountFor = l => { const key = ALIAS[l.name] || l.name.split(" ")[0]; const row = seqRows.find(r => (r.action + " " + r.bureau).includes(key)); return row ? row.amount : ""; };
      for (const l of P.lenders.filter(l => l.fit === "good" && l.name !== "Capital One")) {
        T(day, `Round ${i + 1}`, `Apply: ${l.name}`, (l.rule ? l.rule + " " : "") + l.why, `${l.bureau} (${pct(l.p)})`, amountFor(l));
        i++; day += 14;
      }
      P.stackEnd = day - 14;
      const later = P.lenders.filter(l => l.fit === "warn");
      if (later.length) {
        const wait = Math.max(day + 30, inqMax >= 3 ? 180 : 0);
        later.forEach((l, j) => T(wait + j * 14, "Later", `Optional: ${l.name}`, (l.rule ? l.rule + " " : "") + l.why, `${l.bureau} (${pct(l.p)})`, amountFor(l)));
        day = wait + later.length * 14;
      }
      if (i) T(P.stackEnd + 74, "Grow", "Request credit limit increases, then cool off 60 to 90 days", "Amex reviews on a soft pull; Chase uses a hard pull.", "Amex soft; Chase hard", "+50% to +200%");
      if (!i) T(start1, "Hold", "No lender is a clean fit yet", "Fix the readiness items above, then regenerate the plan.", "None", "");

    } else {
      // builder path from the funding ladder for this tier
      D.seq[P.tier].forEach(r => {
        if (r.product === "Checkpoint") return;
        const d0 = /Day 0/.test(r.when) ? 0 : /Week (\d+)/.test(r.when) ? (+RegExp.$1 - 1) * 7 + 7 : /Month (\d+)/.test(r.when) ? +RegExp.$1 * 30 : null;
        T(d0 == null ? start1 + 30 : Math.max(d0, prep), d0 == null ? r.when : "Build", r.action, r.note || "", r.bureau, r.amount);
      });
    }
    // business funding windows
    const dep = x.deposits || (x.revenue ? x.revenue / 12 : 0);
    if (P.hasEntity) {
      const need = Math.max(0, 6 - (P.tib || 0)) * 30;
      T(need + (need ? 0 : start1), "Business Funding", (P.tib || 0) >= 6 && dep >= 10000 ? "Online business line of credit (soft pull to see offers)" : "Online business line of credit once 6 months in business and steady deposits",
        "Fundbox about 600, Bluevine and OnDeck about 625; bank statements, no hard pull to quote.", "No hard pull to quote", "$5,000 to $100,000");
      if ((P.tib || 0) < 24) T((24 - (P.tib || 0)) * 30, "Business Funding", "Bank line of credit or SBA 7(a) once 2 years in business", "Two years of returns and steady revenue open the lowest-cost capital.", "Lender's choice", "Up to $5M (SBA)");
      else T(Math.max(start1, 30), "Business Funding", "Bank line of credit or SBA 7(a)", "The business has two years of history; price these against the card stack.", "Lender's choice", "Up to $5M (SBA)");
    }
    P.timeline.sort((a, b) => a.day - b.day);

    // benchmarks
    const next = P.tierIdx < 6 ? TIER_LOW[P.tierIdx + 1] : null;
    if (P.mid != null && next) {
      const gap = next - P.mid;
      let months = Math.ceil(gap / 15);
      if (P.util > 0.3) months = Math.max(1, months - 2);
      if (derogTotal) months += 6;
      if (inqMax >= 3) months = Math.max(months, 6);
      months = Math.min(Math.max(months, 1), 24);
      P.bench.push({ when: fmtDate(addDays(x.start, months * 30)), what: `Middle score reaches ${next} (${TIERS[P.tierIdx + 1]} tier)`, how: `${gap} points from ${P.mid}. On-time payments, utilization under 10% and no new hard pulls outside the plan.` });
    }
    if (P.util != null && P.util > 0.1) P.bench.push({ when: fmtDate(addDays(x.start, 35)), what: "Personal utilization under 10%", how: `Total personal balances at or below ${money(0.09 * sum(pc, "limit"))}.` });
    if (inqMax >= 3) P.bench.push({ when: fmtDate(addDays(x.start, 180)), what: "Under 3 hard inquiries per bureau in the past 6 months", how: "Inquiries count in scoring for 12 months and stay on the report for 24." });
    if (P.hasEntity) P.bench.push({ when: fmtDate(addDays(x.start, 120)), what: x.paydex != null && x.paydex >= 80 ? "Keep Paydex at 80 or higher" : "Paydex score of 80 (pays on time)", how: "Pay every vendor on or before the due date; paying early lifts it above 80." });
    if (P.tierIdx >= 3 && P.stackEnd != null) P.bench.push({ when: fmtDate(addDays(x.start, P.stackEnd)), what: "Core business card stack complete", how: "No more than one hard pull per bureau per round, 7 to 14 days apart." });
    if (P.hasEntity && (P.tib || 0) < 24) P.bench.push({ when: fmtDate(addDays(x.start, (24 - (P.tib || 0)) * 30)), what: "2 years in business", how: "Opens bank lines, SBA 7(a) and larger term loans." });
    P.bench.sort((a, b) => new Date(a.when) - new Date(b.when));

    // funding range from the ladder rows used
    const amts = P.timeline.filter(t => /^Round/.test(t.phase)).map(t => (t.amount.match(/\$[\d,]+/g) || []).map(s => +s.replace(/[$,]/g, ""))).filter(a => a.length);
    P.rangeLo = amts.reduce((t, a) => t + a[0], 0); P.rangeHi = amts.reduce((t, a) => t + (a[1] || a[0]), 0);

    // business funding entities by NAICS, stage and score
    const s2 = (x.naics || "").slice(0, 2), s3 = (x.naics || "").slice(0, 3), s4 = (x.naics || "").slice(0, 4);
    const cats = [];
    const pick = (ind, why) => {
      const ok = D.lenders.filter(l => l.ind.startsWith(ind) && (minScore(l.min) == null || P.mid == null || minScore(l.min) <= P.mid + 10)).slice(0, 4);
      if (ok.length) cats.push({ cat: ind, why, list: ok });
    };
    if (P.tierIdx >= 3) pick("Fintech & Corporate", "Corporate cards that underwrite on cash balances, not personal credit.");
    if (["484", "488", "492", "561"].includes(s3) || s2 === "23" || s2 === "42") pick("Invoice Factoring", "Advances against unpaid invoices; approval leans on your customers' credit.");
    if (["23", "48", "11", "21", "31", "32", "33", "62", "72"].includes(s2)) pick("Equipment Financing", "The equipment secures the loan, so score floors are lower.");
    if (s2 === "53" || s3 === "236") pick("Mortgage, DSCR", "Property cash flow and value drive approval.");
    if (P.hasEntity && (P.tib || 0) >= 6) pick("Online Business Lenders", "Lines and term loans based on bank deposits.");
    if (P.hasEntity) pick("SBA, CDFI", "Lowest-cost capital; microloans fit startups and thinner files.");
    if (dep >= 10000 && ["44", "45", "72"].includes(s2)) pick("Merchant Cash Advance", "Fast, but the most expensive option. Use only for short gaps.");
    pick("Vendor / Net-30", "Builds the business credit file with no personal pull.");
    P.cats = cats;
    return P;
  }

  // ------------------------------------------------------------------ render
  const bc = b => { const k = BK[String(b).split(" ")[0]]; return k ? `<span class="b-${k}">${esc(b)}</span>` : esc(b); };
  function render(P) {
    const x = P.x;
    const kp = (v, l) => `<div class="kpi"><b>${v}</b><span>${l}</span></div>`;
    const sb = P.stateBureau;
    let h = `<h2>Funding Strategy for ${esc(x.client)}</h2>
      <p class="note">Prepared ${fmtDate(new Date())}${x.preparer !== "N/A" ? " by " + esc(x.preparer) : ""}. Strategy start ${fmtDate(addDays(x.start, 0))}. Data as of ${esc(D.asof)}.</p>
      <div class="kpis">${kp(P.mid ?? "N/A", "Middle credit score")}${kp(P.tier, "Funding tier")}${kp(pct(P.util), "Personal utilization")}${kp(x.new24 ?? "N/A", "New accounts (24 mo)")}${kp(P.best ? B[P.best] : "N/A", "Strongest report")}${kp(P.tib != null ? P.tib + " mo" : "N/A", "Time in business")}${kp(P.rangeHi ? money(P.rangeLo) + " to " + money(P.rangeHi) : "Build first", "Planning range, card stack")}${kp(money(x.goal), "Funding goal")}</div>
      <h2>Readiness Check</h2>${P.flags.map(fl => `<div class="flag ${fl.lvl}">${esc(fl.t)}</div>`).join("") || `<div class="flag good">No blocking issues found.</div>`}
      <h2>Bureau Plan for ${esc(P.stateName)}</h2>
      <p>Across all lenders, ${esc(P.stateName)} leans ${bc(sb.b)} (${pct(sb.p)}; ${esc(sb.status.toLowerCase())}, ${sb.n} datapoints). Each lender's likely bureau below comes from the state by lender model in the dashboard.</p>
      <table class="res"><thead><tr><th>Order</th><th>Lender</th><th>Likely Bureau</th><th>Fit</th><th>Why</th></tr></thead><tbody>
      ${P.lenders.map((l, i) => `<tr><td>${i + 1}</td><td><b>${esc(l.name)}</b></td><td>${bc(l.bureau)} ${pct(l.p)}</td><td class="fit-${l.fit}">${{ good: "Good", warn: "Caution", bad: "Skip" }[l.fit]}</td><td>${esc(l.why)}${l.rule ? `<br><span class="note">${esc(l.rule)}</span>` : ""}</td></tr>`).join("")}
      </tbody></table>
      <h2>Funding Sequence and Benchmark Timeline</h2>
      <table class="res"><thead><tr><th>Date</th><th>Phase</th><th>Action</th><th>Bureau</th><th>Typical Amount</th></tr></thead><tbody>
      ${P.timeline.map(t => `<tr><td style="white-space:nowrap">${t.date}</td><td>${esc(t.phase)}</td><td><b>${esc(t.action)}</b>${t.detail ? `<br><span class="note">${esc(t.detail)}</span>` : ""}</td><td>${bc(t.bureau)}</td><td>${esc(t.amount)}</td></tr>`).join("")}
      </tbody></table>
      <h3>Benchmarks</h3>
      <table class="res"><thead><tr><th>Target Date</th><th>Benchmark</th><th>How</th></tr></thead><tbody>${P.bench.map(b => `<tr><td style="white-space:nowrap">${b.when}</td><td><b>${esc(b.what)}</b></td><td>${esc(b.how)}</td></tr>`).join("")}</tbody></table>
      <p class="note">Target dates are planning estimates from the inputs, not guarantees. Recheck scores monthly and move dates as results come in.</p>
      <h2>Business Credit Plan</h2>
      <table class="res"><thead><tr><th>Report</th><th>Entered</th><th>Next Step</th></tr></thead><tbody>
      <tr><td>Dun &amp; Bradstreet Paydex</td><td>${x.paydex ?? "N/A"}</td><td>${x.paydex == null ? "Get a D-U-N-S number and add vendors that report to D&amp;B." : x.paydex >= 80 ? "On track. Paying early pushes it above 80." : "Below 80: pay every vendor on or before the due date."}</td></tr>
      <tr><td>Experian Intelliscore Plus</td><td>${x.intelliscore ?? "N/A"}</td><td>${x.intelliscore == null ? "Add vendors that report to Experian Business." : "Higher is lower risk; keep balances current and add trade lines."}</td></tr>
      <tr><td>Equifax Business</td><td>${x.eqbiz ?? "N/A"}</td><td>${x.eqbiz == null ? "Builds from bank and card trade lines that report to Equifax." : "Keep business card and loan payments on time."}</td></tr>
      <tr><td>Creditsafe</td><td>${x.creditsafe ?? "N/A"}</td><td>${x.creditsafe == null ? "Builds from public filings and trade data once the entity is active." : "Higher is lower risk; keep filings current."}</td></tr>
      <tr><td>Trade Lines Reporting</td><td>${x.tradelines ?? "N/A"}</td><td>${(x.tradelines || 0) >= 5 ? "Enough to support store and fleet credit next." : "Target 5 reporting vendors: " + esc(vendorsText()) + "."}</td></tr>
      </tbody></table>
      <h2>Funding Entities That Fit This Business</h2>
      <p>${P.sector ? `NAICS ${esc(x.naics)}: ${esc(P.sector)}.` : "No NAICS code entered, so the list covers general options."} ${P.tib != null ? `${P.tib} months in business.` : ""} ${x.revenue != null ? `Revenue ${money(x.revenue)} a year.` : ""}</p>
      ${P.cats.map(c => `<h3>${esc(c.cat)}</h3><p class="note">${esc(c.why)}</p><table class="res"><thead><tr><th>Lender</th><th>Bureau</th><th>Minimum</th><th>Documentation</th></tr></thead><tbody>${c.list.map(l => `<tr><td><b>${esc(l.name)}</b><br><span class="note">${esc(l.ftype)}</span></td><td>${bc(l.prim)}</td><td>${esc(l.min)}</td><td>${esc(l.doc)}</td></tr>`).join("")}</tbody></table>`).join("")}
      <h2>Rules Behind the Plan</h2>${D.rules.map(r => `<p><b>${esc(r[0])}.</b> ${esc(r[1])}</p>`).join("")}
      ${x.notes ? `<h3>Advisor Notes</h3><p>${esc(x.notes)}</p>` : ""}
      ${x.docs.length ? `<h3>Documents Reviewed</h3><p>${x.docs.map(esc).join(", ")}</p>` : ""}`;
    $("#report").innerHTML = h;
  }
  const vendorsText = () => D.lenders.filter(l => l.ind.startsWith("Vendor") && /no personal pull/i.test(l.min)).slice(0, 4).map(l => l.name.split(" (")[0]).join(", ");

  // ------------------------------------------------------------------ PDF
  function pdf(P) {
    const { jsPDF } = window.jspdf; const x = P.x;
    const doc = new jsPDF({ unit: "pt", format: "letter" });
    const W = doc.internal.pageSize.getWidth(), M = 40;
    const NAVY = [20, 33, 61], TEAL = [47, 212, 196], INK = [16, 24, 38], MUT = [90, 100, 115];
    const COL = { Experian: [42, 120, 214], Equifax: [235, 104, 52], TransUnion: [27, 175, 122] };
    let y = 0;
    doc.setFillColor(...NAVY); doc.rect(0, 0, W, 86, "F");
    doc.setFillColor(...TEAL); doc.rect(0, 86, W, 3, "F");
    doc.setTextColor(255); doc.setFont("helvetica", "bold"); doc.setFontSize(20); doc.text("Credit Stack and Funding Strategy", M, 40);
    doc.setFont("helvetica", "normal"); doc.setFontSize(11);
    doc.text(`${x.client}${x.bizname !== "N/A" ? "  |  " + x.bizname : ""}  |  ${P.stateName}`, M, 60);
    doc.text(`Prepared ${fmtDate(new Date())}${x.preparer !== "N/A" ? " by " + x.preparer : ""}  |  Start ${fmtDate(addDays(x.start, 0))}`, M, 76);
    y = 108;
    const H = t => { if (y > 700) { doc.addPage(); y = 50; } doc.setTextColor(...NAVY); doc.setFont("helvetica", "bold"); doc.setFontSize(14); doc.text(t, M, y); doc.setDrawColor(...TEAL); doc.setLineWidth(1.5); doc.line(M, y + 5, M + 60, y + 5); y += 18; };
    const P_ = (t, size = 10, color = INK) => { doc.setTextColor(...color); doc.setFont("helvetica", "normal"); doc.setFontSize(size); const lines = doc.splitTextToSize(t, W - 2 * M); if (y + lines.length * size * 1.3 > 750) { doc.addPage(); y = 50; } doc.text(lines, M, y); y += lines.length * size * 1.3 + 4; };
    const tbl = (head, body, opts = {}) => { doc.autoTable(Object.assign({ head: [head], body, startY: y, margin: { left: M, right: M }, styles: { fontSize: 8.5, cellPadding: 4, textColor: INK, lineColor: [217, 222, 231], lineWidth: 0.5 }, headStyles: { fillColor: NAVY, textColor: 255, fontStyle: "bold" }, alternateRowStyles: { fillColor: [244, 246, 250] },
      didParseCell: d => { if (d.section === "body") { const t = String(d.cell.raw || ""); const k = Object.keys(COL).find(b => t.startsWith(b)); if (k && opts.bureauCols && opts.bureauCols.includes(d.column.index)) { d.cell.styles.textColor = COL[k]; d.cell.styles.fontStyle = "bold"; } if (opts.fitCol === d.column.index) { d.cell.styles.fontStyle = "bold"; d.cell.styles.textColor = t === "Good" ? [12, 140, 12] : t === "Skip" ? [208, 59, 59] : [185, 122, 0]; } } } }, opts.extra || {})); y = doc.lastAutoTable.finalY + 16; };

    H("Profile Snapshot");
    tbl(["Measure", "Value", "Measure", "Value"], [
      ["Middle credit score", String(P.mid ?? "N/A"), "Funding tier", P.tier],
      ["Experian / Equifax / TransUnion", ["ex", "eq", "tu"].map(k => x.score[k] ?? "N/A").join(" / "), "Strongest / weakest report", `${P.best ? B[P.best] : "N/A"} / ${P.worst ? B[P.worst] : "Even"}`],
      ["Hard inquiries, 6 mo (EX/EQ/TU)", ["ex", "eq", "tu"].map(k => x.inq6[k] ?? 0).join(" / "), "New accounts, 24 mo", String(x.new24 ?? "N/A")],
      ["Personal utilization", pct(P.util), "All cards utilization", pct(P.utilAll)],
      ["Total card limits", money(P.totalLimit), "Total card balances", money(P.totalBal)],
      ["Business entity", x.entity, "NAICS", x.naics ? `${x.naics}${P.sector ? " (" + P.sector + ")" : ""}` : "N/A"],
      ["Time in business", P.tib != null ? P.tib + " months" : "N/A", "Employees", x.employees],
      ["Annual revenue", money(x.revenue), "Monthly deposits", money(x.deposits)],
      ["EIN / D-U-N-S / business bank", [x.ein, x.duns, x.bizbank].map(v => v ? "Yes" : "No").join(" / "), "Paydex", String(x.paydex ?? "N/A")],
      ["Banking relationships", x.banks.join(", ") || "N/A", "Funding goal", money(x.goal)]
    ], { extra: { columnStyles: { 0: { fontStyle: "bold" }, 2: { fontStyle: "bold" } } } });

    H("Readiness Check");
    tbl(["Status", "Finding"], P.flags.map(fl => [{ good: "Good", warn: "Caution", bad: "Fix first" }[fl.lvl], fl.t]), { fitCol: 0, extra: { columnStyles: { 0: { cellWidth: 60 } } } });

    H(`Bureau Plan for ${P.stateName}`);
    P_(`Across all lenders, ${P.stateName} leans ${P.stateBureau.b} (${pct(P.stateBureau.p)}; ${P.stateBureau.status.toLowerCase()}, ${P.stateBureau.n} datapoints).`, 9.5, MUT);
    tbl(["#", "Lender", "Likely Bureau", "Fit", "Why"], P.lenders.map((l, i) => [String(i + 1), l.name, `${l.bureau} ${pct(l.p)}`, { good: "Good", warn: "Caution", bad: "Skip" }[l.fit], l.why + (l.rule ? " " + l.rule : "")]), { bureauCols: [2], fitCol: 3, extra: { columnStyles: { 0: { cellWidth: 20 }, 1: { cellWidth: 90, fontStyle: "bold" }, 2: { cellWidth: 80 }, 3: { cellWidth: 48 } } } });

    H("Funding Sequence and Benchmark Timeline");
    tbl(["Date", "Phase", "Action", "Bureau", "Typical Amount"], P.timeline.map(t => [t.date, t.phase, t.action + (t.detail ? "\n" + t.detail : ""), t.bureau, t.amount]), { bureauCols: [3], extra: { columnStyles: { 0: { cellWidth: 66 }, 1: { cellWidth: 62 }, 3: { cellWidth: 80 }, 4: { cellWidth: 80 } } } });
    if (P.rangeHi) P_(`Planning range for the card stack: ${money(P.rangeLo)} to ${money(P.rangeHi)} in initial limits, before limit increases.`, 9.5, MUT);

    H("Benchmarks");
    tbl(["Target Date", "Benchmark", "How"], P.bench.map(b => [b.when, b.what, b.how]), { extra: { columnStyles: { 0: { cellWidth: 70 }, 1: { cellWidth: 170, fontStyle: "bold" } } } });
    P_("Target dates are planning estimates from the inputs, not guarantees. Recheck scores monthly and move dates as results come in.", 8.5, MUT);

    H("Business Credit Plan");
    tbl(["Report", "Entered", "Next Step"], [
      ["Dun & Bradstreet Paydex", String(x.paydex ?? "N/A"), x.paydex == null ? "Get a D-U-N-S number and add vendors that report to D&B." : x.paydex >= 80 ? "On track. Paying early pushes it above 80." : "Below 80: pay every vendor on or before the due date."],
      ["Experian Intelliscore Plus", String(x.intelliscore ?? "N/A"), x.intelliscore == null ? "Add vendors that report to Experian Business." : "Higher is lower risk; keep balances current and add trade lines."],
      ["Equifax Business", String(x.eqbiz ?? "N/A"), x.eqbiz == null ? "Builds from bank and card trade lines that report to Equifax." : "Keep business card and loan payments on time."],
      ["Creditsafe", String(x.creditsafe ?? "N/A"), x.creditsafe == null ? "Builds from public filings and trade data once the entity is active." : "Higher is lower risk; keep filings current."],
      ["Trade lines reporting", String(x.tradelines ?? "N/A"), (x.tradelines || 0) >= 5 ? "Enough to support store and fleet credit next." : "Target 5 reporting vendors: " + vendorsText() + "."]
    ], { extra: { columnStyles: { 0: { cellWidth: 130, fontStyle: "bold" }, 1: { cellWidth: 60 } } } });

    H("Funding Entities That Fit This Business");
    P_(`${P.sector ? `NAICS ${x.naics}: ${P.sector}. ` : "No NAICS code entered; general options listed. "}${P.tib != null ? P.tib + " months in business. " : ""}${x.revenue != null ? "Revenue " + money(x.revenue) + " a year." : ""}`, 9.5, MUT);
    P.cats.forEach(c => { P_(`${c.cat}: ${c.why}`, 10, NAVY); tbl(["Lender", "Bureau", "Minimum", "Documentation"], c.list.map(l => [l.name, l.prim, l.min, l.doc]), { bureauCols: [1], extra: { columnStyles: { 0: { cellWidth: 170, fontStyle: "bold" } } } }); });

    H("Rules Behind the Plan");
    D.rules.forEach(r => P_(`${r[0]}. ${r[1]}`, 9));
    if (x.notes) { H("Advisor Notes"); P_(x.notes, 9.5); }
    if (x.docs.length) { H("Documents Reviewed"); P_(x.docs.join(", "), 9.5); }
    H("Sources and Limits");
    P_(`Bureau likelihoods come from a logistic regression on consumer-reported inquiry datapoints (2008 to 2026) across ${Object.keys(D.states).length} states and 56 cited sources, as of ${D.asof}. No lender publishes which bureau it pulls by state. Minimum scores are published floors or community estimates. Income, debt-to-income, utilization, account age, recent inquiries and deposits decide outcomes as much as the score. This is a planning reference, not financial, credit or legal advice.`, 8.5, MUT);
    P_("Full data, methods and sources: shamarrobinson.github.io/client-personal-and-business-funding-sequence-dashboard", 8.5, MUT);
    const n = doc.getNumberOfPages();
    for (let i = 1; i <= n; i++) { doc.setPage(i); doc.setFontSize(8); doc.setTextColor(...MUT); doc.text(`${x.client}  |  Credit Stack and Funding Strategy  |  Page ${i} of ${n}`, M, 776); }
    const safe = x.client.replace(/[^A-Za-z0-9]+/g, "_").replace(/^_|_$/g, "") || "Client";
    doc.save(`${safe}_Funding_Strategy_${x.start}.pdf`);
  }

  // ------------------------------------------------------------------ wire up
  f.addEventListener("submit", e => {
    e.preventDefault(); $("#msg").textContent = "";
    if (!D) { $("#msg").textContent = "Lender data is still loading. Try again in a moment."; return; }
    const x = read();
    if (!x.client) { $("#msg").textContent = "Enter the client's name."; f.client.focus(); return; }
    if (!x.state) { $("#msg").textContent = "Choose the client's state."; f.state.focus(); return; }
    lastPlan = plan(x); render(lastPlan);
    $("#out").style.display = "block"; $("#out").scrollIntoView({ behavior: "smooth" });
  });
  $("#pdf").onclick = () => { if (!lastPlan) return; if (!window.jspdf) { $("#msg").textContent = "The PDF library did not load. Check the connection and reload."; return; } pdf(lastPlan); };
  window.__generator = { plan, read, pdf: () => pdf(lastPlan) };
})();
