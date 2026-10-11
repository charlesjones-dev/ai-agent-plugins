# JSON-LD Rules

These rules govern every JSON-LD block the ai-seo plugin writes or validates. `/seo-schema`, `/seo-fix` and `/seo-faq` each keep an identical copy of this file.

## Core Rules (NON-NEGOTIABLE)

1. **JSON-LD only.** Never microdata (`itemscope`/`itemprop`) or RDFa. Google prefers JSON-LD. When migrating microdata or RDFa, preserve every value.
2. **`"@context": "https://schema.org"`**, with HTTPS, never HTTP.
3. **ISO 8601 dates with a timezone** (`2026-04-17T10:00:00-05:00`), never locale-formatted strings.
4. **Absolute URLs**, never relative ones.
5. **Never invent Schema.org types or properties.** If unsure, check Schema.org through Context7, or flag it for the user to research.
6. **Never emit deprecated types or properties.** Cross-check Context7 when it's available.
7. **Mark up only what readers can see.** Google's general structured data guidelines: "Don't mark up content that is not visible to readers of the page."
8. **Never invent content.** Fill values from the page, its data sources or the user. Mark anything else `"PLACEHOLDER: <description>"` for the user to fill, and never leave a placeholder in a file without listing it. Never invent `sameAs` URLs, authors, credentials, ratings, reviews, prices, dates or answers.
9. **Never promise rich results that no longer exist.** Google stopped showing FAQ rich results on May 7, 2026 (and removed its FAQPage documentation in June 2026) and HowTo rich results in September 2023. Say what the markup describes instead.
10. **Type nested entities.** `author` is a `Person` or `Organization` object, not a bare string; `publisher` is an `Organization` with a `logo`.
11. **Serialize safely.** When writing JSON into a `<script>` tag, escape `<` as `\u003c` (for example `JSON.stringify(ld).replace(/</g, '\\u003c')`) so text in the data can't close the tag early, unless the framework's head API already escapes it.
12. **Never add `<meta name="keywords">` to "help" structured data.** It's unrelated and deprecated.

## Required Properties and Common Mistakes

Check for and warn about:

- `@context` using `http://` instead of `https://`
- `@type` missing or not a valid Schema.org type
- Required properties missing:
  - `Article`/`BlogPosting`: `headline`, `datePublished`, `author`, `image`
  - `Product`: `name` + at least one of (`offers`, `review`, `aggregateRating`)
  - `Event`: `name`, `startDate`, `location`
  - `Recipe`: `name`, `image`, `recipeIngredient`, `recipeInstructions`
  - `FAQPage`: `mainEntity[].name` and `mainEntity[].acceptedAnswer.text`
  - `QAPage`: `mainEntity` → `Question` with `name`, `answerCount`, and `acceptedAnswer` or `suggestedAnswer`
- Dates not in ISO 8601
- Relative URLs instead of absolute
- `author` as a string instead of a `Person`/`Organization` object (valid in some cases but schema-poorer)
- Placeholder content left unfilled (e.g., `"PLACEHOLDER: ..."` still in output)
- Mixing microdata with JSON-LD (recommend consolidation to JSON-LD only)
- Markup for content that isn't visible on the page

## Type Rules

### FAQPage and QAPage

- **Visible first.** Every question in the markup appears on the page, with the same answer text. Markup for questions that aren't shown is against Google's guidelines.
- **Optional 🧪.** FAQPage is still valid Schema.org, and Microsoft says schema helps its search and AI systems understand content, but no Google feature uses it since May 2026. Ask before adding it; the visible FAQ is the part that matters.
- **FAQPage vs QAPage.** FAQPage is for questions and answers the site wrote. QAPage is for one question with answers submitted by users (forums, community Q&A); Google still documents it and says a site-written FAQ isn't eligible. Don't mix them.
- **One data source.** Render the visible FAQ and its JSON-LD from the same array, content collection or CMS field, so they can't drift apart.
- **Mark up an FAQ once.** Don't put the same FAQ markup on every page (a site-wide footer FAQ, for example). Mark it up where the FAQ lives.
- **Answers open with the answer** and use only simple HTML (paragraphs, lists, links, line breaks, emphasis); no scripts or complex markup.

### Organization and Person with sameAs

- `Organization` on the homepage or About page: `name`, `url`, `logo`, `description`, `sameAs`, and where true `foundingDate`, `founder`, `address`.
- `Person` for authors: `name`, `url` (their author page), `jobTitle`, `worksFor`, `sameAs`, and optionally `knowsAbout` 🧪.
- `sameAs` lists the entity's own profiles: Wikidata or Wikipedia if they exist, LinkedIn, GitHub, Crunchbase, ORCID for researchers, official social accounts, and review-platform profiles the organization owns. The user supplies every URL. Skip blank ones; never guess one.
- Give each entity an `@id` (`https://example.com/#org`) so other blocks can refer to it.

### LocalBusiness

Use `LocalBusiness` (or a subtype) with name, address, phone, opening hours and geo coordinates, matching the visible name, address and phone (NAP) on every page that shows them. Prompt the user for any value the site doesn't show; never guess.

### Article, BlogPosting and WebPage

`headline`, `author`, `datePublished`, `dateModified`, `image`, and `mainEntityOfPage`; `BreadcrumbList` alongside. Take `dateModified` from a real change (frontmatter or the content file's last git commit, or the user), never today's date by default.

### Review and AggregateRating

Only where Google's policy allows it, such as a `Product` with genuine customer reviews. Self-serving review markup on `LocalBusiness` or `Organization` (a business rating itself) is not allowed. Never invent ratings or reviews.

### Optional and Limited Types 🧪

- `Dataset` on pages that publish data: Google uses it only for Dataset Search, not Google Search.
- `ClaimReview` only for genuine fact-check content: Google is phasing it out of Search; its Fact Check Explorer still reads it.
- `DefinedTerm` / `DefinedTermSet` for glossaries: valid Schema.org; no Google feature depends on it.
- `speakable`: a Google beta for news content in English in the US, read by Google Assistant, which Gemini is replacing. Only for news publishers.
- `HowTo`: valid Schema.org, but no Google feature since September 2023. Don't add it for Google; leave existing markup alone. A real `<ol>` of steps is what engines can lift.

## Patterns

**Article with Author + Publisher:**
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "...",
  "datePublished": "2026-04-17T10:00:00-05:00",
  "dateModified": "2026-04-17T10:00:00-05:00",
  "author": {
    "@type": "Person",
    "name": "Jane Doe",
    "url": "https://example.com/authors/jane-doe"
  },
  "publisher": {
    "@type": "Organization",
    "name": "My Site",
    "logo": {
      "@type": "ImageObject",
      "url": "https://example.com/logo.png",
      "width": 600,
      "height": 60
    }
  },
  "image": "https://example.com/hero.jpg",
  "mainEntityOfPage": { "@type": "WebPage", "@id": "https://example.com/post-slug" }
}
```

**Product with Offer + AggregateRating:**
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "...",
  "image": ["..."],
  "description": "...",
  "sku": "...",
  "brand": { "@type": "Brand", "name": "..." },
  "offers": {
    "@type": "Offer",
    "url": "https://example.com/product",
    "priceCurrency": "USD",
    "price": "29.99",
    "availability": "https://schema.org/InStock",
    "itemCondition": "https://schema.org/NewCondition"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.6",
    "reviewCount": "120"
  }
}
```

**FAQPage** (built from the same data as the visible FAQ):
```tsx
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

**QAPage** (one user-asked question with user-submitted answers):
```json
{
  "@context": "https://schema.org",
  "@type": "QAPage",
  "mainEntity": {
    "@type": "Question",
    "name": "...",
    "text": "...",
    "answerCount": 2,
    "datePublished": "2026-04-17T10:00:00-05:00",
    "author": { "@type": "Person", "name": "..." },
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "...",
      "datePublished": "2026-04-17T12:00:00-05:00",
      "author": { "@type": "Person", "name": "..." },
      "url": "https://example.com/questions/123#answer-1"
    },
    "suggestedAnswer": [
      {
        "@type": "Answer",
        "text": "...",
        "author": { "@type": "Person", "name": "..." },
        "url": "https://example.com/questions/123#answer-2"
      }
    ]
  }
}
```

**BreadcrumbList:**
```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://example.com/" },
    { "@type": "ListItem", "position": 2, "name": "Blog", "item": "https://example.com/blog" },
    { "@type": "ListItem", "position": 3, "name": "Post Title" }
  ]
}
```

**Organization with sameAs** (URLs supplied by the user; Wikidata left blank, so it's skipped):
```tsx
const orgLd = {
  '@context': 'https://schema.org',
  '@type': 'Organization',
  '@id': 'https://example.com/#org',
  name: 'Example Co',
  url: 'https://example.com',
  logo: 'https://example.com/logo.png',
  description: '<one-sentence description from the About page>',
  sameAs: [
    'https://www.linkedin.com/company/<slug>',
    'https://github.com/<org>',
  ],
}
```

**Person with sameAs** (URLs supplied by the user):
```tsx
const personLd = {
  '@context': 'https://schema.org',
  '@type': 'Person',
  name: 'Jane Doe',
  url: 'https://example.com/authors/jane-doe',
  jobTitle: 'Senior Data Analyst',
  worksFor: { '@type': 'Organization', '@id': 'https://example.com/#org', name: 'Example Co' },
  sameAs: [
    'https://www.linkedin.com/in/<slug>',
    'https://github.com/<handle>',
  ],
}
```

**Composite with @graph** (homepage):
```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://example.com/#org",
      "name": "My Site",
      "url": "https://example.com",
      "logo": "https://example.com/logo.png",
      "sameAs": ["https://github.com/<org>", "https://www.linkedin.com/company/<slug>"]
    },
    {
      "@type": "WebSite",
      "@id": "https://example.com/#site",
      "url": "https://example.com",
      "name": "My Site",
      "publisher": { "@id": "https://example.com/#org" },
      "potentialAction": {
        "@type": "SearchAction",
        "target": "https://example.com/search?q={search_term_string}",
        "query-input": "required name=search_term_string"
      }
    }
  ]
}
```

## Framework Injection

Render JSON-LD on the server, in the framework's own head API or a server-rendered `<script type="application/ld+json">`.

**Next.js (App Router):**
```tsx
// app/blog/[slug]/page.tsx
export default async function BlogPost({ params }: { params: { slug: string } }) {
  const post = await getPost(params.slug)
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    headline: post.title,
    datePublished: post.publishedAt,
    dateModified: post.updatedAt,
    author: { '@type': 'Person', name: post.author.name, url: post.author.url },
    image: post.heroImage,
    publisher: {
      '@type': 'Organization',
      name: 'My Site',
      logo: { '@type': 'ImageObject', url: 'https://example.com/logo.png' },
    },
  }
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, '\\u003c') }}
      />
      <article>{/* ... */}</article>
    </>
  )
}
```

**Next.js (Pages Router):** the same `<script>` inside `next/head`.

**Nuxt:**
```vue
<script setup lang="ts">
useHead({
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'BlogPosting',
        headline: post.title,
        datePublished: post.publishedAt,
        author: { '@type': 'Person', name: post.author.name },
      }),
    },
  ],
})
</script>
```

**TanStack Start:**
```tsx
// src/routes/blog/$slug.tsx
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/blog/$slug')({
  loader: ({ params }) => getPost(params.slug),
  head: ({ loaderData }) => ({
    scripts: [
      {
        type: 'application/ld+json',
        children: JSON.stringify({
          '@context': 'https://schema.org',
          '@type': 'BlogPosting',
          headline: loaderData.title,
          datePublished: loaderData.publishedAt,
          author: { '@type': 'Person', name: loaderData.author.name },
        }),
      },
    ],
  }),
  component: BlogPost,
})
```

**Astro:**
```astro
---
const post = Astro.props.post
const jsonLd = {
  '@context': 'https://schema.org',
  '@type': 'BlogPosting',
  headline: post.title,
  datePublished: post.publishedAt,
  author: { '@type': 'Person', name: post.author.name },
}
---
<script type="application/ld+json" set:html={JSON.stringify(jsonLd).replace(/</g, '\\u003c')}></script>
<article><slot /></article>
```

**SvelteKit:**
```svelte
<script lang="ts">
  export let post
  $: jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    headline: post.title,
    datePublished: post.publishedAt,
    author: { '@type': 'Person', name: post.author.name },
  }
</script>

<svelte:head>
  {@html `<script type="application/ld+json">${JSON.stringify(jsonLd).replace(/</g, '\\u003c')}</script>`}
</svelte:head>
```

**Remix / React Router:**
```tsx
// app/routes/blog.$slug.tsx
import { json } from '@remix-run/node'
import { useLoaderData } from '@remix-run/react'

export async function loader({ params }) {
  const post = await getPost(params.slug)
  return json({ post })
}

export default function BlogPost() {
  const { post } = useLoaderData<typeof loader>()
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    headline: post.title,
    datePublished: post.publishedAt,
    author: { '@type': 'Person', name: post.author.name },
  }
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, '\\u003c') }}
      />
      <article>{/* ... */}</article>
    </>
  )
}
```

**Vanilla HTML:**
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "...",
  "datePublished": "2026-04-17T10:00:00-05:00",
  "author": { "@type": "Person", "name": "..." }
}
</script>
```
