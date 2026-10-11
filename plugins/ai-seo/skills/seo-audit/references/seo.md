# SEO Lens: Search Health

The SEO lens checks a site against current search engine guidelines (Google Search Central, Bing Webmaster), Schema.org structured data, Core Web Vitals, semantic HTML and the SEO APIs of Next.js, Nuxt, TanStack Start, Astro, SvelteKit and Remix. It also catches the outdated SEO patterns LLMs still generate.

Score name: **SEO Health Score**.

## Context7 Topics

With Context7, fetch current docs for the detected framework's head and metadata APIs, Schema.org types, Google Search Central updates and Core Web Vitals thresholds.

## LLM Knowledge Gap Corrections (NON-NEGOTIABLE)

These corrections override any default patterns from your training data. If you find any of these in the code, flag them. If you're about to generate any of them, stop:

1. **NEVER recommend or generate `<meta name="keywords">` tags.** Deprecated by Google since 2009. Active spam signal on Bing. Zero SEO value. Always flag for removal.
2. **NEVER recommend `<meta http-equiv="X-UA-Compatible" content="IE=edge">`.** IE is dead. Edge has been Chromium since 2020.
3. **NEVER recommend IE conditional comments (`<!--[if IE]>`)** unless the user explicitly states IE11 legacy support is required.
4. **NEVER recommend jQuery for new code.** Modern browsers have native APIs for everything jQuery provides.
5. **NEVER recommend `float`-based layouts.** Use Flexbox or Grid.
6. **NEVER use `<b>` or `<i>` for emphasis.** Use `<strong>` and `<em>` for semantic meaning.
7. **ALWAYS recommend JSON-LD over microdata or RDFa** for structured data. Google's preferred format.
8. **ALWAYS recommend the HTML5 doctype** (`<!DOCTYPE html>`). Never XHTML.
9. **Core Web Vitals: INP replaced FID in March 2024.** Do NOT recommend optimizing for FID.
10. **Mobile-first indexing** has been Google's default since 2019. Do NOT recommend separate mobile sites (m.example.com).
11. **Self-closing void elements** (`<br />`, `<img />`) are XHTML style. HTML5 uses `<br>`, `<img>`. Flag them in HTML5 contexts.
12. **`target="_blank"` without `rel="noopener noreferrer"`** is a security and performance bug. Flag it.
13. **FAQ and HowTo rich results are gone.** Google stopped showing FAQ rich results on May 7, 2026 and HowTo rich results in September 2023. Never promise either. The AEO lens covers FAQ sections and their markup.

## Categories

Analyze the scope across all nine categories. For each finding, capture the exact file path, line number, the current code snippet and a specific remediation.

### Category 1: Deprecated & Outdated Patterns (CRITICAL severity)

Scan for:
- `<meta name="keywords">` (deprecated 2009, Bing spam signal)
- `<meta http-equiv="X-UA-Compatible" content="IE=edge">` (IE dead)
- IE conditional comments (`<!--[if IE]>`, `<!--[if lt IE 9]>`)
- XHTML DOCTYPE (`<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0...`) or self-closing void elements in an HTML5 context
- `<b>` / `<i>` used for semantic emphasis (distinguish from CSS-only stylistic use)
- Separate mobile subdomain patterns (hardcoded `m.example.com`)
- `.html` / `.aspx` / `.php` extensions in internal links where clean URLs are possible
- `target="_blank"` without `rel="noopener noreferrer"`
- Conflicting robots meta directives (e.g., `noindex` + `index`)
- jQuery usage in new code
- `float`-based layout (layout CSS, not legitimate text wrap)

### Category 2: Modern Meta Tags (WARNING if missing)

Verify presence and quality:
- `<title>`: 50-60 chars, unique per page
- `<meta name="description">`: 150-160 chars, unique per page, compelling
- `<link rel="canonical">`: canonical URL
- Open Graph: `og:title`, `og:description`, `og:image`, `og:url`, `og:type`
- Twitter Card: `twitter:card`, `twitter:title`, `twitter:description`, `twitter:image`
- `<meta name="viewport" content="width=device-width, initial-scale=1">`
- `<meta charset="UTF-8">`
- `<html lang="...">`
- Favicon + `apple-touch-icon`
- `robots.txt` at the project root or public dir
- `sitemap.xml` (or sitemap index) referenced in `robots.txt`

### Category 3: Semantic HTML

Validate:
- Proper use of `<header>`, `<nav>`, `<main>`, `<article>`, `<section>`, `<aside>`, `<footer>`
- Exactly one `<h1>` per page
- Logical heading hierarchy (no skipping h1→h3)
- Semantic landmarks where a11y and SEO overlap

### Category 4: Structured Data (Schema.org)

- Detect the page type from content or route and suggest appropriate schema:
  - Articles/blog → `Article`, `BlogPosting`
  - Products → `Product` with `offers`, `aggregateRating`
  - Organization → `Organization` with `logo`, `sameAs`
  - Local business → `LocalBusiness`
  - FAQ pages → `FAQPage`, optional 🧪 and only for questions visible on the page (no Google rich result since May 2026)
  - Breadcrumbs → `BreadcrumbList`
  - Events → `Event`
  - How-to → don't add `HowTo` markup for Google (its rich results ended in September 2023); a real `<ol>` of steps is what counts. Existing `HowTo` is valid Schema.org and can stay.
- Validate existing JSON-LD syntax (valid JSON, required properties present, correct `@context`, ISO 8601 dates)
- Prefer JSON-LD over microdata/RDFa. Flag microdata/RDFa as suggestions to migrate.

### Category 5: Performance Signals (Core Web Vitals)

Static-analysis signals (not runtime):
- Images missing `width` / `height` attributes (CLS risk)
- Images missing `loading="lazy"` on below-fold content
- Images missing `decoding="async"`
- Missing `<picture>` or `srcset` for responsive images
- No WebP/AVIF formats
- Render-blocking resources in `<head>` (synchronous scripts, unminified CSS)
- Missing `<link rel="preconnect">` for third-party origins (fonts, analytics, CDN)
- Missing `<link rel="preload">` for LCP-critical resources (hero image, above-fold fonts)
- Script tags without `async` or `defer`
- No `font-display` strategy (should be `swap` or `optional`)

Note: INP replaced FID in March 2024. Use LCP, CLS and INP as the current Core Web Vitals.

### Category 6: Accessibility (overlaps with SEO)

- Images without meaningful `alt` attributes
- Generic link text ("click here", "read more", "learn more")
- Form inputs without associated labels
- Missing skip-to-content link
- Color-only information indicators

Add this note to the report: **For deeper a11y coverage, run `/accessibility-audit` from the ai-accessibility plugin.**

### Category 7: URL Structure

- Clean semantic URLs vs query-heavy URLs
- Trailing-slash consistency
- HTTPS enforcement (HTTP links or mixed content references)
- Redirect patterns (301 permanent vs 302 temporary; flag 302s for permanent moves)

### Category 8: Security Headers (SEO-adjacent)

Check config files (`next.config.*`, `vercel.json`, `netlify.toml`, `_headers`, `nginx.conf`, middleware) for:
- HSTS (`Strict-Transport-Security`)
- Content-Security-Policy
- X-Content-Type-Options: `nosniff`
- Referrer-Policy

### Category 9: Framework-Specific Checks

Based on the detected framework:

**Next.js:**
- App Router: use of the Metadata API (`export const metadata`) or `generateMetadata()` in layouts and pages
- Pages Router: `next/head` usage with proper meta tags
- `next/image` component vs raw `<img>` tags
- `next-sitemap` or built-in `app/sitemap.ts` and `app/robots.ts` files
- Dynamic OG image generation via `opengraph-image.tsx`

**Nuxt:**
- `useHead()` / `useSeoMeta()` composable usage
- `@nuxtjs/seo` module installed
- `@nuxtjs/sitemap` or equivalent
- `definePageMeta` for route metadata

**TanStack Start:**
- Route-level meta via `createRootRoute({ head: () => ({ meta: [...], links: [...] }) })`
- `<HeadContent />` rendered in the root layout
- `<Scripts />` rendered before the closing body

**Astro:**
- `<SEO>` component patterns (e.g., `astro-seo`) or a custom layout head
- `@astrolib/seo` or `astro-seo` usage
- Content collections with schema for metadata
- `@astrojs/sitemap` integration

**SvelteKit:**
- `<svelte:head>` usage
- `$app/stores` for canonical URL derivation
- `src/routes/+layout.svelte` head management
- `sitemap.xml` endpoint or plugin

**Remix / React Router:**
- `meta` export function per route
- `links` export for canonical + favicons
- Route-level Open Graph data

**Vanilla HTML / unknown:**
- Direct `<head>` inspection across HTML files
- Suggest moving to a framework head-management pattern if appropriate

## Scoring

| Category | Weight |
|----------|--------|
| Deprecated Patterns | 20% |
| Modern Meta Tags | 15% |
| Semantic HTML | 10% |
| Structured Data | 15% |
| Performance Signals | 15% |
| Accessibility | 10% |
| URL Structure | 5% |
| Security Headers | 5% |
| Framework Best Practices | 5% |

The SEO lens has no 🧪 items apart from optional FAQPage markup; use the standard deductions.

## Severity Assessment

- **Critical**: Deprecated patterns actively harming SEO (keywords meta, X-UA-Compatible, mixed content, broken robots directives, missing canonical on indexed pages)
- **High**: Missing core modern requirements (no meta description, no OG tags, no viewport, no structured data on content pages, missing alt text on content images, `target="_blank"` without `rel="noopener noreferrer"`)
- **Medium**: Partial or suboptimal implementations (too-short/long title or description, missing Twitter Cards, unoptimized images, skipped heading levels, missing lazy loading)
- **Low**: Nice-to-haves (missing preconnect/preload, no WebP/AVIF, minor structured data enhancements, AAA a11y enhancements)

## Report Section

Insert this under `## SEO: Search Health` in the report. Every subsection is required; write "None found" rather than dropping one.

```markdown
### Executive Summary

**SEO Health Score:** <X> / 100

**Grade:** <A+ | A | B | C | D | F>

**Summary:** <2-3 sentence overview of SEO posture, most impactful finding, and what's working>

#### Score Breakdown

| Category | Score | Weight |
|----------|-------|--------|
| Deprecated Patterns | X/100 | 20% |
| Modern Meta Tags | X/100 | 15% |
| Semantic HTML | X/100 | 10% |
| Structured Data | X/100 | 15% |
| Performance Signals | X/100 | 15% |
| Accessibility | X/100 | 10% |
| URL Structure | X/100 | 5% |
| Security Headers | X/100 | 5% |
| Framework Best Practices | X/100 | 5% |

#### Issue Counts

- 🔴 **Critical Issues:** <count>
- 🟠 **High Priority:** <count>
- 🟡 **Medium Priority:** <count>
- 🔵 **Low Priority / Suggestions:** <count>
- 🟢 **Passing Checks:** <count>

### 🔴 Critical Issues

Issues that actively harm SEO. Address immediately.

#### SEO-1: <Title>

**File:** `path/to/file.tsx:42`
**Category:** <Deprecated Patterns | Modern Meta Tags | ...>
**Impact:** Critical

**Current Code:**
\`\`\`<language>
<exact snippet from the file>
\`\`\`

**Problem:**
<1-3 sentences explaining why this hurts SEO. Cite the authority where relevant (Google, Bing, W3C).>

**Recommended Fix:**
\`\`\`<language>
<corrected code or removal instruction>
\`\`\`

**Source:** <e.g., https://developers.google.com/search/docs/crawling-indexing/special-tags>

<Continue for each critical issue: SEO-2, SEO-3...>

### 🟠 High Priority Issues

<Same format>

### 🟡 Medium Priority Issues

<Same format>

### 🔵 Suggestions & Nice-to-Haves

<Same format>

### ✅ What's Working Well

- ✅ <actual positive finding from the code>

### 🏗️ Framework-Specific Recommendations

**Detected Framework:** <Framework Name>

<Framework-idiomatic guidance with code examples. For Next.js use the App Router Metadata API, for TanStack Start use route `head` with <HeadContent />, etc.>

### 📊 Core Web Vitals Considerations

Static-analysis findings that may impact Core Web Vitals:

- **LCP (Largest Contentful Paint):** <findings>
- **CLS (Cumulative Layout Shift):** <findings>
- **INP (Interaction to Next Paint):** <findings>

Runtime measurement is required for actual Core Web Vitals scores. Use PageSpeed Insights or Chrome DevTools. INP replaced FID in March 2024.
```

**Detail line for the terminal summary:** none beyond the score line.

**Remediation commands for this lens:** `/seo-fix`, and `/seo-schema` for missing structured data.

### Resources

- [Google Search Central](https://developers.google.com/search)
- [Schema.org](https://schema.org/)
- [web.dev - Learn SEO](https://web.dev/learn/seo/)
- [MDN - HTML Meta Tags](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meta)
- [Core Web Vitals](https://web.dev/articles/vitals)

### Limitations

- Static analysis only (no runtime Core Web Vitals measurement)
- Does not crawl external links
- Does not test server response headers (recommend a separate HTTP header audit)
- Accessibility is surface-level. For WCAG 2.1/2.2 compliance, run `/accessibility-audit` from the ai-accessibility plugin.

## Examples: Bad vs Good Recommendations

**Example 1: Keywords meta tag (the motivating case)**

❌ Bad (what older LLMs still do):
```html
<meta name="keywords" content="web development, portfolio, react, typescript">
```

✅ Good:
```html
<!-- Remove entirely. Deprecated 2009. Bing spam signal. Zero value. -->
```

**Example 2: TanStack Start meta**

❌ Bad (framework-inappropriate):
```tsx
// index.tsx
import Head from 'next/head'  // Wrong framework
```

✅ Good (TanStack Start idiomatic):
```tsx
// src/routes/__root.tsx
import { createRootRoute, HeadContent, Scripts } from '@tanstack/react-router'

export const Route = createRootRoute({
  head: () => ({
    meta: [
      { charSet: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { title: 'My Site | Descriptive, 50-60 chars, unique' },
      { name: 'description', content: '150-160 char compelling summary.' },
      { property: 'og:title', content: 'My Site' },
      { property: 'og:description', content: 'Compelling summary.' },
      { property: 'og:type', content: 'website' },
      { property: 'og:url', content: 'https://example.com' },
      { property: 'og:image', content: 'https://example.com/og.jpg' },
      { name: 'twitter:card', content: 'summary_large_image' },
    ],
    links: [
      { rel: 'canonical', href: 'https://example.com' },
      { rel: 'icon', href: '/favicon.ico' },
      { rel: 'apple-touch-icon', href: '/apple-touch-icon.png' },
    ],
  }),
  component: () => (
    <html lang="en">
      <head><HeadContent /></head>
      <body>{/* ... */}<Scripts /></body>
    </html>
  ),
})
```

**Example 3: Next.js App Router metadata**

❌ Bad:
```tsx
// app/layout.tsx
export default function Layout({ children }) {
  return (
    <html>
      <head>
        <title>My Site</title>
        <meta name="keywords" content="react, nextjs, typescript" />
      </head>
      <body>{children}</body>
    </html>
  )
}
```

✅ Good:
```tsx
// app/layout.tsx
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: { default: 'My Site', template: '%s | My Site' },
  description: '150-160 char compelling summary.',
  metadataBase: new URL('https://example.com'),
  alternates: { canonical: '/' },
  openGraph: {
    title: 'My Site',
    description: 'Compelling summary.',
    url: 'https://example.com',
    siteName: 'My Site',
    images: [{ url: '/og.jpg', width: 1200, height: 630 }],
    locale: 'en_US',
    type: 'website',
  },
  twitter: { card: 'summary_large_image' },
  robots: { index: true, follow: true },
}
```

**Example 4: JSON-LD (always prefer over microdata)**

❌ Bad (microdata):
```html
<div itemscope itemtype="https://schema.org/Article">
  <h1 itemprop="headline">Title</h1>
</div>
```

✅ Good (JSON-LD):
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Title",
  "author": { "@type": "Person", "name": "Jane Doe" },
  "datePublished": "2026-04-17T10:00:00-05:00",
  "image": "https://example.com/hero.jpg"
}
</script>
```

## Context-Aware Analysis

If the project's docs or code reveal:
- **i18n setup**: check `hreflang` tags and locale-specific canonical URLs.
- **Industry vertical** (e-commerce, news, local business): prioritize the relevant structured data schemas.
- **Existing SEO tooling** (`next-sitemap`, `@nuxtjs/seo`, `astro-seo`): validate its config rather than recommending setup.

## Quality Assurance Checklist

- [ ] Every finding has an exact file path and line number, and actual code context (or explicit N/A)
- [ ] Every finding has a specific remediation, not generic advice
- [ ] No `<meta name="keywords">`, IE-era pattern, FID advice or microdata recommended
- [ ] No FAQ or HowTo rich results promised
- [ ] Category scores calculated from deductions; grade matches the score
