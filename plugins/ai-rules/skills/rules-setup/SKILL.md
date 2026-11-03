---
name: rules-setup
description: "A wizard that adds, upgrades, changes and removes versioned sections of standing instructions in CLAUDE.md, picked from a shared library: reply format, plain wording, messages to other people, PR and commit hygiene, estimates, personal data, Claude in Chrome and iOS simulators. Each section has optional modules and settings, and upgrades merge new versions into sections you edited."
disable-model-invocation: true
---

# Rules Setup

You manage sections of standing instructions in a CLAUDE.md file. Each section comes from the library in this skill's folder, has a version, and can have optional **modules** (parts the user turns on or off) and **options** (values such as a time zone). Installed sections sit between markers that record the version and the user's choices, so you can upgrade them later without losing the user's edits.

## Instructions

**CRITICAL**: This command takes no arguments. If the user typed anything after it, ignore it and gather all input with AskUserQuestion as described below.

Keep messages short. If the user cancels at any step, say "No changes made." and stop.

### AskUserQuestion limits

Every question has 2 to 4 options, and one call holds up to 4 questions. The user can always type their own answer through "Other".

- Split a list longer than 4 into questions of 2 to 4 options each, in catalog order. Balance the split, so 5 becomes 3 + 2, never 4 + 1.
- A list of one becomes a yes/no question.
- A multi-select question can't preselect options. Add "(recommended)" to the label of each option that is on by default.

### Step 1: Find the tools

1. **The library.** `${CLAUDE_SKILL_DIR}/library/catalog.json` lists every section, its current version, every released version with a one-line note, its modules and its options. Each released version of a section is a template at `${CLAUDE_SKILL_DIR}/library/<section-id>/<version>.md`.
2. **Python.** Try `python3 --version`, then `python --version`, then `py -3 --version`. Use the first that prints `Python 3.8` or later. On Windows, `python` can be a stub that opens the Microsoft Store and prints nothing, so skip any command that doesn't print a version. If Python is found, use `${CLAUDE_SKILL_DIR}/scripts/rules.py` for rendering and status. If not, work in **manual mode**: follow [Rendering](#rendering) and [Status by hand](#status-by-hand) yourself.
3. **Git.** Check `git --version`. You use `git diff --no-index` for previews and `git merge-file` for upgrades of edited sections. Claude Code on Windows installs with Git for Windows, so git is normally there. Without git, compare and merge the text yourself, and show the diff as plain text.
4. **A scratch folder.** Use your scratchpad directory if you have one. Otherwise make a temporary folder (`mktemp -d` in Bash, `New-Item -ItemType Directory (Join-Path $env:TEMP "rules-setup-<timestamp>")` in PowerShell). Write every intermediate file there, never next to the target file.

### Step 2: Pick the target file

Ask:

- Question: "Which CLAUDE.md should I set up?"
  - Header: "Target"
  - Options:
    - "User CLAUDE.md (recommended)": `~/.claude/CLAUDE.md`, loaded in every project
    - "Project CLAUDE.md": `./CLAUDE.md`, loaded in this project for everyone who clones it

Resolve the home folder with the first of these that returns a path: `echo "$HOME"` (macOS, Linux, WSL, Git Bash), `$env:USERPROFILE` (PowerShell), `echo %USERPROFILE%` (cmd). Forward slashes work in file paths on Windows.

If the file doesn't exist, ask "No CLAUDE.md at `<path>`. Create it?" with "Yes, create it" and "Cancel". On yes, treat it as empty.

### Step 3: Scan the file

Run `<python> "${CLAUDE_SKILL_DIR}/scripts/rules.py" status "<path>"`, or follow [Status by hand](#status-by-hand). The JSON has:

- `blocks`: each installed section, with its `state`:
  - `current`: matches the library's current version.
  - `edited`: the user changed the text. It is on the current version.
  - `upgrade`: a newer version exists, and the text is unchanged.
  - `edited-upgrade`: a newer version exists, and the user changed the text.
  - `kept`: the user chose to keep their text over the newest version. The block won't be offered for upgrade again until a later version comes out.
  - `newer`: the file was written by a newer version of this plugin. Leave the block alone, and tell the user to run `/plugin marketplace update ai-agent-plugins` and update ai-rules on this machine.
  - `unknown`: the library has no section with this ID, for the same reason as `newer`, or because the section was removed. Offer only Remove for it.
  - `duplicate` or `broken`: a marker problem.
- For upgradable blocks, `changes` (the notes for each version after the installed one) and `new_modules` (modules added since then).
- `unmanaged`: library sections whose heading is in the file without markers, such as sections pasted by hand, with the lines each one covers (`line` to `end_line`).
- `legacy`: markers left by `/workflow-rules`, the ai-workflow skill this one replaces. Retired rules carry their replacement.
- `available`: sections not in the file at all.
- `problems`: marker errors.

Show the user a short status table: each section's title, installed version, current version and state, plus a line for unmanaged sections and legacy rules. If `problems` is not empty, list them and stop. Tell the user to fix the markers by hand, or to delete the broken block, then run `/rules-setup` again. Never guess where a broken block ends.

### Step 4: Offer to adopt existing text

If `unmanaged` or `legacy` is not empty, ask before the main menu:

- Question: "<N> sections in this file match the library but have no markers. Bring them under management so they can be upgraded later?"
  - Header: "Adopt"
  - Options: "Yes, adopt them (recommended)" / "Not now"

On yes, run [Adopt](#adopt), then scan again before the menu.

### Step 5: Main menu

Build the options from the scan, in this order, and leave out any that has nothing to act on:

- "Upgrade <N> sections (recommended)": blocks in state `upgrade` or `edited-upgrade`
- "Add sections": something is in `available`
- "Change modules or options": at least one block is `current`, `edited`, `upgrade`, `edited-upgrade` or `kept`
- "Remove sections": at least one block exists
- "Done": always, when fewer than four options are left

If only "Done" would be left, say "Everything is current. Nothing to change." and stop.

Ask "What would you like to do?" (Header: "Rules setup"). After a flow finishes and the file is written, show the menu again from a fresh scan, until the user picks "Done".

### Add

1. Ask which sections to add, with one multi-select question per catalog group (`groups` in the catalog, used as the header), listing only sections in `available`. Each option's label is the section title, and its description is the section `summary`.
2. If a picked section has `requires` that are neither installed nor picked, such as Messages to other people, which needs Plain wording, ask whether to add the required section too. Recommend yes.
3. Run [Choose modules and options](#choose-modules-and-options) for the picked sections.
4. Render each section at its current version with markers (`render <id> --modules a,b --set key=value ... --markers`).
5. Place each block as described in [Building the new file](#building-the-new-file), then [Preview and write](#preview-and-write).

### Upgrade

1. If more than one block can upgrade, ask "Upgrade all <N> sections (recommended)" / "Pick sections". With "Pick sections", ask a multi-select question of those blocks.
2. For each block, show its version notes from `changes`, one line per version, such as `reply-format 1.0.0 → 1.1.0: Adds a rule for long-running PR watches.`
3. If `new_modules` is not empty, ask whether to turn each one on. Recommend the catalog default. If the new version adds an option the marker doesn't have, ask for it as in [Choose modules and options](#choose-modules-and-options).
4. For a block in state `upgrade`, render the current version with the stored modules and options plus the new choices, and replace the whole block, markers included.
5. For a block in state `edited-upgrade`, go to [Edited sections](#edited-sections).
6. Then [Preview and write](#preview-and-write).

### Change modules or options

1. Ask which installed sections to change (multi-select, grouped as in Add).
2. Ask the questions from [Choose modules and options](#choose-modules-and-options) again, with the stored values as the recommended answers.
3. If nothing changed for a section, skip it.
4. A change always renders the section at the library's current version. If the block is on an older version, tell the user that the change also upgrades it, and show the version notes.
5. If the block's state is `current` or `upgrade`, replace it with the new rendering. If it is `edited`, `edited-upgrade` or `kept`, go to [Edited sections](#edited-sections), with the new choices as "theirs".
6. Then [Preview and write](#preview-and-write).

### Remove

1. Ask which installed sections to remove (multi-select, grouped as in Add). Include `unknown` blocks.
2. If a remaining section `requires` one being removed, warn the user and ask whether to remove both or keep the required one.
3. Delete each block from its begin marker through its end marker. Collapse the blank lines around the gap to one.
4. Then [Preview and write](#preview-and-write).

### Adopt

For each entry in `unmanaged`:

1. Take the text from `line` through `end_line` in the scan. That runs from the heading up to the next `#` or `##` heading, the next marker or the end of the file, and it ignores headings inside fenced code blocks, such as the sample replies in Reply format. In manual mode, find the same range yourself, and skip lines inside ``` or ~~~ fences.
2. Work out which modules the text has, from the subsection headings and content each module adds in the current template, and which option values it uses, such as the time zone it names.
3. Render the current version with those choices, and show `git diff --no-index` between the rendering and the user's text.
4. Ask:
   - Question: "How should I adopt <section title>?"
   - Options:
     - "Keep my text (recommended)": wrap the user's text, exactly as it is, in markers for the current version with the modules and options you found. It will show as `edited`, and later upgrades merge new versions into it.
     - "Use the library text": replace it with the rendering, in markers.
     - "Skip": leave it as it is.

For `legacy` markers from `/workflow-rules`:

1. Retired rules: ask a multi-select question "These rules were retired from /workflow-rules. Remove them?", with each rule's replacement as its description. Recommend removing all of them. If the user keeps one, leave its block and markers untouched.
2. Library rules (not retired): their IDs are the modules of the `pr-hygiene` section. Build one `pr-hygiene` block at the position of the first legacy rule. Use the `## PR and Commit Hygiene` heading, then each rule block's text in its current order, with its `<!-- workflow-rules:id=... -->` and `<!-- /workflow-rules:id=... -->` lines removed. The begin marker gets the current version, and `modules` lists the IDs found. If the text matches the rendering, it shows as `current`. Otherwise it shows as `edited`.
3. Delete the old `## PR and Commit Hygiene` heading. Also delete any other heading the move left with nothing under it, such as `## Scope Discipline` or `## Communication Style` from older versions.

Then [Preview and write](#preview-and-write) once for everything adopted.

### Choose modules and options

For each section, in catalog order:

- **Options shared between sections**, such as `t3`, are asked once and stored in every section that has them.
- **`t3`** (yes/no): recommend yes if this session has tools whose names start with `mcp__t3-code__`, which means it runs in T3 Code. Otherwise recommend no. Ask "Do you use T3 Code?", and say in the description that T3 Code is the app that renders collapsed panels and runs scheduled tasks and thread snoozing.
- **`timezone`** (text): detect the system time zone. On macOS run `readlink /etc/localtime` (the part after `zoneinfo/`). On Linux run `timedatectl show -p Timezone --value`, or read `/etc/timezone`. On Windows run `powershell -NoProfile -Command "(Get-TimeZone).Id"`. Turn it into a short name people say, such as "US Eastern" for `America/New_York` or `Eastern Standard Time`, "US Pacific", "UK time" or "Central European". Offer that name (recommended) and "UTC".
- **Other options**: offer the catalog default (recommended), and let the user type a value through "Other". Values can't contain a double quote.
- **Modules**: list only modules whose `requires` options are on. For example, with `t3` set to no, Reply format offers only Examples. Ask a multi-select question per section with each module's title and summary, and mark the defaults "(recommended)". A section with more than 4 modules gets "All <N> (recommended)" / "Pick" first, then the split questions. A section with one module gets a yes/no question.
- Put up to 4 questions in each AskUserQuestion call.

### Edited sections

Use this when a block's text differs from what its stored version and choices render, and a new rendering must replace it.

1. In the scratch folder, write three files:
   - `base.md`: the block's installed version rendered with its stored modules and options.
   - `mine.md`: the block's current text, between the markers.
   - `new.md`: the new rendering, at the new version and with the new choices.
2. Show the user's edits in a few lines (`git diff --no-index base.md mine.md`), and the version notes.
3. Ask:
   - Question: "You edited <section title>. How should I apply the new version?"
   - Options:
     - "Merge it into my text (recommended)": run `git merge-file -p mine.md base.md new.md` and use its output. Exit code 0 means a clean merge. A positive exit code is the number of conflicts.
     - "Use the new version": replace the text with `new.md`. The user's edits are lost, but the backup keeps them.
     - "Keep my text": leave the text as it is. On an upgrade, keep `v=` at the installed version and add `skip="<current version>"` to the begin marker. On a change, ask again, because keeping the text would ignore the new choices.
4. If the merge has conflicts, show each conflict with both sides. For each, ask "Keep mine" / "Use the new text", or let the user type the text. Never write conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) into the target file.
5. The merged block gets a begin marker with the new version and choices. It will show as `edited`, which is correct.

### Building the new file

- Change only the blocks the flow touches, plus the adopted text and legacy markers in Adopt. Keep every other line of the file exactly as it is.
- Place a new block in catalog order among the managed blocks: just before the first managed block whose section comes later in the catalog. If there is none, place it just after the last managed block. If the file has no managed blocks, place it at the end of the file.
- Leave exactly one blank line between a block and the text around it.
- A begin marker looks like this, with modules in catalog order and options in catalog order:

  ```markdown
  <!-- ai-rules:begin id=reply-format v=1.0.0 modules="panels,snooze,examples" t3="yes" timezone="US Eastern" -->
  ## Reply format
  ...
  <!-- ai-rules:end id=reply-format -->
  ```

  `rules.py render --markers` writes this form. The section's `##` heading is inside the markers. Everything outside the markers belongs to the user.

### Preview and write

1. Write the whole proposed file to `<scratch>/proposed.md`.
2. Show `git diff --no-index -- "<target>" "<scratch>/proposed.md"`. If the diff is long, show the summary (`--stat`) and the hunks for sections you rendered, and say that unchanged library text is left out.
3. Ask "Write these changes to `<target>`?" with "Yes, write them" and "Cancel".
4. On yes, back up the current file first: copy it to `<home>/.claude/backups/ai-rules/<name>-<YYYYMMDD-HHMMSS>.md`, where `<name>` is `user-CLAUDE` for the user file and `<project folder>-CLAUDE` for a project file. Create the folder if needed. Skip the backup only when the file didn't exist.
5. Write the proposed content to the target.
6. Scan again. Each block you touched must now show `current`, or `edited` when the user kept or merged edits, or `kept`. If not, say what is wrong, and tell the user where the backup is.
7. Report in one or two sentences: the target, what was added, upgraded, changed, adopted or removed, and the backup path. Then mention that the sections load in every new Claude Code session that reads this file, and that `/rules-setup` shows new versions after `/plugin marketplace update ai-agent-plugins`.

## Rendering

Rendering turns a template into section text. `rules.py render` does this. In manual mode, follow these rules exactly, so that the result matches what the script would produce:

1. Templates use Mustache-style tags. `{{#name}}...{{/name}}` keeps its content when `name` is on. `{{^name}}...{{/name}}` keeps its content when `name` is off. `{{name}}` is replaced by the option's value. Sections can nest.
2. A name is **on** when it is a module in the block's `modules` list, or an option whose value is `yes`. An option with the value `no` or an empty value is off.
3. A module whose `requires` lists an option that is off is treated as off, even if the user picked it.
4. A line that holds nothing but one section tag (`{{#x}}`, `{{^x}}` or `{{/x}}`) is removed along with its line break.
5. After that, strip trailing spaces from every line, reduce every run of two or more blank lines to one, and remove blank lines at the start and end. The result ends with one line break.

## Status by hand

Without Python, work out each block's state yourself:

1. Find each `<!-- ai-rules:begin ... -->` line and its `<!-- ai-rules:end id=<same id> -->` line. Read `id`, `v`, `modules`, any `skip` and the option attributes.
2. Render the block's installed version with its stored modules and options.
3. Compare the rendering with the text between the markers, ignoring line endings, trailing spaces and blank lines. If git is available, use `git diff --no-index --ignore-all-space --ignore-blank-lines --ignore-cr-at-eol`. Any remaining difference means edited.
4. Compare `v` with the section's `current` in the catalog to decide between `current`, `edited`, `upgrade`, `edited-upgrade`, `kept` (a `skip` at or above `current`) and `newer` (`v` above `current`).
5. Look for library headings (`heading` in the catalog) outside markers, and for `<!-- workflow-rules:id=... -->` markers. Ignore anything inside fenced code blocks, including markers.

## Rules

- Never write the target file without showing the diff and getting a yes.
- Never change text outside the markers, except in Adopt and when removing a block.
- Never edit or remove a block in state `newer`.
- Never invent sections, modules or options that aren't in the catalog. The library is the only source of what can be installed.
- Never auto-create `~/.claude/CLAUDE.md` without asking.

---

The `short-pr-bodies` rule in the `pr-hygiene` section is adapted from `file-pr` in [tstack](https://github.com/t3dotgg/tstack) by Theo Browne (MIT). See [THIRD-PARTY-NOTICES.md](../../THIRD-PARTY-NOTICES.md).
