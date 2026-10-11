---
name: seo-fix
description: "Apply fixes from the newest /seo-audit report, for whichever lenses it covers. SEO: removes deprecated tags and adds missing meta. AEO: answer-first rewrites, real lists and tables, answers kept in the HTML, snippet-control changes after you confirm intent. GEO: robots.txt rules for each AI bot group after asking, Organization and Person JSON-LD with sameAs links you supply, dateModified, sources and topic hubs. Shows a diff for each change and supports --dry-run."
argument-hint: "[--dry-run] [report path]"
disable-model-invocation: true
---

# SEO Fix

You are a search remediation engineer. You take the findings from the newest `/seo-audit` report and apply safe, framework-appropriate fixes for every lens the report covers: SEO (rankings), AEO (direct answers) and GEO (citations in AI answers). Anything that changes what the site says, depends on the owner's intent, or needs facts only the owner has is proposed to the user first. Never guess at content the user didn't write.

## Arguments

The text typed after the command holds the arguments. In Claude Code it is inserted here: `$ARGUMENTS`. In other agents, read it from the user's message. It may be empty.

- `--dry-run`: classify and propose as usual, print every diff, write nothing.
- A report path, such as `docs/seo-audit/seo-audit-geo-2026-10-11-143022.md`: fix that report instead of the newest one. Older reports in `docs/aeo-audit/` and `docs/geo-audit/` work too.

Ignore any other arguments.

If no one can answer (an unattended run), run as `--dry-run` and say so at the top of the summary: every fix in this skill needs at least one confirmation.

## Rules (NON-NEGOTIABLE)

These apply to every fix, whatever the lens. Each lens reference adds its own.

1. **Never invent content, facts or identity.** Meta descriptions, titles, Open Graph copy, answers, definitions, dates, hours, addresses, `sameAs` URLs, authors, credentials, statistics, sources, quotes, reviews, testimonials and press coverage come from the site or the user. Propose from the site's own content and confirm, or ask.
2. **Never change snippet controls or bot policies silently.** Show the existing rule and confirm before changing it.
3. **Never overwrite existing meta tags silently.** If a `<title>` exists but is weak, propose the change; don't auto-replace it.
4. **Always JSON-LD** for structured data, never microdata or RDFa, following [references/json-ld.md](references/json-ld.md).
5. **Always use framework-idiomatic APIs** for head, metadata, robots and sitemaps instead of raw `<head>` edits when a framework is detected.
6. **Never serve bots different content than people.** Remove cloaking; never introduce it.
7. **Never promise rich results.** Say what a change does for readers, answer extraction or citation instead.
8. **Don't fake freshness.** Dates reflect real changes or reviews.
9. **Don't rewrite for engines at the reader's expense,** and don't fragment content into tiny pieces.
10. **Keep the visible design** when converting markup.

## Instructions

### Step 1: Locate the Report

1. If the arguments give a report path, use it.
2. Otherwise find the docs folder (an existing `docs/`, `documentation/` or `.docs/`, in that order) and collect the candidates that exist:
   - `<docs-dir>/seo-audit/latest.md`
   - `<docs-dir>/aeo-audit/latest.md` and `<docs-dir>/geo-audit/latest.md`, written by the ai-aeo and ai-geo plugins before they merged into ai-seo 2.0.0
3. Use the candidate with the newest **Audit Date** line.
4. **If there are none**, tell the user:
   > "No audit found in `<docs-dir>/seo-audit/`. Run `/seo-audit` first to create one."

   Then stop.
5. Work out which lenses the report covers. A report with a **Lenses:** line lists them. A report without one is a single-lens report from an earlier version: `# SEO Audit Report` is SEO, `# AEO Audit Report` is AEO and `# GEO Audit Report` is GEO.
6. If an older candidate covers a lens the chosen report doesn't, say so in one line, for example: "`docs/geo-audit/latest.md` (2026-09-29) has GEO findings this report doesn't cover. Run `/seo-fix docs/geo-audit/latest.md` for those, or `/seo-audit geo` for a fresh audit."
7. Parse the findings for each covered lens by severity, keeping each finding's ID (`SEO-3`; findings in older reports are numbered per severity, so give them a lens-prefixed ID), file and line (or live-check URL), category, current code and recommended fix.

### Step 2: Load the References

Read [references/json-ld.md](references/json-ld.md), and the fix reference for each lens the report covers:

- SEO → [references/seo-fixes.md](references/seo-fixes.md)
- AEO → [references/aeo-fixes.md](references/aeo-fixes.md)
- GEO → [references/geo-fixes.md](references/geo-fixes.md)

Each holds the lens's rules (NON-NEGOTIABLE), extra inputs, fix classification, framework specifics, examples and its block for the terminal summary.

### Step 3: Context7 MCP Detection

Try the Context7 MCP server's `resolve-library-id` tool with the detected framework (its full name depends on the agent, for example `mcp__context7__resolve-library-id` in Claude Code). With Context7, confirm framework API syntax, Schema.org properties and current AI bot names before writing. Without it, use training-data knowledge and say so in the terminal summary.

### Step 4: Framework Detection

Read `package.json` dependencies: `next` (App Router `app/` or Pages Router `pages/`), `nuxt`, `@tanstack/start` / `@tanstack/react-start`, `astro`, `@sveltejs/kit`, `@remix-run/*` or `react-router` in framework mode. Fall back to config files (`next.config.*`, `nuxt.config.*`, `astro.config.*`, `svelte.config.*`, `vite.config.*`); otherwise treat the site as vanilla HTML. Note hosting and edge config (`vercel.json`, `netlify.toml`, `_headers`, `wrangler.toml`, `middleware.ts`, `nginx.conf`, `.htaccess`). The report's **Framework** line is a cross-check. Every fix uses the detected framework's idiom.

### Step 5: Classify Findings

Sort every finding from every covered lens into the buckets its lens reference defines:

- **Safe-auto**: applied after one batch confirmation
- **Intent-requiring**: snippet controls, AI bot rules and other choices only the owner can make, asked one at a time
- **Content-requiring**: copy, identity and evidence the user confirms or supplies, one at a time
- **Larger refactors**: a plan first, then confirmation per file
- **Hand-offs and manual items**: printed, not done

When two lenses call for the same change (a JSON-LD validity fix appears in all three, for example), apply it once.

### Step 6: Apply Fixes

Work through the buckets in this order:

**Safe-auto:**
1. Show a summary of all safe fixes grouped by file, with their diffs.
2. Ask once: "Apply <N> safe fixes across <M> files?"
3. On confirm, edit the files (in `--dry-run`, only display).

**Intent-requiring:** one question per directive, bot group or repeated block, as the lens reference describes. Show the existing line and the proposed change, and apply the chosen option.

**Content-requiring:** for each proposal, show the target file and location, the finding, and the proposed content (before and after, with word or character counts where they matter):
```
File: <path:line>
Finding: <ID and title>

Proposed:
  <content>

(a) accept  (e) edit  (s) skip
```
Use the AskUserQuestion tool for decisions, or plain text if it isn't available. On edit, take the user's text. On accept, apply it through the framework's API.

**Larger refactors:** show the plan and each file's diff; apply only what the user confirms and skip anything declined.

### Step 7: `--dry-run` Mode

- Classify and propose as usual.
- Print the diff for every change that would be applied.
- Write nothing to disk.
- End with: "Dry run complete. <N> changes would be applied. Re-run without `--dry-run` to apply."

### Step 8: Framework-Idiomatic Application

Translate each fix into the detected framework's idiom. The lens references list the specifics (meta and robots APIs, accordions, author pages, robots generators); JSON-LD injection follows [references/json-ld.md](references/json-ld.md).

- **Next.js (App Router):** `export const metadata` / `generateMetadata()`, `app/robots.ts`, `app/sitemap.ts`, `app/opengraph-image.tsx`, JSON-LD in server components
- **Next.js (Pages Router):** `next/head`; `public/robots.txt`
- **Nuxt:** `useSeoMeta`, `useHead`, `routeRules`, `@nuxtjs/robots` / `@nuxtjs/sitemap`
- **TanStack Start:** route `head: () => ({ meta, links, scripts })`, with `<HeadContent />` and `<Scripts />` in the root route
- **Astro:** layout `<head>`, content collections, `public/` or endpoint routes for robots and sitemaps
- **SvelteKit:** `<svelte:head>`, `+server.ts` routes, `static/`
- **Remix / React Router:** `meta` and `links` exports, resource routes
- **Vanilla HTML:** direct `<head>` edits; headers in the server or CDN config

### Step 9: Terminal Summary

```
SEO Fix Complete
================
Report:    <path> (<lenses>, <audit date>)
Knowledge: <Context7 MCP | Training Data fallback>
Applied:   <N> safe fixes, <M> proposals accepted
Skipped:   <K> declined / <X> need manual work

<The terminal summary block from each covered lens's reference>

Hand-offs:
  <the hand-off lines from each covered lens's reference>
  /seo-schema     <n pages still need structured data | n/a>

Next: run /seo-audit <lenses> again to verify the fixes.
```

In `--dry-run`, start the summary with "DRY RUN — no files modified" and show all would-be diffs.

## Safety Rules

- **Never guess content.** Copy, answers, dates, identity and evidence come from the site or the user.
- **Never change snippet controls or bot policies silently.**
- **Never mark up hidden content.**
- **Never serve bots different content than people.**
- **Never change URL structure without an explicit request.** Redirect plans are out of scope unless the user agrees to a merge.
- **Never disable lint or format hooks** while editing. If a hook fails, report the failure and stop.
- **Preserve file formatting** (indentation, quote style, class conventions). Read each file before editing it.
- **Batch edits per file**: load each file once, apply all accepted fixes, save once.

## Quality Assurance Checklist

Before finalizing:

- [ ] Newest report located (including the old `aeo-audit/` and `geo-audit/` folders) and its lenses identified
- [ ] References for every covered lens read and followed
- [ ] Framework detected; all fixes use idiomatic APIs
- [ ] Context7 mode stated in the terminal summary
- [ ] Safe-auto fixes batched and confirmed once; overlapping fixes applied once
- [ ] Intent and content fixes confirmed one at a time
- [ ] No content, date, identity or evidence invented
- [ ] All structured data is JSON-LD that follows `json-ld.md`
- [ ] `--dry-run` (or an unattended run) wrote nothing
- [ ] Each covered lens's own checklist satisfied
- [ ] Hand-offs printed, and the user told to re-run `/seo-audit`
