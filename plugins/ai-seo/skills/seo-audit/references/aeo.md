# AEO Lens: Answer Readiness

Answer Engine Optimization (AEO) is the practice of structuring content so an answer engine can lift one passage as **the** answer to a specific question: a featured snippet, a voice assistant reply, a direct answer box, or the question-and-answer pair an assistant quotes word for word. The goal is to be the concise answer to a question, not one of many sources.

Score name: **Answer Readiness Score**.

Stay in the AEO column of the lens table. Topical authority, evidence, authorship and AI crawler policy belong to the GEO lens; rankings, meta tags and performance belong to the SEO lens. Reference them instead of repeating their checks.

**What the engines say.** Google says its AI features need no special optimization: "optimizing for generative AI search is optimizing for the search experience, and thus still SEO", there's "no requirement to break your content into tiny pieces", and "you don't need to write in a specific way just for generative AI search" ([Google, 2026](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)). Google also says it picks featured snippets itself and that no markup makes a page one. Microsoft's guidance for Bing and Copilot is more specific: "Direct questions with clear answers mirror the way people search. Assistants can often lift these pairs word for word", along with concise one- to two-sentence answers, self-contained sentences, lists and tables, and not hiding answers in tabs or expandable menus ([Microsoft, October 2025](https://about.ads.microsoft.com/en/blog/post/october-2025/optimizing-your-content-for-inclusion-in-ai-search-answers)). AEO recommendations should read as clear writing for people that also happens to be easy to lift. Never recommend writing for engines at the reader's expense.

## Context7 Topics

With Context7, fetch Google Search Central docs on featured snippets and snippet controls, Schema.org `FAQPage` / `QAPage` / `DefinedTerm`, Google's structured data policies, and the detected framework's head and metadata APIs.

## LLM Knowledge Gap Corrections (NON-NEGOTIABLE)

These overrides apply to every AEO finding and recommendation:

1. **AEO is not GEO.** AEO asks "will an engine lift this passage as the answer to this question?" GEO asks "will AI answers cite or mention this site among other sources?" Do not score topical authority, original research, brand mentions or AI training and search crawler policy in this lens. Those belong to the GEO lens.
2. **No markup makes a page a featured snippet.** Google: "Google systems determine whether a page would make a good featured snippet." There is no featured-snippet schema. Clear answers and clean structure raise the odds; nothing guarantees selection. Third-party tracking (Ahrefs, 2025; vendor data) also shows featured snippets on fewer results as AI Overviews spread, so don't promise one.
3. **FAQ rich results are gone.** Google limited them to government and health sites in August 2023, stopped showing them entirely on May 7, 2026, and removed its FAQPage documentation in June 2026. Never promise FAQ rich results. FAQPage is still a valid Schema.org type and Microsoft says schema helps its search and AI systems understand content, so markup on a visible FAQ is optional 🧪. The visible FAQ section is what matters.
4. **HowTo rich results are gone too.** Google stopped showing them in September 2023. Don't add HowTo markup to win a Google feature. A real `<ol>` of steps under a clear heading is what an engine can lift as a list.
5. **Structured data must match visible content.** Google's general structured data guidelines: "Don't mark up content that is not visible to readers of the page." Never mark up questions or answers that aren't shown on the page.
6. **QAPage and FAQPage are different.** QAPage is for a page built around one question where users can submit answers (forums, community Q&A); Google still documents it and says a site-written FAQ isn't eligible. FAQPage is for questions and answers the site itself wrote. Don't mix them up.
7. **Speakable is legacy.** Google's `speakable` is still documented as a beta for news content, in English, in the US, read by Google Assistant on Google Home devices. Gemini is replacing Google Assistant and Google hasn't said Gemini uses `speakable`. Only mention it for news publishers, marked 🧪.
8. **Snippet controls cut both ways.** `nosnippet`, `max-snippet:0` (or a very small value) and `data-nosnippet` keep text out of featured snippets and, per Google, out of AI Overviews and AI Mode. `noindex` removes the page from the index altogether. On Bing, `nocache` limits Copilot answers to the URL, title and snippet, and `noarchive` keeps the content out of Copilot answers. Flag them on answer pages, but treat them as possibly deliberate: report, don't assume.
9. **Google-Extended doesn't control Search.** Blocking the `Google-Extended` token affects Gemini training and grounding, not featured snippets, AI Overviews or AI Mode. Google also offers a Search Console setting ("Search generative AI" → Exclude), available to all sites since August 31, 2026, that removes a site from AI Overviews and AI Mode. It isn't visible in code, so list it as a manual check.
10. **Lists and tables must be real HTML.** Use `<ol>` for steps, `<ul>` for unordered items and `<table>` with `<th>` for comparisons. Microsoft recommends "bulleted lists, numbered steps, and comparison tables". Divs styled to look like lists, `<br>`-separated lines and CSS-grid "tables" are harder to lift.
11. **Word-count targets are heuristics.** Google says it "does not provide an exact minimum length" for featured snippets. The common "40–50 words" target comes from SEMrush's featured snippet studies (vendor research); Microsoft suggests "one- to two-sentence responses". Use these as guides, mark word-count findings 🧪, and never pad or cut an answer to hit a number.
12. **Answer first, context second.** The direct answer belongs in the first sentence under the question heading. Preambles ("Great question!", "In this article we'll explore…", a paragraph of backstory) push the answer away from the question.
13. **Important answers should be visible.** An accordion that renders its answer only after a click (`{open && <Answer />}`, `v-if`, `{#if open}`) leaves the answer out of the HTML crawlers receive: Critical on the main FAQ or help pages and for a page's primary answer, High elsewhere. Collapsed content that is still in the HTML (`<details>`, `hidden`, CSS) is readable by Google, but Microsoft warns "AI systems may not render hidden content". Keep the page's main answers visible by default and use collapsed sections for secondary questions.
14. **Don't invent questions or answers.** Questions come from the site's content, the user, or query data the user provides. Answers come from the site's content or the user. Never fabricate facts, figures or "People also ask" data.
15. **Don't rewrite for engines at the reader's expense.** Google says there's no need to write in a special way for AI. Recommend changes that also make the page clearer for people; skip ones that only chase an engine.
16. **Zero-click is the tradeoff.** Winning the direct answer to a simple fact can reduce clicks. Report this plainly; don't promise traffic.
17. **Never recommend cloaking.** Bots and people must get the same content.

## Preparation

### Load the Question Map (if present)

Look for the latest question map from `/seo-questions`:

1. `<docs-dir>/seo-audit/question-map-latest.md`
2. `<docs-dir>/aeo-audit/question-map-latest.md` (written by the ai-aeo plugin before it merged into ai-seo 2.0.0)

If both exist, use the one with the newer **Date** line. Read it, use its target questions, their mapped pages and its gaps in Category 2, and record `QUESTION_MAP = "<path> (<date>)"`.

If neither exists, set `QUESTION_MAP = "none"`. Category 2 is then scored only on the questions the site already asks in its headings, and the report recommends running `/seo-questions`.

### Identify Answer Pages

List the pages whose job is to answer questions: docs and guides, blog posts, FAQ and help-center pages, glossary pages, product and pricing pages that carry FAQs, comparison pages, and location pages for local businesses. Exclude utility pages (auth, cart, checkout, account, legal) from content checks; still include them in the snippet-control check if they carry site-wide directives.

Record the list. The report states how many answer pages were analyzed.

## Categories

Analyze every answer page across the nine categories. For each finding capture: file path, line number, the current code or copy (or `N/A — absent`), a specific fix and the category. Record each issue once, in the category that fits best: answers gated behind a click go in Category 4; a page rendered entirely on the client goes in Category 9; a live-check confirmation adds evidence to the existing finding instead of creating a second one.

### Category 1: Answer-First Formatting

- For each question-shaped heading (H2/H3, or an FAQ item), read the first paragraph under it. Does its **first sentence** answer the question directly?
- Flag preambles before the answer: restating the question, "Great question", "In this article…", "Let's dive in", backstory, or a sales pitch.
- Paragraph answers: count the words in the answering paragraph. Roughly 40–50 words (SEMrush's featured snippet studies) or one to two sentences (Microsoft) are guides 🧪, not rules. Flag answers that take more than about 100 words to make the point, and fragments that don't stand alone.
- Inverted pyramid: the answer, then supporting detail, then edge cases.
- Long pages (>1,000 words) open with a short summary or "key takeaways" block that answers the page's main question.
- Answers that depend on surrounding context ("as shown above", "this", "it" with no antecedent) don't survive being lifted alone. Microsoft asks for "sentences that make sense even when pulled out of context".
- Vague claims in answers ("innovative", "eco", "industry-leading") with no specifics. Microsoft: "Terms like innovative or eco mean little without specifics."

### Category 2: Question Coverage & Headings

- Headings phrased as the questions people ask (what, how, why, when, where, who, can, does, is, should, vs). One question per section.
- Heading hierarchy is clean: one H1, H2 for main questions, H3 for follow-ups. No skipped levels inside answer content.
- Follow-up questions are answered on the same page (cost, duration, alternatives, "is it safe", "how long", comparisons) where they naturally belong. These are the questions "People also ask" boxes expand.
- Keyword-stuffed headings ("Best Cheap Laptops 2026 Deals") instead of a natural question ("What's the best budget laptop in 2026?").
- Don't turn every heading into a question. Narrative and reference pages can keep descriptive headings; flag only answer pages where the reader arrives with a question.
- **With a question map:** every target question has a page that answers it directly; gaps and competing pages are findings here.
- **Without a question map:** report which question patterns the site already covers and recommend `/seo-questions`.

### Category 3: Concise Definitions

- Pages about a term, product category or concept open with a one-sentence definition: "X is a Y that does Z."
- Definitions are short (one or two sentences) before the elaboration.
- Glossary pages exist for sites with heavy jargon (docs, finance, health, legal, technical products), with one term per heading.
- `DefinedTerm` / `DefinedTermSet` markup for glossaries 🧪 (valid Schema.org; no Google feature depends on it).
- The same term is defined the same way across pages.

### Category 4: Snippet-Ready Structure

- Steps use `<ol>` (or markdown `1.`). Unordered sets use `<ul>`. Flag divs styled as lists, `<br>`-separated lines and lists drawn with CSS only.
- Comparisons and specs use `<table>` with a header row (`<th>`). Flag CSS-grid or flexbox "tables" and tables rendered as images.
- List items are short and parallel; steps are in order and start with a verb.
- Answer text is real text, not inside images, canvas, SVG `<text>`, video only, or a PDF. Microsoft advises against "relying on PDFs for core information" and putting key information only in images.
- **Answer text is in the initial HTML.** Flag accordions, tabs and "read more" toggles that render their content only after interaction (React `{open && …}`, Vue `v-if`, Svelte `{#if}`, client-side fetch on expand). Critical on the main FAQ or help pages and for a page's primary answer; High elsewhere.
- **Main answers are visible by default.** Content collapsed with `<details>`, `hidden`, `v-show` or CSS is in the HTML and Google reads it, but Microsoft warns "AI systems may not render hidden content". Flag a page whose primary answer sits inside a collapsed element (Medium); collapsed secondary questions are fine.
- Decorative symbols in answer text (arrows, star strings, runs of punctuation) that Microsoft says can confuse extraction. Low.

### Category 5: Snippet Eligibility & Indexing Controls

Search the codebase for every place a robots directive can come from:

- `<meta name="robots">`, `<meta name="googlebot">`, `<meta name="bingbot">` in templates and layouts.
- Framework APIs: Next.js `metadata.robots` / `generateMetadata` (`nosnippet`, `googleBot: { 'max-snippet': … }`), Nuxt `useSeoMeta({ robots })` / `useHead`, TanStack Start route `head`, Astro layouts, SvelteKit `<svelte:head>`, Remix `meta` exports.
- `X-Robots-Tag` response headers: `next.config.*` `headers()`, middleware, `vercel.json`, `netlify.toml`, `_headers`, `nginx.conf`, `.htaccess`, server code.
- `data-nosnippet` attributes.
- `robots.txt` rules that block Googlebot or Bingbot from answer paths.
- Canonicals on answer pages that point to a different URL.

Flag on answer pages: `noindex`, `nosnippet`, `max-snippet:0` or a value too small to hold an answer, `data-nosnippet` wrapped around answer text, and Bing's `nocache` / `noarchive` (which limit or remove the content from Copilot answers). Severity is Critical when the directive is site-wide and looks accidental (for example copied from a staging config), High when it covers a section of answer pages. Always phrase the finding as "confirm this is intended" because these controls are sometimes deliberate.

Also list one manual check in the report: whether the Search Console setting "Search generative AI" is set to Exclude, which removes the site from AI Overviews and AI Mode. Code can't show it.

### Category 6: FAQ Sections & Structured Data

- Pages where readers bring recurring questions (product, pricing, support, policies) have a visible FAQ section, and its answers open with the answer.
- No markup for questions that aren't visible on the page (against Google's general structured data guidelines). High.
- Existing `FAQPage` JSON-LD matches the visible questions and answers. Adding FAQPage where it's missing is optional 🧪: no Google feature has used it since May 2026; Microsoft says schema helps its systems understand content. Never present it as a way to get a rich result.
- No identical FAQ block marked up across many pages (for example a site-wide footer FAQ repeated on every route).
- Forum or community Q&A pages use `QAPage` with `Question`, `answerCount`, `acceptedAnswer` / `suggestedAnswer`, and author and date fields. A site-written FAQ marked as QAPage is a finding.
- `HowTo` markup: don't add it for Google. If it exists, leave it (valid Schema.org) and note it no longer produces a Google feature.
- Answer pages carry basic `Article` / `BlogPosting` / `WebPage` markup with `headline`, `author`, `datePublished` and `dateModified`, plus `BreadcrumbList`. Deeper entity and author work belongs to the GEO lens.
- Validate existing JSON-LD: valid JSON, `@context: "https://schema.org"`, correct `@type`, required properties, ISO 8601 dates, absolute URLs. Flag microdata and RDFa; recommend JSON-LD.
- Best practice: render the visible FAQ and its JSON-LD from **one data source** so they can't drift apart.

### Category 7: Voice & Assistant Readiness

- Answers read well aloud: a complete sentence that makes sense without the page around it, no "click here", no answer that exists only in a table or image.
- Local businesses: `LocalBusiness` (or a subtype) JSON-LD with name, address, phone, opening hours and geo, matching the visible NAP (name, address, phone) on every page that shows it. "Near me" and "is it open now" questions depend on this kind of data.
- Assistant crawlers can reach answer pages: Applebot (Siri, Spotlight, Safari) and Amzn-SearchBot (Alexa and Amazon search features) aren't blocked in robots.txt. Report only, with no deduction; full crawler policy belongs to the GEO lens.
- `speakable`: only for news publishers, marked 🧪 (beta, English, US, Google Assistant devices that Gemini is replacing).
- Don't claim a "voice search schema" exists. Voice assistants answer from their own search indexes, partners and models; concise, factual sentences are what this audit can check.

### Category 8: Answer Trust Signals

Light checks only; the GEO lens covers authorship and evidence in depth.

- Answers that change over time (prices, versions, laws, schedules) show a visible "last updated" date and carry `dateModified`.
- Factual answers in health, finance, legal and safety topics link to a source. Authorship and reviewer credentials are scored by the GEO lens; mention it rather than scoring them here.
- No contradictory answers to the same question on different pages.

### Category 9: Technical Answer Accessibility

- Answer pages are server-rendered or static. Client-only rendering of answer content is Critical.
- Correct status codes (no 200 on error pages; redirects for moved answers).
- Mobile viewport set; text readable without zoom.
- Title, meta description and H1 describe the page's main question or topic (Microsoft names them as signals AI systems use); deeper meta checks belong to the SEO lens.
- Overlap with the SEO lens (performance, Core Web Vitals) is referenced, not re-scored.

### Framework-Specific Checks

**Next.js:**
- App Router answer pages are server components or static; flag `'use client'` on page-level content components that hold the answer text.
- `metadata.robots` / `generateMetadata` for `nosnippet` and `max-snippet`; `next.config.*` `headers()` and `middleware.ts` for `X-Robots-Tag`.
- FAQ accordions: client components that render answers conditionally. Keep the answer in the HTML and the main answers expanded.
- JSON-LD rendered in a server component with `<script type="application/ld+json">`.

**Nuxt:**
- `ssr: false` or route rules that disable SSR on answer pages.
- `useSeoMeta({ robots })`, `routeRules` headers, `nuxt.config` `app.head`.
- Accordions using `v-if` for answers (not in the HTML) vs `v-show` (in the HTML).

**TanStack Start:**
- SSR enabled; route `head: () => ({ meta: [...] })` for robots directives; `<HeadContent />` in the root route.

**Astro:**
- Static or server output for answer pages; client-only islands (`client:only`) holding answer text are a finding.
- FAQ components using `<details>`; content collections as the single source for visible FAQ and JSON-LD.

**SvelteKit:**
- `export const ssr = false` on routes holding answers; `{#if open}` accordions; `<svelte:head>` robots meta.

**Remix / React Router:**
- `meta` export for robots; loader-provided answer text rendered on the server; conditional accordion rendering.

**Vanilla HTML:**
- Direct `<head>` and markup inspection; server or CDN config for `X-Robots-Tag`.

## Live Check Items

When the live check runs, pick the highest-value answer pages (FAQ, glossary, top guides) for the shared fetch list. For each fetched page, report:

- Status and redirects.
- `X-Robots-Tag` header and `<meta name="robots|googlebot|bingbot">` values actually served.
- Whether the answer text found in the source (the first sentence under each question heading) appears in the served HTML. If not, the answer is client-rendered: Critical.
- Whether the main answers sit inside collapsed elements (`<details>` without `open`, `hidden`, `aria-hidden`, `display:none` classes).
- Whether FAQ JSON-LD in the served HTML matches the visible questions.
- `data-nosnippet` around answer text.
- Canonical URL.

Compare the deployed `/robots.txt` with the repo's version. A CDN or host can rewrite robots.txt (Cloudflare's managed robots.txt, for example), so the deployed file is the one that counts.

## Scoring

| Category | Weight |
|----------|--------|
| Answer-First Formatting | 20% |
| Question Coverage & Headings | 15% |
| Concise Definitions | 10% |
| Snippet-Ready Structure | 15% |
| Snippet Eligibility & Indexing Controls | 15% |
| FAQ Sections & Structured Data | 10% |
| Voice & Assistant Readiness | 5% |
| Answer Trust Signals | 5% |
| Technical Answer Accessibility | 5% |

Experimental 🧪 findings deduct half their tier. A category with nothing to check (for example Voice & Assistant Readiness on a site with no answer pages that need it) scores 100 and says "not applicable" in the breakdown.

## Severity Assessment

- **Critical**: Stops pages from being used as answers. Accidental site-wide `noindex` / `nosnippet` / `max-snippet:0`; answer content rendered only on the client; answers only rendered after a click on the main FAQ or help pages, or for a page's primary answer.
- **High**: Answers exist but can't be lifted cleanly. Question headings whose first paragraph doesn't answer the question; steps or comparisons drawn with divs; other answers only rendered after a click; markup for questions that aren't visible; `data-nosnippet`, `nocache` or `noarchive` on answer pages; QAPage/FAQPage mix-ups; answer pages with a canonical pointing elsewhere.
- **Medium**: Partial or weak. Keyword-stuffed headings; long preambles; definitions buried mid-page; main answers collapsed by default; missing summary on long pages; contradictory answers across pages; repeated site-wide FAQ markup; FAQPage that no longer matches the visible FAQ.
- **Low / Experimental 🧪**: Heuristics and optional markup. Word-count tuning, adding FAQPage to a visible FAQ, `DefinedTerm` glossaries, `speakable` for news content, decorative symbols, follow-up question suggestions.

When a fix needs copy the site doesn't have, say so and leave it to `/seo-fix` or `/seo-faq` to collect from the user.

## Report Section

Insert this under `## AEO: Answer Readiness` in the report. Every subsection is required; write "None found" or "Not run" rather than dropping one.

```markdown
### What is AEO?

Answer Engine Optimization (AEO) structures content so a search or answer engine can lift one passage as the direct answer to a specific question: a featured snippet, a voice assistant reply, a direct answer box, or a question-and-answer pair an assistant quotes. Its goal is to be *the* concise answer. Generative Engine Optimization (GEO) is the related discipline: being cited and mentioned inside longer AI answers that draw on many sources. <If the GEO lens isn't in this report: "Run `/seo-audit geo` for that.">

No markup guarantees a direct answer. Engines choose answers automatically, and Google says its AI features need nothing beyond normal SEO. This section measures how clearly the site answers the questions its readers bring, which is what every engine can use.

### Executive Summary

**Answer Readiness Score:** <X> / 100

**Grade:** <A+ | A | B | C | D | F>

**Summary:** <2–3 sentences: overall readiness, the biggest gap, what already works.>

#### Score Breakdown

| Category | Score | Weight |
|----------|-------|--------|
| Answer-First Formatting | X/100 | 20% |
| Question Coverage & Headings | X/100 | 15% |
| Concise Definitions | X/100 | 10% |
| Snippet-Ready Structure | X/100 | 15% |
| Snippet Eligibility & Indexing Controls | X/100 | 15% |
| FAQ Sections & Structured Data | X/100 | 10% |
| Voice & Assistant Readiness | X/100 | 5% |
| Answer Trust Signals | X/100 | 5% |
| Technical Answer Accessibility | X/100 | 5% |

#### Issue Counts

- 🔴 **Critical:** <n>
- 🟠 **High:** <n>
- 🟡 **Medium:** <n>
- 🔵 **Low / Suggestions:** <n>
- 🟢 **Passing checks:** <n>

Items marked 🧪 rest on industry heuristics or limited features rather than documented engine behavior. Apply judgment.

### Snippet Eligibility Status

| Directive | Where | Scope | Looks intended? |
|-----------|-------|-------|-----------------|
| <noindex / nosnippet / max-snippet:N / data-nosnippet / nocache / noarchive / X-Robots-Tag> | `<file:line>` or live header | <site-wide / section / page> | <yes / unclear / likely accidental> |

<"No snippet restrictions found on answer pages." if empty.>

**Manual check:** in Search Console, Settings → "Search generative AI". "Exclude" removes the site from AI Overviews and AI Mode.

### Question Coverage

<With a question map: table of target question → page → status (answered first / answered but buried / partial / missing / competing pages). Without one: the question patterns found in headings, and a note to run `/seo-questions`.>

### 🔴 Critical Issues

#### AEO-1: <Title>

**File:** `path/to/file.ext:42` <or **Source:** live check (<url>)>
**Category:** <Category>
**Impact:** Critical

**Current Code:**
\`\`\`<language>
<exact snippet, or "N/A — element absent">
\`\`\`

**Problem:**
<1–3 sentences on why this stops the page being picked as an answer.>

**Recommended Fix:**
\`\`\`<language>
<code or rewritten copy>
\`\`\`

**Why it matters for AEO:**
<How this affects whether an engine can lift the passage.>

**Source:** <documentation link>

### 🟠 High Priority Issues

<Same format.>

### 🟡 Medium Priority Issues

<Same format.>

### 🔵 Suggestions & Experimental Practices 🧪

<Same format. Mark heuristics and limited features with 🧪.>

### ✅ What's Working Well

- ✅ <real positive finding>

### Live Check

<Only when run: per-URL table of status, robots directives served, answer text in initial HTML (yes/no), main answer visible without interaction (yes/no), FAQ markup matches visible text (yes/no/n/a), canonical. Note any repo/live differences. Otherwise "Not run.">

### 🏗️ Framework-Specific Recommendations

**Detected Framework:** <Framework>

<Framework-idiomatic guidance: where robots directives live, how to render answers server-side, accordion patterns that keep answers in the HTML (and main answers visible), rendering FAQ JSON-LD from the same data as the visible FAQ.>

### 📊 Content Analysis Summary

- **Answer pages analyzed:** <n>
- **Question-shaped headings:** <n> (<n> answered in the first sentence)
- **Median answer paragraph length:** <n> words
- **Definitional openings on concept pages:** <n>/<n>
- **Lists and tables in real HTML:** <n>/<n>
- **Visible FAQ sections:** <n> (<n> with matching FAQPage JSON-LD)
- **Answers rendered only after interaction:** <n>
- **Main answers collapsed by default:** <n>
```

**Detail lines for the terminal summary:**

```
AEO details:
  Answer pages analyzed:      <n>
  Question headings:          <n>  (answer-first: <n>)
  Visible FAQ sections:       <n>  (with matching FAQPage JSON-LD: <n>)
  Snippet controls on answer pages: <none | list>
```

**Remediation commands for this lens:** `/seo-fix`, `/seo-faq` to build or validate FAQ sections and FAQPage/QAPage markup, `/seo-questions` to map target questions to pages and find gaps.

### Resources

- [Featured snippets and your website (Google)](https://developers.google.com/search/docs/appearance/featured-snippets)
- [Robots meta tag, data-nosnippet and X-Robots-Tag (Google)](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag)
- [AI features and your website (Google)](https://developers.google.com/search/docs/appearance/ai-features)
- [Search Console control for AI features (Google)](https://support.google.com/webmasters/answer/16908024)
- [Bing controls for Copilot: NOCACHE and NOARCHIVE (Microsoft)](https://blogs.bing.com/webmaster/september-2023/Announcing-new-options-for-webmasters-to-control-usage-of-their-content-in-Bing-Chat)
- [Optimizing for generative AI search (Google)](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
- [Optimizing your content for inclusion in AI search answers (Microsoft)](https://about.ads.microsoft.com/en/blog/post/october-2025/optimizing-your-content-for-inclusion-in-ai-search-answers)
- [FAQPage (Schema.org)](https://schema.org/FAQPage)
- [QAPage structured data (Google)](https://developers.google.com/search/docs/appearance/structured-data/qapage)
- [General structured data guidelines (Google)](https://developers.google.com/search/docs/appearance/structured-data/sd-policies)
- [Speakable (Google, beta, news only)](https://developers.google.com/search/docs/appearance/structured-data/speakable)
- [Schema.org](https://schema.org/)

### Limitations

- Static analysis estimates readiness. It can't see which queries trigger a featured snippet today or who holds it.
- Engines choose direct answers automatically and change how they do it often.
- Word-count and formatting targets are industry heuristics, marked 🧪. Google publishes no length rule.
- Third-party tracking shows featured snippets on fewer results as AI Overviews spread; readiness here also serves "People also ask", assistants and AI answers, but no engine documents how it picks a quoted passage.
- Voice assistants now run on large models with their own sources (Gemini, Alexa+, Siri), which isn't documented well enough to test from code.
- Doesn't measure traffic or zero-click effects. Use Search Console and Bing Webmaster Tools for that.

## Examples: Bad vs Good Recommendations

**Example 1: Answer buried under a preamble**

❌ Current:
```markdown
## How long does a passport renewal take?

Renewing a passport is something many travelers put off until the last minute. In this guide we'll walk through everything you need to know, from forms to fees, so you can plan ahead with confidence. Processing times vary depending on several factors...
```

✅ Recommended (answer first, detail second):
```markdown
## How long does a passport renewal take?

Routine passport renewals take <N–N weeks>, and expedited renewals take <N–N weeks>, not counting mailing time. Times change with seasonal demand, so check the current estimate before you apply.
```
The figures come from the site's own content or the user. The audit never supplies them.

**Example 2: A list drawn with divs**

❌ Current:
```html
<div class="steps">
  <div class="step">Open Settings</div>
  <div class="step">Choose Billing</div>
  <div class="step">Select Cancel plan</div>
</div>
```

✅ Recommended:
```html
<h2>How do I cancel my plan?</h2>
<ol class="steps">
  <li>Open Settings.</li>
  <li>Choose Billing.</li>
  <li>Select Cancel plan.</li>
</ol>
```

**Example 3: Accordion answer missing from the HTML (React)**

❌ Current:
```tsx
{open && <p className="answer">{item.answer}</p>}
```

✅ Recommended (answer always in the HTML; the first few items open by default):
```tsx
<details open={i < 3}>
  <summary>{item.question}</summary>
  <p className="answer">{item.answer}</p>
</details>
```
Google reads collapsed content that's in the HTML. Microsoft warns AI systems may not, so keep the page's main answers expanded or in the body text.

**Example 4: FAQ markup that doesn't match the page**

❌ Current: the page shows three questions; the JSON-LD lists eight, five of them hidden.

✅ Recommended: build the visible FAQ and the JSON-LD from the same array.
```tsx
const faqs = [
  { q: 'Do you ship internationally?', a: 'Yes. We ship to <countries from site content>.' },
]

const faqLd = {
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  mainEntity: faqs.map(f => ({
    '@type': 'Question',
    name: f.q,
    acceptedAnswer: { '@type': 'Answer', text: f.a },
  })),
}
```

**Example 5: Site-wide snippet block (Next.js)**

❌ Current (`app/layout.tsx`):
```ts
export const metadata: Metadata = {
  robots: { index: true, follow: true, nosnippet: true },
}
```

✅ Recommended (if unintended):
```ts
export const metadata: Metadata = {
  robots: { index: true, follow: true, googleBot: { 'max-snippet': -1 } },
}
```
Report it as "confirm this is intended". Some publishers block snippets on purpose.

**Example 6: Definition buried mid-page**

❌ Current: the page titled "What is a Roth IRA?" spends two paragraphs on retirement planning before defining the term.

✅ Recommended: open with "A Roth IRA is an individual retirement account funded with after-tax money, so qualified withdrawals in retirement are tax-free." Then elaborate.

## Context-Aware Analysis

- **i18n**: check answers in each locale; flag locales where answers fall back to the default language.
- **Content vertical**: help centers and docs weight Categories 1, 2 and 4; glossaries and education weight Category 3; local businesses weight Category 7; forums weight QAPage in Category 6; news weights Category 8 and allows `speakable`.
- **Existing tooling**: if `@nuxtjs/seo`, `next-seo`, `astro-seo` or a CMS FAQ block is in use, validate its config rather than recommending a new package.

## Quality Assurance Checklist

- [ ] Answer pages listed and counted
- [ ] Question map used if present (new or old folder), or `/seo-questions` recommended
- [ ] Every robots directive source searched (meta, framework API, headers config, middleware, `data-nosnippet`, robots.txt)
- [ ] Accordion and tab answers checked for presence in the initial HTML, and main answers for visibility
- [ ] FAQ markup compared with visible text
- [ ] No FAQ or HowTo rich results promised
- [ ] Heuristics and limited features marked 🧪
- [ ] Live check section filled in or marked "Not run"
