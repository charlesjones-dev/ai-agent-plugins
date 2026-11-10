# Plan template

A plan is written for an executor that knows nothing. It hasn't seen the advisor's session, the audit, the other plans or any earlier conversation. It may be a smaller, cheaper model. Assume it follows explicit instructions well, and that it's weak at filling gaps, at resolving ambiguity and at knowing when to stop.

Three properties let a weaker model carry out a plan:

1. **It stands alone.** Everything the executor needs is in the file: paths, code excerpts, conventions and commands.
2. **Every step has a check.** Each step ends with a command and the result to expect. The executor never has to judge whether it succeeded.
3. **It has hard limits.** It lists what's out of scope, and it names the conditions under which the executor stops and reports instead of improvising.

Name each file `NNN-short-slug.md`, numbered in the recommended order, such as `001-batch-order-queries.md`. `<plans>` below is the plans folder: `plans/`, or `improve-plans/` when the repository already uses `plans/` for something else.

## Template

```markdown
# Plan NNN: <Imperative title: what is true after this plan lands>

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before you move to the
> next step. If anything in "STOP conditions" happens, stop and report. Do not
> improvise. When you finish, update this plan's status row in
> `<plans>/README.md`, unless a reviewer dispatched you and told you that they
> maintain the index.
>
> **Drift check (run first)**: `git diff --stat <planned-at SHA>..HEAD -- <in-scope paths and every file this plan quotes>`
> If one of those files changed since this plan was written, compare the
> "Current state" excerpts with the live code before you go on. A mismatch is
> a STOP condition.

## Status

- **Priority**: P1 | P2 | P3 (P1: do first, because the leverage is high or other plans need it. P2: worth doing. P3: optional)
- **Effort**: S | M | L
- **Risk**: LOW | MED | HIGH
- **Depends on**: <plans>/NNN-*.md (or "none")
- **Category**: bug | security | perf | tests | tech-debt | migration | dx | docs | direction
- **Planned at**: commit `<short SHA>`, <YYYY-MM-DD>
- **Issue**: <GitHub issue URL, only when the plan was published with `--issues`>

## Why this matters

Two to five sentences: the problem, what it costs today, and what improves
when this lands. The executor and the human reviewer both read this for the
intent. Intent is what lets the executor make a correct call when a detail in
the plan is off.

## Current state

The facts the executor needs, written out here. Never "as discussed" or "see
the audit".

- The relevant files, each with one line on its role:
  - `src/orders/api.ts`: the order-list endpoint. It holds the N+1 query (lines 130-160).
- Short excerpts of the code as it is today, with `file:line` markers. Give
  enough for the executor to confirm that it's looking at the right code.
- The repository conventions that apply, with one exemplar file: "Error
  handling follows the Result pattern. See `src/lib/result.ts` and its use in
  `src/users/api.ts:40-60`. Match it."
- Vocabulary and design constraints from the repository's intent and design
  docs: the domain terms to use in names and comments, the design tokens and
  components to reuse, or the decision record this work must stay consistent
  with. Quote the lines. The executor hasn't read those docs.

## Commands you will need

| Purpose   | Command                  | Expected on success |
|-----------|--------------------------|---------------------|
| Install   | `pnpm install`           | exit 0              |
| Typecheck | `pnpm typecheck`         | exit 0, no errors   |
| Tests     | `pnpm test -- <filter>`  | all pass            |
| Lint      | `pnpm lint`              | exit 0              |

(The exact commands for this repository, confirmed during recon. Never guessed.
Leave out a row when the repository has no command for it, and say so.)

## Suggested executor toolkit

(Optional. Include it only when the executor's environment plausibly has the
skill or tool. Otherwise leave the section out.)

- Skills the executor should use if it has them, and for which step.
- Reference docs worth reading first, by path or URL.

## Scope

**In scope** (the only files you may change):
- `src/orders/api.ts`
- `src/orders/api.test.ts` (create)
- `<plans>/README.md` (this plan's status row only)

**Out of scope** (do NOT touch, even though they look related):
- `src/orders/legacy-api.ts`: a deprecated path that is due for deletion.
  A change there wastes effort and risks the v1 clients that still use it.
- Any change to the public response shape. Clients depend on it.

## Git workflow

(From recon. Match what the repository already does.)

- Branch: `improve/NNN-<slug>`, or the repository's own branch naming if it has one.
- Commit per step or per logical unit. Message style: <the repository's style, with one example from `git log`>.
- Do NOT push or open a pull request unless the operator told you to.

## Steps

### Step 1: <imperative title>

What to do, precisely. Name exact files and symbols. Show the target code
shape when the step depends on it: the pattern to produce, not always every
line.

**Verify**: `<command>` → <expected output>

### Step 2: ...

(Keep each step small enough to verify alone. Order the steps so the codebase
works between them where possible: add the new path, switch the callers, then
remove the old path. A step can end in an expected failure, such as a new test
that fails before the fix. Then the expected result says so.)

## Test plan

- The new tests to write, in which file, and the cases they cover: the happy
  path, the bug or regression this plan fixes, and named edge cases.
- The existing test to use as the pattern: "model it on `src/users/api.test.ts`".
- Verification: `<test command>` → all pass, including the N new tests.

## Done criteria

Machine-checkable. ALL must hold:

- [ ] `pnpm typecheck` exits 0
- [ ] `pnpm test` exits 0, and the new tests for <X> exist and pass
- [ ] `grep -rn "<old pattern>" src/` returns no matches
- [ ] No file outside the in-scope list is modified (`git status`)
- [ ] The status row in `<plans>/README.md` is updated

## STOP conditions

Stop and report (do not improvise) if:

- The code at the locations in "Current state" doesn't match the excerpts.
  The codebase has drifted since this plan was written.
- A step's verification fails twice after a reasonable fix attempt.
- The fix seems to need a change to an out-of-scope file.
- You find that the assumption "<key assumption>" is false.

## Maintenance notes

For whoever owns this code after the change lands:

- Future changes that will interact with this one, such as "if this endpoint
  gains pagination, revisit the batching from step 2".
- What a reviewer should look at closely in the pull request.
- Any follow-up this plan deferred, and why.
```

## The index: `<plans>/README.md`

The advisor writes the index after the plans. Executors and reviewers update it.

```markdown
# Implementation plans

Written by the improve skills on <date>. Carry the plans out in the order
below unless the dependencies say otherwise. Each executor: read the whole plan
before you start, honor its STOP conditions, and update your row when you
finish.

## Execution order & status

| Plan | Title | Priority | Effort | Depends on | Status |
|------|-------|----------|--------|------------|--------|
| 001  | ...   | P1       | S      | none       | TODO   |
| 002  | ...   | P1       | M      | 001        | TODO   |

Status values: TODO | IN PROGRESS | DONE | BLOCKED (with a one-line reason) |
REJECTED (with a one-line reason, such as "fixed independently" or "approach
abandoned"). A reviewer that approves a branch nobody has merged yet writes
`DONE (approved on <branch>, not merged)`.

## Dependency notes

- 002 needs 001 because <reason>.

## Findings not planned yet

- <finding>, `file:line`: vetted, with no plan yet. (So a later run can offer it again.)
- <lead>, `file:line`: not confirmed. (So a later run can check it.)

## Findings considered and rejected

- <finding>: not worth doing because <one line>. (So nobody audits it again.)
```

When nobody chose the plans, as in an unattended run, add one line under the title that says how they were chosen, such as "the top 3 by leverage".

## Quality bar

Check each plan against this list before you finish it:

- Could a model that has never seen this repository carry out the plan with only the plan file and the repository? If a step needs something from the advisor's session, write that into the plan.
- Is every verification a command with an expected result, and never a judgment such as "make sure it works"?
- Does every step name exact files and symbols, and never "the relevant module"?
- Do the STOP conditions name this plan's real risks, and not boilerplate?
- Would a reviewer who reads only "Why this matters" and "Done criteria" understand what they're approving?
- Is the file free of secret values? Give locations and credential types only.
- Is "Planned at" filled in, and does the drift check cover the Scope section and every file the plan quotes?
- Does the plan quote a file that an earlier plan changes? Then list that plan under "Depends on", or say that the excerpt is only a model to follow.
- For a security finding, does the plan describe the code change, the configuration change and the tests, and leave out step-by-step misuse details? A regression test can hold the smallest input that triggers the bug. Nothing else in the plan shows how to use the weakness against a running system.
