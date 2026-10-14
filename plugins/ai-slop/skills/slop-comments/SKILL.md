---
name: slop-comments
description: "Find code comments that add nothing to the code (narration, history, commented-out code, stale notes, signature restatements) and the workarounds they explain, then plan which to delete, which to rewrite, and which workarounds to fix at the cause. Report-only until the user approves, unless run with --fix. Use when the user runs /slop-comments, asks to remove, prune or clean up code comments, or asks which comments or workarounds in a codebase should go."
argument-hint: "[path, glob or all] [--fix]"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Agent
  - Bash(git diff *)
  - Bash(git log *)
  - Bash(git blame *)
  - Bash(git ls-files *)
  - Bash(git merge-base *)
  - Bash(git symbolic-ref *)
---

# Prune code comments

Agents copy what's already in a codebase. A comment that narrates the code teaches the next agent to narrate, and a comment that explains a workaround teaches it to write another workaround. Find the comments that add nothing and delete them. For each workaround a comment explains, work out from first principles whether to fix the cause, delete the workaround, or keep it with a comment that names the cause.

The default is deletion: a comment stays only when a keep rule in [comment-rules.md](comment-rules.md) clearly applies. One exception: never delete a comment and leave the workaround it explains. A workaround and its comment go together, or stay together with the cause named.

## Arguments

Arguments: $ARGUMENTS

Claude Code replaces the placeholder on the line above with the text typed after the command, and leaves the line empty when there is none. In agents that leave the placeholder unreplaced, use the text the user typed after the command.

- **Scope**, optional:
  - Nothing: the current branch's changes, meaning the diff from the merge base with the default branch plus staged, unstaged and untracked files. Only the comments the diff adds or changes are in scope, plus older comments in the changed hunks that the change made wrong. Leave the rest of each file alone, so the diff stays reviewable.
  - A path or glob: every comment in the matching files.
  - `all`: every comment in the repo's tracked source files.
- `--fix`: apply the plan without waiting for approval (see step 6). Use it for unattended runs. Without it, the skill reports and stops.

Examples:

- `/slop-comments`
- `/slop-comments src/billing/`
- `/slop-comments all`
- `/slop-comments "src/**/*.ts" --fix`

## 1. Load the project's rules

Read whichever of these exist: `CLAUDE.md`, `AGENTS.md`, `.cursor/rules/`, `CONTRIBUTING.md`, a knowledge base (`.claude/rules/kb/` or `.claude/kb/`), and the lint config. Note:

- comment conventions the project documents, such as doc comments on every export, a license header on every file, `// MARK:` sections, or a TODO format with issue numbers. These override comment-rules.md;
- lint rules that require comments (`jsdoc/require-jsdoc`, pylint `missing-function-docstring`, SwiftLint `missing_docs`, Rust `#![deny(missing_docs)]`). Keep what they require, and trim only the lines that restate the signature;
- doc generators the project publishes from (TypeDoc, Sphinx, rustdoc, DocC, Javadoc, godoc). Their source comments are public docs;
- the typecheck, lint and test commands, for step 6.

Then read [comment-rules.md](comment-rules.md). It's the checklist for every step below.

## 2. List the files

- **Default scope:** find the default branch ref. `git symbolic-ref --short refs/remotes/origin/HEAD` prints it as `origin/<default>`; otherwise use `origin/main` or `origin/master`, or the local branch when there's no remote. Take `git merge-base HEAD <ref>` as `<base>`, and list the changed files with `git diff --name-only <base>` plus `git ls-files --others --exclude-standard`. Read the hunks with `git diff <base>`. If nothing has changed, say so and ask whether to run on a path or on `all`. In an unattended run, stop there.
- **Path or glob:** the matching files.
- **`all`:** `git ls-files`, source code only.

Skip these in every scope, and say in the report what you skipped:

- vendored and third-party code (`vendor/`, `third_party/`, `node_modules/`, copied libraries);
- generated files: a `Code generated ... DO NOT EDIT` or `@generated` header, build output, lockfiles, minified files, snapshots;
- database migrations that have already run, since editing them rewrites history;
- config files such as YAML, TOML and `.env.example`, unless the arguments name them. Their comments are often the only docs for each setting;
- Markdown and other prose. `/slop-rewrite` covers those.

Count the comments per file with a rough grep for the language's comment markers, to see how big the job is. If more than about 20 files or a few hundred comments are in scope and your agent can run subagents, split the files by directory across parallel read-only subagents. Give each one its file list, the path to comment-rules.md, and this brief: "For every comment in these files, report `file:line`, the exact text, a verdict from comment-rules.md (delete, rewrite, encode, workaround or keep) and a one-line reason. For a workaround, also report what it works around and the evidence (`git log -L` or `git blame` on its lines, the commit message, any linked issue). When you aren't sure a keep rule applies, mark it delete and say what made you doubt it. Don't edit anything." You make the final call. Read every workaround and every doubted keep yourself.

## 3. Sort every comment

Read each file in full, not only the comment lines. Whether a comment is stale, or only restates the code, depends on the code around it. Give each comment one verdict from comment-rules.md:

- **Delete.**
- **Rewrite:** a keep whose wording is wrong, vague or longer than it needs to be.
- **Encode:** a comment that asks people to follow a rule the code doesn't enforce ("must be called after init", "keep in sync with X", "do not reorder"). Turn the rule into something that fails when it's broken, then delete the comment. If nothing fits, it's a keep, rewritten to give the reason.
- **Workaround:** the comment explains code that exists to get around a problem, including comment-form lint and type suppressions. See step 4.
- **Keep.**

## 4. Investigate each workaround from first principles

Don't take the comment's word for it. "IMPORTANT", "do not remove", "too risky to change" and "needed for X" are leads to check. They don't prove anything. For each workaround:

1. Read the workaround, the code it protects, and that code's callers.
2. Find where it came from: `git log -L <start>,<end>:<file>` or `git blame`, the commit message, and any linked issue or PR.
3. Name the cause in one sentence: what goes wrong without the workaround, and where the fault is. If you can't name it, say so. That's a question for the owner, not a reason to keep the code.
4. Check whether the cause still exists, by behavior rather than version numbers. A comment that names an old version can be wrong about which versions have the problem. Find the version the project actually resolves (the lockfile, or the installed package), then check that version's behavior in its installed source, changelog or release notes. Also check the browser or OS targets (`browserslist`, `engines`, the deployment target), and whether the code path it guards still runs. Note what you checked. If you can't check, such as when the dependency isn't installed and you have no web access, say so and make it a question.
5. Pick one outcome:
   - **Fix the cause:** the fault is in this codebase. Describe the change that removes the need for the workaround, such as awaiting the promise instead of a `setTimeout`, fixing the type instead of casting to `any`, or fixing the ordering instead of retrying. Size it: small (one function), medium (one module), or large (crosses modules or changes a public API). Name the tests that cover it, or say there are none.
   - **Delete:** the cause is gone. The bug was fixed in a version the project already uses, the target that needed it is no longer supported, or the code path is dead. The workaround and its comment both go.
   - **Keep and name the cause:** the fault is outside the codebase and still live, such as a browser bug, a vendor API quirk or a platform limit. Keep the workaround, and rewrite the comment to say what the cause is, link it, and say when the workaround can go.

   If the "workaround" turns out to be ordinary handling of documented behavior, it isn't one. See comment-rules.md, and judge the comment like any other.

When the answer depends on something only the owner knows, such as whether customers still run an old browser or whether a feature flag is on in production, make it a question.

## 5. Write the report

- Cite `file:line` and quote the comment.
- List every deletion, since step 6 works from the list, but group them by kind and quote only two or three per kind.
- Give every workaround its cause, the evidence, the outcome, and for a cause fix its size and tests.
- Drafted comments can't add facts. If a rewrite needs a bug link, version or date you can't find, ask for it under Questions.

Use this format:

```text
<One paragraph: the scope (the diff from <base>, the paths, or all), how many files and comments you read, what you skipped and why, the typecheck, lint and test commands step 6 will run (or that the project has none), the verdict in one or two sentences, and "I haven't changed anything.">

| Verdict | Comments |
|---|---|
| Delete | <n> |
| Rewrite | <n> |
| Encode, then delete | <n> |
| Workaround: fix the cause | <n> |
| Workaround: delete with its comment | <n> |
| Workaround: keep and name the cause | <n> |
| Keep | <n> |

## Delete
### <Kind> (<n>)
- `file:line` "<quote>"

## Workarounds
### Fix the cause
- **<Short label>** (`file:line`): "<quote>"
  - **Cause:** <one sentence, with the evidence: commit, issue, versions checked>
  - **Fix:** <the change>. Size: <small | medium | large>. Tests: <names, or none>
### Delete with its comment
- **<Short label>** (`file:line`): "<quote>". **Why it's safe:** <evidence that the cause is gone>
### Keep and name the cause
- **<Short label>** (`file:line`): "<quote>" → "<rewritten comment>"

## Encode, then delete
- `file:line` "<quote>" → <the type, assertion, test, lint rule or CODEOWNERS entry that replaces it>. Size and tests too, when it changes an exported API

## Rewrite
- `file:line` "<quote>" → "<new comment>"

## Kept
<Counts by keep rule, and any comment that's a good model for the rest.>

## Plan
<Numbered batches, each listing its files, in this order:
1. Deletions, rewrites and "keep and name the cause" comments. These change no behavior.
2. Workarounds whose cause is gone.
3. Constraints to encode.
4. Cause fixes, smallest first. Each medium or large fix, or API-changing encode, is its own batch.
Mark each batch that waits on a question.>

## Questions
<Numbered so the owner can answer "1. yes 2. no". Ask only what the code and git history can't tell you: browser or OS support, whether a flag or customer is still live, whether a dependency can be upgraded, whether a large refactor is wanted now. For each, say what you'll do for each answer and what you'll assume if they skip it. If there are none, say so.>
```

Without `--fix`, end your turn after the report.

## 6. Apply

Start when the owner answers, or straight after the report with `--fix`.

- Apply the batches in order, with targeted edits. When you delete a comment, delete its line too, and don't leave a stray blank line or reformat the code around it.
- Run the typecheck and lint after batch 1, and the tests after each later batch. If a cause fix breaks tests and the right fix isn't clear, revert that fix, keep the workaround with a comment that names the cause, and report it as open. If the project has no checks, say so in the final report.
- With `--fix`, apply batch 1, then batches 2 and 3 and the small cause fixes when tests cover the code they change, skipping anything that waits on a question. Leave the rest, and every question, in the final report as open.
- Don't commit or push unless asked.

## 7. Stop new ones

If the project's agent instructions have no rule about comments, offer to add one to wherever it keeps them (`AGENTS.md`, `CLAUDE.md` or a `.cursor/rules/` file). Adjust it to match what the owner decided:

```markdown
## Code comments
- Write a comment only for what the code can't say: a reason a reader can't see (an external bug, a spec, a measured trade-off), a surprising behavior, or a public API contract.
- Don't narrate the code, record history (commits do that), or leave commented-out code. Every TODO links an issue.
- Don't copy a workaround from elsewhere in the codebase. Fix the cause, or ask.
- Enforce a rule that matters with a type, assertion or test, not a comment.
```

Ask before adding it. With `--fix`, put it in the final report instead.

End with what changed in each batch, the test results for each cause fix, and what's still open.
