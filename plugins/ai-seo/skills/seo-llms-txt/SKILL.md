---
name: seo-llms-txt
description: "Generate, update and validate llms.txt and llms-full.txt, a Markdown site index some coding tools read (Google Search ignores it). Analyzes site structure, writes a spec-compliant index and optional full-content companion, wires it into the framework build, adds discovery hints, and validates existing files against the llmstxt.org spec. Supports --dry-run."
argument-hint: "[generate|update|validate] [full=yes|no] [type=docs|blog|product|mixed] [--dry-run]"
disable-model-invocation: true
---

# llms.txt Generator

You are a specialist in the `llms.txt` protocol (https://llmstxt.org/), proposed by Jeremy Howard in 2024. `llms.txt` is a Markdown index of a website designed for LLM consumption: the LLM equivalent of `sitemap.xml`, but optimized for human-readable, content-first retrieval. `llms-full.txt` is the companion that carries the full content rather than only links.

Your job: detect the project, analyze its content, and produce correctly formatted `llms.txt` (and optionally `llms-full.txt`), or validate existing ones and flag problems. In the ai-seo plugin this belongs to the GEO lens; `/seo-audit geo` scores it.

**Set expectations honestly.** Google says Google Search ignores llms.txt, and no other major AI search provider has said it uses the file for ranking or citation. Some coding tools read it when loading documentation, and Chrome Lighthouse's agentic browsing audit checks for it. It's cheap to publish and keep current; it is not a citation lever. Tell the user this once, before generating.

## LLM Knowledge Gap Corrections (NON-NEGOTIABLE)

1. **`llms.txt` is a real proposal; don't dismiss it or oversell it.** It exists and some tools read it, but Google Search ignores it and no AI search provider has said it affects citations.
2. **`llms.txt` and `llms-full.txt` are different files.** `llms.txt` = concise Markdown index. `llms-full.txt` = full content. Never merge them.
3. **Markdown throughout.** No HTML fallback. The spec is strict Markdown.
4. **Structure matters.** Required: H1 title (the only section the spec requires). Recommended: a blockquote description, H2 section headers, bulleted links with descriptive text and one-line summaries.
5. **Link to Markdown content where possible.** If a page has a `.md` companion, link to that rather than the `.html`-rendered URL.
6. **Concise index, not a sitemap dump.** `llms.txt` should curate the most useful entry points, not list every URL. `llms-full.txt` can be expansive.
7. **Do not invent content.** If content doesn't exist, don't fabricate titles or summaries. Read real files or prompt the user.
8. **Location matters.** `llms.txt` must be served from the web root (`/llms.txt`), not nested. Use framework-idiomatic static-asset placement.

## Arguments

The text typed after the command holds the arguments. In Claude Code it is inserted here: `$ARGUMENTS`. In other agents, read it from the user's message. It may be empty.

| Argument | Answers | Values |
|----------|---------|--------|
| `generate`, `update` or `validate` | Question 1, Mode | Create `llms.txt`, refresh it from current content, or check it against the spec |
| `full=yes` or `full=no` | Question 2, Full text | Whether to also generate `llms-full.txt` |
| `type=docs`, `type=blog`, `type=product` or `type=mixed` | Question 3, Site type | How to organize the sections |
| `--dry-run` | | Print the would-be files and write nothing |

Ask only for what the arguments leave out. If no one can answer (an unattended run), use Validate mode when `llms.txt` exists and Generate mode when it doesn't, without `llms-full.txt`, with the site type inferred from the content. Skip the discovery-hint offers in Step 9 and list them in the summary as not added.

## Instructions

### Step 1: Context7 MCP Detection

Try the Context7 MCP server's `resolve-library-id` tool with `"llmstxt"` or the detected framework (its full name depends on the agent, for example `mcp__context7__resolve-library-id` in Claude Code). Record the mode. If unavailable, operate from training data and say so.

### Step 2: Interactive Configuration

Use the AskUserQuestion tool, or ask in plain text if it isn't available. Skip any question the arguments answered.

- Question 1: "What do you want to do?"
  - Header: "Mode"
  - Options:
    - "Generate new llms.txt" (creates if missing)
    - "Update existing llms.txt" (refreshes from current content)
    - "Validate existing llms.txt" (spec compliance check only)

- Question 2 (if generating/updating): "Also generate llms-full.txt, the full-content companion?"
  - Header: "Full text"
  - Options: "Yes" / "No, index only"

- Question 3 (if generating/updating): "Approximate site type?"
  - Header: "Site type"
  - Options: "Documentation" / "Blog or publication" / "Product or company site" / "Mixed" (a portfolio counts as a product or company site)

The site type guides section organization (docs → by topic or guide level, blog → by recency or category, product → by feature, etc.).

### Step 3: Framework Detection

Read `package.json` dependencies (`next`, `nuxt`, `@tanstack/start` / `@tanstack/react-start`, `astro`, `@sveltejs/kit`, `@remix-run/*` / `react-router`), falling back to config files; otherwise vanilla HTML. Record the framework and version, then determine the correct static-asset path:

| Framework | `llms.txt` path |
|-----------|-----------------|
| Next.js | `public/llms.txt` OR `app/llms.txt/route.ts` |
| Nuxt | `public/llms.txt` OR `server/routes/llms.txt.ts` |
| TanStack Start | `public/llms.txt` OR route handler |
| Astro | `public/llms.txt` OR `src/pages/llms.txt.ts` |
| SvelteKit | `static/llms.txt` OR `src/routes/llms.txt/+server.ts` |
| Remix | `public/llms.txt` OR `app/routes/llms[.]txt.ts` |
| Vanilla HTML | web root `/llms.txt` |

Prefer static files for simple content; use route handlers only when dynamic generation is needed (e.g., auto-sync from a CMS).

### Step 4: Content Analysis

Discover the site's content:

1. Glob content sources based on the framework:
   - Next.js App Router: `app/**/page.{mdx,md,tsx}` + content directories.
   - Nuxt: `content/**/*.md` if Nuxt Content is present; else route pages.
   - Astro: `src/content/**/*.{md,mdx}`.
   - SvelteKit: `src/routes/**/+page.{md,svelte}`.
   - Remix: `app/routes/**/*.{md,mdx,tsx}`.
   - Vanilla: crawl `*.html` files.
2. Extract for each discovered page:
   - URL (derive from the path + detected base URL; prompt for the domain if it can't be resolved)
   - Title (frontmatter → H1 → filename fallback)
   - One-line description (frontmatter description → first paragraph truncated)
   - Markdown companion URL if present (same path + `.md` suffix or content-collection source)
   - Last modified date (frontmatter → git mtime)
3. Classify pages by type if multi-section:
   - Documentation: grouped by topic or Getting Started / Guides / Reference / API
   - Blog: posts by year or category
   - Product: features / pricing / docs / changelog
   - Portfolio: projects / about / contact
4. Identify "essential" pages (About, Getting Started, overview docs) that MUST appear in `llms.txt`.

### Step 5: Generate or Validate

#### Generation path

Emit `llms.txt` per the spec:

```markdown
# <Site Name>

> <One-sentence description of what the site is and what a reader/LLM will find here.>

<Optional: a paragraph (not a blockquote) of additional context, scope, or positioning. Keep concise.>

## <Section 1, e.g. Documentation>

- [<Page title>](<absolute URL or .md companion URL>): <one-line summary>
- [<Page title>](<URL>): <one-line summary>

## <Section 2, e.g. Guides>

- [<Page title>](<URL>): <one-line summary>

## Optional

- [<Secondary resource>](<URL>): <one-line summary; lower priority for LLM retrieval>
```

Rules applied during generation:
- Always absolute URLs (prompt for the base domain if it can't be resolved from config).
- Link to `.md` companion URLs when available; otherwise the HTML URL.
- Section headers are H2. Sub-groups can use unordered lists with sub-headers only if necessary.
- The spec treats the `## Optional` section as lower-priority items. Use it for deprioritized but still-relevant content.
- Keep the total file under ~8KB where possible (it's a concise index). If content exceeds that, move detail into `llms-full.txt`.

#### `llms-full.txt` generation

If requested, emit the full-content companion. Structure:

```markdown
# <Site Name>: Full Content Export

> Full Markdown export of <site-name> content for LLM consumption. Generated on <ISO timestamp>.

---

## <Page Title>

Source: <URL>
Last modified: <date>

<Full Markdown content of the page>

---

## <Next Page Title>

<...>
```

Rules:
- One page per `## <Title>` section, separated by `---`.
- Include the source URL and last-modified line immediately under the heading.
- Insert the actual Markdown content (not HTML, not rendered output).
- For Next.js/MDX, serialize from the source `.mdx` file (strip JSX components to plain text where they appear inline; keep frontmatter only as source metadata lines above the content).
- Order pages by importance: essentials first, then main sections, then optional or archived.

#### Validation path

For an existing `llms.txt`, report:
- H1 title present: ✅/❌
- Blockquote description present immediately after the H1: ✅/❌
- Valid Markdown (parse test): ✅/❌
- All links reachable (spot-check): ✅/❌ with a list of broken links
- Links point to Markdown-accessible URLs where possible: ✅/⚠️ with a list of HTML-only links that have `.md` companions available
- File size reasonable (< ~8KB for the index): ✅/⚠️ with the byte count
- Freshness: content source files newer than the `llms.txt` mtime; list stale sections

Print the validation results in the terminal. Offer to save them as `<docs-dir>/seo-audit/llms-txt-validation-YYYY-MM-DD-HHMMSS.md` (`<docs-dir>` is an existing `docs/`, `documentation/` or `.docs/`, or `docs/`). Never write them next to `llms.txt`, where the site would publish them.

### Step 6: Framework-Specific Generation

**Next.js (static):**
Write `public/llms.txt`. Optional: add a build script.
```json
// package.json
"scripts": {
  "build:llms": "tsx scripts/generate-llms-txt.ts",
  "build": "npm run build:llms && next build"
}
```

**Next.js (dynamic route):**
```ts
// app/llms.txt/route.ts
export async function GET() {
  const body = await buildLlmsTxt()
  return new Response(body, {
    headers: { 'Content-Type': 'text/markdown; charset=utf-8' },
  })
}
```

**Nuxt:**
- Static: `public/llms.txt`.
- Dynamic: `server/routes/llms.txt.ts` returning the Markdown string with a `text/markdown` content type.

**Astro (dynamic via endpoint):**
```ts
// src/pages/llms.txt.ts
import type { APIRoute } from 'astro'
import { getCollection } from 'astro:content'

export const GET: APIRoute = async () => {
  const posts = await getCollection('blog')
  const body = buildLlmsTxt(posts)
  return new Response(body, { headers: { 'Content-Type': 'text/markdown; charset=utf-8' } })
}
```

**SvelteKit:**
```ts
// src/routes/llms.txt/+server.ts
import type { RequestHandler } from './$types'

export const GET: RequestHandler = async () => {
  const body = await buildLlmsTxt()
  return new Response(body, { headers: { 'Content-Type': 'text/markdown; charset=utf-8' } })
}
```

**TanStack Start:**
A route handler at the static-asset level, or a server function that writes `public/llms.txt` during the build.

**Remix:**
```ts
// app/routes/llms[.]txt.ts
import type { LoaderFunctionArgs } from '@remix-run/node'
export async function loader({ request }: LoaderFunctionArgs) {
  return new Response(await buildLlmsTxt(), {
    headers: { 'Content-Type': 'text/markdown; charset=utf-8' },
  })
}
```

**Vanilla HTML:**
Write directly to the web root. Optional: a small Node or Python script to regenerate it from a manifest file.

For any framework where a static file is written, also offer to add a build-time generator script so `llms.txt` stays in sync automatically.

### Step 7: Build Pipeline Order (IMPORTANT)

When both `llms.txt` and `sitemap.xml` are generated at build time, **`llms.txt` MUST be generated before the sitemap**. The sitemap includes a `/llms.txt` entry and should reference the file's real mtime; if the sitemap is generated first, it either misses the entry or records a stale timestamp.

Framework by framework:

- **Next.js:** no order issue when both are served through the Metadata API (`app/sitemap.ts` + `app/llms.txt/route.ts`). Both resolve per request (or during `next build` through the same graph), so no explicit ordering is needed. It only matters if a custom `scripts/generate-llms-txt.ts` writes `public/llms.txt` at build time; in that case run it before `next build`:
  ```json
  "scripts": {
    "build:llms": "tsx scripts/generate-llms-txt.ts",
    "build":      "npm run build:llms && next build"
  }
  ```
- **Nuxt:** if a custom generator script runs alongside `@nuxtjs/sitemap`, run the llms.txt writer in a pre-build hook (a `"prebuild"` script, or a Nitro plugin ordered before the sitemap module).
- **Astro (endpoint vs static):** an endpoint (`src/pages/llms.txt.ts`) resolves at request time, so there's no order issue. A static `public/llms.txt` written by a script needs to run before `astro build` so `@astrojs/sitemap`'s `customPages` and mtime are accurate:
  ```json
  "scripts": {
    "build:llms": "tsx scripts/generate-llms-txt.ts",
    "build":      "npm run build:llms && astro build"
  }
  ```
- **Vite / SvelteKit / Remix / TanStack Start (custom build scripts):** whenever a Vite plugin or npm script generates both, run llms.txt first and the sitemap second. If the user has a single orchestrating script, print a warning and suggest the corrected order rather than silently reshuffling it.

### Step 8: Markdown Companion Routes (optional) 🧪

Markdown copies of pages help coding assistants that read documentation, and some CDNs (Cloudflare's Markdown for Agents) can serve them to clients that send `Accept: text/markdown`. They are **not** an AI search lever: Google's guide says Markdown isn't needed, and Google's and Bing's search representatives have said Markdown copies for bots are unnecessary. Offer them only for developer documentation, or when the site already keeps its content in Markdown:

- Next.js: `app/docs/[slug].md/route.ts` reading from the same MDX source.
- Astro: a `src/pages/docs/[slug].md.ts` endpoint returning the content collection's raw Markdown.
- SvelteKit/Remix: an analogous route returning `text/markdown`.

A Markdown copy must say the same thing as the HTML page. If they exist, reference the `.md` URLs in `llms.txt`.

### Step 9: Wire Discoverability Signals (after writing)

After writing `llms.txt`, offer these discovery hints. Skip each one if it's already present or doesn't apply. 🧪 They help tools that look for the file find it; they don't affect search rankings or AI citations.

**1. `<link rel="alternate">` in `<head>`**

Prompt: "Also add a `<head>` link hint pointing at `/llms.txt`? (recommended)"

On accept, wire it through the framework-idiomatic head API. Skip silently if the hint already exists anywhere in the resolved head.

- **Next.js (App Router):** `app/layout.tsx` metadata:
  ```ts
  export const metadata: Metadata = {
    alternates: {
      types: { 'text/markdown': '/llms.txt' },
    },
  }
  ```
- **Nuxt:** root layout or `app.vue`:
  ```ts
  useHead({
    link: [{ rel: 'alternate', type: 'text/markdown', title: 'llms.txt', href: '/llms.txt' }],
  })
  ```
- **Vue + `@unhead/vue`:** the equivalent `useHead` call in the root component.
- **Astro:** in the base layout's `<head>`:
  ```astro
  <link rel="alternate" type="text/markdown" title="llms.txt" href="/llms.txt" />
  ```
- **SvelteKit:** `src/routes/+layout.svelte`:
  ```svelte
  <svelte:head>
    <link rel="alternate" type="text/markdown" title="llms.txt" href="/llms.txt" />
  </svelte:head>
  ```
- **Remix:** root `meta` export:
  ```ts
  export const meta: MetaFunction = () => [
    { tagName: 'link', rel: 'alternate', type: 'text/markdown', title: 'llms.txt', href: '/llms.txt' },
  ]
  ```
- **Vanilla HTML:** inject into each page's `<head>`:
  ```html
  <link rel="alternate" type="text/markdown" title="llms.txt" href="/llms.txt">
  ```

**2. `/llms.txt` entry in `sitemap.xml`**

Prompt: "Add `/llms.txt` to your sitemap so sitemap-reading crawlers discover it?"

Detect the sitemap source and patch it. Skip if the entry is already present, or if the project has no sitemap.

- **Next.js `app/sitemap.ts`:** append:
  ```ts
  { url: `${SITE}/llms.txt`, changeFrequency: 'monthly' as const, priority: 0.5 }
  ```
- **Static `public/sitemap.xml`:** insert before `</urlset>`:
  ```xml
  <url>
    <loc>https://<domain>/llms.txt</loc>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>
  ```
- **Nuxt `@nuxtjs/sitemap`:** add it to `sitemap.urls` or the module config.
- **Astro `@astrojs/sitemap`:** use the `customPages` option.

The order rule in Step 7 applies when both files are generated at build time.

**3. `robots.txt` comment**

Prompt: "Add a `# LLM index` comment pointing at `/llms.txt` in `robots.txt`?"

On accept, append (or insert near the top):
```
# LLM index: https://<domain>/llms.txt
```
Derive `<domain>` from the detected base URL, sitemap or env config. Prompt once if it can't be resolved. For frameworks that generate robots.txt through a route (Next.js `app/robots.ts`, SvelteKit `+server.ts`, etc.), if the generator can't express comments cleanly, direct the user to add it to a static `public/robots.txt` instead.

### Step 10: Terminal Summary

```
llms.txt Complete
=================
Mode:       <Generate | Update | Validate | + llms-full.txt>
Framework:  <framework>
Knowledge:  <Context7 MCP | Training Data fallback>

llms.txt:
  Path:         <path>
  Status:       <created | updated | validated | unchanged>
  Size:         <N bytes>
  Sections:     <count>
  Links:        <count>
  .md links:    <count> / <total>

llms-full.txt:
  Path:         <path or "not generated">
  Size:         <N bytes>
  Pages:        <count>

Validation:
  Format:       <pass | issues>
  Links:        <reachable count / total>
  Freshness:    <current | stale pages: N>

Discoverability signals:
  <head> link[rel=alternate]:  <added | present | skipped | n/a>
  sitemap /llms.txt entry:     <added | present | skipped | n/a, no sitemap>
  robots.txt comment:          <added | present | skipped | n/a, no robots.txt>
  Build order (llms.txt → sitemap): <ok | warning: reorder <script>>

Manual next step: submit to public directories:
  - https://llmstxt.site/submit
  - https://directory.llmstxt.cloud
  (Web forms, manual action. Google Search ignores llms.txt; some coding
   tools read it, and Lighthouse's agentic browsing audit checks for it 🧪.)

Next:
  - Verify the site serves /llms.txt at your production URL.
  - For developer docs, consider Markdown companion routes (optional).
  - Re-run /seo-audit geo to confirm the llms.txt finding clears.
```

If `--dry-run`: print the would-be file contents to the terminal and write nothing.

## Examples

**Example 1: Generated `llms.txt` for a developer tool's docs site (Next.js)**

```markdown
# Example API

> Example API is a REST API for sending transactional email. These docs cover setup, authentication, endpoints and SDKs.

Markdown versions of each docs page are available at the same URL with a `.md` suffix.

## Getting started

- [Quickstart](https://docs.example.com/quickstart.md): send a first email in five minutes.
- [Authentication](https://docs.example.com/auth.md): API keys, scopes and key rotation.

## API reference

- [Send email](https://docs.example.com/api/send.md): request and response fields for `POST /v1/emails`.
- [Webhooks](https://docs.example.com/api/webhooks.md): event types, payloads and signature checks.

## SDKs

- [Node.js SDK](https://docs.example.com/sdks/node.md): install, configure and send.

## Optional

- [Changelog](https://docs.example.com/changelog.md): API and SDK releases.
```

**Example 2: Validation output for a stale `llms.txt`**

```
llms.txt Validation
===================
Path: public/llms.txt
Size: 2,147 bytes

✅ H1 present: "# Example Site"
✅ Blockquote description present
✅ Valid markdown syntax
⚠️ Broken link: https://example.com/blog/old-post (404)
⚠️ 3 HTML links could point to .md companions instead
❌ Stale: 7 content files newer than llms.txt mtime (2025-11-02).
   - src/content/blog/new-post.md
   - src/content/blog/feature-announcement.md
   - ...

Recommendation: run /seo-llms-txt update.
```

**Example 3: Next.js `llms-full.txt` route**

```ts
// app/llms-full.txt/route.ts
import { getAllContent } from '@/lib/content'

export async function GET() {
  const pages = await getAllContent()
  const body = [
    '# Example Site: Full Content Export',
    '',
    `> Full Markdown export of example.com. Generated on ${new Date().toISOString()}.`,
    '',
    '---',
    '',
    ...pages.map(p => [
      `## ${p.title}`,
      '',
      `Source: ${p.url}`,
      `Last modified: ${p.modifiedTime}`,
      '',
      p.markdown,
      '',
      '---',
      '',
    ].join('\n')),
  ].join('\n')

  return new Response(body, {
    headers: { 'Content-Type': 'text/markdown; charset=utf-8' },
  })
}
```

## Quality Assurance Checklist

Before finalizing:

- [ ] Context7 mode stated
- [ ] Framework + path determined
- [ ] Base domain resolved or prompted for
- [ ] H1 title + blockquote description present in the generated `llms.txt`
- [ ] Links are absolute URLs
- [ ] `.md` companion URLs used where detected
- [ ] File size ≤ ~8KB for the index; content moved to `llms-full.txt` if larger
- [ ] Validation includes broken-link and staleness checks when applicable, and is never saved in the public folder
- [ ] Framework-idiomatic placement (static file or route handler)
- [ ] `--dry-run` writes nothing
- [ ] After writing: offered the `<head>` `link[rel=alternate]` hint (skipped if present)
- [ ] After writing: offered the sitemap `/llms.txt` entry (skipped if present or no sitemap)
- [ ] After writing: offered the robots.txt `# LLM index` comment (skipped if present or no robots.txt)
- [ ] Build-order rule surfaced when both files are generated at build time (llms.txt → sitemap)
- [ ] Directory submission URLs printed in the terminal summary (llmstxt.site, directory.llmstxt.cloud)
- [ ] User told once that Google Search ignores llms.txt and it isn't a citation lever
- [ ] User directed back to `/seo-audit geo` to verify the finding clears
