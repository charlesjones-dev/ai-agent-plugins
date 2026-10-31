# Crawl Checks

The checks for `/seo-crawl`, split into three passes. Each pass worker reads **Shared setup**, **Host traps** and its own pass. Every check says what to request, what a healthy site returns, and where the fix usually goes. The severities are starting points. The coordinator sets the final severity with the guide in SKILL.md.

## Shared setup

### User agents

Use these exact strings. They hold no personal data.

```bash
UA_GOOGLEBOT_MOBILE='Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
UA_GOOGLEBOT_DESKTOP='Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/130.0.0.0 Safari/537.36'
UA_BROWSER='Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
UA_BINGBOT='Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)'
```

Google indexes the mobile version first, so the Googlebot smartphone fetch is the one that counts most.

### Requests

Shell variables don't carry over between commands in most agents, so set the user agent and folder in each command that uses them. Fetch without `-L`, so each redirect hop shows:

```bash
curl -sS --max-time 20 -A "$UA_GOOGLEBOT_MOBILE" -D "$OUT/pricing.gm.h" -o "$OUT/pricing.gm.html" \
  -w 'pricing.gm %{http_code} %{size_download}B ttfb=%{time_starttransfer}s -> %{redirect_url}\n' \
  "https://example.com/pricing"; sleep 1
```

- **Redirect chain:** add `-L -o /dev/null -w '%{num_redirects} %{url_effective}\n'`.
- **Bytes over the wire:** `curl -sS -o /dev/null -H 'Accept-Encoding: br, gzip' -w '%{size_download}\n' <url>`.
- **Decoded bytes:** `curl -sS --compressed <url> | wc -c`.
- **Same bytes for every user agent:** `shasum -a 256 "$OUT"/pricing.*.html`, or `sha256sum` on Linux.
- Keep a request log (`>> "$OUT/requests.log"`) so the report can count requests.

### Parsing

Run the bundled parser with `python3 -I` and the absolute path the coordinator gave you. It reads saved files and never fetches.

| Command | Prints |
|---------|--------|
| `crawl_facts.py page FILE --url URL` | JSON: title and length, description, canonical, robots meta, hreflang, Open Graph and Twitter tags, icons, headings and skipped levels, landmarks, word count, JavaScript-shell guess, images, internal and external links, render-blocking head resources, JSON-LD errors and types, form fields, mixed content |
| `crawl_facts.py robots FILE --agent Googlebot --agent Bingbot --agent '*' --path /x` | The group each crawler obeys under RFC 9309, allow or disallow for each path with the deciding rule, and warnings for named groups that drop the `*` rules |
| `crawl_facts.py sitemap FILE` | JSON: every `loc` and `lastmod`, hosts, lastmod spread, duplicates, non-HTML entries, size limits |
| `crawl_facts.py image FILE` | Format, pixel size and bytes |

`words` undercounts languages written without spaces, such as Japanese and Chinese. Use `text_chars` for those pages. If `python3` isn't installed, read the saved files directly and say so in the report.

## Host traps

These come up again and again. Check each one that applies before you trust the repo's config.

1. **A config file works only on the host that reads it.**

   | File | Read by |
   |------|---------|
   | `_headers`, `_redirects` | Netlify and Cloudflare Pages |
   | `netlify.toml` | Netlify |
   | `vercel.json` | Vercel |
   | `staticwebapp.config.json` | Azure Static Web Apps |
   | `firebase.json` | Firebase Hosting |
   | `serve.json` | the `serve` package |
   | `.htaccess` | Apache |
   | `nginx.conf`, Caddyfile | only the server that loads it |

   A container that runs a different static server, such as sirv, http-server or a custom Node server, ignores all of them. For every header and redirect the repo sets, look for it in the live response. When it's missing, the fix goes where the running server or the CDN applies it.
2. **Prerendered files can skip the app's middleware.** Some frameworks serve prerendered pages before server middleware runs. Nuxt's Nitro does this, so headers set in `server/middleware` reach only server-rendered pages. Check headers on one prerendered page and one server-rendered page.
3. **A single-page app fallback turns every URL into a 200.** Options such as `--single`, `try_files $uri /index.html` or a `/* /index.html 200` rewrite answer unknown, old and login-only URLs with the empty app shell.
4. **CDN defaults change what's served.** Cloudflare sends `cache-control: max-age=14400` (its 4-hour default browser cache time) when the origin sends no `cache-control`. CDNs can rewrite or replace robots.txt (Cloudflare's managed robots.txt, for example) and can challenge or block crawlers, including AI crawlers, by default. The deployed file is the one that counts.
5. **A spoofed user agent isn't the crawler.** CDNs verify real Googlebot and Bingbot by IP address. A challenge for your spoofed Googlebot string may not reach the real one, and a pass doesn't prove the real one gets through. Search Console's URL Inspection and Bing Webmaster Tools show what the crawler got.
6. **Your own access can be special.** An IP allowlist, VPN or zero-trust bypass can let your requests through to a staging host that the public can't reach. Then a "staging is public" result is inconclusive, not proof.
7. **The repo may not be what's deployed.** Compare something distinctive, such as the JSON-LD, a build hash in an asset name, or a recent copy change, before you blame a file.

## Pass A: Crawl and index

A1. **Same page for every user agent.** Fetch each page on the list with the Googlebot smartphone, Googlebot desktop and browser user agents, then compare the hashes. If they differ, compare again after removing nonces, CSRF tokens, timestamps and request IDs. A different title, body text or link set is cloaking risk (High). A 403, 429, 503 or challenge page for Googlebot only is bot protection. Report it as High with "confirm in Search Console", because real Googlebot may pass.

A2. **Title and content in the served HTML.** For each page meant to rank, run `page` on the Googlebot smartphone copy. Check that the title, meta description, one h1 and the main text are there without JavaScript. `looks_like_js_shell: true`, or a few dozen words on a page that shows hundreds in a browser, means the content arrives only after JavaScript (High for pages meant to rank). Google renders JavaScript later and not always, and most other search and AI crawlers don't run it. The fix is server rendering or prerendering for those routes.

A3. **Status codes and redirects.** Expect one 301 or 308 hop that keeps the path and query string for each of:
- `http://` to `https://`
- `www` to the apex, or the other way, whichever the canonical tags use
- page variants: trailing slash or none (whichever the canonical uses), `/index.html`, `.html`, uppercase letters, a default-language prefix such as `/en/`, and double slashes

Variants that return 200 with the right canonical are Low. Variants whose canonical points at themselves are Medium. A 302 or 307 for a permanent move should be a 301 or 308. Chains longer than one hop are Low. Fetch each redirect from the repo's redirect config and confirm it fires (see Host traps 1). Compare HEAD with GET on two pages. A route that answers HEAD with 404 or 405 is Low, because some link checkers and tools use HEAD.

A4. **Soft 404s.** Fetch two made-up URLs, such as `/zq-not-a-page-<random>` and `/<a real section>/zq-<random>`. Expect 404 or 410. A 200 with the app shell or "not found" text is a soft 404 (Medium). While the server can't return a real 404, the shell and the not-found route both need `noindex`. Also check that 404 pages send no canonical or hreflang links to URLs that don't exist.

A5. **Login and app routes.** Fetch each route from the router signed out, and never log in. Expect a redirect to the login page, a 401 or 403, or a page with `noindex`. A 200 shell with no robots tag or with `index` is Medium. Routes with a token in the path, such as invites, shares, password resets, unsubscribe and magic links, need `noindex` and must stay out of the sitemap. Check that the signed-out HTML of such a page doesn't show a name or email address (Medium, High if the URLs are linked or listed anywhere public).

A6. **Canonical tags.** Each indexable page has exactly one canonical. It's an absolute URL on the canonical scheme and host. It points at the page itself, and it matches the sitemap `loc` and `og:url`. When the app also sets head tags in the browser, read that code. A canonical built from `location.pathname` copies trailing slashes and wrong casing.

A7. **Robots signals.** Read the `<meta name="robots">` and `googlebot` tags and the `X-Robots-Tag` header. When they disagree, Google applies the stricter one, so report the conflict. `noindex` or `none` on a page meant to rank is High.

A8. **hreflang** (multilingual sites). Each language version lists every other version and itself, with an `x-default`. Every target is absolute, returns 200 and is canonical. `<html lang>` matches the page's language.

A9. **Pagination.** `?page=2` and similar pages point their canonical at themselves, not at page 1, and link onward with real `<a href>` links.

A10. **Staging, preview and API hosts.** For each host from Step 2, fetch `/` and `/robots.txt` with the browser user agent. Expect a login wall (401, 403 or a redirect to a login), plus `noindex` or `Disallow: /` as a safety net. A staging host that serves the site with `index` is High when the public can reach it, but read Host traps 6 first. A canonical pointing at production limits the damage. An API host should answer `/` with a 404 or 401, not a page.

## Pass B: Robots, sitemaps and structured data

B1. **robots.txt.** Fetch it on the canonical host. It should return 200 with `text/plain` and be under 500 KiB. A 5xx makes Google pause crawling the site. A 404 means everything is allowed. Run `robots` with `--agent Googlebot`, `--agent Bingbot`, `--agent '*'` and every AI crawler the file names, against every page meant to rank, every login route and `/`. Check for:
- **The named-group trap.** A crawler obeys only the most specific group that names it. A `User-agent: Googlebot` group with `Allow: /` drops every Disallow in the `*` group for Googlebot. The parser warns about this. Fix it by putting several `User-agent:` lines on one group, or by repeating the Disallow lines in each named group (Medium).
- **A Disallow on a page that relies on `noindex`.** Google can't read a `noindex` on a page it may not crawl, and it can still index the URL from links ("Indexed, though blocked by robots.txt"). To keep a page out, allow crawling and send `noindex` (Low).
- **Blocked rendering files.** CSS, JavaScript and image paths that pages need must stay crawlable.
- **The Sitemap line** is an absolute URL on the production host.
- **Unsupported lines,** such as `Noindex:`, `Crawl-delay` and `Host:`. The parser lists them.
- **Drift.** Compare the deployed file with the repo's version, and say which one a CDN changed.

B2. **Sitemaps.** Fetch every sitemap that robots.txt lists, plus `/sitemap.xml`. Each should return 200 with no redirect, or a permanent redirect at most, and parse with `sitemap`. Check that:
- every `loc` is absolute, on the canonical scheme and host, with no duplicates;
- every URL returns 200 with no redirect, sends no `noindex`, and has a canonical equal to its `loc`. Fetch them all up to the page budget, and sample each template type beyond it;
- it lists no login routes, token routes, staging hosts or non-HTML files such as `llms.txt` or JSON;
- every page meant to rank is in it;
- `lastmod` reflects real content changes. One date on every URL is usually the build date, and Google ignores a `lastmod` it can't trust (Low). A date in the future is wrong;
- a hand-written sitemap in the repo isn't shadowed by a generated one, or the other way round.

`changefreq` and `priority` are harmless. Google ignores both.

B3. **Structured data.** For each page, run `page` and read `json_ld`. Check that:
- every block parses and uses `https://schema.org`, with absolute URLs;
- the types fit the page;
- the content matches what a visitor sees. Search the served HTML for each FAQ question, HowTo step, price and breadcrumb name. Markup for content that isn't on the page breaks Google's guidelines (Medium);
- breadcrumbs don't link to the current page twice or to a page that doesn't exist, and pages in other languages point at their own language's URLs;
- the site's Organization is one node referenced by `@id`, not repeated several times per page (Low);
- there's no self-serving review or AggregateRating markup about the site's own business;
- the logo is a raster image at least 112 px wide.

Google stopped showing FAQ rich results on May 7, 2026 and HowTo rich results in September 2023. Valid markup for visible content can stay, but never promise either.

B4. **llms.txt**, if the site has one. It returns 200 as `text/plain`, and its links resolve. Search engines don't use it, so it never belongs in the sitemap. Use `/seo-llms-txt validate` for more.

## Pass C: Page quality and delivery

C1. **Titles and descriptions.** Each page has its own. Keep titles to about 60 characters, counting any " | Brand" suffix the template adds, and descriptions to about 150 to 160. Inner pages that reuse the homepage's title or description are Medium. Over-long ones are Low.

C2. **Headings and landmarks.** One h1 on each page meant to rank, and no skipped levels (an h2 followed by an h4). Footer and menu labels shouldn't be headings. One `<main>` per page holds the page's own content. `main_before_header: true` means it wraps the site header too.

C3. **Images.** Content images have alt text, and `alt=""` is right for decoration. The `width` and `height` attributes match the file's real ratio, which avoids layout shift. Fetch the image and run `image`. A file more than twice as wide as its display size, or a hero image over about 200 KB, is worth resizing or serving as WebP or AVIF. The first large image (the likely LCP image) shouldn't be lazy-loaded.

C4. **Social cards.** `og:title`, `og:description`, `og:image`, `og:url` (equal to the canonical) and `og:type`, plus `twitter:card`. The `og:image` is absolute, returns 200 as an image, and is about 1200×630. Open the card for each language or script the site uses, if you can view images. Generated cards can lack a font for Cyrillic, Chinese, Japanese or Korean and show empty boxes (Medium).

C5. **Icons and manifest.** A favicon, a 180×180 `apple-touch-icon`, and manifest icons whose real sizes match their declared sizes, with at least one icon marked `"purpose": "any"`.

C6. **Weight on the critical path.** On each main template, list the render-blocking stylesheets and synchronous head scripts from `page`. Measure each one's compressed and decoded size. A blocking stylesheet over about 50 KB compressed, or script that loads on every page at over about 150 KB compressed, is worth tracing. Find what's inside it, such as a full icon or flag set, every language's content, or a Markdown or syntax-highlighting engine. Then find which import pulls it in. These sizes are rough guides, not Google thresholds.

C7. **Compression and caching.** HTML, CSS and JavaScript come with `content-encoding: br` or `gzip`. Hashed assets (`/assets/*-<hash>.js`, `/_next/static/`, `/_nuxt/`) send `cache-control: public, max-age=31536000, immutable`. HTML has a short cache time or revalidates. See Host traps 4 for Cloudflare's default.

C8. **Fonts.** Count the font files that load for the first render. Preload the main text and heading fonts, and use `font-display: swap` or `optional`. Drop the weights the site doesn't use.

C9. **Core Web Vitals.** Unless `psi=no`, call the PageSpeed Insights API once for each of up to three main templates, with the mobile strategy:

```bash
curl -sS --max-time 90 "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?strategy=mobile&url=<url-encoded page URL>" -o "$OUT/psi-home.json"
```

Report the field data (`loadingExperience`, from real Chrome users) when Google has it, and the lab LCP, CLS and TBT. Without an API key the quota is small, and a 429 is common. Then say so, and tell the user to run https://pagespeed.web.dev for those pages. Never estimate a Core Web Vitals number. Label risks you inferred from sizes as inferred.

C10. **Mobile.** The viewport is `width=device-width, initial-scale=1`, with no `maximum-scale=1` or `user-scalable=no`. When a page has form fields, read the CSS that styles inputs, selects and textareas, including design tokens and mobile media queries. A font size under 16px makes iOS Safari zoom in when the field gets focus (Low). Tap targets should be about 48 px with space between them.

C11. **Security headers.** On HTML responses, check for:
- `Strict-Transport-Security` with `max-age` of at least one year;
- `X-Content-Type-Options: nosniff`;
- `X-Frame-Options`, or CSP `frame-ancestors`;
- `Referrer-Policy`;
- any `Content-Security-Policy` and `Permissions-Policy` the repo means to send.

Check one prerendered page and one server-rendered page (Host traps 2). Headers the repo sets but the response lacks are Medium, because the fix the repo intends never took effect. Recommend `includeSubDomains` only when every subdomain serves HTTPS. Recommend `preload` only when the user asks for it, because the preload list covers every subdomain and leaving it takes months.

C12. **Mixed content and links.** Pages load no `http://` resources. Fetch every unique internal link from the pages on the list. Each should return 200 directly. Public pages shouldn't link to login-only pages or to URLs that redirect. Fetch each unique external link once at the same polite rate. Point links that redirect at their final URL, and fix links that fail. Every `target="_blank"` link has `rel="noopener"` or `rel="noreferrer"`.

C13. **Files that shouldn't be public.** Fetch only the paths that the repo's public folder contains. Never guess at paths. Config files that the host ignores, such as `/_headers` or `/serve.json`, and stale copies of generated files are Low, but they mislead the next person who reads the repo.

## Where fixes go

Name the exact place in the findings table:

- **A repo file and line:** code, config, content or a build script.
- **A host or CDN setting:** the provider, the menu path, the rule type, the match expression and the value. For example, a redirect rule at the CDN for `/signup` that keeps the query string.
- **A platform setting,** for a site built on a hosted platform. Look for the indexing switch first:
  - WordPress: Settings > Reading > "Discourage search engines from indexing this site", and the SEO plugin's settings.
  - Shopify: the store password page, which blocks indexing, and the `robots.txt.liquid` template.
  - Webflow: Site settings > SEO, which controls indexing of the `webflow.io` subdomain.
  - Wix and Squarespace: the SEO and site visibility settings.
- **An environment variable or secret,** such as a flag that marks staging as not indexable.
- **Project docs,** when the README, CLAUDE.md or a knowledge base states a wrong fact about the hosting or SEO setup. The next agent will trust it.
