"""One place for the data date and the next scheduled update.

On each quarterly refresh, set AS_OF to the refresh date. NEXT_UPDATE moves forward on its own
(AS_OF plus one quarter), and every output that imports this module shows the new dates:
the Tableau Story (build_story.py, story_images.py), the slide deck (deck/build_deck.py) and the generator data.
"""
from datetime import date

AS_OF = date(2026, 10, 7)
CYCLE_MONTHS = 3


def add_months(d, n):
    m = d.month - 1 + n
    y, m = d.year + m // 12, m % 12 + 1
    days = [31, 29 if y % 4 == 0 and (y % 100 or y % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
    return date(y, m, min(d.day, days))


def fmt(d):
    return f"{d.strftime('%B')} {d.day}, {d.year}"


NEXT_UPDATE_DATE = add_months(AS_OF, CYCLE_MONTHS)
ASOF = fmt(AS_OF)                    # "October 7, 2026"
NEXT_UPDATE = fmt(NEXT_UPDATE_DATE)  # "January 7, 2027"

if __name__ == "__main__":
    print(ASOF, "->", NEXT_UPDATE)
