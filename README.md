# Utah AI Safety Hub

Website for the Utah AI Safety Hub, a community for people across Utah who want advanced AI to go well.

Live at https://utahaisafety.org

## How the site is built

The pages are plain HTML and CSS. Each page's content lives in `src/`, and `tools/build.py` wraps it in the shared header and footer to produce the HTML files in the repository root. A GitHub Action ([`.github/workflows/build.yml`](.github/workflows/build.yml)) runs the build and publishes the site on every push to `main`, so changes go live about a minute after you save them.

| To change | Edit |
|---|---|
| A page's content | `src/pages/<page>.html` (the first line is the page's title) |
| The announcement bar, navigation, or site description | `src/site.json` |
| The header, footer, or `<head>` on every page | `src/layout.html` |
| Colors, fonts, and layout | `style.css` |
| Interactive behavior (theme toggle, contour readout) | `site.js` |

Don't edit the HTML files in the repository root; the next build overwrites them.

### Editing in the browser

Open a file in `src/` on GitHub, click the pencil icon, make the change, and commit. The Action rebuilds and publishes the site. Watch progress under the repository's **Actions** tab.

- **Events:** in `src/pages/events.html`, copy an existing `<div class="event">` block and change the date, title, place, and description. Move finished events under "Past".
- **Announcement bar:** change `announcement` in `src/site.json`.

### Building locally

```sh
python3 tools/build.py            # rebuild the pages (no dependencies)
python3 -m http.server            # preview at http://localhost:8000
```

## Images and logo

These are generated once and committed; rerun the scripts only to change them. They need `pip install -r tools/requirements.txt`. Downloaded elevation tiles and fonts are cached in `tools/.cache/` (not committed).

| Script | Produces |
|---|---|
| `tools/hero_contours.py` | `images/contours-timpanogos.svg` (home page contours) and `images/timpanogos-elevation.bin` (the live elevation readout) |
| `tools/logo.py` | `brand/svg/` (the logo kit) |
| `tools/logo_png.sh` | `brand/png/`, `favicon.ico`, `favicon.svg`, `apple-touch-icon.png` (needs Google Chrome) |

The contours and logo come from real elevation data for Mount Timpanogos: [AWS Terrain Tiles](https://registry.opendata.aws/terrain-tiles/), built mainly from USGS 3DEP data. The logo kit and its usage notes are in [`brand/`](brand/README.md).

## Sign-up form

The Join page (`src/pages/contact.html`) embeds an Airtable form. Submissions land in the **Sign-ups** table of the hub's Airtable base. To change the questions, edit the form in Airtable; the website picks up the change automatically.

## Custom domain

The site uses the custom domain utahaisafety.org, registered and managed in Cloudflare (DNS only, not proxied). GitHub Pages issues the HTTPS certificate. The domain is verified for the utah-ai-safety-hub organization under Settings → Pages.
