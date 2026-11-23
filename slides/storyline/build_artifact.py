"""Turn a ghost-deck data.js plus the template index.html beside this script into one artifact page.

Usage: python -I build_artifact.py <data.js> <out.html> "<page title>"
The Artifact tool wraps the page in its own <html>/<head>/<body>, so the output carries only
the title, the side-gutter meta, the template's style, the data and the template's script.
"""
import pathlib
import re
import sys

here = pathlib.Path(__file__).parent
data_path, out_path, title = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3]
html = (here / "index.html").read_text(encoding="utf-8")
data = data_path.read_text(encoding="utf-8").replace("</script", "<" + "\\" + "/script")
style = re.search(r"<style>.*?</style>", html, re.S).group(0)
script = re.search(r"<script>\s*\(function\(\)\{.*?</script>", html, re.S).group(0)
out_path.write_text(
    f'<title>{title}</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n'
    + style + '\n<main id="app"></main>\n<script>\n' + data + '\n</script>\n' + script + '\n',
    encoding="utf-8")
print(out_path, len(out_path.read_text(encoding="utf-8")) // 1024, "KB")
