"""Rewrite generated slides into the Slides artifact's closed HTML subset."""
import re, sys, json
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString, Tag
BLOB = json.load(open(sys.argv[2])); SIZES = json.load(open(sys.argv[3]))
INLINE = {"span", "b", "i", "u", "a", "br"}
TEXT = {"p", "h1", "h2", "h3", "li", "td", "th"}
def css(t):
    d = {}
    for part in (t.get("style") or "").split(";"):
        if ":" in part:
            k, v = part.split(":", 1); d[k.strip().lower()] = v.strip()
    return d
def put(t, d): t["style"] = ";".join(f"{k}:{v}" for k, v in d.items()) if d else None; (t.attrs.pop("style") if not d else None)
POS = {"position", "left", "top", "right", "bottom", "width", "height", "opacity", "transform"}
CHILD = {"flex", "flex-grow", "flex-shrink", "flex-basis", "align-self", "justify-self", "min-width", "min-height", "max-width", "max-height", "grid-column", "grid-row", "aspect-ratio"}
BOX = {"padding", "background", "border", "border-top", "border-right", "border-bottom", "border-left", "border-radius", "box-shadow", "filter", "mix-blend-mode"}
TXT = {"font-family", "font-size", "font-weight", "font-style", "line-height", "letter-spacing", "text-align", "text-transform", "white-space", "text-decoration", "color", "text-shadow", "font-variant-numeric"}
LAY = {"display", "flex-direction", "flex-wrap", "gap", "align-items", "justify-content", "justify-items", "grid-template-columns", "grid-template-rows", "overflow"}
ALLOW = {"div": POS | CHILD | BOX | LAY | {"font-family", "font-size", "line-height", "color", "letter-spacing", "text-align", "text-transform"},
         "p": POS | CHILD | BOX | TXT, "h1": POS | CHILD | BOX | TXT, "h2": POS | CHILD | BOX | TXT, "h3": POS | CHILD | BOX | TXT,
         "span": {"color", "font-weight", "font-style"}, "b": {"color"}, "a": {"color"},
         "img": POS | CHILD | {"object-fit", "border", "border-radius", "box-shadow", "filter"},
         "section": {"background", "color", "font-family", "font-size", "line-height", "display", "flex-direction", "padding", "gap", "align-items", "justify-content", "position"},
         "table": {"font-family", "font-size", "color", "background", "border", "width", "padding"}, "tr": {"background"},
         "td": {"padding", "color", "font-family", "font-size", "font-weight", "text-align", "width"}, "th": {"padding", "color", "font-family", "font-size", "font-weight", "text-align", "width"}}
def fix_vals(k, v):
    v = v.replace(" .", " 0.")
    if v.startswith("."): v = "0" + v
    if k in ("top", "bottom", "left", "right") and v.startswith("-"): v = "0"
    if k == "display": v = {"inline-flex": "flex", "inline-block": None, "block": None, "inline": None}.get(v, v)
    if k == "background" and "url(" in v: v = None
    return v
def clean(t):
    d = css(t); allow = ALLOW.get(t.name, set()); out = {}
    for k, v in d.items():
        if k not in allow: continue
        v = fix_vals(k, v)
        if v: out[k] = v
    if t.name in TEXT - {"td", "th", "li"} | {"div"} and out.get("display") and t.name != "div": out.pop("display")
    put(t, out)

def run(src, dst):
    name = src.stem
    soup = BeautifulSoup(src.read_text(), "html.parser")
    sec = soup.find("section")
    # 0 plain images: exact pixel boxes from the original layout
    for j, img in enumerate(sec.find_all("img")):
        w, h = SIZES[name]["img"][j]; d = css(img)
        d = {k: v for k, v in d.items() if k in ("align-self",)}; d.update(width=f"{w}px", height=f"{h}px"); d["object-fit"] = "contain"; put(img, d)
        if img["src"].startswith("assets/"): img["src"] = BLOB[img["src"][7:]]
        img["alt"] = img.get("alt") or Path(img["src"]).stem.replace("_", " ") + " diagram"
    # 1 snapped graphics -> images
    for el in sec.select("[data-snap]"):
        d = css(el); w = int(re.sub(r"\D", "", d.get("width", "528")))
        img = soup.new_tag("img", src=BLOB[el["data-snap"] + ".png"], alt=el["data-snap"].replace("_", " ") + " chart")
        h = {"habits": round(w * 1062 / 1720)}.get(el["data-snap"], round(w * 706 / 1056))
        img["style"] = f"width:{w}px;height:{h}px;object-fit:contain"; el.replace_with(img)
    # 2 background-image divs -> pinned img (+ scrim when the box is only a photo)
    k = 0
    for el in sec.find_all("div"):
        d = css(el); m = re.search(r"url\((?:assets/)?([^)]+)\)", d.get("background", ""))
        if not m: continue
        w, h = SIZES[name]["bg"][k]; k += 1
        img = soup.new_tag("img", src=BLOB[m.group(1)], alt="")
        flow = [c for c in el.children if isinstance(c, Tag) and css(c).get("position") != "absolute"]
        if flow:
            d.pop("background"); d["position"] = "relative"; d["overflow"] = "hidden"; put(el, d)
            put(img, {"position": "absolute", "left": "0", "top": "0", "width": f"{w}px", "height": f"{h}px", "object-fit": "cover"})
            el.insert(0, img); continue
        box = {"position": "absolute", "right": "0", "top": "0", "width": f"{w}px", "height": f"{h}px"}
        put(img, dict(box, **({"opacity": d["opacity"]} if "opacity" in d else {}), **{"object-fit": "cover"}))
        scrim = soup.new_tag("div"); put(scrim, dict(box, background="linear-gradient(90deg,#07090C 0%,rgba(7,9,12,0) 55%)"))
        el.replace_with(img); img.insert_after(scrim)
        par = img.parent; pd = css(par)
        if par.name == "div": pd["overflow"] = "hidden"; put(par, pd)
    # 3 table cells: plain text with inline marks only
    for td in sec.find_all(["td", "th"]):
        for dv in td.find_all("div"): dv.unwrap()
    # 4 spans that are boxes become blocks
    for sp in sec.find_all("span"):
        d = css(sp)
        if "display" in d: sp.name = "div"
        elif any(k in d for k in ("background", "padding", "width", "height", "border-radius", "border", "font-size", "letter-spacing", "font-family")):
            if sp.find_parent(list(TEXT)): # inside text: drop size props only
                continue
            sp.name = "p"
    # 5 divs holding inline content become text boxes
    for dv in reversed(sec.find_all("div")):
        kids = [c for c in dv.children if not (isinstance(c, NavigableString) and not c.strip())]
        inl = [c for c in kids if isinstance(c, NavigableString) or c.name in INLINE]
        if not inl: continue
        if len(inl) == len(kids):
            dv.name = "p"; d = css(dv)
            if d.get("display") == "flex" and "height" in d and "justify-content" in d:  # centered badge
                d["text-align"] = "center"; d["line-height"] = d["height"].replace("px", "") + "px"
            for k in ("display", "flex-direction", "align-items", "justify-content", "gap"): d.pop(k, None)
            put(dv, d); continue
        run_ = []
        def flush():
            if not run_: return
            p = soup.new_tag("p"); run_[0].insert_before(p)
            for c in run_: p.append(c.extract())
            run_.clear()
        for c in list(dv.children):
            if isinstance(c, NavigableString) and not c.strip(): continue
            if isinstance(c, NavigableString) or c.name in INLINE: run_.append(c)
            else: flush()
        flush()
    # 6 p inside p -> span
    for p in sec.find_all("p"):
        if p.find_parent("p"): p.name = "span"
    # 7 font-weight etc on container divs -> push to child text
    for dv in sec.find_all("div"):
        d = css(dv)
        for k in ("font-weight", "font-style", "white-space", "text-decoration"):
            if k in d:
                v = d.pop(k)
                for t in dv.find_all(["p", "h1", "h2", "h3"]):
                    td = css(t); td.setdefault(k, v); put(t, td)
        put(dv, d)
    for t in sec.find_all(True):
        if t.name in ("aside",): continue
        clean(t)
        for a in list(t.attrs):
            if a.startswith("data-") and a not in ("data-transition", "data-build-in", "data-text"): del t[a]
    # tabs: keep labels on one line
    for p in sec.find_all("p"):
        d = css(p)
        if "letter-spacing" in d and len(p.get_text()) < 12: d["white-space"] = "nowrap"; put(p, d)
    n = len(sec.find_all(True)) - 1
    dst.write_text(str(sec)); return n
if __name__ == "__main__":
    d = Path(sys.argv[1])
    for f in sorted(d.glob("*.html")):
        print(f.stem, run(f, f))
