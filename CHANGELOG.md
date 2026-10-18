# Change Log

## 2026-10-17 (late night)

- Presentation: freshness check reloads the page once when a newer build is live, so a browser's saved copy never shows outdated slides.
- Tableau Story: "View Slideshow" link in the side panel of all 12 cards (opens the standalone presentation).
- Tableau Story card 3: Out of Scope matches the slides (approval odds line removed; "legal, tax or investment advice"); Data and Method diagrams use the balanced alignment and wider boxes.
- Presentation slide 6: wider diagram boxes (tighter gaps between steps) so fewer values wrap.
- Presentation: image and font links carry a content version tag, so browsers show updated slides immediately instead of a cached copy.
- Presentation slide 6: balanced text in both diagrams; values line up in one column per box and every box in a row starts on the same line, centered vertically.
- Presentation slide 6 (Data and Method): larger-type flow diagrams that fill the slide; the ETL panel text is about 60% larger.
- Next update date shown everywhere the data date appears: Tableau Story side panel, Overview card, Sources card and Help text; slides 1, 2 and 12; the Funding Generator. Set in one place, `analysis/update_schedule.py`: change AS_OF on each quarterly refresh and the next update (AS_OF plus one quarter) rolls forward in every output. Current: as of October 7, 2026; next update January 7, 2027.
- Presentation slide 9 (Decision Tree): larger-type tree that fills the slide height.
- Presentation slide 7 (Share Maps): the "In Tableau, click a state" badge now links to the Tableau Public story (also clickable in the PDF).
- Presentation slide 4 (Out of Scope): removed the approval odds line; the advice line now reads "legal, tax or investment advice".
- Presentation slide 3 (Funding Ladder): the step table now spans the full slide width with larger text, and a wider ladder chart closes the gap beside the rules panel.
- Story card 11 (Sources): new link buttons for the Slideshow, Slideshow PDF, Dashboard Website and Funding Generator.
- Slideshow moved to this site at `presentation/`: a standalone 12-slide presentation with self-hosted fonts, arrow-key, click and swipe navigation, full-screen mode and a downloadable PDF. No sign-in, no third-party branding. The Slideshow links on every page and in the README now point here. Built by `analysis/build_presentation.py`.
- New page and Story card 12, **Credit Stack and Funding Generator**: a form for a client's 3-bureau scores, inquiries, late payments, cards (limits and utilization), banking relationships, entity, NAICS, time in business, revenue, employees and business credit scores (Paydex, Experian Intelliscore, Equifax Business, Creditsafe). It returns a readiness check, a state-specific bureau plan for each major lender, an ordered application sequence with dated rounds, benchmarks, a business credit plan and funding entities matched to the NAICS code, and downloads it all as a PDF. Runs entirely in the browser; nothing is uploaded or saved.
- `analysis/build_generator_data.py` builds `data/generator.json` from the same files as the dashboard and Story.

## 2026-10-17 (night)

- All maps: base map state and country names turned off; bold black state labels drawn on the maps instead (state abbreviations on Pick a Lender, bold black share and status labels on the Share Maps and Close Calls maps).
- Share Maps: color ramps now start from a light tint of each bureau color, so black labels read on every state.
- Larger type across the whole story: native Tableau text up 20%, card image text up 15%.
- Pick a Lender map: tie colors are now light, high-contrast hues (lime for Experian / Equifax, aqua for Experian / TransUnion, yellow for Equifax / TransUnion, lilac for all three) so single-bureau states stand out and each tie is easy to tell apart.
- Pick a Lender map: states with no recorded pulls for the chosen lender now show in light gray as "No Data: No Pulls Recorded" instead of blank, with a tooltip explaining why.
- Pick a Lender tooltip: bureau counts separated with " | " so they no longer run together.

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
