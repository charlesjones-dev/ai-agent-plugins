# AEO Lens Fixes

Fixes for findings in a report's AEO section (IDs `AEO-n`, or any finding in an AEO report from the ai-aeo plugin). They make each answer easy to lift: answer first, under a clear question, in real HTML that's present when the page loads. Anything that changes what the site says, or that may have been set on purpose, is proposed to the user first.

## Rules (NON-NEGOTIABLE)

1. **Never write facts the site doesn't contain.** Answer-first rewrites reorder and tighten existing copy. If the answer isn't on the page or elsewhere in the site, ask the user for it.
2. **Never add FAQ markup for content that isn't visible.** Generate FAQPage JSON-LD from the same data that renders the visible FAQ (see `json-ld.md`).
3. **Never remove snippet controls without asking.** `noindex`, `nosnippet`, `max-snippet`, `data-nosnippet`, Bing's `nocache` / `noarchive` and `X-Robots-Tag` may protect paywalled, licensed or legal content.
4. **Never promise rich results.** Google stopped showing FAQ rich results on May 7, 2026 and HowTo rich results in September 2023. Say what the change does for readers and answer extraction instead.
5. **Don't rewrite for engines at the reader's expense.** Google says there's no need to write in a special way for AI search. Every rewrite should also make the page clearer for people.
6. **Keep the visible design.** When converting div lists or grid "tables" to real HTML, keep class names and add style resets so the page looks the same.
7. **New FAQ sections are built by `/seo-faq`.** Question gaps and competing pages come from `/seo-questions`.

## Inputs

Besides the report, read the latest question map if there is one: `<docs-dir>/seo-audit/question-map-latest.md`, or `<docs-dir>/aeo-audit/question-map-latest.md` from the ai-aeo plugin (use the newer by its **Date** line if both exist). Its "competing pages" entries feed the larger refactors below.

## Classification

**Safe-auto fixes** (show all diffs, confirm once as a batch):
- Convert div- or `<br>`-based lists to `<ol>` / `<ul>` when the markup maps one-to-one. Keep the classes; add `list-style: none; padding: 0` (or the project's utility classes) if the old markup had no bullets.
- Fix JSON-LD validity: `http://schema.org` → `https://schema.org`, non-ISO dates → ISO 8601, relative URLs → absolute, invalid JSON.
- Migrate microdata or RDFa to JSON-LD, preserving every value.
- Remove FAQ JSON-LD entries for questions that aren't visible on the page.
- Change forum or community Q&A pages from `FAQPage` to `QAPage` when the question, answers, authors and dates are already in the data.

**Intent-requiring fixes** (ask per directive):
- **Snippet controls.** Each `noindex`, `nosnippet`, `max-snippet`, `data-nosnippet`, `nocache`, `noarchive` or `X-Robots-Tag` on answer pages. Ask:
  - "`<directive>` at `<file:line>` covers `<scope>`. Keep it, remove it, or narrow it to `<suggested scope>`?"
  - Options: Keep / Remove / Narrow scope, plus Set `max-snippet:-1` when the directive is `nosnippet` or `max-snippet`
  - Show the existing line and the proposed change before editing.
- The same FAQ block marked up on many pages. Ask which page should carry the markup (usually the dedicated FAQ page), then remove it from the rest. The visible FAQ can stay everywhere.
- Existing `HowTo` markup: keep (valid Schema.org, harmless) or remove (no longer a Google feature). Default to keep.
- Missing `FAQPage` JSON-LD on a visible FAQ. Ask once for the whole site: "Add FAQPage markup to visible FAQs? No Google feature uses it since May 2026; Microsoft says schema helps its systems understand content." If yes, build it from the FAQ's own data (or the visible text verbatim when it's hard-coded).

**Content-requiring fixes** (propose and confirm each one):
- **Answer-first rewrites.** Move the sentence that answers the question to the top and cut the preamble. Show before and after with word counts. If no sentence on the page answers the question, ask the user for the answer.
- **Question headings.** Propose a natural question for each keyword-style heading on an answer page. The user accepts, edits or skips.
- **Definitional openings.** Draft "X is a Y that Z" from the page's own content and ask the user to confirm it's accurate.
- **Summary blocks** for long pages: draft from the page's own headings and answers.
- **Visible "last updated" dates** on time-sensitive answers. Offer the content file's last git commit date as the default and let the user change it; the date must reflect a real review.
- **LocalBusiness data.** Prompt for name, address, phone, hours and coordinates. Never guess.

**Larger refactors** (plan first, confirm per file):
- Accordions, tabs and "read more" toggles that render answers only after interaction → patterns that keep the answer in the HTML (`<details>`, the `hidden` attribute, `v-show`, CSS classes). Keep the existing animation and state where possible.
- Main answers collapsed by default → expanded by default, or moved into the body text with the accordion kept for secondary questions. Microsoft warns AI systems may not read hidden content.
- CSS-grid or flexbox "tables" → `<table>` with `<thead>` and `<th>` when the structure is clear.
- Client-only answer pages → server-rendered or static.
- Long pages → question-led sections.
- Definitions scattered across the site → a glossary page (one term per heading).
- Competing pages from the question map → choose one owner per question; the others link to it (or are merged with a redirect if the user agrees).

**Hand-offs** (print the command for the user to run, don't do the work here):
- New FAQ sections, or FAQs for question-map gaps → `/seo-faq`.
- Missing or unmapped target questions → `/seo-questions`.
- Authorship, sources, entity `sameAs` and AI crawler rules belong to the GEO lens. If this report covers GEO, they're fixed in the same run; otherwise suggest `/seo-audit geo` first.

## Framework Specifics

- **Next.js (App Router):** robots directives in `metadata.robots` / `generateMetadata()` (`robots: { index, follow, nosnippet, googleBot: { 'max-snippet': -1 } }`); headers in `next.config.*` `headers()` or `middleware.ts`. Accordions: move answer text out of `{open && …}`; use `<details>`, or keep the client toggle but render the text with `hidden={!open}`.
- **Next.js (Pages Router):** `next/head` for robots meta and JSON-LD; same accordion rule.
- **Nuxt:** `useSeoMeta({ robots })`, `routeRules` headers; `v-if` → `v-show` for answers.
- **TanStack Start:** route `head: () => ({ meta: [{ name: 'robots', content: '…' }] })`.
- **Astro:** layout `<head>` for robots meta; `client:only` islands that hold answer text → server-rendered components; `<details>` for FAQ items.
- **SvelteKit:** `<svelte:head>`; `{#if open}` → `hidden={!open}` or `<details>`; remove `export const ssr = false` from answer routes after confirmation.
- **Remix / React Router:** `meta` export; render answer text from the loader on the server.
- **Vanilla HTML:** direct edits; `X-Robots-Tag` in the server or CDN config.

## Examples

**Example 1: Snippet control (intent-requiring)**

Finding: `app/(docs)/layout.tsx:8` sets `robots: { nosnippet: true }` for every docs page.

Prompt:
```
nosnippet at app/(docs)/layout.tsx:8 covers all 140 docs pages.
It keeps docs text out of featured snippets and Google's AI features.

  (a) Keep it
  (b) Remove it
  (c) Narrow it to the pages that need it
  (d) Replace with max-snippet:-1
```

User picks (b). Apply:
```diff
 export const metadata: Metadata = {
-  robots: { index: true, follow: true, nosnippet: true },
+  robots: { index: true, follow: true },
 }
```

**Example 2: Div list to `<ol>` (safe-auto)**

```diff
-<div class="steps">
-  <div class="step">Open Settings</div>
-  <div class="step">Choose Billing</div>
-</div>
+<ol class="steps">
+  <li class="step">Open Settings.</li>
+  <li class="step">Choose Billing.</li>
+</ol>
```
Add `.steps { list-style: none; padding: 0; }` if the design had no numbers. Keep the numbers visible if the steps are sequential.

**Example 3: Accordion answer kept in the DOM (larger refactor, React)**

```diff
-<button onClick={() => setOpen(!open)}>{item.question}</button>
-{open && <p>{item.answer}</p>}
+<button aria-expanded={open} aria-controls={`faq-${i}`} onClick={() => setOpen(!open)}>
+  {item.question}
+</button>
+<p id={`faq-${i}`} hidden={!open}>{item.answer}</p>
```

**Example 4: FAQPage from existing data (after the user opts in)**

The page already renders `faqs` from `src/data/pricing-faq.ts`. Add markup from the same array, using the FAQPage pattern and the framework injection in `json-ld.md`:
```tsx
import { faqs } from '@/data/pricing-faq'

const faqLd = {
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  mainEntity: faqs.map(f => ({
    '@type': 'Question',
    name: f.question,
    acceptedAnswer: { '@type': 'Answer', text: f.answer },
  })),
}
```

## Terminal Summary Block

```
AEO snippet controls:
  Kept:     <list or "none">
  Removed:  <list or "none">
  Narrowed: <list or "none">

AEO changes by category:
  Answer-First Formatting:        <n>
  Question Coverage & Headings:   <n>
  Concise Definitions:            <n>
  Snippet-Ready Structure:        <n>
  Snippet Eligibility & Indexing Controls: <n>
  FAQ Sections & Structured Data: <n>
  Voice & Assistant Readiness:    <n>
  Answer Trust Signals:           <n>
  Technical Answer Accessibility: <n>
```

Hand-off lines for the summary: `/seo-faq` (<n> pages need a new or updated FAQ section) and `/seo-questions` (<run to map target questions | map is current>).

## Checklist

- [ ] Every snippet-control change confirmed by the user
- [ ] No answer, date or business detail invented
- [ ] FAQPage added only after the user opted in, and built from the visible FAQ's data
- [ ] Visible design preserved when converting markup
- [ ] Hand-offs to `/seo-faq` and `/seo-questions` printed
