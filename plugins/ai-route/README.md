# AI-Route plugin

Routes a task to the best model and effort that [T3 Code](https://github.com/pingdotgg/t3code) can run now, and starts the work on it.

T3 Code runs models from several providers in one app. Picking one by hand for each task means checking leaderboards, remembering which effort levels each provider allows, and writing a new brief. `/route-task` does that:

- reads the live model list from T3 Code, so it never offers a model you can't run
- ranks the models by benchmark scores that match the kind of task, such as coding, design or research, and caches the research for 30 days
- adds each model's vendor facts (knowledge cutoff, context window, intended use, stated limits) and your own notes and past results
- picks an effort level, not only a model, by your effort setting: `cost`, `balanced` or `quality`
- starts the work in this thread, a new thread or a child task, with a full brief
- keeps a rules pointer in the global rules file of each harness that doesn't load `~/.claude/CLAUDE.md`, so a Grok or Antigravity thread still follows your rules

It runs only in T3 Code, because it needs T3 Code's tools to list models and start threads. A Grok thread in T3 Code loads Claude Code plugins and has T3 Code's tools, so the command can run there too.

## Available skills

### `/route-task`

```text
/route-task <task>                                  # ask mode: top 3 picks, you choose
/route-task --yolo <task>                           # start the top pick with no question
/route-task --effort cost|balanced|quality <task>   # override the effort setting for one run
/route-task --refresh                               # research every available model again now
/route-task --note <model> <text>                   # add an observation to a model's cache file
```

The command runs only when you type it. It never routes a thread's first message by itself.

#### Each run

1. Lists the models with `orchestrator_capabilities`, and skips providers that are disabled or can't run child tasks.
2. Checks the rules pointer for each harness. See [Rules pointer](#rules-pointer).
3. Researches each model that has no cache file, or one older than 30 days, in one subagent. It reads the benchmark sites, stores the raw scores for each model and effort with the site's name for the model and the fetch date, and reads the vendor's release notes once.
4. Puts the task in a category and ranks the candidates. Hard filters come first: a harness that lacks a tool the task needs is out. Then the category-matched scores decide, weighed by the effort setting. Your own results outweigh benchmarks once there are enough of them.
5. In ask mode, shows the top three picks with their scores, cost and time per task, and one line of reasoning. In yolo mode, starts the top pick.
6. Logs one row: the date, the task, the pick, the mode, the reason, and whether you overrode the recommendation.

#### Effort settings

| Setting | Picks |
| --- | --- |
| `cost` | The cheapest model and effort that scores within 10 points of the best for this kind of task |
| `balanced` | The cheapest model and effort that scores within 3 points of the best. Extra effort that adds only a point or two is skipped |
| `quality` | The highest score, whatever it costs |

#### Modes

- **stay**: the pick is this thread's model and effort, so the work runs here.
- **new thread**: a new T3 thread in the same project and checkout, on the picked model. This is the default for back-and-forth work.
- **child task**: a T3 child task for a defined piece of work, such as a review or a bounded fix.

Every brief tells the new model to read `~/.claude/CLAUDE.md` and the repository's rules first.

## Rules pointer

Only Claude Code loads `~/.claude/CLAUDE.md`. The Grok CLI reads its global rules from `~/.grok/`, and the Antigravity CLI from `~/.gemini/config/rules/`. Both cut off a rules file at a size cap (10,000 characters and 24,000 bytes), so a copy of a long CLAUDE.md would lose its end.

The router writes a short block instead, at the end of each harness's global rules file:

```markdown
<!-- route-task: rules pointer v2 -->
At the start of every session, read ~/.claude/CLAUDE.md in full and follow it.
In a repository, also read its CLAUDE.md and .claude/rules/ before you plan or edit.
Some rules name Claude Code tools. Where you lack that tool, follow the rule's intent with your own tools.
<!-- /route-task -->
```

- It checks for the block on every run.
- It backs up a file before it changes it, and never edits text outside its own markers.
- When a new version of the block ships, it replaces only its own block. Version 2 replaces the version 1 block that ai-t3 wrote.
- `syncRules` sets what it does when the block is missing: `ask` (the default), `auto` or `off`.
- For a harness it has no profile for, it says so and doesn't guess a path.

The profiles cover Claude Code, the Grok CLI, the Antigravity CLI and the Codex CLI.

## Files

The router keeps its data in `~/.claude/model-router/`, on your machine only:

| File | Holds |
| --- | --- |
| `config.json` | Your settings. The first run copies the defaults here |
| `models/<model-id>.md` | Benchmark scores by effort, the sites' names for the model, vendor facts, a summary from the data, and your own observations. A refresh never overwrites your observations |
| `log.md` | One row per run |
| `backups/` | Rules files from before the router changed them |

### Settings

| Key | Default | Meaning |
| --- | --- | --- |
| `mode` | `ask` | `ask` or `yolo` |
| `effort` | `balanced` | `cost`, `balanced` or `quality` |
| `syncRules` | `ask` | `ask`, `auto` or `off` |
| `cacheDays` | `30` | Days before a model is researched again |
| `balancedMargin` | `3` | Points `balanced` gives up to save cost and time |
| `costMargin` | `10` | Points `cost` gives up to save cost |
| `preferOtherProviders` | `false` | Prefer a harness other than the current thread's, such as Grok when the thread runs Claude Code, when two picks are close. Two instances of the same harness count as one |
| `skipProviders` | `[]` | Provider instances the router never offers, such as one you keep for one kind of work |
| `smallTasksStay` | `true` | With `balanced`, a lookup, a short summary or one quick check stays in the current thread when its model scores within `costMargin` of the best |
| `minOwnOutcomes` | `3` | Your results needed before they outweigh benchmarks |
| `sites` | four sites | The benchmark sites. Add or remove any |

### Benchmark sites

| Site | Read with | Gives |
| --- | --- | --- |
| [Artificial Analysis](https://artificialanalysis.ai/leaderboards/models) | Web fetch | Intelligence index, cost and time per task, context window |
| [Arena](https://arena.ai/leaderboard) | Web fetch | Agent Arena Index, Coding Index and category boards |
| [Slopalytics](https://slopalytics.com/) | Claude in Chrome | Artificial Analysis data for each effort level |
| [LiveBench](https://livebench.ai/) | Claude in Chrome | Overall and seven category scores, cost per successful task |

Slopalytics and LiveBench need JavaScript, so the research subagent reads them in your browser through Claude in Chrome. Without it, the router uses the other sites. A model on no leaderboard, such as an automatic model picker, gets "no benchmark data" and low confidence, and is never the recommended pick unless your own results support it.

## Requirements

- [T3 Code](https://github.com/pingdotgg/t3code), with at least one provider that can run child tasks
- Claude in Chrome, for the two JavaScript-only sites (optional)

## Installation

```
/plugin marketplace add charlesjones-dev/ai-agent-plugins
/plugin install ai-route@ai-agent-plugins
```

### Upgrading from ai-t3

This plugin was named ai-t3, and its command was `/t3-route`, before version 2.0.0. The new names follow T3 Code's guidance for third-party tools. Claude Code moves your enabled setting to ai-route, but you still need to run `/plugin install ai-route@ai-agent-plugins` once.

Your settings, research cache and log stay in `~/.claude/model-router/`. On its first run, `/route-task` replaces the old `t3-route` rules pointer in each harness's rules file with the new block.

## Plugin details

- **Name:** AI-Route
- **Version:** 2.0.0
- **License:** MIT
- **Author:** Charles Jones

## Contributing

Bug reports and fixes are welcome. See [CONTRIBUTING.md](../../CONTRIBUTING.md).

## License

MIT License. See [LICENSE](LICENSE).
