---
name: slop-audit
description: Audit a codebase's user-facing copy, metadata and page layouts for AI-written tells ("AI slop") and for factual errors in that copy. Scores each area, gives a concrete fix for every finding, and ends with numbered clarifying questions. Report-only until the user answers. Use when the user runs /slop-audit or asks for an AI slop audit, an AI-writing check, or whether a site, app or README "reads as AI-written".
argument-hint: '[scope or exclusions, e.g. "skip blog posts" or "only /about"] [live URL]'
allowed-tools: [Read, Glob, Grep, Agent]
---

# AI slop audit

Find the copy that reads as machine-written, the layouts that read as templates, and the statements that are wrong. Then give the owner a plan they can approve in one reply. The audit changes nothing; edits start only after the owner answers.

Arguments: `$ARGUMENTS`. Read them as scope (areas to include or skip) and, if a URL is present, the live site to check claims against. With no arguments, audit every user-facing surface in the repo.

## 1. Load the project's own rules first

Read whichever of these exist: `CLAUDE.md`, `AGENTS.md`, a knowledge base (`.claude/rules/kb/`, `.claude/kb/` or an older `docs/kb/`: its `_index.md`, `_global-learnings.md`, and anything named voice, style, writing, brand or copy), `DESIGN.md`, and notes from earlier audits. Note:

- owner rules about voice and positioning: what the owner does and doesn't offer, banned words, audience;
- house-style choices that look like tells but are deliberate (heading case, bold inline headers, a brand metaphor, a design element DESIGN.md defends). These override the generic signals, so don't flag them;
- decisions from earlier audits, so you don't re-ask settled questions;
- the live URL (site config, `package.json` homepage, `CNAME`, README) if the arguments didn't give one.

Then read [signals.md](signals.md). It's the checklist for every step below.

## 2. List every user-facing surface

Make the list before reading, so the report can say exactly what it covered. Depending on the codebase:

- **Web:** every page and route; shared layout (header, footer, nav); components that carry copy; data files that feed cards (products, projects, case studies, testimonials, FAQs); 404 and error pages; legal pages; forms (labels, placeholders, validation, success and failure messages); transactional emails; server error text users can see.
- **Metadata:** meta titles and descriptions, OG and Twitter tags and images, JSON-LD, `llms.txt` and `llms-full.txt`, `manifest.json`, RSS titles.
- **Apps:** localized strings, onboarding, paywall, empty states, alerts, App Store and Play metadata (fastlane `metadata/`, release notes).
- **Libraries and CLIs:** README, docs site, `--help` text, error messages, package description.

Skip whatever the arguments or a project rule exclude, and say in the report what you skipped.

If more than about 15 files carry copy, split them by area across parallel read-only subagents (Explore or general-purpose). Give each one its file list, the path to signals.md, and this brief: "Report every candidate with `file:line`, the exact quote and the signal name. Don't edit anything. Report everything you find; don't filter by severity." You do the scoring and filtering. Read the worst areas yourself before scoring them.

## 3. Read the copy and record findings

For each finding, record the area, `file:line`, the exact quote, the signal, and a concrete fix. Quote the text rather than paraphrasing it.

## 4. Count habits that repeat across areas

Grep every surface from step 2 and report counts, including how many files each appears in:

- em dashes in rendered copy and metadata (not code comments);
- the main tagline or positioning sentence, and how many surfaces repeat it;
- verb and adjective triplets, "No X, no Y, no Z" lists, "X, not Y" slogans;
- any word the copy leans on ("honest", "seamless", "real", a brand metaphor).

## 5. Check the facts behind the copy

These are errors, not slop. They get their own section and come first in the fix plan.

- **Legal pages against the code.** For every third party, cookie, tracker or data flow the privacy policy names, confirm the code uses it. Look for ones it misses: fonts, analytics, ad pixels, session replay, error tracking, email providers. If there's a live URL, fetch the page (`curl -sL`) and check which scripts actually load.
- **Copy against other copy.** Reply times, prices, product lists, counts, names and dates that differ between pages, emails and metadata.
- **Claims against reality.** A privacy or security claim that another page contradicts ("no ad trackers" on one page, a case study about installing a Meta Pixel on another). Also claims nothing in the repo backs up, stale stack descriptions, and hard-coded "New" or "Latest" labels.
- **Dead ends.** Error messages that send users to something that doesn't exist, nav or footer lists that miss products, OG images or components that are never wired up.

If you can't confirm a number from the repo or the live site, turn it into a question. Don't decide it yourself.

## 6. Visual pass

Read the page compositions. If the live site or a dev server is easy to reach and the session has a browser tool (Playwright MCP or similar), look at it too. Flag the template stacks and decorative patterns listed in signals.md. Judge each page as a whole: every block can be fine on its own while the stack still reads as a template.

## 7. Score each area

Score each area from 0 to 100 for how AI-written it reads:

| Score | Meaning |
|---|---|
| 0–15 | Specific and first-hand, with at most a stray tell |
| 16–35 | Mostly specific; a few tells a line edit fixes |
| 36–55 | A clear pattern a careful reader notices |
| 56–75 | Template-shaped; reads as generated |
| 76–100 | Generic throughout; nothing first-hand worth keeping |

Legal boilerplate is expected. Score legal pages on tone and filler only, and list their wrong statements under errors. Group small areas into one row (for example "Privacy, terms, 404") instead of padding the table.

## 8. Write the report

Rules for every finding:

- **Every finding gets a fix.** A fix says what to do: the replacement line, what to cut, what to merge, or what the rewrite must contain. "Rewrite this" on its own isn't a fix.
- **Drafted rewrites can't add facts.** If a better line needs a number, client name, capability or date you can't confirm, ask for it under Questions and write the draft without it.
- **Cite `file:line` and quote the text.**
- **Name what's already good,** so fixes can copy it ("the product cards are specific; use them as the model").
- **Write the report plainly:** short sentences, no em dashes outside quotes, no slogans. The report shouldn't contain the tells it reports.

Use this format:

```text
<One paragraph: the surfaces you covered (list them), anything you skipped and why, the verdict in one or two sentences (where the slop is concentrated, what's in good shape), and "I haven't changed anything.">

| Area | Slop (0–100) | Main tells |
|---|---|---|
<one row per area, highest score first>

## Habits repeated across the <site / app / docs>
<each habit with its count and file:line examples, then one **Fix:** for the habit as a whole>

## <Area>   (one section per area, in table order; areas under ~15 only appear under Already clean)
- **<Short label>** (`file:line`): "<quote>". <Why it reads as slop, in one sentence.>
  - **Fix:** <concrete action or replacement line>

## Visual
<template stacks and decorative patterns, each with a **Fix:**>

## Errors (not slop)
- **<Label>** (`file:line`): <what the copy says, what's true, and how you checked>. **Fix:** <action>

## Already clean
<what to keep, and which parts to use as the model>

## Fix plan
<Numbered batches in the order you'd do them, each listing the files it touches. Errors first, then the shared positioning sentence and every metadata surface that repeats it, then areas by score. Mark each batch that waits on a question.>

## Defaults I'll use unless you say otherwise
<Judgment calls you'll make without asking, one line each with the reason. Include rules carried over from earlier audits or the project KB.>

## Questions
<Numbered so the owner can answer "1. yes 2. no ...". Ask only about facts the owner alone knows, or real trade-offs that change the fix. For each, say what you'll do for each answer and what you'll assume if they skip it. Common ones: are these figures accurate; do you offer <service> now; is <third party> still on; who is this copy for; what should <list> include.>
```

There's almost always something only the owner knows, such as figures, services, audience, or which third parties are switched on. If you really have no questions, say so in that section. End your turn after the report, without starting any edits.

## 9. When the owner answers

- Apply their answers and any defaults they didn't override. Use your own judgment on everything else, and ask only when a fix is blocked.
- Keep each rewrite the same length or shorter, and match the voice of the copy listed under Already clean.
- Copy leaks into metadata. After you change a positioning line, grep for the old wording across every surface from step 2 (meta descriptions, JSON-LD, `llms.txt`, manifest, OG text, emails) and remove every match. Keep meta descriptions within the project's limit, or 155 characters if none is documented.
- If hero copy feeds a generated OG image, regenerate the image. If a legal page's content changes, update its effective date and mention that you did.
- Run the project's checks (typecheck, lint, build, and any audit scripts). If a dev server is easy to start, look at the changed pages in a browser.
- Record the owner's answers as rules wherever the project keeps conventions (its KB via `/kb-add` if the ai-knowledge plugin is installed, `CLAUDE.md`, or a voice doc), so later sessions don't bring the old copy back.
- Report what changed in each area. List the calls the owner may want to check, such as new facts you wrote in their voice, removed visual elements, or changed policy dates. Also list anything still open. Don't commit or push unless asked. If meta descriptions changed, list the URLs to resubmit for indexing.
