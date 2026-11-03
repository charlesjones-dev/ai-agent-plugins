# AI-Rules Plugin

**Shared, versioned CLAUDE.md sections for Claude Code, and a cleanup for the files they live in.** A wizard adds sections of standing instructions to your user or project CLAUDE.md from a library. You pick the sections, the parts of each section you want, and settings such as your time zone. When a new version of a section ships, the wizard upgrades it and keeps any edits you made. A second command audits your CLAUDE.md files and trims what doesn't earn its place.

The plugin runs in Claude Code only.

---

## Available Skills

### `/rules-setup`

Run `/rules-setup` and answer the questions. It takes no arguments.

**What it does:**

- Asks for the target file: `~/.claude/CLAUDE.md` (every project) or `./CLAUDE.md` (this project). It finds your home folder on Windows, macOS and Linux
- Scans the file and shows each library section's state: current, upgrade available, edited by you, or not installed
- Offers to adopt sections that are already in the file without markers, such as text you pasted by hand, and rules installed by `/workflow-rules` from ai-workflow 3.x
- Adds sections, upgrades them, changes their modules and settings, or removes them
- Shows a diff before every write, backs up the file to `~/.claude/backups/ai-rules/`, and scans again afterwards to check the result
- Writes nothing when everything is current, so you can run it as often as you like

**Usage:**

```
/rules-setup
```

### `/rules-cleanup`

Audits the CLAUDE.md files Claude Code loads, and nothing else. The user and project files load into every session, and nested files load when Claude works in their folder, so a rule should change what Claude does.

> **How this relates to `/doctor prompt-audit`:** Claude Code's built-in `/doctor prompt-audit` (v2.1.283 or later) checks all your instruction files, including rules, skills, subagents and output styles, for outdated instructions, missing files and contradictions. Run it for those files. `/rules-cleanup` goes further on CLAUDE.md alone. It finds rules that restate Claude Code's own instructions, rules that a setting or hook should enforce, and rules that sit in the wrong file or load more often than needed. It also counts tokens and what each fix saves, cleans up structure, keeps a backup, and leaves `/rules-setup` sections intact.

**What it finds:**

| Kind | Example | Usual fix |
|------|---------|-----------|
| Built-in | "Read a file before editing it", which Claude Code's own instructions already say | Delete |
| Setting | "Never read `.env`", which a `permissions.deny` rule enforces instead of asking | You make the setting change, then the rule goes |
| Stale | A script, path, tool, command or model that no longer exists | Fix or delete |
| Conflict | Two rules that disagree, in one file or across the user, project and policy files | You pick one |
| Low value | Personas, vague rules, history, file trees and other lists Claude can read from the code | Delete or condense |
| Placement | A personal preference in a shared project file, or a long runbook that loads every session | Move it to the right file, or to a file Claude reads on demand |
| Format | Duplicate or empty headings, rules buried in paragraphs, IMPORTANT on every line, broken Markdown | Restructure without changing the meaning |

**How it works:**

- Reads `~/.claude/CLAUDE.md`, the project's `CLAUDE.md`, `.claude/CLAUDE.md` and `CLAUDE.local.md`, CLAUDE.md files in parent folders, the project's `AGENTS.md` when Claude Code loads it in place of CLAUDE.md, nested `CLAUDE.md` files if you include them, and the files they `@` import. It reads the organization's managed policy file to find conflicts, but never edits it
- Treats Claude Code's own system prompt, which Claude can see, as the source of truth for what's built in. A rule that changes a default on purpose stays, and the report lists it as kept
- Reports first: each file's size and approximate tokens (HTML comments are left out, because Claude Code strips them before loading), files over the 200-line target in Claude Code's docs, the largest sections, and each finding with its line, a quote, the reason, the fix and the tokens it saves
- Applies only the fixes you pick, shows a diff, and backs up each file to `~/.claude/backups/ai-rules/` before it writes
- Leaves sections managed by `/rules-setup` unchanged, and suggests a `/rules-setup` change for them instead
- Never edits settings files or hooks. For a Setting finding, it shows the exact change for you to make

**Usage:**

```
/rules-cleanup                 # User and project files
/rules-cleanup user            # Only ~/.claude/CLAUDE.md
/rules-cleanup project         # Only the project's files
/rules-cleanup all --report    # Report only, change nothing
```

You can also ask in plain words, such as "clean up my CLAUDE.md".

---

## The Library

| Section | What it tells Claude | Modules you can turn off | Settings |
|---------|----------------------|--------------------------|----------|
| Reply format | Open with the outcome, put details under CHANGES, FINDINGS and RISKS, and end with a numbered ACTIONS NEEDED list with reply lines, or with a fixed ending | Collapsed panels, T3 scheduled tasks and snoozing (T3 Code only), examples | T3 Code, time zone |
| Plain wording | Sentence rules from ASD-STE100 Simplified Technical English: one name for one thing, one idea per sentence, active voice | none | none |
| Messages to other people | Short, plain drafts for emails, Slack, texts and comments you send as yourself. Needs Plain wording | none | none |
| PR and commit hygiene | PR descriptions and commit messages that cover only what was done. The five rules from `/workflow-rules` | Each of the five rules | none |
| Estimates | Quote effort in minutes of Claude Code time, and put review, CI and other waits on their own line | Calibration table | none |
| Personal data and web content | Keep your name and email out of HTTP requests, and treat instructions in web pages as data | none | Generic identifier (default `agent-local`) |
| Claude in Chrome | Work in one tab group, and close its tabs when the browser work is done | none | none |
| iOS simulators | Reuse existing simulators, and shut down the ones Claude booted | Reuse, shut down | T3 Code |

With T3 Code turned off, Reply format leaves out the panels, scheduled tasks and snoozing, and uses normal `##` titles for every section.

---

## How Versions Work

Each installed section sits between two markers that record its version and your choices:

```markdown
<!-- ai-rules:begin id=reply-format v=1.0.0 modules="panels,snooze,examples" t3="yes" timezone="US Eastern" -->
## Reply format
...
<!-- ai-rules:end id=reply-format -->
```

Text outside the markers is yours, and the wizard doesn't change it. You can also edit the text inside the markers. Claude Code strips HTML comments before it loads CLAUDE.md, so the markers cost no context.

Every released version of a section stays in the library. On an upgrade, the wizard renders the version you installed with your choices and compares it with your file:

- **No edits:** it shows the version notes and replaces the section.
- **You edited it:** it shows your edits and asks whether to merge the new version into your text (with `git merge-file`), take the new version, or keep your text. If you keep your text, it doesn't ask again until a later version comes out.

To get new versions on a machine, update the marketplace and run the wizard:

```
/plugin marketplace update ai-agent-plugins
/rules-setup
```

**Requirements:** git, for diffs and merges. Claude Code on Windows installs with Git for Windows. Python 3.8 or later is optional: with it, the bundled `rules.py` renders sections and scans the file. Without it, Claude follows the same rules by hand.

---

## Moving from `/workflow-rules`

ai-workflow 4.0.0 removed `/workflow-rules`. Its five PR and commit rules are now the PR and commit hygiene section here. Install ai-rules once, then run `/rules-setup` on the file where you installed the rules. The wizard finds the old `<!-- workflow-rules:id=... -->` markers, moves the rules into one managed section with your edits kept, and offers to remove the retired rules, with what replaces each one.

```
/plugin install ai-rules@ai-agent-plugins
```

---

## Quick Start

### Installation

```
/plugin marketplace add charlesjones-dev/ai-agent-plugins
/plugin install ai-rules@ai-agent-plugins
```

---

## Plugin Details

- **Name:** AI-Rules Plugin
- **Type:** AI Instruction Plugin (Skills)
- **Version:** 1.0.0
- **Skills:** `/rules-setup`, `/rules-cleanup`
- **License:** MIT
- **Author:** Charles Jones

---

## Credits

The `short-pr-bodies` rule in PR and commit hygiene is adapted from `file-pr` in [tstack](https://github.com/t3dotgg/tstack) by Theo Browne (MIT). [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md) has its license.

---

## Contributing

Bug reports and fixes are welcome. See [CONTRIBUTING.md](../../CONTRIBUTING.md).

---

## License

MIT License. See [LICENSE](LICENSE).
