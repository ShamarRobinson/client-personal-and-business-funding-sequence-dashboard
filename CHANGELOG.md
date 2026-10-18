# Change Log

## 2026-10-17 (late evening)

- Share Maps card: 2x2 map grid with lower-48 framing so each map gets more room; compact State Detail panel.
- Close Calls card: new ivory, taupe, gold and slate status colors with dark map labels; deck slide matched.
- Full-screen view: cards enlarged from 1110 x 740 to 1320 x 880 (story frame 1344 x 1020) so they fill a 1080p screen.
- Repository renamed to lowercase: client-personal-and-business-funding-sequence-dashboard.

## October 17, 2026 (evening)

- Story is now 11 cards: the Funding Ladder has its own page right after the Overview (ladder, what each step looks like, five rules for climbing); Recommendations has its own page right before Sources; Sources is the last page under the Story title.
- Stronger decision tree: five override checks, three bureau branches with three if/then cases each, and four ordering rules.
- Slide deck updated to 12 slides in the same order.

- Main title is now "FP&A: Credit Stacking & Funding Sequencing Strategy" in the Story, side panel and deck cover.

- Every number in the KPI worked examples, KPI list, tile tooltips, map tooltips and State Detail card now says what it is in parentheses.
- Tile tooltips explain how each number is calculated, what it means and how to use it; the Keep Only and Exclude buttons are hidden.
- The Overview, Maps and Decide tabs are clickable (cards 1, 4 and 7). The Help button is renamed About.
- Cards resized to 1110 x 740 (Story 1134 x 880) so a card fits a 1080p screen; links now open the full-screen view, which starts at the top with no page header to scroll past.

## October 17, 2026 (redesign)

- The side menu on every card is clickable: each row is a navigation button that opens its card.

- Tableau Story condensed from 16 cards to 8 dashboard cards with an app-style layout: side panel navigation, header band with Overview, Maps and Decide tabs, and a Help popover on each card.
- New dark theme taken from the cover photo of metal cards: near-black canvas, charcoal panels with sharp edges, teal-to-orange edge lines. Photos added to the overview, Data and Method, Market and KPIs, Decide and Recommendations panels.
- Title changed to "FP&A: Credit Stacking & Funding Sequencing Strategy", with "Which Bureau Will They Pull?" kept as a subheading. The Tableau Public link is unchanged.
- Added tooltips with formulas on every number, a KPI list that opens a detail card, a State Detail card on the share maps, chance bars nested in the close-call map tooltip, annotation callouts, numbered coach marks and a guided walkthrough.
- Maps use a dark base map and dark-to-bright ramps in each bureau's color.
- Slide deck condensed from 24 slides to 10 in the same theme, with the cover photo on the title slide; the deck source is now in `deck/`.

## October 17, 2026

- Tableau Story rebuilt with 16 cards. New opening: an introduction with context, purpose, sources, update cadence and data limits, then who it serves, scope and key terms.
- Added the components the story was missing: market context with sourced facts, ten KPIs with formulas and worked examples, where every number comes from (with clickable sources) and a recommendation for each stakeholder.
- Close calls is now an interactive dashboard: click a state on the verdict map to see its result and the chance of each bureau.
- The decision tree, data flow, share equation, funding ladder and scorecard were redrawn as clean images in a data-model style.
- Each bureau keeps one color everywhere (Experian blue, Equifax orange, TransUnion green), on the maps and as bold text wherever a bureau is named.
- Titles and subheadings use Title Case. The map data is embedded in the workbook so it opens in Tableau Public Desktop.
- The slide deck was updated to match: a new second slide on context, purpose, sources, updates and limits, plus market context, key terms, two KPI slides, recommendations and where the numbers come from.
