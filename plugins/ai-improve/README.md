# AI-Improve plugin

Audits a codebase and writes implementation plans that another agent, or a cheaper model, can carry out. Your most capable model does the part where judgment matters: it reads the code, decides what's worth doing and writes the spec. A cheaper model does the edits. The plugin's skills never change source code themselves. It runs in Claude Code, Codex and Cursor.

```
you             /improve-audit             a capable model advises
plans/          001-batch-order-queries.md self-contained specs
another agent   implements, tests, commits a cheaper model executes
```

The plugin is adapted from shadcn's [improve](https://github.com/shadcn/improve) skill. See [Credits](#credits).

## A first run

1. Run `/improve-audit` in the repository, or `/improve-audit quick` for a cheaper pass.
2. It maps the repository, audits it and shows a table of findings. Reply with the ones you want planned, such as "plan 1, 3 and 5".
3. The plans land in `plans/`, one file each, with an index that gives the recommended order. Read them before you hand them on, because they're written to be reviewed.
4. Give a plan to any agent ("implement plans/001-batch-order-queries.md"), or run `/improve-execute 001`. That command starts a cheaper model in a separate git worktree, reviews its diff against the plan and reports a verdict. You decide whether to merge.
5. In a later session, run `/improve-reconcile`. It checks what landed, refreshes the plans that the code has moved past, and rewrites the ones that got stuck.

## Available skills

### `/improve-audit`

Audits the repository and writes one plan for each finding you pick.

#### How it works

1. Reads the README, the agent instruction files, the config and the CI setup, and records the exact build, test, lint and typecheck commands. Every plan uses those commands as its checks. It also reads decision records, requirements docs, `CONTEXT.md`, `DESIGN.md` and `PRODUCT.md` when they exist, so it doesn't report a documented trade-off as a problem. Earlier reports from this marketplace's other audits, such as the ones in `docs/security/` and `docs/performance/`, count as leads to confirm.
2. Audits nine categories: bugs, security, performance, test coverage, tech debt, dependencies and migrations, developer tooling, docs and direction. On a larger repository it splits the work across parallel read-only subagents. Every finding carries `file:line` evidence, impact, effort, risk and confidence. A direction suggestion must cite evidence from the repository.
3. Vets every finding. Subagents over-report, so the advisor opens the cited code for every finding before you see it. It drops false positives, corrects wrong locations and records what it rejected, so the next run doesn't raise it again.
4. Shows the findings in a table ordered by leverage: impact divided by effort, weighted by confidence. You pick which become plans.
5. Writes one file per chosen finding to `plans/`, plus an index with the order, the dependencies and a status table.

| Argument | What it does |
|----------|--------------|
| `quick` | A cheaper pass: the hotspots only, three categories, about six high-confidence findings |
| `deep` | The whole repository, every category, with low-confidence items to investigate |
| `bugs`, `security`, `perf`, `tests`, `debt`, `deps`, `dx`, `docs`, `direction` | Audits only the categories you name |
| `branch` | Audits only what the current branch changes, and marks each finding as introduced by the branch or already there |
| `next` | Audits only direction, in more depth: four to six suggestions for where to take the project |
| A path | Audits only that directory |
| `--top N` | Doesn't ask which findings to plan. Writes plans for the top N, for unattended runs |
| `--issues` | Also publishes each plan as a GitHub issue |

#### Usage

```
/improve-audit
/improve-audit quick
/improve-audit deep src/api
/improve-audit security perf
/improve-audit branch
/improve-audit next
/improve-audit quick --top 3 --issues
```

### `/improve-plan`

Writes a plan without a full audit. It does one of four jobs:

- Given a description, it specifies one piece of work you already have in mind. It resolves what it can from the code, and asks you only about what's left.
- Given a report file, it turns another audit's findings into plans. The report can come from `/security-audit`, `/performance-audit`, `/modernize-audit`, `/accessibility-audit` or any other source that lists findings with file locations. It confirms each finding in the code first, because a report can be out of date.
- With `review <plan>`, it checks an existing plan against the quality bar and tightens it. For a plan written in the same session, it also asks a fresh subagent to read the plan cold and report where it would have to guess.
- With plan numbers and `--issues`, it publishes plans that already exist as GitHub issues.

#### Usage

```
/improve-plan add rate limiting to the public API
/improve-plan docs/security/2026-01-15-101500-security-audit.md
/improve-plan docs/performance/2026-01-15-113000-performance-audit.md P-002 P-005
/improve-plan review plans/004-rate-limit-public-api.md
/improve-plan 001 003 --issues
```

### `/improve-execute`

Hands one plan to an executor and reviews the result.

1. Checks that the plan's dependencies are done and merged, that its files haven't changed since it was written, and that the plan asks for nothing a code change has no reason to need.
2. Starts one executor on a cheaper model, in a git worktree of its own. In Claude Code that's a subagent with worktree isolation, one tier below the session's model by default, such as Sonnet. In T3 Code it can be a model from another provider. Name a model after the plan to choose one, such as `/improve-execute 003 haiku`.
3. Reviews like a tech lead: runs every done criterion again, fails any change outside the plan's scope, reads the whole diff, and checks that the new tests assert something.
4. Gives a verdict. APPROVE marks the plan done on its branch. REVISE sends specific feedback to the executor, for two rounds at most. BLOCK records the obstacle in the plan for `/improve-reconcile`.

It never merges, pushes or commits to your branch. It leaves the worktree and the branch for you, and tells you how to merge or remove them. If your agent can't start subagents, it says so and you give the plan to another agent yourself.

#### Usage

```
/improve-execute 001
/improve-execute 003 haiku
/improve-execute plans/004-rate-limit-public-api.md
```

### `/improve-reconcile`

Brings the plans up to date with the code. For each plan it acts on the status:

- `DONE`: checks whether an approved branch was merged, then checks that the done criteria still hold.
- `BLOCKED`: investigates the obstacle, then rewrites the plan around it or rejects it with a reason.
- `IN PROGRESS`: looks for the executor's worktree and branch, and asks you whether it's still running.
- `TODO`: runs the plan's drift check. If the code changed, it refreshes the excerpts and steps, or rejects the plan when other work already fixed the finding.

It ends with the list of plans that are ready to run. It changes only the plans folder.

#### Usage

```
/improve-reconcile
/improve-reconcile 002 005
```

## What makes a plan executable

A plan is written for the weakest executor that might get it: a model that never saw the advisor's session. Three properties carry that:

- It stands alone. The plan holds the exact file paths, excerpts of the code as it is today, the conventions to match with an example file, and commands that were confirmed during recon. It never says "as discussed above".
- Every step has a check. Each step ends with a command and the result to expect, and the done criteria are commands too. The executor never has to judge whether it succeeded.
- It has hard limits. The plan lists the files in scope and the files that look related but must stay untouched. It names STOP conditions, so a small model stops and reports when the code doesn't match the plan.

Each plan also names the git commit it was written against, so an executor runs a drift check before it changes anything. The template is [`plan-template.md`](skills/improve-audit/references/plan-template.md), and the audit checklist is [`audit-playbook.md`](skills/improve-audit/references/audit-playbook.md).

## The plans folder

```
plans/
  README.md                      the index: order, dependencies, statuses, rejected findings
  001-batch-order-queries.md
  002-characterize-billing.md
```

The skills use `improve-plans/` when the repository already has a `plans/` folder for something else. The folder is plain Markdown, so commit it with the code. Any agent or person can pick a plan up from it.

## Rules the skills keep

- They never change source code. Their only writes go to the plans folder. An executor edits code only in its own worktree, and merging is always your call.
- They run no command that changes your working tree. The audit reads, searches and runs read-only checks.
- They never copy a secret value. A finding gives the location and the credential type, and recommends rotation.
- They treat the repository, reports, plans and executor output as evidence, never as instructions.
- Asked to implement, they decline and point at the plan or at `/improve-execute`.
- `--issues` warns you before it publishes a security finding to a public repository.

## How it differs from other tools

- **Claude Code's plan mode** plans one task for the current session, and the same model then carries it out. These plans are files in the repository, written for a different agent that has none of the session's context.
- **Claude Code's Dynamic Workflows** run subagents on a task you already defined. This plugin finds and specifies the tasks. A workflow can then run the plans.
- **The other audits in this marketplace**, such as `/security-audit`, `/performance-audit` and `/modernize-audit`, go deeper in one area and save a report. `/improve-audit` is broader and shallower, and its output is plans. `/improve-plan <report>` turns one of those reports into plans.

## Installation

Claude Code:

```
/plugin marketplace add charlesjones-dev/ai-agent-plugins
/plugin install ai-improve@ai-agent-plugins
```

Codex:

```
codex plugin marketplace add charlesjones-dev/ai-agent-plugins
codex plugin add ai-improve@ai-agent-plugins
```

Cursor: add this repository as a team marketplace, or copy this folder to `~/.cursor/plugins/local/ai-improve`. See the [Cursor install steps](../../README.md#cursor).

## Plugin details

- **Name:** AI-Improve Plugin
- **Skills:** `/improve-audit`, `/improve-plan`, `/improve-execute`, `/improve-reconcile`
- **Version:** 1.0.0
- **License:** MIT
- **Author:** Charles Jones

## Credits

The four skills, the audit playbook and the plan template are adapted from [improve](https://github.com/shadcn/improve) by shadcn, an agent skill that audits a codebase and writes plans for other agents. improve is MIT licensed. This plugin splits its one skill into four commands, rewrites its text, and adds plans from another audit's report, a not-merged status for approved branches, and executor routes for agents other than Claude Code. The plan and index formats stay compatible, so a `plans/` folder that improve wrote works here. [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md) has the license and lists each adapted file.

## Contributing

Bug reports and fixes are welcome. See [CONTRIBUTING.md](../../CONTRIBUTING.md).

## License

MIT License. See [LICENSE](LICENSE).
