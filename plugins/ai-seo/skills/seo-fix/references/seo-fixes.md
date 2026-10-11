# SEO Lens Fixes

Fixes for findings in a report's SEO section (IDs `SEO-n`, or any finding in an ai-seo 1.x report). Ambiguous changes, such as writing meta descriptions or choosing words for titles, are proposed to the user for confirmation. Never guess at content the user didn't write.

## Rules (NON-NEGOTIABLE)

1. **NEVER re-insert `<meta name="keywords">` tags.** Deprecated 2009. Bing spam signal.
2. **NEVER re-insert `<meta http-equiv="X-UA-Compatible">`.** IE is dead.
3. **NEVER re-insert IE conditional comments**, unless the user explicitly states IE11 support is required.
4. **NEVER recommend jQuery, `float` layouts, `<b>`/`<i>` for semantic emphasis, the XHTML doctype, FID optimization, or separate mobile sites.**
5. **ALWAYS generate JSON-LD for structured data** (never microdata or RDFa), following `json-ld.md`.
6. **ALWAYS use framework-idiomatic head management** (Next.js Metadata API, Nuxt `useSeoMeta`, TanStack Start route `head` with `<HeadContent />`, etc.) instead of raw `<head>` edits when a framework is detected.

## Classification

**Safe-auto fixes** (no content needed; confirm once as a batch):
- Remove `<meta name="keywords">` tags
- Remove `<meta http-equiv="X-UA-Compatible">` tags
- Remove IE conditional comments
- Add `rel="noopener noreferrer"` to `target="_blank"` links
- Add `loading="lazy"` to below-fold images (when the position can be inferred from HTML order or explicit class/id markers)
- Add `decoding="async"` to images
- Add `width`/`height` to images where intrinsic dimensions can be resolved (check adjacent CSS, import-based images like `next/image`, or the image file itself if accessible)
- Add `async` or `defer` to third-party `<script>` tags
- Add a missing `<html lang="en">` (default to `en`; ask the user if an `i18n` config suggests a non-English project)
- Fix XHTML-style self-closing void elements (`<br />` → `<br>`, `<img />` → `<img>`) in HTML5 contexts
- Replace `<b>`/`<i>` used for semantic emphasis with `<strong>`/`<em>` (when the context shows emphasis intent, not styling)
- Add `<meta charset="UTF-8">` if missing
- Add `<meta name="viewport" content="width=device-width, initial-scale=1">` if missing
- Fix JSON-LD validity and migrate microdata or RDFa to JSON-LD (see `json-ld.md`)

**Content-requiring fixes** (propose and confirm each one):
- Writing a meta description: propose one from the page content and ask for approval or an edit
- Writing a `<title>`: propose one from the `<h1>` or page content
- Writing Open Graph / Twitter Card copy
- Canonical URLs (need the domain: ask once and reuse it for the session)
- Structured data for pages with none: propose the schema type and its filled values, following `json-ld.md`. For a whole-site pass, the user can run `/seo-schema` instead.

**Larger refactors** (propose a plan first, confirm per file):
- Div soup → semantic HTML5 (`<div class="header">` → `<header>`)
- Heading hierarchy fixes (may need visual context)
- URL structure changes (may break inbound links; recommend a redirect plan)

## Generate Missing Files

Offer to generate these if missing. Ask for the site domain once and reuse it across all generated files.

**robots.txt** (at the public root or the framework's convention). If the report also covers the GEO lens, ask its three bot-group questions first (see `geo-fixes.md`) and add those rules. Otherwise:
```
User-agent: *
Allow: /

Sitemap: https://<domain>/sitemap.xml
```

**Sitemap starter** (framework-idiomatic):
- Next.js App Router → `app/sitemap.ts` returning the route list
- Nuxt → suggest installing `@nuxtjs/sitemap` with a minimal config
- Astro → suggest the `@astrojs/sitemap` integration
- SvelteKit → generate a `src/routes/sitemap.xml/+server.ts` stub
- Remix → generate an `app/routes/sitemap[.]xml.ts` stub
- Vanilla → ask the user for the URL list and generate a static `sitemap.xml`

## Framework Specifics

- **Next.js (App Router):** meta fixes → `export const metadata` or `generateMetadata()` in `app/layout.tsx` or per-route `page.tsx`; robots → `app/robots.ts`; sitemap → `app/sitemap.ts`; OG image → `app/opengraph-image.tsx`.
- **Next.js (Pages Router):** `next/head` with explicit `<Head>` tags.
- **Nuxt:** `useSeoMeta({...})` in `<script setup>` or `app.vue`; `useHead({ link: [{ rel: 'canonical', href: ... }] })`.
- **TanStack Start:** route-level `head: () => ({ meta: [...], links: [...] })` in `createRoute`/`createRootRoute`; make sure `<HeadContent />` and `<Scripts />` are in the root layout.
- **Astro:** per-page `<head>` in the layout, or the `astro-seo` / `@astrolib/seo` `<SEO>` component if already installed.
- **SvelteKit:** `<svelte:head>` in `+layout.svelte` or `+page.svelte`.
- **Remix / React Router:** `meta` export function; `links` export for canonical and favicons.
- **Vanilla HTML:** direct `<head>` edits.

## Examples

**Example 1: Remove keywords meta (safe-auto)**

Before (app/layout.tsx):
```tsx
<meta name="keywords" content="react, nextjs, portfolio" />
<meta name="description" content="My portfolio" />
```

After:
```tsx
<meta name="description" content="My portfolio" />
```

**Example 2: Propose a meta description (content-requiring)**

```
File: src/routes/__root.tsx (TanStack Start)
Missing: meta name="description"

Proposed (from the H1 and first paragraph):
  "Example Co builds scheduling software for dental clinics: online booking, reminders and staff calendars, with setup guides and pricing for each plan."

(155 chars, within the 150-160 target range)

(a) accept  (e) edit  (s) skip
```

**Example 3: Refactor div soup to semantic HTML**

Before:
```html
<div class="page-header">
  <div class="site-nav">...</div>
</div>
<div class="main-content">...</div>
<div class="page-footer">...</div>
```

Proposed:
```html
<header>
  <nav>...</nav>
</header>
<main>...</main>
<footer>...</footer>
```

(Ask: apply this refactor in `src/components/Layout.tsx`?)

## Terminal Summary Block

```
SEO changes by category:
  Deprecated Patterns: <count>
  Modern Meta Tags:    <count>
  Semantic HTML:       <count>
  Structured Data:     <count>
  Performance:         <count>
  ...
Generated: <robots.txt | sitemap | none>
```

## Checklist

- [ ] No `<meta name="keywords">` or IE-era pattern inserted anywhere
- [ ] Existing meta tags proposed for change, never silently replaced
- [ ] URL structure untouched unless the user asked
