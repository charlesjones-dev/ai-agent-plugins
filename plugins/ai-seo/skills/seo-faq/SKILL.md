---
name: seo-faq
description: "Build, update or validate visible FAQ sections and, if you want it, their FAQPage or QAPage JSON-LD. Drafts questions and answers from a page's own content, the latest question map or answers you supply, renders the FAQ and any markup from one data source, and checks existing markup against the visible text. Supports --dry-run."
argument-hint: "[build|update|gaps|validate] [page path] [markup=yes|no] [--dry-run]"
disable-model-invocation: true
---

# SEO FAQ Builder

You build FAQ sections that answer engines can lift cleanly (the AEO lens): one real question per item, an answer that opens with the answer, visible on the page in the initial HTML, with FAQPage (or QAPage) JSON-LD generated from the same data so the two never drift apart. You also validate FAQ markup that already exists.

The JSON-LD rules are in [references/json-ld.md](references/json-ld.md). Read its core rules and its FAQPage and QAPage section before writing or validating markup.

## Rules (NON-NEGOTIABLE)

1. **Visible first.** Every question in the markup appears on the page, with the same answer text. Google's structured data policies treat markup for hidden content as a violation.
2. **Answers come from the site or the user.** Draft answers only from content the site already publishes (cite the source `file:line`) or from text the user supplies. Never invent prices, policies, timelines, figures or guarantees.
3. **Answer first.** The first sentence of each answer answers the question. Keep answers short and link to the page with the detail.
4. **FAQPage vs QAPage.** FAQPage is for questions and answers the site wrote. QAPage is for one question with answers submitted by users (forums, community Q&A). Don't mix them.
5. **No rich-result promises.** Google stopped showing FAQ rich results on May 7, 2026 and removed its FAQPage documentation in June 2026. FAQPage is still valid Schema.org, and Microsoft says schema helps its systems understand content, so markup is optional 🧪. The visible FAQ is the part that matters; ask before adding markup.
6. **Mark up an FAQ once.** Don't put the same FAQ markup on every page (a site-wide footer FAQ, for example). Mark it up where the FAQ lives.
7. **One data source.** The visible FAQ and the JSON-LD are rendered from the same array, content collection or CMS field.
8. **Answers in the initial HTML, main answers visible.** Use `<details>`/`<summary>` or a toggle that hides with `hidden` or CSS; never render the answer only after a click. Google reads collapsed content, but Microsoft warns "AI systems may not render hidden content", so leave the most important questions open by default (`<details open>`) or answer them in the body text.
9. **No keyword padding.** Don't add near-duplicate questions that rephrase the same one ("How much is X?", "What does X cost?", "X price?"). Pick one phrasing.
10. **Accessible markup.** `<details>`/`<summary>`, or a `<button>` with `aria-expanded` and `aria-controls` pointing at the answer.

## Arguments

The text typed after the command holds the arguments. In Claude Code it is inserted here: `$ARGUMENTS`. In other agents, read it from the user's message. It may be empty.

| Argument | Answers | Values |
|----------|---------|--------|
| `build`, `update`, `gaps` or `validate` | Question 1, FAQ mode | Build a new FAQ, update an existing one, fill gaps from the question map, or validate FAQ markup across the site |
| A page path, such as `app/pricing/page.tsx` | Question 2, Page | A file in the repository |
| `markup=yes` or `markup=no` | Question 3, Markup | Add FAQPage (or QAPage) JSON-LD, or the visible FAQ only |
| `--dry-run` | | Print the would-be files and write nothing |

Ask only for what the arguments leave out. If no one can answer (an unattended run), use Validate mode unless a mode was given, and treat any other mode as `--dry-run`, since every drafted answer needs your review.

## Instructions

### Step 1: Context7 MCP Detection

Try the Context7 MCP server's `resolve-library-id` tool with the detected framework (its full name depends on the agent, for example `mcp__context7__resolve-library-id` in Claude Code). With Context7, confirm Schema.org `FAQPage` / `QAPage` properties and the framework's head API. Without it, say so in the summary.

### Step 2: Interactive Configuration

Use the AskUserQuestion tool, or ask in plain text if it isn't available. Skip any question the arguments answered.

- **Question 1:** "What do you want to do?"
  - Header: "FAQ mode"
  - Options:
    - "Build a new FAQ section for a page"
    - "Update an existing FAQ"
    - "Fill gaps from the question map" (uses the latest question map from `/seo-questions`)
    - "Validate FAQ markup across the site"
- **Question 2** (all modes except Validate): "Which page?" List up to three likely candidates you found (pages with an FAQ, pricing or product pages, help pages) plus a free-text option for a path.
- **Question 3** (all modes except Validate): "Add FAQPage JSON-LD as well as the visible FAQ?"
  - Options: "Yes, add markup" (optional; no Google feature uses it since May 2026, but it describes the Q&A to other engines) / "Visible FAQ only"
  - For a page where users submit answers, offer QAPage instead.

### Step 3: Framework and Existing FAQ Detection

1. Detect the framework from `package.json` dependencies (`next`, `nuxt`, `@tanstack/start` / `@tanstack/react-start`, `astro`, `@sveltejs/kit`, `@remix-run/*` / `react-router`), falling back to config files; otherwise vanilla HTML. Detect the docs folder (an existing `docs/`, `documentation/` or `.docs/`, or `docs/`) for the question map and validation results.
2. Find existing FAQ code: components or files named `faq`, `faqs`, `accordion`, `questions`; content collection entries or frontmatter with `faq`/`faqs` fields; CMS schemas with FAQ blocks; existing `FAQPage` or `QAPage` JSON-LD.
3. Reuse the existing FAQ component and data shape when there is one. Create new files only when nothing exists.

### Step 4: Gather Candidate Questions (build, update, fill-gaps modes)

Collect candidates, each tagged with its source:

- **Page content:** questions the page already answers in prose but doesn't ask (a "Refunds" paragraph answers "Can I get a refund?").
- **Site content:** related answers on other pages (support docs, policies) that belong in this FAQ.
- **Question map:** gaps assigned to this page in the latest question map: `<docs-dir>/seo-audit/question-map-latest.md`, or `<docs-dir>/aeo-audit/question-map-latest.md` from the ai-aeo plugin. If both exist, use the one with the newer **Date** line.
- **User:** ask "Any questions you want included?" (free text, optional).

Print the candidates as a numbered list with sources, then ask: "Keep all" / "Let me pick" (the user replies with numbers through the free-text option) / "Start over with my own list".

### Step 5: Draft Answers

For each kept question:

1. Find the answer in the site's content. Draft a short answer whose first sentence answers the question, then one or two sentences of detail, and a link to the full page if one exists.
2. Record the source (`file:line`) under the draft.
3. If the site doesn't contain the answer, mark it `NEEDS ANSWER` and ask the user for it. Don't guess.
4. Show each item for review:
   ```
   Q3. Can I change plans mid-cycle?
   Draft (38 words): Yes. You can upgrade or downgrade at any time from Settings → Billing, and the price difference is prorated to the day. ...
   Source: content/help/billing.md:22

   (a) accept  (e) edit  (s) skip
   ```

### Step 6: Render (skip in Validate mode)

1. **Data:** write or update one data source: a TypeScript/JSON data file, a content collection entry, frontmatter, or the existing CMS field. Example shape:
   ```ts
   export const faqs = [
     { question: 'Can I change plans mid-cycle?', answer: 'Yes. You can upgrade or downgrade at any time...' },
   ] as const
   ```
2. **Visible FAQ:** render a section with a heading such as "Frequently asked questions" and one item per entry, using `<details>`/`<summary>` or the existing accessible accordion. Answers stay in the HTML, and the first few (or the most important) items are open by default.
3. **JSON-LD** (if the user chose markup): generate FAQPage (or QAPage) from the same data, following [references/json-ld.md](references/json-ld.md), in the framework's head API or a server-rendered `<script type="application/ld+json">`.
4. **Placement:** near the content it supports, usually after the main content and before the footer.
5. Show the full diff and ask for confirmation before writing. In `--dry-run`, print and stop.

### Step 7: Validate (Validate mode, and after every build)

Check every page with FAQ or QAPage markup:

- Every marked-up question is visible on the page, and its answer text matches.
- Every visible FAQ item on a page with markup is in the markup (or the omission is deliberate).
- The same FAQ markup doesn't repeat across many pages.
- FAQPage isn't used for user-submitted Q&A, and QAPage isn't used for site-written FAQs.
- `QAPage` has `mainEntity` → `Question` with `name`, `answerCount`, and `acceptedAnswer` or `suggestedAnswer`.
- Answers open with the answer; flag answers over ~100 words 🧪.
- Answer text uses only simple HTML (paragraphs, lists, links, line breaks, emphasis); no scripts or complex markup.
- Valid JSON, `@context: "https://schema.org"`, absolute URLs.
- Answers render in the initial HTML.

Print the validation results in the terminal. Ask whether to save them as `<docs-dir>/seo-audit/faq-validation-YYYY-MM-DD-HHMMSS.md`; an unattended run doesn't save them.

### Step 8: Framework Patterns

**Next.js (App Router):**
```tsx
// app/pricing/faq.tsx (server component)
import { faqs } from './faq-data'

export function PricingFaq() {
  const ld = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqs.map(f => ({
      '@type': 'Question',
      name: f.question,
      acceptedAnswer: { '@type': 'Answer', text: f.answer },
    })),
  }
  return (
    <section aria-labelledby="faq-heading">
      <h2 id="faq-heading">Frequently asked questions</h2>
      {faqs.map((f, i) => (
        <details key={f.question} open={i < 3}>
          <summary>{f.question}</summary>
          <p>{f.answer}</p>
        </details>
      ))}
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(ld).replace(/</g, '\\u003c') }} />
    </section>
  )
}
```

**Nuxt:**
```vue
<script setup lang="ts">
import { faqs } from '~/data/pricing-faq'
useHead({
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      mainEntity: faqs.map(f => ({ '@type': 'Question', name: f.question, acceptedAnswer: { '@type': 'Answer', text: f.answer } })),
    }),
  }],
})
</script>

<template>
  <section aria-labelledby="faq-heading">
    <h2 id="faq-heading">Frequently asked questions</h2>
    <details v-for="(f, i) in faqs" :key="f.question" :open="i < 3">
      <summary>{{ f.question }}</summary>
      <p>{{ f.answer }}</p>
    </details>
  </section>
</template>
```

**Astro:** keep the FAQ in the page's content collection frontmatter (`faqs:`), render `<details>` items in the layout, and emit JSON-LD with `<script type="application/ld+json" set:html={JSON.stringify(ld)} />`.

**SvelteKit:** a `+page.ts` (or `+page.server.ts`) load returns `faqs`; render `{#each}` with `<details>`; JSON-LD in `<svelte:head>` with `{@html}` on a serialized string.

**TanStack Start:** data from the route loader; JSON-LD via route `head` `scripts`; `<details>` items in the component.

**Remix / React Router:** loader returns `faqs`; render server-side; JSON-LD in the route component or via `meta`.

**Vanilla HTML:** `<details>` items and a JSON-LD `<script>` written from the same source list (or a small build script if the FAQ repeats in several places).

Escape `<` as `<` when serializing JSON-LD into a script tag (as in the Next.js example) so answer text can't close the tag early. Apply the same escaping in the Nuxt, Astro and SvelteKit versions unless the framework's head API already escapes it.

### Step 9: Terminal Summary

```
SEO FAQ Complete
================
Mode:       <Build | Update | Fill gaps | Validate>
Framework:  <framework>
Knowledge:  <Context7 MCP | Training Data fallback>

Page:       <path or "site-wide validation">
Questions:  <n> added, <n> updated, <n> removed
Answers:    <n> from site content, <n> from you, <n> still NEEDS ANSWER
Data file:  <path>
Markup:     <FAQPage | QAPage | none (visible FAQ only)>, matches visible text: <yes | issues | n/a>

Validation:
  Pages with FAQ markup:      <n>
  Hidden or mismatched items: <n>
  Repeated across pages:      <n>
  Wrong type (FAQ vs QA):     <n>

Note: Google stopped showing FAQ rich results in May 2026. The visible FAQ is what readers and engines use.

Next: run /seo-audit aeo to re-score, or /seo-questions to find more gaps.
```

In `--dry-run`, say "DRY RUN — no files modified" and print the would-be files.

## Quality Assurance Checklist

- [ ] Existing FAQ component and data reused where present
- [ ] Every answer traced to site content or the user; none invented
- [ ] Each answer opens with the answer
- [ ] Visible FAQ and JSON-LD rendered from one source, following `json-ld.md`
- [ ] Answers present in the initial HTML, main ones open by default; accordion accessible
- [ ] User chose whether to add markup
- [ ] FAQPage vs QAPage chosen correctly
- [ ] No duplicate FAQ markup across pages
- [ ] No rich results promised
- [ ] Diff shown and confirmed before writing; `--dry-run` wrote nothing
