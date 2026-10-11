---
name: slop-rewrite
description: "Rewrite a file, or a block of text pasted after the command, to remove AI writing patterns (humanize it). Uses the same signal list as /slop-audit and adjusts to the kind of text (technical docs, README, blog post, PR or changelog) and to a light, standard or heavy rewrite."
argument-hint: "[type=docs|readme|blog|pr] [level=light|standard|heavy] [file, glob, or pasted text]"
disable-model-invocation: true
allowed-tools: [Read, Write, Edit, Grep, Glob, AskUserQuestion]
---

# Rewrite AI-sounding text

Rewrite text so it reads as written by a person: specific, plain and in the author's voice. Work from [signals.md](signals.md), the checklist `/slop-audit` also uses. Keep the meaning, and don't add facts.

## Arguments

Arguments: $ARGUMENTS

Claude Code replaces the placeholder on the line above with everything typed after the command, including pasted text over several lines, and leaves the line empty when there is none. In agents that leave the placeholder unreplaced, use the text the user typed after the command.

Read the arguments in this order:

1. **Settings** at the start, all optional: `type=` (`docs`, `readme`, `blog` or `pr`) and `level=` (`light`, `standard` or `heavy`).
2. **Input**, everything after the settings:
   - If it's a path or glob that matches files in the project, rewrite those files.
   - Otherwise, it's pasted text. Rewrite it as given, however many lines it runs to. Don't look for a file.
   - If nothing follows the settings, ask for the input (step 1).

Examples:

- `/slop-rewrite README.md`
- `/slop-rewrite type=blog level=standard docs/posts/launch.md`
- `/slop-rewrite type=pr level=light`, followed by a pasted PR description on the next lines

Ask only for what the arguments leave out. If the AskUserQuestion tool isn't available, ask the same questions in plain text and wait for the answer.

## Step 1: Get the input (only when the arguments gave none)

Use AskUserQuestion:

- Question: "What do you want to rewrite?"
  - Header: "Input"
  - Options:
    - "Text I'll paste" (description: "Paste the text in your next message")
    - "A file in the project" (description: "Give a file path or glob pattern")
    - "Scan project docs" (description: "Find Markdown and text files in README, CHANGELOG, docs/ and similar")
  - multiSelect: false

- **Text I'll paste:** ask the user to paste the text in their next message, then wait for it.
- **A file in the project:** ask for the path or glob, then read the files.
- **Scan project docs:** find `**/*.md`, `**/*.txt` and `**/docs/**`, list them, and let the user pick.

## Step 2: Content type (skip when `type=` was given)

When a file's name settles it, use that type and say so: `README*` is `readme`, and `CHANGELOG*` is `pr`. Otherwise use AskUserQuestion:

- Question: "What kind of text is this?"
  - Header: "Content type"
  - Options:
    - "Technical docs / API reference" (description: "Precision matters; no added personality")
    - "README / project docs" (description: "Light personality is fine; remove inflation")
    - "Blog post / article" (description: "Full personality; every signal applies")
    - "PR description / commit / changelog" (description: "Brevity first; strip filler")
  - multiSelect: false

## Step 3: Rewrite level (skip when `level=` was given)

Use AskUserQuestion:

- Question: "How heavy should the rewrite be?"
  - Header: "Level"
  - Options:
    - "Light (Recommended)" (description: "Fix clear AI tells only and keep most of the original")
    - "Standard" (description: "Fix every signal found and rewrite sentences where needed; keep the structure")
    - "Heavy" (description: "Rewrite freely for a natural voice; may restructure")
  - multiSelect: false

When no one can answer (an unattended run on files), use `level=light`, take the type from the file name or use `docs`, and say which defaults you used.

## Step 4: Rewrite

1. If you're in a project, read its writing rules first: `CLAUDE.md`, `AGENTS.md`, and any voice, style or brand doc. House style overrides the signals, so don't "fix" a documented choice.
2. Find the signals from [signals.md](signals.md) in the text. For prose, the sentence-level, chatbot, formatting and developer-text sections matter most. Check claims and numbers too.
3. Apply the content-type rules below.
4. Rewrite at the chosen level:
   - **Light:** fix clear tells only, such as filler phrases, hedging, chatbot leftovers, curly quotes in Markdown, emoji headings and em dashes.
   - **Standard:** fix every signal found and rewrite sentences where needed, keeping the structure.
   - **Heavy:** rewrite freely for a natural voice, restructure paragraphs, vary the rhythm and make vague lines specific.
5. Keep the meaning. Don't invent facts, numbers, names or quotes. When a line only works with a fact you don't have, such as an unmeasured figure, keep it general and list it as a question.
6. Keep each rewrite the same length or shorter, unless the level is heavy and the original was too vague to stand.

## Step 5: Results

- **Pasted text:** show the rewrite as one block that's easy to copy. Below it, list what changed, grouped by signal. Don't write any files.
- **Files:** show the rewrite, or a diff for long files, then the list of changes. Ask before applying the edits, and apply them as targeted edits rather than replacing the whole file.
- In both cases, end with any questions from step 4, such as figures the author should confirm.

## Content-type rules

| Content type | Personality | Focus | Skip |
|---|---|---|---|
| Technical docs / API reference | None. No first person, opinions or humor. | Remove filler, hedging and promotional language. Keep precision. | Voice and personality rules |
| README / project docs | Light. Brief asides are fine. | Remove promotional inflation, buzzword stacks and vague claims. Keep specifics. | Heavy personality, humor |
| Blog post / article | Full. Opinions, humor and varied rhythm are welcome. | Every signal applies. Add voice and specificity. | Nothing |
| PR / commit / changelog | None. Brevity above all. | Strip filler, hedging and promotional language. Compress. | Voice and personality rules; lists are fine |

## Voice and personality

Apply these fully to blog posts, lightly to READMEs, and not at all to technical docs, PRs, commits or changelogs.

- **Vary the rhythm.** Short sentences, then longer ones that take their time. Even sentence length is a tell even when the words are fine.
- **Have opinions.** "I'm not sure how I feel about this yet" reads as a person; a neutral list of pros and cons doesn't.
- **Admit mixed feelings.** "Impressive, and a little unsettling" beats a clean pro/con list.
- **Use "I" when it fits.** First person isn't unprofessional. "Here's what bugs me" signals someone thinking.
- **Be specific about feelings.** Not "this is concerning" but "there's something odd about agents running at 3am while nobody watches."
- **Let some mess in.** Perfect parallel structure reads as generated. Asides and half-formed thoughts read as human.

## Examples

**Inflated language** (README, standard)

> Nestled in the heart of downtown, this groundbreaking startup serves as a testament to the vibrant innovation ecosystem, showcasing the intricate interplay between technology and community.

> The startup is based downtown. It builds inventory tools for restaurants.

**Negative parallelism, false range and trailing -ing** (docs, standard)

> It's not just about code quality; it's about fostering a culture of excellence. The tool encompasses everything from automated testing to seamless deployment, ensuring teams can overcome challenges.

> The tool runs your tests and deploys your code.

**Chatbot leftovers** (docs, light)

> Great question! Here is an overview of the authentication system. As of my last update, the library supports OAuth 2.0. I hope this helps!

> The authentication system uses OAuth 2.0.

**PR padding** (pr, light)

> This PR addresses the issue where a race condition was occurring in the queue drain process.

> Fix race condition in queue drain.
