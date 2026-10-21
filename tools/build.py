"""Build the site's HTML pages from src/.

    python3 tools/build.py

Each file in src/pages/ is the body of one page. Its first line names the page,
for example <!-- title: About -->, and an optional second line gives the summary
search engines show, <!-- description: ... -->. src/layout.html wraps every page in the shared
<head>, header, and footer, and src/site.json holds the site-wide settings
(announcement bar, navigation, description). The finished pages are written to the
repository root, where GitHub Pages serves them, along with sitemap.xml and
robots.txt for search engines.

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


def organization_json(cfg):
    """Structured data so search engines know who the site belongs to."""
    org = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Utah AI Safety Hub",
        "url": cfg["site_url"] + "/",
        "logo": cfg["site_url"] + "/brand/png/uash-tile-pine-512.png",
        "email": cfg["email"],
        "description": cfg["description"],
        "areaServed": {"@type": "State", "name": "Utah"},
        "address": {"@type": "PostalAddress", "addressLocality": "Salt Lake City", "addressRegion": "UT", "addressCountry": "US"},
    }
    if cfg.get("same_as"):
        org["sameAs"] = cfg["same_as"]
    return '    <script type="application/ld+json">' + json.dumps(org, ensure_ascii=False) + "</script>"


def write_sitemap(cfg, names):
    urls = "".join(
        f"  <url><loc>{cfg['site_url']}/{'' if n == 'index.html' else n}</loc></url>\n" for n in sorted(names, key=lambda n: n != "index.html"))
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {cfg['site_url']}/sitemap.xml\n")


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
        description = cfg["description"]
        second, _, rest = body.partition("\n")
        d = re.fullmatch(r"<!-- description: (.+) -->", second.strip())
        if d:
            description, body = d.group(1), rest

        nav = "\n".join(
            f'                <a href="{{{{root}}}}{item["href"]}"{" aria-current=\"page\"" if item["href"] == fname else ""}>{item["label"]}</a>'
            for item in cfg["nav"])
        values = {
            "full_title": cfg["home_title"] if fname == "index.html" else f"{title} · Utah AI Safety Hub",
            "description": description,
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
            "head_extra": ('\n    <meta name="robots" content="noindex">' if not_found
                           else "\n" + organization_json(cfg) if fname == "index.html" else ""),
        }
        html = fill(fill(layout, values), {"root": values["root"]})
        if not_found:
            # Links inside the announcement bar are relative too.
            html = html.replace('<a href="contact.html', '<a href="/contact.html')
        (ROOT / fname).write_text(html)
    write_sitemap(cfg, [p.name for p in pages if p.name != "404.html"])
    print(f"Built {len(pages)} pages, sitemap.xml, and robots.txt.")


if __name__ == "__main__":
    main()
