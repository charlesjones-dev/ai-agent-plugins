# Comment rules

The checklist for `/slop-comments`. Project rules (CLAUDE.md, AGENTS.md, Cursor rules, the KB, lint config) override anything here. The examples are illustrative and mix languages.

**The test:** if you delete this comment, does a careful reader lose something they couldn't get in a minute from the code, the names, the types, the tests or `git log`? If not, it goes. When you aren't sure a keep rule applies, it goes.

**The exception:** a workaround's comment never goes while the workaround stays. An unexplained hack is worse than an explained one, and it still gets copied.

**What counts as one comment:** a block of consecutive comment lines, such as a doc comment, or a label plus the commented-out code under it. Split a block only when its lines get different verdicts.

## Delete

| Kind | What it looks like | Fix direction |
|---|---|---|
| Narration | `// loop through the users`, `# increment the counter`, `// return the result`, `// Step 2: validate the input` | Delete. If the code doesn't say it clearly, rename something or extract a function instead |
| History | `// Updated to use the new API`, `// Fixed bug where…`, `// Changed from forEach to map`, `// Added for JIRA-123`, `// New implementation`, `// Refactored` | Delete. Git keeps the history |
| Commented-out code | Disabled blocks kept "just in case" | Delete. Git keeps it |
| Stale | Describes behavior the code no longer has, or names a function, parameter, flag or file that doesn't exist | Delete, or rewrite it if what it meant is still true and still needed |
| Signature restatement | `@param id the id`, `@returns the user`, `"""Gets the user."""` on `get_user()`, `/// Initializes a new instance` | Delete the lines that restate. Keep units, ranges, errors and side effects the signature doesn't show |
| Banners and dividers | `// ===== Helpers =====`, `/**********/`, `# --- Constants ---` | Delete. A file that needs banners to be readable may need splitting |
| Agent leftovers | `// Here's the updated function`, `// Add your logic here`, `// TODO: implement` in finished code, `// Replace with your API key`, `// This is a simplified version`, `// In a real app you would…` | Delete. If it marks work that's really missing, raise it as a question |
| Vague TODOs | `TODO: clean this up`, `FIXME`, `HACK` or `XXX` with no issue, owner or condition | If you can tell what it means and it's small and in scope, do it now; if it's bigger, ask whether to file an issue. If you can't tell what it means, delete it, and ask only about something concrete you found nearby. Either way the comment goes |
| Obvious language notes | `// async function`, `// constructor`, `// using map for immutability`, `// for performance` with no measurement behind it | Delete |
| Hedges and apologies | `// not sure why this is needed`, `// just in case`, `// for safety`, `// a bit hacky but it works` | Treat it as a workaround: find out whether the code is needed, then delete the comment along with the code or replace it with the reason |
| Dead directives | A directive no tool reads where it sits: `// @ts-check` in a `.ts` file (TypeScript honors it only in JavaScript), a suppression for a linter or rule the project doesn't configure, a `# noqa` on a line with no warning | Delete. If the suppressed rule would protect correctness, fix the code it was hiding too |
| Test scaffolding | `// Arrange`, `// Act`, `// Assert`, `// should return true` above `expect(result).toBe(true)` | Delete, unless the project's test style requires them |

## Encode, then delete

A comment that asks people to follow a rule the code doesn't enforce:

- `// must be called after init()`
- `// keep in sync with schema.ts`
- `// do not reorder: the API depends on this order`
- `// IMPORTANT: always check permissions first`
- `// do not change this wording`
- `// talk to <name> before changing this`

Turn the rule into something that fails when it's broken, then delete the comment:

- a type: a required parameter, a state or branded type, an enum the compiler checks exhaustively;
- a runtime assertion or guard;
- a test, such as one that pins the order or checks that two lists match;
- a lint rule or CI check;
- a CODEOWNERS entry, for "talk to someone before changing this".

Pick the smallest enforcement that works. On an exported or shared API, prefer a runtime assertion or a test to a type redesign, and plan a redesign the way you'd plan a cause fix, with a size and the tests that cover it.

If none fits, keep the comment and rewrite it to give the reason, so the next reader can judge it. A rule with no reason ("do not change") is what makes agents leave bad code alone.

## Workarounds

A comment that explains code which exists to get around a problem:

- `// setTimeout so the DOM has updated`
- `// retry 3 times because the API is flaky`
- `// sleep so the server is ready`
- `// cast to any, the types are wrong`
- `// copy the array or it gets mutated`
- `// call it twice or the state doesn't update`
- `// workaround for…`, `// hack:`, `// IMPORTANT: do not remove`

Not every guard a comment calls a hack is a workaround. Code that handles a dependency's documented behavior (a parser that throws on bad input, an API that paginates) or invalid input is the function's contract. Judge its comment like any other: delete it if the code says enough, or rewrite it to state the behavior, without the "hack" label.

Comment-form suppressions are workarounds too: `// eslint-disable-next-line`, `// biome-ignore`, `// @ts-ignore`, `// @ts-expect-error`, `# type: ignore`, `# noqa`, `// nolint`, `// swiftlint:disable`, `// NOSONAR`. Look up the rule each one turns off.

- If the project doesn't run that linter or rule, the suppression is dead (see Delete).
- If the rule protects correctness or safety (`no-floating-promises`, `react-hooks/exhaustive-deps`, a type error), change the code, not the rule.
- If it's a style rule the team doesn't follow, the fix may be turning the rule off in config instead of suppressing it file by file. Ask.
- A suppression that stays names its reason on the same line. Prefer `@ts-expect-error` to `@ts-ignore`, since it fails once the error is gone.

Investigate each one as step 4 of the skill describes. The outcome is one of three: fix the cause, delete the workaround with its comment because the cause is gone, or keep it with a comment that names the cause.

## Keep

Only these:

| Kind | What it looks like |
|---|---|
| Tooling directives | Anything a tool reads where it sits: `// @ts-check`, `/* webpackChunkName: "x" */`, `/* @vite-ignore */`, `//go:build`, `//go:generate`, `//go:embed`, `# frozen_string_literal: true`, `# -*- coding: utf-8 -*-`, shebangs, `// prettier-ignore`, `/* istanbul ignore next */`, `/*! … */` comments a minifier preserves, editor markers the project uses (`// MARK:`, `#region`). Suppressions are directives too, but check them as workarounds |
| Legal | License and copyright headers, SPDX lines, and attribution a license requires |
| Public API contracts | Doc comments on a published or shared API that tell callers what the signature can't: units, valid ranges, what `null` means, errors thrown, side effects, thread safety, an example. Rust doc examples run as tests, and so do Python `>>>` examples when the project runs doctest. Trim the lines that only restate the signature |
| Reasons a reader can't see | Why the code is this way when the cause is outside the code: a spec section, an RFC, a vendor or platform bug, a regulation, a measured performance trade-off. Best with a link, and for anything temporary, when it can go |
| Surprises | Behavior that would trip up a careful reader, such as "Returns the cached value even when `force` is set, because the upstream API rate-limits refreshes." If the code can change so it stops surprising, prefer that |
| Dense notation | A regex, bit math or a formula that would take a careful reader more than a minute to work out, with its source. A short regex like `^\d{4}-\d{2}-\d{2}$` doesn't qualify. First try named capture groups, named constants or a well-named helper, and keep the comment only if those aren't enough |
| Tracked TODOs | A TODO with an issue link or a concrete condition: `TODO(#412): remove after the v3 migration ships` |
| Required by the project | Comments the project's documented rules or lint config require |

## Rewriting a comment that stays

- Lead with the reason, not the mechanics.
- Link the source: the issue, the bug report, the spec.
- For a temporary workaround, say when it can go: "Remove when browserslist drops Safari 16."
- Keep it to a line or two, and leave out history ("we used to…").
- Don't add facts. If the rewrite needs a link, version or date you can't find, ask the owner for it.

## Examples

**Narration and history** (delete)

```ts
// Updated to filter inactive users
// Loop through users and keep the active ones
const active = users.filter((u) => u.isActive);
```

```ts
const active = users.filter((u) => u.isActive);
```

**Workaround with the cause in this codebase** (fix the cause)

```js
// HACK: wait for the modal to render before focusing
setTimeout(() => input.focus(), 100);
```

The modal mounts after an async state update. Focus the input from the modal's own mount hook, or await the update, and delete both the timeout and the comment.

**Workaround with the cause outside the codebase** (keep and name the cause)

```css
/* fix for safari */
.panel > * + * { margin-top: 1rem; }
```

```css
/* Safari <version> <what it gets wrong> (<bug link>).
   Remove when browserslist drops Safari <version>. */
.panel > * + * { margin-top: 1rem; }
```

**Unenforced constraint** (encode, then delete)

```py
# must call connect() before query()
```

Have `connect()` return a `Connection` that owns `query()`, so calling them in the wrong order can't type-check, then delete the comment.
