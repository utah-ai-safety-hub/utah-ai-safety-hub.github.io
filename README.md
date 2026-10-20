# Utah AI Safety Hub

Website for the Utah AI Safety Hub, a new community on the Wasatch Front for people who want to help advanced AI go well. It runs reading groups, co-working, and events in Salt Lake City and Utah County.

Live at https://utah-ai-safety-hub.github.io

The site is plain HTML and CSS with no build step. GitHub Pages serves it from the `main` branch.

## Editing

You can edit any page in the GitHub web editor (open the file and click the pencil icon).

- **Events:** edit `events.html`. Copy an existing `<div class="event">` block and change the date, title, place, and description. Move finished events under "Past".
- **Sign-up form:** the form on `contact.html` posts to the URL in `FORM_ENDPOINT` at the top of `site.js`. Create a free form at [Formspree](https://formspree.io), then paste its URL there. Until then, the form tells visitors that sign-ups open soon.
- **Shared header and footer:** these are copied into every page, so change all six HTML files when you edit them.
- **Colors and fonts:** these are set at the top of `style.css`.

## Custom domain

When you have a domain such as utahaisafety.org, add a `CNAME` file containing the domain, then point the domain's DNS at GitHub Pages. Also update the `og:url` and canonical links in each page.
