# Client Personal and Business Funding Sequence Dashboard

**Live dashboard:** https://shamarrobinson.github.io/Client-Personal-and-Business-Funding-Sequence-Dashboard/

| View | Link |
| --- | --- |
| Dashboard site (this repository, GitHub Pages) | [shamarrobinson.github.io/Client-Personal-and-Business-Funding-Sequence-Dashboard](https://shamarrobinson.github.io/Client-Personal-and-Business-Funding-Sequence-Dashboard/) |
| Interactive maps and Story (Tableau Public) | [FP&A: Credit Stacking & Funding Sequencing Strategy: Which Bureau Will They Pull?](https://public.tableau.com/views/ClientPersonalandBusinessFundingSequenceDashboard/WhichBureauWillTheyPull?:showVizHome=no) (full screen, fits one screen with no scrolling) · [profile page](https://public.tableau.com/app/profile/shamar.robinson/viz/ClientPersonalandBusinessFundingSequenceDashboard/WhichBureauWillTheyPull) |
| Slideshow | [Presentation](https://claude.ai/artifact/95vnkBxejyTxzMTD5QAxnw) |
| Full workbook | [data/Inquiry_Database_Expanded.xlsx](data/Inquiry_Database_Expanded.xlsx) |

A dashboard and database of which credit bureau each lender pulls by state, with funding type, average score needed, documentation level, and a funding sequence for every credit score tier.

## About the Data

| | |
| --- | --- |
| **Context** | Every hard inquiry lands on one of three credit reports (**Experian**, **Equifax** or **TransUnion**). Lenders do not publish which one they pull or how it changes by state, so a wrong forecast can stack inquiries on a client's weakest report. |
| **Sources** | A 355-row inquiry table from 16 states plus 670 outside state-level datapoints from 56 cited sources: Doctor of Credit issuer tables (2008 to 2019), the myFICO Forums state grid (July 2023) and 2025 to 2026 forum posts, MyBankTracker, CardRight, StackEasy, and lender and review pages for minimum scores. Every source is listed on the [Sources & Notes page](https://shamarrobinson.github.io/Client-Personal-and-Business-Funding-Sequence-Dashboard/sources.html). |
| **As of** | Research completed October 7, 2026. |
| **Updates** | Lender minimums are reviewed every quarter. Each new inquiry datapoint reruns the cleaning, maps and regression from the scripts in [analysis/](analysis). |
| **Limits** | Consumer-reported (no lender publishes its bureau by state); uneven in age (the largest tables cover 2008 to 2016); some states rest on fewer than 10 pulls; minimum scores are published floors or community estimates. A planning reference, not financial advice. |

Context facts used in the story: [myFICO, Do Credit Inquiries Lower Your FICO Score?](https://www.myfico.com/crediteducation/CreditChecks.aspx); [FTC, In FTC Study, Five Percent of Consumers Had Errors on Their Credit Reports (Feb 2013)](https://www.ftc.gov/news-events/news/press-releases/2013/02/ftc-study-five-percent-consumers-had-errors-their-credit-reports-could-result-less-favorable-terms); [CFPB, Analysis of Differences between Consumer- and Creditor-Purchased Credit Scores (Sep 2012)](https://files.consumerfinance.gov/f/201209_Analysis_Differences_Consumer_Credit.pdf).

## Dashboard Pages

| Page | What it shows |
| --- | --- |
| [Dashboard](https://shamarrobinson.github.io/Client-Personal-and-Business-Funding-Sequence-Dashboard/index.html) | Headline metrics and charts |
| [Lender Database](https://shamarrobinson.github.io/Client-Personal-and-Business-Funding-Sequence-Dashboard/lenders.html) | 204 lenders in 19 industry sections |
| [All States & Banks](https://shamarrobinson.github.io/Client-Personal-and-Business-Funding-Sequence-Dashboard/states.html) | The original 355 inquiry rows, cross-checked |
| [Bureau by State](https://shamarrobinson.github.io/Client-Personal-and-Business-Funding-Sequence-Dashboard/matrix.html) | 670 outside state-level datapoints |
| [Funding Sequence](https://shamarrobinson.github.io/Client-Personal-and-Business-Funding-Sequence-Dashboard/sequence.html) | Application order for each score tier |
| [Bureau Likelihood](https://shamarrobinson.github.io/Client-Personal-and-Business-Funding-Sequence-Dashboard/likelihood.html) | Regression: most likely bureau in close-call states, and by lender |
| [Sources & Notes](https://shamarrobinson.github.io/Client-Personal-and-Business-Funding-Sequence-Dashboard/sources.html) | Sources, column guide and data limits |

## Tableau Public

The [Tableau Story "FP&A: Credit Stacking & Funding Sequencing Strategy: Which Bureau Will They Pull?"](https://public.tableau.com/views/ClientPersonalandBusinessFundingSequenceDashboard/WhichBureauWillTheyPull?:showVizHome=no) has 11 dashboard cards in an app-style layout: a clickable side menu (each row opens its card), a header band with clickable Overview, Maps and Decide tabs (cards 1, 5 and 8), and an About button on every card. Each card is 1110 x 740 so it fits a 1080p screen; the full-screen link removes the Tableau Public page header so nothing needs scrolling after a click. The theme is a dark "metal card" look taken from the cover photo, with sharp-edged panels and teal-to-orange edge lines. Each bureau keeps one color everywhere: **Experian** blue, **Equifax** orange, **TransUnion** green.

| Card | What it shows |
| --- | --- |
| 1. Overview | Cover photo, headline numbers, context, purpose, sources, update cadence, data limits and a guided walkthrough |
| 2. Funding Ladder | Seven score steps with their moves, what each step looks like (products, example lenders, bureau pulled, typical limit) and five rules for climbing |
| 3. Market and KPIs | Bureau shares and close-call count, a KPI list that opens a detail card, scope and who it serves |
| 4. Data and Method | Enrichment flow, the extract, transform, load process, the cleaning steps and the cross-check result |
| 5. Pick a Lender | Map of each lender's most-pulled bureau by state, with a lender drop-down and lenders grouped by habit |
| 6. Share Maps | Experian, Equifax and TransUnion share maps; click a state to open its State Detail card |
| 7. Close Calls | Click a state for the model's best forecast; hover a state to see its chance bars inside the tooltip |
| 8. Decision Tree | Five override checks, three bureau branches with three if/then cases each, four ordering rules, and four real forecasts |
| 9. Scorecard | Each issuer's bureau habit and where every number comes from |
| 10. Recommendations | Best move, when to choose it, why, next move, what to watch out for and which card to open, for five stakeholder types |
| 11. Sources | Every source as a clickable list, under the Story title |

Interactive features: tooltips with formulas on every number, nested charts (chance bars inside the close-call map tooltip, inline data bars in the State Detail card), dynamic detail cards (KPI, state and close-call panels), annotation callouts, numbered coach marks and a walkthrough, and an About popover on each card. Every number in a worked example or tooltip says what it is in parentheses, for example 466 (Experian pulls in Florida) ÷ 885 (all bureau pulls in Florida) = 53% (Experian's share).

### How the Numbers Work: KPIs

| KPI | Formula | Worked example (as of Oct 7, 2026) |
| --- | --- | --- |
| **KPI 1. Bureau Share of Pulls** | pulls on one bureau in a state ÷ all bureau pulls in that state | Florida, Experian: 466 ÷ 885 = 53% |
| **KPI 2. National Share of Pulls** | one bureau's pulls ÷ all 3,003 recorded pulls | Experian 1,616 ÷ 3,003 = 54%; Equifax 25%; TransUnion 21% |
| **KPI 3. Lead Margin** | top bureau share − second bureau share, in points | Texas: Experian 66% − TransUnion 17% = 49 points |
| **KPI 4. Close Call** | a state whose lead margin is under 20 points | 24 of 49 states; Alabama ties Experian and Equifax at 38% |
| **KPI 5. Issuer Bureau Habit** | an issuer's pulls on one bureau ÷ its recorded pulls | American Express 87% Experian; Synchrony 62% TransUnion |
| **KPI 6. Predicted Likelihood** | regression probability for a typical application; the three add to 100% | Alabama: Experian 43%, Equifax 33%, TransUnion 24% |
| **KPI 7. Leader Stability** | refits out of 150 where the same bureau stays on top | Connecticut 95% (clear lean); Alabama 83% (moderate lean) |
| **KPI 8. Model Lift** | 1 − (model log loss ÷ baseline log loss) | 1 − (0.903 ÷ 1.041) = 13% lower error; accuracy 55% vs 50% |
| **KPI 9. Cross-Check Result** | rows confirmed, partly confirmed or fitting the national pattern ÷ checkable rows | 193 of 355 rows checked (84 + 6 + 103); 0 contradicted |
| **KPI 10. Lender Confidence Mix** | lenders at each confidence level ÷ 204 | 39 High (19%), 104 Medium (51%), 61 Low (30%) |

### How the Story Is Built

[analysis/build_story.py](analysis/build_story.py) rebuilds the workbook from the published version in [tableau/source](tableau/source): it embeds the map data ([data/tableau/lender_state.csv](data/tableau/lender_state.csv)) as an extract, builds the 8 dashboard cards, the KPI, State Detail and close-call panels, the Help popovers and the close-call explorer from [regression_state_long.csv](data/tableau/regression_state_long.csv), recolors the maps and bolds every bureau name in its color. The infographics are drawn by [analysis/story_images.py](analysis/story_images.py) as images so they look the same on Tableau Public as in Desktop. The output is [tableau/Client_Personal_and_Business_Funding_Sequence_Dashboard.twbx](tableau/Client_Personal_and_Business_Funding_Sequence_Dashboard.twbx); card captions are in [tableau/story_points.md](tableau/story_points.md).

## Regression: Close-Call States

[analysis/bureau_regression.py](analysis/bureau_regression.py) fits a multinomial logistic regression (multiple regression for a three-way outcome) on 2,901 bureau-pull datapoints. Predictors: state, lender, data era, and lender-in-state for the 14 major issuers. A close call is a state where the top two bureaus are within 20 points in the recorded pulls (24 states).

| Model (5-fold cross-validation, whole reports held out) | Log loss | Accuracy |
| --- | --- | --- |
| State + lender + era + lender in state | 0.903 | 55% |
| Lender + era only | 0.905 | 55% |
| National shares only | 1.041 | 50% |

The lender explains most of which bureau is pulled; the state adds a little, mainly through lenders whose bureau changes by state. For a typical application, Experian is the most likely bureau in all 24 close-call states: 15 with a clear or moderate lean, 4 still toss-ups (Hawaii, Kansas, South Carolina, Virginia) and 5 with too little data to call. Outputs are in [data/tableau](data/tableau) (`regression_*.csv`, `Tableau_Regression_Data.xlsx`) and on the [Bureau Likelihood page](https://shamarrobinson.github.io/Client-Personal-and-Business-Funding-Sequence-Dashboard/likelihood.html).

## Files

- `index.html`, `lenders.html`, `states.html`, `matrix.html`, `sequence.html`, `likelihood.html`, `sources.html`: site pages
- `analysis/`: regression model, Tableau extract scripts, the story builder and its infographics
- `tableau/`: the rebuilt Tableau workbook, its source and the story captions
- `data/regression.json`: regression results the Likelihood page reads
- `assets/`: shared styles and script, plus the photos used in the Story and the deck
- `deck/`: the 10-slide deck (Slides artifact files) and `build_deck.py`, which writes it
- `data/db.json`: data the site reads
- `data/Inquiry_Database_Expanded.xlsx`: full workbook
- `data/tableau/`: Tableau-ready CSV and Excel files

Bureau data is consumer-reported. Scores are published minimums or community estimates. Reference information only, not financial advice.
