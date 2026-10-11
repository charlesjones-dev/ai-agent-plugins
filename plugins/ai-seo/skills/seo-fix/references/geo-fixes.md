# GEO Lens Fixes

Fixes for findings in a report's GEO section (IDs `GEO-n`, or any finding in a GEO report from the ai-geo plugin). They make the site easier for AI answer engines to reach, trust and cite. Anything that depends on the owner's intent (which bots to allow) or on facts only the owner has (profile URLs, sources, credentials, press coverage) is asked for, never guessed.

## Rules (NON-NEGOTIABLE)

1. **Never block AI bots wholesale without asking.** Ask separately about training crawlers, AI search indexers and user-triggered fetchers.
2. **robots.txt doesn't bind every bot.** OpenAI (ChatGPT-User), Perplexity (Perplexity-User), Meta (meta-externalfetcher), Amazon (Amzn-User) and Google (Google-Agent) say their user-triggered fetchers may not follow it. If the user needs a block to hold, point them to firewall or CDN rules; don't pretend robots.txt enforces it.
3. **Google-Extended doesn't remove a site from AI Overviews or AI Mode.** The controls for those are `nosnippet`, `data-nosnippet`, `max-snippet`, `noindex` and the Search Console setting "Search generative AI" → Exclude. Never block Googlebot or Bingbot unless the user explicitly wants out of search.
4. **Never invent identity or evidence.** `sameAs` URLs, author names, credentials, statistics, quotes, sources, reviews, testimonials and press coverage come from the user or the site. Prompt; don't guess.
5. **Never recommend client-only rendering for content.** Propose server rendering or static generation.
6. **Preserve deliberate bot policies.** Read existing robots.txt rules and confirm before changing them.
7. **Don't fake freshness.** Set `dateModified` from real changes (git history or the user), never to today's date by default.
8. **Prefer changes that help readers.** Google says there's no need to write a special way for AI search. Don't fragment content or add text only an engine would want.
9. **llms.txt files are created and validated by `/seo-llms-txt`.** This skill only adds discovery hints when the file already exists.

## Inputs

1. If the report's GEO Score Breakdown has no "Topical Authority" row, an ai-geo version earlier than 1.2.0 wrote it. Tell the user its categories differ from this version and recommend re-running `/seo-audit geo` first. Continue with the GEO findings only if they want to.
2. Read the GEO section's Live Check and Off-site Snapshot if present.

## Classification

**Safe-auto fixes** (show all diffs, confirm once as a batch):
- Add `dateModified` to existing `Article` / `BlogPosting` / `WebPage` JSON-LD, and `article:modified_time` where Open Graph is used, when the value can be read from frontmatter or the content file's last git commit.
- Fix JSON-LD validity: `http://schema.org` → `https://schema.org`, non-ISO dates, relative URLs, invalid JSON.
- Migrate microdata or RDFa to JSON-LD, preserving every value.
- **llms.txt discovery hints** (only if `/llms.txt` exists, and skipped if already present):
  - `<head>`: `<link rel="alternate" type="text/markdown" title="llms.txt" href="/llms.txt">` in the root layout via the framework head API (Next.js `metadata.alternates.types`, Nuxt `useHead`, Astro layout, SvelteKit `<svelte:head>`, Remix `meta`, vanilla `<head>`).
  - Sitemap: a `/llms.txt` entry. For Next.js `app/sitemap.ts`, push `{ url: '<base>/llms.txt', changeFrequency: 'monthly', priority: 0.5 }`. For a static `sitemap.xml`:
    ```xml
    <url>
      <loc>https://<domain>/llms.txt</loc>
      <changefreq>monthly</changefreq>
      <priority>0.5</priority>
    </url>
    ```
    If both files are generated at build time, the llms.txt generator must run before the sitemap generator. Warn with the suggested order; don't reorder silently.
  - robots.txt: a `# LLM index: https://<domain>/llms.txt` comment. Derive `<domain>` from the canonical URL, sitemap or env config; ask once if it can't be resolved. If a generator such as Next.js `app/robots.ts` can't express comments, suggest a static `public/robots.txt` instead.

**Intent-requiring fixes** (ask the user):
- **robots.txt AI bot rules.** Ask three questions:
  1. "Allow AI **training** crawlers? (GPTBot, ClaudeBot, Google-Extended, Applebot-Extended, meta-externalagent, Amazonbot, CCBot, MistralAI-Training, Bytespider)"
  2. "Allow AI **search** indexers, so the site can be cited in AI search answers? (OAI-SearchBot, Claude-SearchBot, PerplexityBot, Meta-WebIndexer, Amzn-SearchBot, MistralAI-Index, DuckAssistBot)"
  3. "Allow **user-triggered** fetchers, which load a page when someone asks an assistant about it? (ChatGPT-User, Claude-User, Perplexity-User, meta-externalfetcher, Amzn-User, MistralAI-User, Google-Agent) Several of these say robots.txt may not apply."

  Options for each: Allow all / Block all / Mixed. For Mixed, ask in free text which bots in that group to block. Googlebot, Bingbot and Applebot are left alone unless the user raises them. If robots.txt already has per-bot rules, show them and ask: Keep existing / Replace / Merge.
- **Retired bot names** (`anthropic-ai`, `Claude-Web`, `FacebookBot`): show each with its current equivalent (`ClaudeBot`, `Claude-User`, `meta-externalagent`) and ask whether to switch. Switching can turn a rule that did nothing into a real block, and can clash with rules already set for the current name, so fold it into the questions above rather than applying it automatically.
- **Blocks that must hold.** If the user blocks a group and wants it enforced, explain that robots.txt is a request and list where to enforce it (CDN bot or AI-crawler settings, WAF rules matching verified bots, host firewall). Don't write WAF config unless the project already manages it in code and the user asks.
- **Deployed policy differs from the repo** (from the live check, e.g. a CDN's managed robots.txt or default AI-crawler blocking): explain the difference and where it's configured. Manual.
- **Opting out of Google's AI features.** Only if the user wants it: explain the options (Search Console "Search generative AI" → Exclude, which keeps normal results; or `nosnippet` / `max-snippet`, which also shortens normal snippets). Google-Extended is not one of them. Apply a `nosnippet` or `max-snippet` change with the snippet-control confirmation in `aeo-fixes.md`, even when the report doesn't cover AEO.
- **`Content-Signal` lines** 🧪: offer to add a line that matches the answers above (e.g. `Content-Signal: search=yes, ai-input=yes, ai-train=no`). It states a preference; it enforces nothing.
- **Ineffective tags:** `noai` / `noimageai` meta tags. Explain no major AI provider documents them, and offer the robots.txt rule that expresses the same intent. Keep or remove.
- **User-agent logic in middleware** that blocks bots: keep or remove. Logic that changes content for bots is cloaking: propose removal.

**Content-requiring fixes** (propose and confirm each one):
- **Organization JSON-LD** with `name`, `url`, `logo`, `description` and `sameAs`, following `json-ld.md`. Prompt for the profile URLs (Wikidata, Wikipedia, LinkedIn, GitHub, Crunchbase, official social accounts, review-platform profiles the organization owns). Blank fields are skipped.
- **Person JSON-LD and author pages.** Prompt for each author's name, role, employer, short bio, credentials and profile URLs. Offer to scaffold `/authors/<slug>` pages with bylines linking to them.
- **"Reviewed by" lines** for health, finance, legal and safety content: reviewer name and credentials from the user.
- **Unsourced statistics.** For each one, ask: add a source (the user gives the URL and publisher), replace it with the site's own measured data and a methodology note, or remove the number. Never search for a plausible source and insert it unconfirmed.
- **Methodology notes** for data pages: sample, dates, method and limitations, drafted from the page and confirmed by the user. Offer `Dataset` JSON-LD 🧪 (used by Google Dataset Search, not Google Search).
- **Press coverage.** Link each "as featured in" logo to the article (URLs from the user), or build a Press page listing headline, publication and date.
- **Testimonials and case studies.** Ask for attribution (name, role, company) the user has permission to publish; leave anonymous ones as they are and note them.
- **Review profiles.** Ask for the URLs of the business's profiles on review platforms and directories; add them to the footer or About page and to `Organization.sameAs` where they're the organization's own profiles.
- **About page entity definition.** Draft the opening lines (who, what, where, since when) from existing site content and confirm.
- **Misleading superlatives.** Propose a specific, supportable alternative or ask for the evidence.

**Larger refactors** (plan first, confirm per file):
- Client-only content pages → server-rendered or static.
- **Topic hubs.** For each thin core topic, propose a hub page outline built from the existing pages (title, one-paragraph intro from existing copy, grouped links), plus the internal links to add: hub → subpages, subpages → hub, and between close siblings.
- Orphan pages: propose where each should be linked from.
- Thin or duplicate pages: propose merging into the stronger page with a redirect.
- Context-dependent paragraphs and walls of text: rewrite so each paragraph stands on its own and covers one idea. Don't fragment content into tiny pieces.
- Remove cloaking.

**Manual action items** (print in the summary, never automate):
- Off-site inconsistencies from the snapshot: third-party profiles with an old name, wrong description or outdated pricing.
- Wikidata item (if the organization meets Wikidata's notability policy), review platforms, industry directories, independent coverage, disclosed community participation.
- Track citations: Bing Webmaster Tools AI Performance, Search Console's Generative AI performance report, server logs.
- llms.txt directory submissions: https://llmstxt.site and https://directory.llmstxt.cloud (web forms).
- CDN or host bot settings, if the live check found differences.

## Applying robots.txt Changes

1. Find the robots source (`public/robots.txt`, project root, `static/robots.txt`, or a generator such as `app/robots.ts`).
2. Read the existing rules.
3. Ask the three questions.
4. Show the proposed robots.txt as a diff and confirm.
5. For generated robots files, emit framework source rather than a raw file. Next.js example (training blocked; AI search and user-triggered fetchers allowed):
   ```ts
   // app/robots.ts
   import type { MetadataRoute } from 'next'

   const training = ['GPTBot', 'ClaudeBot', 'Google-Extended', 'Applebot-Extended', 'meta-externalagent', 'Amazonbot', 'CCBot', 'MistralAI-Training', 'Bytespider']
   const aiSearch = ['OAI-SearchBot', 'Claude-SearchBot', 'PerplexityBot', 'Meta-WebIndexer', 'Amzn-SearchBot', 'MistralAI-Index', 'DuckAssistBot']
   const userFetchers = ['ChatGPT-User', 'Claude-User', 'Perplexity-User', 'meta-externalfetcher', 'Amzn-User', 'MistralAI-User', 'Google-Agent']

   export default function robots(): MetadataRoute.Robots {
     return {
       rules: [
         { userAgent: '*', allow: '/' },
         { userAgent: training, disallow: '/' },
         { userAgent: aiSearch, allow: '/' },
         { userAgent: userFetchers, allow: '/' },
       ],
       sitemap: 'https://<domain>/sitemap.xml',
     }
   }
   ```

Collect content inputs with AskUserQuestion (free text through "Other" where needed), or in plain text, then show each proposal:
```
File: app/about/page.tsx
Adding Organization JSON-LD with sameAs.

Profile URLs (blank to skip):
  Wikidata:
  LinkedIn:
  GitHub:
  Crunchbase:
  Other:

Proposed JSON-LD:
  <preview>

(a) accept  (e) edit  (s) skip
```

## Framework Specifics

- **Next.js (App Router):** robots → `app/robots.ts` (as above); sitemap → `app/sitemap.ts`; dates → `generateMetadata()` with `openGraph.modifiedTime` and JSON-LD `dateModified`; author pages → `app/authors/[slug]/page.tsx` with `generateStaticParams`.
- **Next.js (Pages Router):** `next/head` for meta and JSON-LD; `public/robots.txt`.
- **Nuxt:** `useSeoMeta({ articleModifiedTime })`; `@nuxtjs/robots` config or `public/robots.txt`.
- **TanStack Start:** route `head: () => ({ meta: [...] })` for `article:modified_time`.
- **Astro:** content collection `updatedDate`; `public/robots.txt` or `src/pages/robots.txt.ts`.
- **SvelteKit:** `<svelte:head>` in `+layout.svelte` / `+page.svelte`; `src/routes/robots.txt/+server.ts` or `static/robots.txt`.
- **Remix / React Router:** `meta` export; a resource route for robots.txt.
- **Vanilla HTML:** direct `<head>` edits; robots.txt at the web root.

## Examples

**Example 1: robots.txt (intent-requiring)**

Existing rules block GPTBot and OAI-SearchBot. The user answers: training = block, AI search = allow, user-triggered = allow.

```diff
 User-agent: GPTBot
 Disallow: /

-User-agent: OAI-SearchBot
-Disallow: /
+User-agent: OAI-SearchBot
+Allow: /
+
+User-agent: ClaudeBot
+Disallow: /
+
+User-agent: Claude-SearchBot
+Allow: /
```
Summary note: "OpenAI says robots.txt may not apply to ChatGPT-User. If you need user-triggered fetches blocked, use your CDN's bot rules."

**Example 2: Unsourced statistic (content-requiring)**

```
File: content/blog/reporting-costs.md:12
"Most teams waste a third of their week on manual reporting."

This number has no source. Choose:
  (a) Add a source  → publisher, year and URL
  (b) Use our own data → figure, sample and how it was measured
  (c) Remove the number
```

**Example 3: Organization with sameAs (content-requiring)**

The user supplies LinkedIn and GitHub and leaves Wikidata blank. Build it with the Organization pattern in `json-ld.md`, listing only the two URLs given.

**Example 4: dateModified from git (safe-auto)**

```tsx
// app/blog/[slug]/page.tsx
export async function generateMetadata({ params }): Promise<Metadata> {
  const post = await getPost(params.slug) // modifiedTime from the file's last commit
  return {
    openGraph: {
      type: 'article',
      publishedTime: post.publishedTime,
      modifiedTime: post.modifiedTime,
    },
  }
}
```

**Example 5: Topic hub (larger refactor)**

Twelve posts about one topic link only to the homepage. Proposal: `app/guides/<topic>/page.tsx` with an intro taken from the strongest post, the twelve posts grouped under three subtopic headings, and a "Part of the <topic> guide" link added to each post. Shown as a plan, then per-file diffs.

## Terminal Summary Block

```
robots.txt: <created | updated | unchanged>
  Training bots allowed:        <list or "none">
  AI search bots allowed:       <list or "none">
  User-triggered bots allowed:  <list or "none">
  Note: <ChatGPT-User, Perplexity-User, ... may not follow robots.txt | n/a>

GEO changes by category:
  AI Crawler Access:              <n>
  Technical AI Accessibility:     <n>
  Topical Authority:              <n>
  Original Research & Evidence:   <n>
  Expert Perspectives & Authorship: <n>
  External Validation:            <n>
  Entity Clarity:                 <n>
  Extractable Passages:           <n>
  Content Freshness:              <n>
  llms.txt & Markdown Access:     <n>

Manual next steps:
  - <off-site fixes from the snapshot>
  - <review platforms / directories / Wikidata>
  - <CDN or host bot settings>
  - Track citations: Bing Webmaster Tools AI Performance, Search Console Generative AI report
  - llms.txt directories: https://llmstxt.site, https://directory.llmstxt.cloud
```

Hand-off line for the summary: `/seo-llms-txt` (<llms.txt missing or stale | n/a>).

## Checklist

- [ ] Pre-1.2.0 GEO reports flagged
- [ ] Three separate bot-group questions asked; existing rules shown before changes
- [ ] robots.txt limits explained for user-triggered fetchers
- [ ] Google-Extended not used as an AI Overviews opt-out
- [ ] No profile URL, author, credential, statistic, source, quote, review or press item invented
- [ ] Dates from real changes only
- [ ] Manual action items printed
