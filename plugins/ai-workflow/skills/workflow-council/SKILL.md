---
name: workflow-council
description: "Reviews a change in a loop with models from several providers, by default the latest from Anthropic, OpenAI and xAI. Each round they review read-only and give a verdict and a score. It fixes what they're right about and pushes back with evidence on the rest, until they approve or the round budget runs out. With one member it's a second-opinion loop. The first run asks which models sit on the council and saves the answer. Use when the user says 'council', 'sol loop' or 'second opinion', or asks for a review from another provider's model."
argument-hint: "[members, such as gpt,grok] [--base <ref>] [--setup [repo]] [--rounds N] [--unattended] [PR number] [what to review]"
---

# /workflow-council - Cross-model review loop

Get review from strong models of several providers, and loop until they agree the change is right. Every round costs the user money for each member. Keep the loop short and the change small.

User provided: $ARGUMENTS

`--unattended` means nobody is watching, as when the workflow-babysit skill runs the council. Then never ask the user anything. With no saved council, use the built-in default. A member that can't be reached is left out and named in the report, and a finding still disputed at the end is declined, with both sides written into the results.

`--setup` runs the [first-run setup](#first-run-setup) even when a council is saved, saves the answer, and stops. `--setup repo` saves it for the current repository instead of for the user.

## Members

Take the members from the first of these that applies:

1. The arguments, such as `gpt`, `gpt,grok` or `claude,gpt,grok`. "sol loop", or a request for a second opinion from one model, means that one member. "sol loop" means OpenAI's newest GPT Sol model.
2. The repository's saved council: `.claude/workflow-council.json` in the repository root.
3. The user's saved council: `~/.claude/workflow-council.json`.
4. Council members named in the project's or user's CLAUDE.md or AGENTS.md. Older setups use this.
5. Nothing saved: run the [first-run setup](#first-run-setup). With `--unattended`, don't ask. Use the built-in default instead, and say in the report that no council is saved and that `/workflow-council --setup` saves one.

The built-in default is three members: the newest flagship model from Anthropic, OpenAI and xAI.

Resolve each member when you run, from the route's model list. Never hardcode a model ID from memory. Use high reasoning effort unless the saved council sets another.

### Saved council file

Both files have the same format:

```json
{
  "members": [
    { "model": "Claude Opus", "effort": "high" },
    { "model": "GPT Sol", "effort": "high" },
    { "model": "Grok", "effort": "xhigh", "provider": "grok" }
  ]
}
```

- `model` is a family name or an exact model ID. A family name, such as "GPT Sol", means the newest model in that family on the route, so the council moves to new releases by itself. An exact ID, such as `gpt-6.1-sol`, pins that model.
- `effort` is optional. Use it where the route lets you set an effort. It defaults to `high`.
- `provider` is optional. It picks the T3 Code provider or the CLI when more than one offers the model, such as Grok through both the Grok and Cursor providers.

If a file isn't valid JSON, or has no `members` list, say so. Then treat that file as missing.

### First-run setup

1. **Find the reachable models**, with the routes in step 2:
   - In T3 Code, call `orchestrator_capabilities`. Every provider that can run child tasks counts, with the newest flagship model in each family.
   - In Claude Code, a Claude subagent is always reachable. Check the CLIs with `command -v codex grok agent cursor-agent`, and check that `agent --version` reports Cursor.
2. **Ask one question** with the AskUserQuestion tool, with `multiSelect: true`:
   - Question: "Which models should sit on your council? Pick models from at least two providers." Header: "Council".
   - Up to four options, one per reachable provider. Label each with the model family and its provider, such as "GPT Sol (OpenAI)". In the description, give the exact model the route offers now and the route, such as "gpt-6.1-sol through T3 Code".
   - Mark the built-in default members "(Recommended)", and list them first. If more than four providers are reachable, name the others in the question, so the user can type one under "Other".
   - Without the AskUserQuestion tool, ask in plain text with a numbered list, and wait for the answer.
3. **Save the answer.** Write `~/.claude/workflow-council.json`, or `.claude/workflow-council.json` in the repository root with `--setup repo`. Save family names, unless the user typed an exact model ID. Save `provider` only when more than one provider offers that model.
4. **Tell the user in one line** where the council is saved, and that `/workflow-council --setup` or editing the file changes it. Then go on with the review, unless the run was `--setup`.

If a member can't be reached, say which one and why, and ask whether to go on with the others (with `--unattended`, go on without it). Never put another model in its place on your own.

## Budget

- 3 rounds by default. Round 1 reviews the whole change. Later rounds review only the changed code and the open findings.
- Go up to 5 rounds only when a blocker or should finding stays open with evidence and the change touches security, permissions, auth, data loss, or state and concurrency. `--rounds N` or the user can set another limit.
- Stop early when a round returns only nits. Declined nits, and fixes to comments, docs or formatting, need no new round.
- Each member reviews alone. It must not start subagents or other reviewers.
- Keep a ledger: finding ID, member, severity, outcome and evidence, plus token usage if the route reports it. Never guess any of these.

## 1. Scope the change

Run `git status --short`. Don't stash, discard or include unrelated changes. If the change's paths separate cleanly from unrelated work, limit the review to them. Otherwise stop and ask.

Find the base after `git fetch origin`:

- **`--base <ref>`**: use that ref as the base, and skip the rules below. `--base HEAD` reviews only the uncommitted changes. A request in plain words, such as "only the uncommitted changes", means the same.
- **A PR**: `gh pr view <N> --json baseRefName,headRefOid`. Check out its branch only if the working tree is clean. Confirm that `HEAD` is the PR's head, or ahead of it only by this change. The base is `git merge-base HEAD origin/<baseRefName>`.
- **Local work**: `git merge-base HEAD origin/<default branch>`. With no remote, use a base the user names, or `HEAD` for uncommitted changes only.
- **A long-lived branch**: if the current branch is one that stays ahead of the default branch, such as `staging` or `develop`, the merge base would pull in earlier work the user didn't ask about. Ask which base to use, and recommend `HEAD` when there are uncommitted changes. With `--unattended`, use `HEAD` when there are uncommitted changes.

The change is the base compared with the working tree in those paths, plus untracked files. Use the same diff command in every round. Write the intent and what's out of scope in one or two sentences.

Run the checks that cover the change. Don't send code that the change breaks. Note missing checks, and checks that already failed before the change, in the brief.

## 2. Start the members

Pick a route for each member. Record the provider, model and effort each round used, but only as the route reports them.

### In T3 Code

Use this route when the `delegate_task` tool exists.

1. Call `orchestrator_capabilities` once, and pick each member's model and effort option from it.
2. Start one `delegate_task` per member, all in parallel, with `role: "review"`, `mode: "async"`, the brief as `task`, and the model and options in `target`. Save each `taskId`, and use a new `clientRequestId` every round.
3. Wait for the completion notices. Don't poll, and don't start a second reviewer for the same member.

A child's `childThreadId` is storage, not a place to send the next round. Never use `t3_thread_send`, `create_threads` or `t3_thread_launch` for review. Every round is a new `delegate_task`.

### In Claude Code

- **A Claude member**: a fresh subagent (the Agent tool, general-purpose type) with the brief, on the model the user asked for. It reads code and runs only read-only commands.
- **Another provider's member**: that provider's own CLI, run non-interactively and read-only from the repo root. Check the CLI's `--help` before the first run, because flags change between versions.

  Write the brief to a file with `mktemp`, and pass it from that file as below. Never paste the brief or the diff into a double-quoted argument, because the shell would run any backticks or `$(...)` in it.
  - **OpenAI**, through the Codex CLI: `codex exec --sandbox read-only --ephemeral -m <model> -c model_reasoning_effort="high" -o <answer file> - < "$brief"`. Leave out `-m` to use the user's configured model.
  - **xAI**, through the Grok CLI (`grok`): `grok --prompt-file "$brief" --permission-mode plan --no-subagents -m <model> --output-format plain > <answer file>`. Plan mode blocks file edits but still lets the member read files and run `git diff`. `grok models` lists the models, and `--reasoning-effort` sets the effort when the model takes one. Never pass `--always-approve` or `--permission-mode bypassPermissions`.
  - **Any model Cursor offers**, through the Cursor CLI: `agent -p --mode ask --model <model> --output-format text "$(cat "$brief")"`. `--mode ask` keeps it read-only, and `agent --list-models` lists the models. Never pass `--force` or `--yolo`. The Grok CLI also installs a command named `agent`, so check first that `agent --version` reports Cursor. Older Cursor installs name it `cursor-agent`. A brief passed as an argument has a size limit (128 KB on Linux), so when the diff is larger, list the changed files in the brief and let the member read them.

  Start every member in parallel, each as a background Bash command with a 15-minute timeout. Write each answer to a file and read only the final message.

A CLI that isn't installed, or isn't signed in, makes that member unreachable.

### Guard the working tree

Before each round, record a fingerprint of the working tree, and compare it after the round:

```bash
{ git rev-parse HEAD; git diff HEAD; git ls-files --others --exclude-standard | while IFS= read -r f; do shasum "$f"; done; } | shasum
```

If it changed, a member edited a file or committed. Stop and tell the user, and don't keep the change. Don't try to undo it yourself, because the member may have edited a file that holds the change under review. With `--unattended`, end the council there and report which member changed what. The skill that started the council stops on that report.

## 3. The brief

Members get no history, so the round 1 brief carries everything:

```text
Review only. Do not edit files, commit, push, comment on GitHub, or start subagents.
Repo: <absolute path>  Base: <SHA>
Intent: <1-2 sentences>  Out of scope: <list>
Checks: <command: result, for each check>
Change: git diff <base> [-- <paths>], plus these untracked files: <list>.
[Or, for a member that can't run commands: the diff, pasted below.]
Read the surrounding code. Find bugs, broken callers, and mismatches with the intent.
Skip style unless it hides a bug. Hold the change to the smallest one that meets the
intent: flag code, tests, or guards the intent does not need.
Severity: blocker = the intended case is wrong. should = a real bug that callers will
hit, within the intent. nit = everything else, including other paths, rare cases,
small performance costs, and extra compatibility.
Reply in exactly this format:
VERDICT: APPROVE or CHANGES
SCORE: <0-10>
<prefix>1 [blocker|should|nit] <file>:<line> <claim>. Fix: <suggestion>
```

Give each member its own ID prefix, such as `O` for OpenAI, `X` for xAI and `A` for Anthropic, and keep the IDs stable across rounds.

## 4. Answer the findings

Check each finding, and its severity, yourself. Another path, a rare case or a small cost is a nit, whatever label it came with.

- **Agree**: make the smallest fix. Prefer deleting or narrowing code over adding a lock, cache, helper or option. Fix the case that happened. Add one focused test that fails without the fix, if the intent needs it.
- **Disagree**: say why, with evidence: a file and line, a test or command output.
- **Out of scope, or a nit**: decline it in one line, and list it as a follow-up.

Update the ledger. Run the checks again, and `git diff --shortstat <base>`. If the review grew the diff, cut it back first. Don't agree with a finding just to end the loop. Fight scope creep: it's your job to keep the change the size the goal needs.

## 5. The next round

Start one only when budget remains and a blocker or should is open, behavior code changed, or the last approval doesn't cover the current diff.

Send each member a fresh brief: the round 1 brief, the ledger (`fixed:`, `disagree:` and `declined:` lines with evidence), the same base diff, and what changed since the last round. Ask it to check only the open IDs and the changed code, and to mark each earlier ID `resolved` or `still open: <reason>`. In T3 Code, that's a new `delegate_task`. With a CLI, it's a new run.

## 6. Stop

- **Agreed**: every member returns APPROVE on the current diff, no blocker or should is open, and you have no concern of your own.
- **Stuck**: a finding is still disputed after two replies, or the budget ran out. Show both sides in two or three lines each, and let the user decide with the AskUserQuestion tool, your recommendation first. With `--unattended`, don't ask: decline the finding, and put both sides in the results. Running out of budget isn't approval.

Don't push during the loop. After agreement, push only if the user asked you to push, ship or update the PR.

If the work is in a PR, put the results in its description, never in a comment. Write the body to a file and run `gh pr edit <N> --body-file <file>`. Place this section above the attribution line at the end, and keep anything a review bot wrote into the description:

```markdown
## Council review

Rounds: 2

| Member | Round 1 | Round 2 |
| --- | --- | --- |
| GPT (Codex CLI, high) | 7/10 | 9/10 |
| Grok (Grok CLI) | 8/10 | 10/10 |

Verdict: approved
```

Name each member by the model the route reported, and add the effort only if the route confirmed it. If a member gave no score, write `no score`. Never invent one. If there's no PR yet, put the same section in your final reply, so the skill that opens the PR can add it to the description.

## 7. Report

- The rounds, and each member's model and route.
- What the members changed, and the diff size before and after (`git diff --shortstat`).
- The findings you fixed, and the ones you declined, each with its reason.
- Token usage, if the routes reported it. Otherwise say they didn't.
- Whether you pushed.

---

Adapted from `council` and `sol-loop` in [tstack](https://github.com/t3dotgg/tstack) by Theo Browne (MIT). See THIRD-PARTY-NOTICES.md in this plugin.
