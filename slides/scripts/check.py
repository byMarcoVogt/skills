"""Render slides at 1920x1080 and measure them against the design system's tokens.

  python check.py --tokens <tokens.json> <deck project folder | slide.html | preview.html> ...
      [--report report.json] [--shots <folder>]

A deck project folder is what a Claude Slides artifact holds under project/ (deck.json + slides/).
Prints one line per error and "PASS"/"FAIL" per slide; exit code 1 when any slide fails.
Needs Python and a Chromium. Playwright's headless shell is found by itself on Windows, macOS and Linux; or set CHROME.
"""
import argparse, html, json, os, pathlib, re, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
FONTS_URL = ("https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400..700"
             "&family=Inter:wght@400..700&display=swap")
CACHE = pathlib.Path(os.environ.get("LOCALAPPDATA", pathlib.Path.home() / ".cache")) / "slides-check" / "fonts"


def fonts_css():
    """The design system's web fonts, fetched once into a local cache, so a run never waits on the network."""
    css_file = CACHE / "fonts.css"
    if not css_file.exists():
        import urllib.request
        CACHE.mkdir(parents=True, exist_ok=True)
        ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
        css = urllib.request.urlopen(urllib.request.Request(FONTS_URL, headers=ua), timeout=30).read().decode()
        for i, url in enumerate(sorted(set(re.findall(r"url\((https://[^)]+)\)", css)))):
            local = CACHE / f"f{i}.woff2"
            local.write_bytes(urllib.request.urlopen(urllib.request.Request(url, headers=ua), timeout=60).read())
            css = css.replace(url, local.as_uri())
        css_file.write_text(css, encoding="utf-8")
    return "<style>" + css_file.read_text(encoding="utf-8") + "</style>"


# What the Slides viewer does that a plain browser does not: its base rules and its own elements.
SLIDES_BASE = ("section *{box-sizing:border-box}section h1,section h2,section h3,section h4,section p{margin:0}"
               "section aside{display:none}x-icon{display:inline-block;flex:none}x-shape{display:block}"
               "x-shape[kind=diamond]{clip-path:polygon(50% 0,100% 50%,50% 100%,0 50%)}"
               "x-shape[kind=ellipse]{border-radius:50%}x-shape[kind=rounded]{border-radius:16px}"
               "x-shape[kind=arrow-right]{clip-path:polygon(0 30%,60% 30%,60% 0,100% 50%,60% 100%,60% 70%,0 70%)}"
               "x-shape[kind=arrow-left]{clip-path:polygon(100% 30%,40% 30%,40% 0,0 50%,40% 100%,40% 70%,100% 70%)}")


def find_chrome():
    if os.environ.get("CHROME"):
        return os.environ["CHROME"]
    home = pathlib.Path.home()
    bases = [pathlib.Path(p) for p in (os.environ.get("PLAYWRIGHT_BROWSERS_PATH"),) if p]
    bases += [pathlib.Path(os.environ.get("LOCALAPPDATA", home / "AppData/Local")) / "ms-playwright",
              home / "Library/Caches/ms-playwright", home / ".cache/ms-playwright"]  # Windows, macOS, Linux
    names = ("chrome-headless-shell.exe", "chrome-headless-shell", "headless_shell", "chrome.exe", "chrome", "Chromium")
    hits = [h for base in bases for pat in ("chromium_headless_shell-*", "chromium-*")
            for d in sorted(base.glob(pat), reverse=True) for h in sorted(d.rglob("*")) if h.name in names and h.is_file()]
    if not hits:
        sys.exit("No Chromium found. Install one with: pip install playwright && python -m playwright install "
                 "chromium-headless-shell, or set CHROME to a Chrome or Chromium binary.")
    return str(hits[0])


def px(v):
    return float(str(v).replace("px", "").replace("%", ""))


def rules(tokens_path):
    t = json.loads(pathlib.Path(tokens_path).read_text(encoding="utf-8"))
    sp = {x["name"]: x["value"] for x in t.get("spacing", {}).get("tokens", [])}
    col = {x["name"]: (x["value"]["light"] if isinstance(x["value"], dict) else x["value"]) for x in t["color"]["tokens"]}
    sizes = [px(s["fontSize"]) for g in t["type"]["groups"] for s in g["styles"]]
    missing = [k for k in ("margin-top", "margin-side", "margin-bottom", "footer-rule", "title-line-max") if k not in sp]
    if missing:
        sys.exit(f"tokens.json lacks {', '.join(missing)}; the check takes every position from the tokens.")
    fam = t["type"].get("families", {})
    css = ":root{" + "".join(f"--{k}:{v};" for k, v in col.items()) + "".join(f"--{k}:{v};" for k, v in sp.items()) +         "".join(f"--{x['name']}:{x['value']};" for x in t.get("radius", {}).get("tokens", [])) +         "".join(f"--font-{k}:{v};" for k, v in fam.items()) + "}"
    h2rgb = lambda h: "rgb(%d, %d, %d)" % tuple(int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    return {"width": 1920, "height": 1080, "marginTop": px(sp["margin-top"]), "marginSide": px(sp["margin-side"]),
            "marginBottom": px(sp["margin-bottom"]), "footerRule": px(sp["footer-rule"]),
            "titleLineMax": px(sp["title-line-max"]) / 100, "titleMaxLines": 2, "minFont": min(sizes),
            "muted": h2rgb(col["muted"]), "surface": h2rgb(col["surface"]), "annotationTolerance": 2}, css


def slides_of(target):
    """(name, slide file, extra head) for each slide: a deck's slides in order with its deck.css and faces, or one file."""
    p = pathlib.Path(target)
    if p.is_dir():
        proj = p / "project" if (p / "project" / "deck.json").exists() else p
        deck = json.loads((proj / "deck.json").read_text(encoding="utf-8"))
        head = ""
        if (proj / "deck.css").exists():
            head += "<style>" + (proj / "deck.css").read_text(encoding="utf-8") + "</style>"
        for face in deck.get("faces", {}).values():
            if face.get("href") and face.get("family") not in ("Inter", "Newsreader"):
                head += f'<link rel="stylesheet" href="{html.escape(face["href"])}">'
        order = deck.get("order", [])
        rest = [f.stem for f in sorted((proj / "slides").glob("*.html")) if f.stem not in order]
        return [(sid, proj / "slides" / f"{sid}.html", head) for sid in order + rest]
    return [(p.parent.name if p.name == "preview.html" else p.stem, p, "")]


def page(slide_html, rl, check_js, css="", head=""):
    body = re.sub(r"^\s*<!--.*?-->", "", slide_html, count=1, flags=re.S)
    # the same fonts come from the local cache; a slide's own Google Fonts link would only wait on the network
    body = re.sub(r"<link[^>]+fonts\.googleapis\.com[^>]*>", "", body)
    return ("<!doctype html><html data-theme=\"light\"><head><meta charset=\"utf-8\">" + fonts_css() +
            head + "<style>" + css + "html,body{margin:0;background:#fff}section{position:relative;width:1920px;height:1080px;box-sizing:border-box}</style>"
            "<style>" + SLIDES_BASE + "</style></head><body>" + body +
            # Slides places a pinned element relative to the div it is in, even a static one; copy that.
            "<script>document.querySelectorAll('section div').forEach(function(d){if(getComputedStyle(d).position==='static')d.style.position='relative'})</script>" +
            "<script>window.__RULES=" + json.dumps(rl) +
            ";function __go(){var f=document.fonts;window.__FONTS=[f.check('52px Newsreader'),f.check('24px Inter')];" + check_js + "}" +
            "window.addEventListener('load',function(){Promise.race([document.fonts.ready,new Promise(function(r){setTimeout(r,3000)})]).then(__go)});</script></body></html>")


def run(chrome, rl, css, name, path, head, shots):
    check_js = (HERE / "check.js").read_text(encoding="utf-8")
    tmp = pathlib.Path(tempfile.gettempdir()) / f"slidecheck-{re.sub(r'[^A-Za-z0-9_-]', '_', name)}.html"
    tmp.write_text(page(path.read_text(encoding="utf-8"), rl, check_js, css, head), encoding="utf-8")
    flags = [chrome, "--headless", "--disable-gpu", "--hide-scrollbars", "--window-size=1920,1080", "--virtual-time-budget=8000"]
    dom = subprocess.run(flags + ["--dump-dom", tmp.as_uri()], capture_output=True, text=True, encoding="utf-8", timeout=120).stdout
    m = re.search(r'<pre id="__check"[^>]*>(.*?)</pre>', dom, re.S)
    if shots:
        pathlib.Path(shots).mkdir(parents=True, exist_ok=True)
        clean = tmp.with_name(tmp.stem + "-shot.html")
        clean.write_text(page(path.read_text(encoding="utf-8"), rl, "", css, head), encoding="utf-8")
        subprocess.run(flags + [f"--screenshot={pathlib.Path(shots).resolve() / (name + '.png')}", clean.as_uri()], capture_output=True, timeout=120)
    if not m:
        return {"slide": name, "file": str(path), "errors": [{"code": "NOT_MEASURED", "element": "", "detail": "the page did not report; nothing was checked"}]}
    res = json.loads(html.unescape(m.group(1)))
    return {"slide": name, "file": str(path), **res}


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("targets", nargs="+")
    ap.add_argument("--tokens", required=True)
    ap.add_argument("--report")
    ap.add_argument("--shots")
    a = ap.parse_args()
    (rl, css), chrome = rules(a.tokens), find_chrome()
    results = [run(chrome, rl, css, n, p, h, a.shots) for t in a.targets for n, p, h in slides_of(t)]
    for r in results:
        print(("PASS " if not r["errors"] else "FAIL ") + r["slide"])
        for e in r["errors"]:
            print(f"  {e['code']}: {e['element']} - {e['detail']}")
    if a.report:
        pathlib.Path(a.report).write_text(json.dumps({"rules": rl, "slides": results}, ensure_ascii=False, indent=1), encoding="utf-8")
    failed = sum(1 for r in results if r["errors"])
    print(f"{len(results) - failed} of {len(results)} slides pass")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
