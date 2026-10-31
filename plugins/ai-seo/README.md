# AI-SEO Plugin

**Audits a site's code for search rankings, direct answers and citations in AI answers, crawls the live site to check what search engines get, and fixes what it finds, in Claude Code, Codex and Cursor.** It catches the outdated SEO patterns LLMs still generate, checks that each page answers its question in a form an engine can lift, and checks whether AI answer engines can reach, trust and cite the site.

---

## What This Plugin Does

The plugin looks at a site through three lenses. `/seo-audit` runs any of them, or all three in one report with a separate score for each.

| | SEO | AEO | GEO |
|---|-----|-----|-----|
| **Goal** | Rank in the organic results | Be the single direct answer | Be cited or mentioned inside multi-source AI answers |
| **Surfaces** | Search results pages | Featured snippets, voice replies, answer boxes, "People also ask" | ChatGPT, Perplexity, Claude, Gemini, Copilot, AI Overviews, AI Mode |
| **Main tactics** | Crawlability, meta tags, performance, links | FAQ sections, clean schema, concise definitions, answer-first paragraphs, question headings | Topical authority, original research, expert perspectives, third-party validation |
| **Score** | Search Health | Answer Readiness | Citation Readiness |

**SEO** checks the basics search engines rank on, and removes what LLMs still add from old training data, such as the keywords meta tag and IE-era markup.

**Answer Engine Optimization (AEO)** structures content so an engine can lift one passage as the direct answer to a question: a featured snippet, a voice assistant reply, a direct answer box, or a question-and-answer pair an assistant quotes word for word. The usual tactics are FAQ sections, clean schema markup, concise definitions, answer-first paragraphs and clear question headings.

**Generative Engine Optimization (GEO)** makes a site worth citing, synthesizing and mentioning inside AI answers that draw on many sources. The levers are deep topical authority, original research, expert perspectives and validation from other sites, on top of letting the right crawlers in. The term comes from [Aggarwal et al. (KDD 2024)](https://arxiv.org/abs/2311.09735): in their benchmark, adding quotations, statistics and citations to sources raised a page's visibility in generative engine answers the most, and keyword stuffing did worse than nothing. Later academic work found AI search leans heavily on third-party coverage and favors newer content.

What the engines themselves say:

- **Google** says optimizing for its AI features "is still SEO": no special markup, files, Markdown or chunking, and inauthentic mentions don't help. It picks featured snippets itself; no markup makes a page one. Content people find unique and useful matters most.
- **Microsoft** (Bing and Copilot) is more specific: direct questions with clear answers, one- to two-sentence responses, self-contained sentences, lists and tables, important answers that aren't hidden in tabs or expandable menus, and schema markup.

No AI provider publishes how it picks answers or citations, so the AEO and GEO lenses treat their checks as things that raise the odds, prefer changes that also help readers, and mark heuristics with 🧪.

`/seo-crawl` covers what the code can't show. A site can be live and still not be findable: the served HTML can be an empty shell, unknown URLs can return 200, robots.txt can mean something other than what its author meant, and headers or redirects in the repo may never reach production. The crawl fetches the deployed site the way search engines do, traces each problem to the file or host setting behind it, and says whether fixing it is worth the effort.

---

## Moving from ai-aeo and ai-geo

ai-aeo and ai-geo merged into ai-seo in version 2.0.0 (October 2026). Their audits are now lenses of `/seo-audit`, their fix skills are part of `/seo-fix`, and their other skills were renamed:

| Old command | New command |
|-------------|-------------|
| `/aeo-audit` | `/seo-audit aeo` |
| `/geo-audit` | `/seo-audit geo` |
| `/aeo-fix` | `/seo-fix` |
| `/geo-fix` | `/seo-fix` |
| `/aeo-faq` | `/seo-faq` |
| `/aeo-questions` | `/seo-questions` |
| `/geo-llms-txt` | `/seo-llms-txt` |

Claude Code users run `/plugin install ai-seo@ai-agent-plugins` once. The marketplace points the old names at ai-seo, so an existing ai-aeo or ai-geo install's setting switches over by itself. In Codex and Cursor, add ai-seo and remove ai-aeo and ai-geo.

New audits go to `docs/seo-audit/`. Reports already in `docs/aeo-audit/` and `docs/geo-audit/` stay where they are: `/seo-fix` can still apply them, the trend arrows in a new audit compare against them, and `/seo-audit`, `/seo-faq` and `/seo-questions` still read a question map there. Each lens keeps the categories and weights it had, so scores stay comparable.

---

## Available Skills

| Command | Purpose |
|---------|---------|
| `/seo-audit [seo\|aeo\|geo\|all]` | Audit the site through one or more lenses and write a timestamped report with a score per lens. Optional live URL check and web search for brand mentions. |
| `/seo-crawl [URL]` | Crawl the live site as Googlebot and a browser, read-only, and report what search engines get, where each fix goes, and whether the fixes are worth it. Works with or without the site's repo. |
| `/seo-fix` | Apply fixes from the newest audit, whatever lenses it covers, with a diff for each change. Supports `--dry-run`. |
| `/seo-schema` | Generate and validate JSON-LD structured data, including Organization and Person with `sameAs` and FAQPage or QAPage. |
| `/seo-faq` | Build, update or validate visible FAQ sections and, if you want it, their FAQPage or QAPage markup. Supports `--dry-run`. |
| `/seo-questions` | Map the questions the site should answer to the page that answers each one, and find gaps and competing pages. |
| `/seo-llms-txt` | Generate, update or validate `llms.txt` and `llms-full.txt`. Supports `--dry-run`. |

All seven run only when you call them. Each asks for what its arguments leave out, and runs with documented defaults when no one is there to answer.

### `/seo-audit`

```
/seo-audit                                              # asks for everything
/seo-audit aeo                                          # one lens
/seo-audit all . https://example.com search=no commit=yes   # asks nothing
/seo-audit geo https://example.com search=yes brand="Example Co"
```

**Settings**, each answerable by an argument:

- **Lenses:** `seo`, `aeo`, `geo`, `all`, or two joined by a comma (`aeo,geo`). With none given, it asks, with "All" first.
- **Scope:** a path, or `.` for the entire solution.
- **Version control:** `commit=yes` keeps reports in git; `commit=no` adds `docs/seo-audit/` to `.gitignore`.
- **Live check** (AEO and GEO): a production URL turns it on; `live=no` skips it. It fetches up to ten pages with a normal browser user agent and reports the robots directives actually served, whether answers and content are in the HTML before any script runs, and whether FAQ markup matches the page. For GEO it also compares the deployed robots.txt with the repo and tests how the site responds to AI user agents. Run it only against sites you own or are authorized to test.
- **Web search** (GEO): `search=yes` takes a dated snapshot of third-party mentions and reviews of the brand and notes descriptions that don't match the site. It isn't scored, because results change from run to run. `brand=`, `topics=` and `people=` set the search terms; otherwise they're pre-filled from the site.

An unattended run audits all three lenses across the whole repository, leaves `.gitignore` alone, and skips the live check and web search unless the arguments ask for them.

The skill detects your framework, checks whether Context7 MCP is available, reads the latest question map for the AEO lens, runs each lens's categories, and writes one report. With all three lenses, the report has a section and a score for each lens, a shared action plan and no combined score. A problem two lenses share is written out once and counted in both.

**SEO lens:**

| Category | Weight | What it checks |
|----------|--------|----------------|
| Deprecated Patterns | 20% | Keywords meta, X-UA-Compatible, IE comments, XHTML style, `<b>`/`<i>` misuse, mobile subdomains, `target="_blank"` without `rel="noopener noreferrer"` |
| Modern Meta Tags | 15% | `<title>`, description, canonical, Open Graph, Twitter Card, viewport, charset, `lang`, favicon, robots.txt, sitemap.xml |
| Semantic HTML | 10% | `<header>`, `<nav>`, `<main>`, single `<h1>`, heading hierarchy |
| Structured Data | 15% | JSON-LD presence, valid `@context`, correct types, required properties |
| Performance Signals | 15% | Image dimensions, `loading="lazy"`, `decoding="async"`, WebP/AVIF, preconnect, preload, `async`/`defer` scripts, `font-display` |
| Accessibility (SEO overlap) | 10% | Alt text, generic link text, form labels, skip link |
| URL Structure | 5% | Clean URLs, trailing slash, HTTPS, redirect patterns |
| Security Headers | 5% | HSTS, CSP, X-Content-Type-Options, Referrer-Policy |
| Framework Best Practices | 5% | Next.js Metadata API, Nuxt `useSeoMeta`, TanStack Start `<HeadContent />`, Astro `<SEO>` (from the third-party `astro-seo` package), SvelteKit `<svelte:head>`, Remix `meta` export |

**AEO lens:**

| Category | Weight | What it checks |
|----------|--------|----------------|
| Answer-First Formatting | 20% | The first sentence under each question answers it; no preambles; summaries on long pages; answers that stand alone |
| Question Coverage & Headings | 15% | Natural question headings, clean hierarchy, follow-up questions, coverage of the question map |
| Concise Definitions | 10% | "X is a Y that Z" openings on concept pages, glossaries, consistent definitions |
| Snippet-Ready Structure | 15% | Real `<ol>`, `<ul>` and `<table>`; answers as text, not images or PDFs; answers in the initial HTML and main answers visible |
| Snippet Eligibility & Indexing Controls | 15% | `noindex`, `nosnippet`, `max-snippet`, `data-nosnippet`, Bing `nocache` / `noarchive`, `X-Robots-Tag` in config and middleware, canonicals |
| FAQ Sections & Structured Data | 10% | Visible FAQ sections, markup that matches them, QAPage vs FAQPage, JSON-LD validity |
| Voice & Assistant Readiness | 5% | Answers that read well aloud, `LocalBusiness` data, assistant crawlers not blocked |
| Answer Trust Signals | 5% | Dates on answers that change, sources on health, finance and legal answers, no contradictions between pages |
| Technical Answer Accessibility | 5% | Server rendering, status codes, mobile viewport |

**GEO lens:**

| Category | Weight | What it checks |
|----------|--------|----------------|
| AI Crawler Access | 15% | robots.txt rules for training crawlers, AI search indexers and user-triggered fetchers; Googlebot, Bingbot and Applebot; `Content-Signal` lines; retired bot names; middleware that treats bots differently |
| Technical AI Accessibility | 10% | Server-rendered or static content, content in the initial HTML, status codes, HTTPS, no cloaking |
| Topical Authority | 15% | Core topics, pages per topic, hub pages, internal links, orphan and thin pages |
| Original Research & Evidence | 15% | First-party data, methodology, statistics with linked sources, named quotations, primary sources, unsupported superlatives |
| Expert Perspectives & Authorship | 10% | Bylines, author pages, `Person` markup, reviewers on health, finance and legal topics, editorial pages |
| External Validation | 10% | Links to review profiles and press coverage, attributed testimonials, review markup that follows policy |
| Entity Clarity | 10% | `Organization` markup with `sameAs`, About page definition, consistent naming |
| Extractable Passages | 5% | Paragraphs that stand on their own, one idea per section, no walls of text |
| Content Freshness | 5% | Visible "last updated" dates, `dateModified`, stale time-sensitive pages |
| llms.txt & Markdown Access 🧪 | 5% | `llms.txt` format and discovery hints, Markdown copies matching the HTML |

Findings are rated Critical, High, Medium or Low, with 🧪 on heuristics and proposals. Each one has an ID (`SEO-1`, `AEO-1`, `GEO-1`), a file and line (or a live-check URL), the current code and a specific fix.

**Example terminal summary:**

```
SEO Audit Complete
==================
Project:      example-site
Framework:    Next.js 15.2
Knowledge:    Context7 MCP
Lenses:       SEO, AEO, GEO
Live check:   https://example.com
Web search:   not run
Question map: docs/seo-audit/question-map-latest.md (2026-10-04)

Scores (each lens on its own, not combined):
  SEO  Search Health:       84/100 (C)  📈 vs previous (78)
  AEO  Answer Readiness:    71/100 (D)  ➡️ vs previous (70)
  GEO  Citation Readiness:  62/100 (F)  first run

Critical: 3  High: 9  Medium: 14  Low: 6  Experimental 🧪: 4

Top 3 Critical Issues:
  1. SEO-1 Deprecated keywords meta tag         (app/layout.tsx:12)
  2. AEO-1 FAQ answers rendered only on click   (components/Faq.tsx:31)
  3. GEO-1 OAI-SearchBot blocked in robots.txt  (public/robots.txt:8)

Full report: docs/seo-audit/seo-audit-all-2026-10-11-143022.md
Index:       docs/seo-audit/README.md
Latest:      docs/seo-audit/latest.md
```

### `/seo-crawl`

```
/seo-crawl                                  # finds the production URL in the repo, or asks
/seo-crawl https://example.com
/seo-crawl https://example.com pages=80 staging=https://staging.example.com save=yes
```

`/seo-audit` reads the code. `/seo-crawl` asks the deployed site, with curl only, what a crawler gets. It works on any kind of site: static, single-page app, server-rendered, or a hosted platform such as WordPress or Shopify. With the repo in the working directory it ties each finding to a file and line. Without one it names the host or platform setting instead.

1. **Maps the site.** It works out the framework, the rendering mode for each group of routes, the hosting chain (origin, proxy, CDN), the pages meant to rank and the routes behind login. It also checks which of the repo's header and redirect files the running host reads. `_headers`, `_redirects`, `vercel.json` and `serve.json` each work only on their own host.
2. **Runs three passes,** as parallel subagents when the agent supports them, or one after another:
   - **Crawl and index:** the same HTML for the Googlebot smartphone, Googlebot desktop and browser user agents, the title and content present without JavaScript, status codes, redirects and URL variants, soft 404s, login and token routes, canonical and robots signals, hreflang, and staging and API hosts.
   - **Robots, sitemaps and structured data:** robots.txt parsed under RFC 9309, including a named group such as `User-agent: Googlebot` that silently drops every `*` rule, every sitemap URL fetched and checked against its canonical, and JSON-LD that parses and matches the visible page.
   - **Page quality and delivery:** titles, descriptions, headings, images, social cards, icons, the compressed and decoded size of render-blocking files, caching, fonts, PageSpeed Insights data, mobile input sizes, security headers on static and server-rendered pages, and links.
3. **Re-checks** every high and medium finding itself before it reports, and rules out the usual false alarms: a challenge only for the spoofed user agent, an IP allowlist that lets your own requests into staging, and a repo that differs from what's deployed.
4. **Reports** the Googlebot check, a findings table with the evidence (the command and its output) and where each fix goes, what already looks good, a `yes`, `partly` or `no` verdict, and follow-ups such as Search Console checks.
5. **Offers the fixes.** Nothing changes until you pick them. Repo changes come with diffs and the project's own build, lint and tests. Host and CDN changes come as exact steps, made through the provider's API only when you ask and supply access.

The crawl sends only GET and HEAD requests, one at a time at about one per second, with no logins, scanners or guessed paths, and stays under about 600 requests. Run it only against sites you own or are authorized to test. It bundles `crawl_facts.py`, a standard-library Python parser for the saved robots.txt, HTML, sitemap and image files. With `save=yes` the report goes to `docs/seo-audit/`, and the next saved crawl lists what was fixed, what is still open and what is new.

### `/seo-fix`

```
/seo-fix                     # apply fixes from the newest report
/seo-fix --dry-run           # show every would-be diff, write nothing
/seo-fix docs/geo-audit/latest.md   # fix a specific report
```

Reads the newest report in `docs/seo-audit/` (or an older one in `docs/aeo-audit/` or `docs/geo-audit/`) and fixes every lens it covers. Findings are sorted into:

- **Safe fixes**, confirmed once as a batch. SEO: removing keywords meta, X-UA-Compatible and IE comments; adding `rel="noopener noreferrer"`, image `loading`/`decoding`, `async`/`defer`, and missing `lang`, charset and viewport; fixing XHTML void elements and `<b>`/`<i>` emphasis. AEO: div lists to `<ol>`/`<ul>`, removing markup for questions that aren't on the page. GEO: `dateModified` from git history and llms.txt discovery hints. All lenses: JSON-LD validity and microdata to JSON-LD, done once.
- **Fixes that need your intent:** every `noindex`, `nosnippet`, `max-snippet`, `data-nosnippet`, `nocache` or `noarchive` on answer pages (keep, remove or narrow); three separate questions about AI training crawlers, AI search indexers and user-triggered fetchers before robots.txt changes; retired bot names, `Content-Signal` lines, repeated FAQ markup, and whether to add FAQPage markup at all.
- **Fixes that need your content**, confirmed one by one: meta descriptions, titles and Open Graph copy; answer-first rewrites drawn from the page's own text, question headings and definitional openings; `Organization` and `Person` markup with the profile URLs you supply, author pages, sources for unsourced statistics, links to press coverage. It never invents any of them.
- **Larger refactors:** semantic HTML, heading hierarchy, accordions that load answers on click, client-only pages, topic hub pages and internal links, and pages that compete for the same question.
- **Manual steps** it prints but doesn't automate: third-party profiles, review platforms and directories, CDN bot settings, and tracking citations.

It also offers to create a missing robots.txt and a framework-idiomatic sitemap. An unattended run behaves like `--dry-run`, since every fix needs at least one confirmation.

### `/seo-schema`

```
/seo-schema                                # asks for the target
/seo-schema src/routes/blog/$slug.tsx      # one route
```

Produces Schema.org JSON-LD for detected content types and validates existing blocks. It owns the plugin's JSON-LD rules, which `/seo-fix` and `/seo-faq` follow too.

- **Types:** `Article` / `BlogPosting` (with `Person` author and `Organization` publisher), `Product` (with `Offer` and `AggregateRating`), `Organization` and `Person` with `sameAs` links you supply, `LocalBusiness`, `FAQPage` and `QAPage` for visible Q&A, `BreadcrumbList`, `Event`, `Recipe`, `VideoObject`, `Course`, `JobPosting`, and composite `@graph` structures.
- **Checks:** `https://` context, valid types, required properties, ISO 8601 dates, absolute URLs, typed nested entities, markup that matches visible content, FAQPage vs QAPage, and no self-serving review markup.
- **Output:** the JSON-LD, the code to inject it in your framework, and a list of placeholders to fill. It writes only after you confirm.

It doesn't promise rich results that no longer exist: Google dropped FAQ rich results in May 2026 and HowTo rich results in 2023.

### `/seo-faq`

```
/seo-faq                                   # build, update or validate interactively
/seo-faq build app/pricing/page.tsx markup=no
/seo-faq validate
/seo-faq --dry-run
```

Drafts questions and answers from the page's own content, the question map, or answers you supply, and shows the source for each draft. It renders the visible FAQ and any markup from one data source so they can't drift apart, keeps answers in the HTML with the main ones open, and can validate every FAQ on the site.

### `/seo-questions`

```
/seo-questions
/seo-questions csv=exports/queries.csv search=yes
```

Starts from the questions your site already asks in its headings and FAQs. You can add questions by typing them, from a query export (Search Console, Bing Webmaster Tools, or the grounding queries in Bing's AI Performance report), from web search suggestions linked to where they were found, or from your earlier map. It merges duplicates, gives each question one owner page, and marks it answered first, buried, partial, missing or competing. The AEO lens scores question coverage against the latest map.

### `/seo-llms-txt`

```
/seo-llms-txt                    # generate, update or validate interactively
/seo-llms-txt update full=yes
/seo-llms-txt --dry-run
```

Generates, updates or validates `llms.txt` (and optionally `llms-full.txt`), places it where your framework serves static files, and offers discovery hints in the `<head>`, sitemap and robots.txt. Google Search ignores `llms.txt`. Some coding tools read it, and Chrome Lighthouse's agentic browsing audit checks for it. It's cheap to publish, but it isn't a citation lever.

### Related plugins

- `/accessibility-audit` ([ai-accessibility](../ai-accessibility/)) covers WCAG compliance. The SEO lens checks only where accessibility and SEO overlap.
- `/performance-audit` ([ai-performance](../ai-performance/)) covers runtime performance beyond the static Core Web Vitals signals here.

---

## What LLMs Often Get Wrong

**SEO:**

| What LLMs often recommend | What this plugin enforces |
|---------------------------|---------------------------|
| `<meta name="keywords" content="...">` | **Remove.** Google deprecated it in 2009, and Bing uses it as a spam signal. |
| `<meta http-equiv="X-UA-Compatible" content="IE=edge">` | **Remove.** IE was retired in 2022, and Edge has used Chromium since 2020. |
| `<!--[if IE]>...<![endif]-->` conditional comments | **Remove**, unless the project states IE11 support. |
| "Add jQuery for DOM manipulation" | **Use native APIs.** |
| `float` columns | **Flexbox / Grid.** |
| `<b>Important!</b>` / `<i>aside</i>` | **`<strong>` / `<em>`** for semantic meaning. |
| Microdata (`itemscope`/`itemprop`) or RDFa | **JSON-LD**, Google's preferred format. |
| `<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML...">` | **`<!DOCTYPE html>`**, the HTML5 doctype. |
| "Optimize FID" | **Measure INP, LCP and CLS.** INP replaced FID in March 2024. |
| "Create a mobile subdomain m.example.com" | **Responsive design.** Google has used mobile-first indexing since 2019. |
| `<br />`, `<img />`, `<hr />` | **`<br>`, `<img>`, `<hr>`** in HTML5 contexts. |
| `<a href="..." target="_blank">` | **Add `rel="noopener noreferrer"`** for security and performance. |
| Raw `<head>` edits in framework projects | **Framework head APIs** (Metadata API, `useSeoMeta`, route `head`, etc.). |

**AEO:**

| What LLMs often do | What this plugin does |
|--------------------|-----------------------|
| Promise FAQ rich results from FAQPage markup | Google stopped showing FAQ rich results on May 7, 2026; markup is optional |
| Recommend HowTo markup for step lists | Uses a real `<ol>`; HowTo results ended in 2023 |
| Suggest "featured snippet schema" | No such markup exists; Google chooses snippets itself |
| Recommend `speakable` for voice search | Mentions it only for news publishers, as a legacy beta |
| Treat a word count (often "40–60 words") as a Google rule | Treats length as a heuristic; Google sets no minimum |
| Put answers in accordions that load on click | Flags answers missing from the initial HTML |
| Mark up FAQ entries that aren't on the page | Marks up only visible questions, from the same data |
| Miss a `nosnippet` set in a layout or header | Searches meta tags, framework APIs, header config, middleware and `data-nosnippet` |
| Write FAQ answers from thin air | Drafts only from your site or your answers |

**GEO:**

| What LLMs often do | What this plugin does |
|--------------------|-----------------------|
| Treat GEO as a synonym for SEO or AEO | Keeps citation checks in the GEO lens and direct-answer checks in the AEO lens |
| Split AI bots into "training" and "citation" only | Uses three groups: training, AI search and user-triggered |
| Block Google-Extended to leave AI Overviews | Explains it doesn't, and names the real controls |
| Assume robots.txt stops every AI bot | Notes which fetchers say it may not apply |
| Call llms.txt a ranking or citation signal | Rates it Low or Medium 🧪; Google Search ignores it |
| Recommend Markdown copies of pages for AI search | Treats them as optional and informational 🧪 |
| Suggest splitting content into small chunks for AI | Checks that paragraphs stand on their own, without fragmenting them |
| Invent statistics, quotes or sources to "add evidence" | Asks you for the source, your own data, or removal |
| Fabricate `sameAs` URLs, authors or reviews | Asks you; never invents identity or reviews |
| Recommend chasing mentions anywhere | Points to earned coverage and flags inauthentic tactics |
| Recommend cloaking for AI bots | Flags user-agent content changes as Critical |

---

## AI Crawler Reference

**Training crawlers and tokens**

| Bot | Operator | What it controls |
|-----|----------|------------------|
| `GPTBot` | OpenAI | Model training |
| `ClaudeBot` | Anthropic | Model training |
| `Google-Extended` | Google | A robots.txt token, not a crawler: Gemini training and grounding in Gemini Apps and Vertex AI. It doesn't affect Google Search, AI Overviews or AI Mode |
| `Applebot-Extended` | Apple | A token, not a crawler: Apple generative AI training |
| `meta-externalagent` | Meta | AI training and product improvement |
| `Amazonbot` | Amazon | Amazon products and services; may train Amazon AI models |
| `CCBot` | Common Crawl | Open web corpus many models train on |
| `MistralAI-Training` | Mistral | Model training |
| `Bytespider` | ByteDance | Reported as training; no vendor documentation |

**AI search indexers**

| Bot | Operator | Feeds |
|-----|----------|-------|
| `OAI-SearchBot` | OpenAI | ChatGPT search |
| `Claude-SearchBot` | Anthropic | Claude search |
| `PerplexityBot` | Perplexity | Perplexity search (not training) |
| `Meta-WebIndexer` | Meta | Meta AI search |
| `Amzn-SearchBot` | Amazon | Alexa and Amazon search features (not training) |
| `MistralAI-Index` | Mistral | Mistral search (not training) |
| `DuckAssistBot` | DuckDuckGo | DuckAssist answers (not training) |
| `Googlebot` | Google | Google Search, including AI Overviews and AI Mode |
| `Bingbot` | Microsoft | Bing, which grounds Copilot |
| `Applebot` | Apple | Siri, Spotlight and Safari |

**User-triggered fetchers**

| Bot | Operator | Follows robots.txt? |
|-----|----------|---------------------|
| `ChatGPT-User` | OpenAI | OpenAI says it "may not apply" |
| `Claude-User` | Anthropic | Yes |
| `Perplexity-User` | Perplexity | Perplexity says it "generally ignores" it |
| `meta-externalfetcher` | Meta | Meta says it "may bypass" it |
| `Amzn-User` | Amazon | Amazon says it may not follow all directives |
| `MistralAI-User` | Mistral | See Mistral's docs |
| `Google-Agent` | Google | Generally not; it acts on a user's request |

**A common setup** blocks training crawlers and allows AI search indexers and user-triggered fetchers, so the site can be cited without contributing training data. `/seo-fix` asks about each group separately. If a block has to hold, it needs CDN or firewall rules, because several fetchers say robots.txt may not apply.

**Google's AI features** are controlled by `nosnippet`, `data-nosnippet`, `max-snippet`, `noindex`, and the Search Console setting "Search generative AI" → Exclude, not by Google-Extended. **Copilot** respects Bing's `nocache` and `noarchive`.

**Your CDN may change the policy.** Since July 2025 Cloudflare has blocked AI crawlers by default on new domains, and its managed robots.txt can add rules. The live check compares the deployed file with the repo.

---

## Measuring Citations

The audit measures readiness, not how often you're cited. To track that:

- **Bing Webmaster Tools → AI Performance** shows citations in Copilot and Bing AI summaries, with cited pages and grounding queries.
- **Google Search Console → Generative AI performance report** shows impressions in AI Overviews and AI Mode.
- **Server logs** show visits from the AI user agents above (check them against each operator's published IP ranges).
- **A fixed question list** asked of each assistant every month shows trends. `/seo-questions` can build the list.

---

## llms.txt Primer

`llms.txt` is a Markdown index of a site's key pages, served at `/llms.txt`. Jeremy Howard proposed it at https://llmstxt.org/ in 2024. Google says Google Search ignores it, and no other major AI search provider has said it uses it. Some coding tools read it, and Chrome Lighthouse's agentic browsing audit checks for it, so it's most useful for developer documentation 🧪.

```markdown
# Site Name

> One-sentence description of the site.

## Section

- [Page title](https://example.com/page): one-line summary.
- [Another page](https://example.com/another): one-line summary.

## Optional

- [Secondary resource](https://example.com/secondary): summary.
```

- The H1 title is the only required part. A blockquote summary after it is optional in the spec, but the audit checks for it.
- H2 sections group bulleted links, each with a one-line summary.
- An `## Optional` section holds links a reader can skip when it needs a shorter context.

`llms-full.txt` is a companion with the full Markdown content of the linked pages.

---

## Report Output

Reports go to `docs/seo-audit/`. If the project already uses `documentation/` or `.docs/`, the skills write there instead.

```
docs/seo-audit/
├── README.md                                  # Index: audits with a score and trend per lens, and question maps
├── latest.md                                  # Copy of the newest audit
├── seo-audit-all-2026-10-11-143022.md         # Timestamped audits; the lenses are in the name
├── seo-audit-aeo-2026-10-04-091544.md
├── question-map-latest.md                     # Copy of the newest question map
├── question-map-2026-10-04-150110.md          # Timestamped question maps
├── crawl-latest.md                            # Copy of the newest saved /seo-crawl report
├── crawl-2026-10-12-091500.md                 # Timestamped crawls, saved with save=yes
├── faq-validation-2026-10-04-152245.md        # Optional /seo-faq validation results
└── llms-txt-validation-2026-10-04-153010.md   # Optional /seo-llms-txt validation results
```

The index has one row per audit:

| Date | Lenses | SEO | AEO | GEO | Critical | Report |
|------|--------|-----|-----|-----|----------|--------|
| 2026-10-11 14:30:22 | SEO, AEO, GEO | 84/100 C 📈 | 71/100 D ➡️ | 62/100 F first run | 3 | [view](./seo-audit-all-2026-10-11-143022.md) |
| 2026-10-04 09:15:44 | AEO | — | 70/100 D 📈 | — | 1 | [view](./seo-audit-aeo-2026-10-04-091544.md) |

**Trend indicators** compare each lens with the previous audit that covered it: 📈 improved (score up ≥3), 📉 regressed (score down ≥3), ➡️ unchanged (±2). 🔄 marks a GEO score that can't be compared because the previous GEO audit came from ai-geo before 1.2.0, which used different categories. An index from ai-seo 1.x is converted to this format on the next audit.

Timestamped files are never overwritten. `latest.md`, `question-map-latest.md` and `crawl-latest.md` are file copies, not symlinks, so they work on every platform. Saved crawls get their own **Crawls** table in the index, with the URL, page count, findings by severity and the verdict.

---

## Framework Support

Each skill detects the framework from `package.json`, config files and directory structure, then uses that framework's own APIs:

- **Next.js** (App Router + Pages Router): Metadata API, `generateMetadata`, `app/sitemap.ts`, `app/robots.ts`, `app/opengraph-image.tsx`, JSON-LD in server components
- **Nuxt:** `useSeoMeta`, `useHead`, `routeRules`, `@nuxtjs/seo`, `@nuxtjs/sitemap`, `@nuxtjs/robots`
- **TanStack Start:** `createRootRoute`/`createFileRoute` with `head: () => ({ meta, links, scripts })`, `<HeadContent />` + `<Scripts />` in root
- **Astro:** layout `<head>`, `astro-seo`, `@astrojs/sitemap`, content collections, endpoint routes
- **SvelteKit:** `<svelte:head>`, `+server.ts` routes, prerendering
- **Remix / React Router:** `meta` / `links` exports, loaders, resource routes
- **Vanilla HTML:** direct `<head>` inspection and edits

The audit also reads hosting and edge config (`vercel.json`, `netlify.toml`, `_headers`, `wrangler.toml`, `middleware.ts`, `nginx.conf`, `.htaccess`), which can set headers or treat bots differently.

---

## Context7 MCP Integration

When [Context7 MCP](https://github.com/upstash/context7) is installed, the skills use it for current documentation: Google Search Central guidelines, featured snippets and snippet controls, Schema.org types and required properties, AI crawler docs (OpenAI, Anthropic, Google, Perplexity, Apple, Meta, Amazon), the llms.txt proposal, Core Web Vitals thresholds, and your framework's head APIs.

Without Context7, the skills fall back to training-data knowledge, say so in the terminal output and the report header, and mark more AEO and GEO items with 🧪.

Install it in Claude Code:

```bash
claude mcp add context7 -- npx -y @upstash/context7-mcp
```

Restart Claude Code after installing. In Codex or Cursor, add Context7 through that agent's MCP settings.

---

## Limits

- `/seo-audit` is static analysis of HTML, JSX, Vue, Svelte and Astro files and their config. Apart from the optional live check, it sends no HTTP requests, so it can't measure real LCP, CLS or INP or check external links for 404s. `/seo-crawl` covers the live site.
- `/seo-crawl` sees what the server sends to a spoofed crawler user agent, not what real Googlebot got, because CDNs verify crawlers by IP address. It doesn't run JavaScript, and its Core Web Vitals numbers come only from the PageSpeed Insights API, whose free quota is small. Search Console and Bing Webmaster Tools remain the only proof of what's indexed.
- Accessibility coverage is limited to the SEO overlap. For WCAG 2.1/2.2 compliance, use `/accessibility-audit` from ai-accessibility.
- It can't see which queries show a featured snippet today or who holds it. Engines choose answers themselves and change how they do it often, and third-party tracking shows featured snippets on fewer results as AI Overviews spread.
- Voice assistants now run on large models with their own sources, which can't be tested from code.
- No AI provider publishes how it picks citations. The GEO categories and weights are judgment informed by the GEO research and Google's and Microsoft's guidance.
- The off-site snapshot is a dated sample of web search results, not a full census of mentions.
- robots.txt states a policy; it doesn't prove enforcement. Live user-agent tests are indicative, because CDNs verify real crawlers by IP address.
- It doesn't measure traffic, zero-click effects or citation frequency. See [Measuring Citations](#measuring-citations).

---

## Quick Start

### Installation

Claude Code:

```
/plugin marketplace add charlesjones-dev/ai-agent-plugins
/plugin install ai-seo@ai-agent-plugins
```

Codex:

```
codex plugin marketplace add charlesjones-dev/ai-agent-plugins
codex plugin add ai-seo@ai-agent-plugins
```

Cursor: add this repository as a team marketplace, or copy this folder to `~/.cursor/plugins/local/ai-seo`. See the [Cursor install steps](../../README.md#cursor).

### Recommended Flow

```
# 1. Map the questions your pages should answer (optional, improves the AEO lens)
/seo-questions

# 2. Baseline audit of all three lenses, plus a crawl of the live site
/seo-audit all
/seo-crawl https://example.com save=yes

# 3. Review docs/seo-audit/latest.md, then preview and apply fixes
/seo-fix --dry-run
/seo-fix

# 4. Fill the gaps the fix run hands off
/seo-schema
/seo-faq
/seo-llms-txt

# 5. After the deploy, re-audit and re-crawl to confirm; the trend arrows should point up
/seo-audit all
/seo-crawl https://example.com save=yes
```

---

## Resources

- [Google Search Central](https://developers.google.com/search)
- [Optimizing for generative AI search (Google)](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
- [Optimizing your content for inclusion in AI search answers (Microsoft)](https://about.ads.microsoft.com/en/blog/post/october-2025/optimizing-your-content-for-inclusion-in-ai-search-answers)
- [Schema.org](https://schema.org/)
- [Core Web Vitals](https://web.dev/articles/vitals) (LCP, CLS, INP)
- [GEO: Generative Engine Optimization (Aggarwal et al., KDD 2024)](https://arxiv.org/abs/2311.09735)
- [llms.txt proposal](https://llmstxt.org/)
- [Context7 MCP](https://github.com/upstash/context7)

---

## Plugin Details

- **Name:** AI-SEO Plugin
- **Type:** AI Instruction Plugin (Skills)
- **Skills:** `/seo-audit`, `/seo-crawl`, `/seo-fix`, `/seo-schema`, `/seo-faq`, `/seo-questions`, `/seo-llms-txt`
- **Version:** 2.1.0
- **License:** MIT
- **Author:** Charles Jones

---

## Contributing

Bug reports and fixes are welcome. See [CONTRIBUTING.md](../../CONTRIBUTING.md).

---

## License

MIT License. See [LICENSE](LICENSE).
