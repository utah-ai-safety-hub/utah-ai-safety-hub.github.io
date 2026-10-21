"""Build the site's HTML pages from src/.

    python3 tools/build.py

Each file in src/pages/ is the body of one page. Its first line names the page,
for example <!-- title: About -->. src/layout.html wraps every page in the shared
<head>, header, and footer, and src/site.json holds the site-wide settings
(announcement bar, navigation, description). The finished pages are written to the
repository root, where GitHub Pages serves them.

Stylesheet and script links get a short content hash (style.css?v=...) so browsers
fetch the new files after each change.
"""
import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"


def version(name):
    return hashlib.sha1((ROOT / name).read_bytes()).hexdigest()[:8]


def fill(template, values):
    def sub(match):
        key = match.group(1)
        if key not in values:
            raise KeyError(f"layout.html uses {{{{{key}}}}} but the build has no value for it")
        return values[key]
    return re.sub(r"\{\{(\w+)\}\}", sub, template)


def main():
    cfg = json.loads((SRC / "site.json").read_text())
    layout = (SRC / "layout.html").read_text()
    css_v, js_v = version("style.css"), version("site.js")

    pages = sorted((SRC / "pages").glob("*.html"))
    for path in pages:
        text = path.read_text()
        first, _, body = text.partition("\n")
        match = re.fullmatch(r"<!-- title: (.+) -->", first.strip())
        if not match:
            raise SystemExit(f"{path.relative_to(ROOT)}: first line must be <!-- title: Page name -->")
        title, fname = match.group(1), path.name
        not_found = fname == "404.html"

        nav = "\n".join(
            f'                <a href="{{{{root}}}}{item["href"]}"{" aria-current=\"page\"" if item["href"] == fname else ""}>{item["label"]}</a>'
            for item in cfg["nav"])
        values = {
            "full_title": "Utah AI Safety Hub" if fname == "index.html" else f"{title} · Utah AI Safety Hub",
            "description": cfg["description"],
            "site_url": cfg["site_url"],
            "url_path": "" if fname == "index.html" else fname,
            "announcement": cfg["announcement"],
            "nav": nav,
            "join_current": ' aria-current="page"' if fname == "contact.html" else "",
            "body": body.rstrip(),
            "css_v": css_v,
            "js_v": js_v,
            # The 404 page is served at any missing URL, so its links must start from the site root.
            "root": "/" if not_found else "",
            "head_extra": '\n    <meta name="robots" content="noindex">' if not_found else "",
        }
        html = fill(fill(layout, values), {"root": values["root"]})
        if not_found:
            # Links inside the announcement bar are relative too.
            html = html.replace('<a href="contact.html', '<a href="/contact.html')
        (ROOT / fname).write_text(html)
    print(f"Built {len(pages)} pages.")


if __name__ == "__main__":
    main()
