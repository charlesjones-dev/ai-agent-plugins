---
name: kb-learn
description: "Saves team knowledge (corrections, rules, decisions, codebase gotchas) to the project's knowledge base in .claude/rules/kb/. Invoke it yourself in only two cases: (1) your context holds the instruction 'ai-knowledge auto-capture is on for this project' and such a learning just came up; pass `auto` and the learning. (2) The user explicitly asks you to save or add something to the knowledge base, KB or team rules; pass `auto` and that thing. A user stating a rule, convention or correction is not a request to save it: without the auto-capture instruction, don't invoke this skill for it. Typed as /kb-learn, it reviews the whole conversation and asks before saving."
argument-hint: "[auto <learning> | focus]"
---

# Save learnings to the knowledge base

Read [kb-format.md](kb-format.md) first. It defines the layout, frontmatter, load modes, writing rules and the auto-capture setting used below.

Arguments (may be empty): $ARGUMENTS

| Arguments | Path |
|---|---|
| First word is `auto` | **Quick save**: save one learning without questions, then report it in one line |
| Anything else, or nothing | **Review**: go through the conversation (or the focus the arguments name) and ask before saving |

Use quick save in two situations only:

- **Auto-capture**: your context holds the instruction that begins "ai-knowledge auto-capture is on for this project" (the plugin's session-start hook adds it), and a learning a teammate would need just came up.
- **The user asked**: the user explicitly asked to save a specific thing to the knowledge base ("save that to the KB", "add this to the team rules"). The request is the approval, so don't ask again.

A user who states a rule, convention or correction ("a rule for this team: ...") hasn't asked you to save it. Without the auto-capture instruction, that's not a reason to save. If you invoked this skill yourself and neither situation applies, stop: write nothing and don't mention the knowledge base.

When the user asks to go through everything the conversation taught, use the review path instead.

Claude Code's auto memory saves personal notes on one machine. This skill is for knowledge the team should share: rules a teammate's session would also need.

## Quick save

### 1. Check the knowledge base

Run the checks from kb-format.md without printing their details. If there's a 1.x knowledge base, write nothing and reply with one line: `📖 Not saved to KB: this project has a 1.x knowledge base. Run /kb-migrate first.` If there's no knowledge base, reply `📖 Not saved to KB: there's no knowledge base here. Run /kb-init first.`

### 2. Take one learning

Use the text after `auto`. If there's none, take the most recent correction, rule, decision or gotcha in the conversation. Save exactly one learning per call.

Under auto-capture, skip it without writing or printing anything if it's:

- a personal preference rather than a team rule (it belongs in auto memory or `CLAUDE.local.md`);
- a detail that only matters for the current task;
- something the code already makes obvious;
- too vague to change what a future session does.

When the user asked, save it even if it looks personal. In both cases, never store a secret value: keep the rule and drop the value.

### 3. Look for what's already there

Search `.claude/rules/kb/` and `.claude/kb/` for the learning's key terms (Grep), and read the articles that match and `_global-learnings.md`.

- If an article already says it, write nothing. Under auto-capture, print nothing. When the user asked, reply `📖 Already in KB: {path}.`
- If it contradicts a rule in an article, the new learning replaces that rule.

### 4. Pick the destination

1. An existing article on the same topic. It keeps its load mode.
2. Otherwise a new article in a category folder:
   - **scoped**, with `paths`, when the learning is tied to specific folders or file types. Check the globs with Glob before writing;
   - **on-demand** in `.claude/kb/` when it's about a topic or task rather than files;
   - **`_global-learnings.md`** only for a short rule that applies to nearly every task in the project, and only while that file stays under about 40 lines. It loads every session.

Never create any other pinned article in a quick save.

### 5. Write

Get today's date once (kb-format.md, Dates).

- Add the learning as one imperative bullet under `## Key rules`, with a short reason if it isn't obvious. When replacing a rule, edit that bullet instead.
- A new article gets the frontmatter and body from kb-format.md: a title, a one-sentence description and `## Key rules`, with no Context or Related section. If `_global-learnings.md` doesn't exist yet, create it with `tags: [global, cross-cutting]`, `created`, `last-updated`, the heading `# Global learnings` and `## Key rules`.
- Update `last-updated`, and add a tag if the learning brings a new topic.
- Add a line to `_index.md` for a new scoped or on-demand article, from kb-format.md (The index rule). If a tag was added to an existing article that has a line, update its keywords.
- Append to the log:

  ```markdown
  ## [{date}] learn | {Auto-saved | Saved on request}: {the rule, shortened}
  - {Created | Updated}: {path}
  ```

### 6. Report in one line

End your reply with exactly one line, using the path relative to `.claude/rules/kb/` or `.claude/kb/`:

- `📖 Saved to KB: conventions/api-errors.md (scoped to src/api/**). Say "undo" to remove it.`
- `📖 Saved to KB: tools/release.md (on demand). Say "undo" to remove it.`
- `📖 Saved to KB: _global-learnings.md (loads every session). Say "undo" to remove it.`
- `📖 Updated KB: conventions/api-errors.md (replaced the old rule on status codes). Say "undo" to restore it.`

Under auto-capture, then carry on with the user's task.

## Undo

When the user says "undo", or asks to remove what was just saved, reverse the most recent quick save exactly, unless they name a different one:

- a new article: delete the file and remove its `_index.md` line;
- a changed `_index.md` line: restore it;
- a new `_global-learnings.md`: delete the file;
- an updated article: remove the added bullet, or put the replaced rule back, and restore the `last-updated` and `tags` values it had;
- the log: remove the entry the save appended.

Use edits rather than `git checkout`, so other uncommitted changes in those files stay. Change nothing else, and reply in one line: `📖 Removed from KB: {path}.` or `📖 Restored KB: {path}.`

## Review

This is the path for a typed `/kb-learn`. Arguments that aren't `auto` name a focus ("the deploy fix", "testing"): extract only learnings about it. Otherwise review the whole conversation.

### Step 1: Check the knowledge base

Run the checks from kb-format.md: stop if there's a 1.x knowledge base (point to `/kb-migrate`) or no knowledge base (point to `/kb-init`), and pass on any git warning.

### Step 2: Extract learnings

Review the conversation from start to finish (or the focus) and collect:

1. **Mistakes and anti-patterns**: what was tried and failed, what the user corrected, patterns called out as wrong for this project.
2. **Confirmed practices**: approaches that worked, patterns the user confirmed, conventions specific to this codebase.
3. **Institutional knowledge**: external systems, team conventions, client requirements, domain rules that the code doesn't show.
4. **Team workflow**: how this project is built, tested, released or reviewed ("run the integration tests before merging", "this repo uses pnpm").
5. **Codebase rules**: structure, gotchas and non-obvious behavior ("the auth middleware must load before the route handlers").

Leave out:

- personal preferences that aren't team rules (those belong in auto memory or `CLAUDE.local.md`);
- anything a future session could read straight from the code, unless it's a gotcha;
- vague observations that wouldn't change what Claude does.

Never record secrets. Record the rule about them ("Service X's key comes from an environment variable"), and describe sensitive endpoints generically ("the internal staging API").

For each learning, decide:

- **Load mode**: scoped when it only matters for certain folders or file types (give the globs); global learning when it applies across the project and is short; on-demand when it's tied to a task or topic rather than to files.
- **Destination**: an existing article on the topic, or a new one in a category folder.
- **Tags**, and other articles worth listing in its Related section.

### Step 3: Compare with the knowledge base

Read the articles that touch the same topics, and `_global-learnings.md` if it exists. Drop learnings they already state. When a learning contradicts an existing rule, plan to replace the old rule: the conversation is newer.

### Step 4: Propose

```text
Proposed knowledge base updates
===============================

New articles
  1. .claude/rules/kb/testing/integration-tests.md (scoped: tests/integration/**)
     tags: testing, database
     - "Reset the test database with the fixture loader, not migrations"
     - "Integration tests need the local queue running"

Updates
  2. .claude/kb/tools/release.md (on-demand)
     - "Tag releases from main only" (new)
     - "Bump the API version in openapi.yaml" (replaces "Bump it in package.json")

Global learnings (load every session)
  3. "Use the shared logger; never console.log in server code"

Links
  - integration-tests ↔ release
```

Ask with AskUserQuestion:

- Header: "Knowledge Base Update"
- Question: "Here's what I'd save from this conversation. Save it?"
- Options: "Save all" | "Let me pick" | "Cancel"

With "Let me pick", go through the learnings one by one and ask whether to include each, and whether its destination or load mode should change.

### Step 5: Write

Get today's date once (kb-format.md, Dates) and use it for every date below.

1. **New articles**: use the frontmatter and body from kb-format.md, in the folder that matches the load mode (`paths` only for scoped articles).
2. **Existing articles**: add the learnings under the right section without duplicating entries, and replace rules they contradict. Update `last-updated` only if the content changed, and add new tags and links.
3. **Global learnings**: if `.claude/rules/kb/_global-learnings.md` doesn't exist, create it (frontmatter `tags: [global, cross-cutting]`, `created`, `last-updated`; heading `# Global learnings`; rules under `## Key rules`). Add each learning as a bullet, merge near-duplicates, replace contradicted entries, and remove placeholder text. Keep the file short: it loads every session. If it passes about 40 lines, suggest moving area-specific rules into scoped articles with `/kb-prune`.
4. **Related**: where a new article and an existing one bear on the same tasks, list each in the other's `## Related` section as a path (kb-format.md, Related articles). Update `last-updated` on any article whose content changed.
5. **Index**: add a line to `_index.md` for each new scoped or on-demand article, and update the keywords on the line of any article whose `tags` changed.
6. **Log**: append

   ```markdown
   ## [{date}] learn | Conversation learnings saved
   - Created: {paths}
   - Updated: {paths}
   - Global learnings: {n} added
   ```

### Step 6: Report

Show how many articles were created and updated, how many global learnings were added, the links added, and each new article's load mode. Remind the user that the knowledge reaches teammates once it's committed.

### Quality rules

- Write so a future session gets the point in the fewest tokens: a sentence, not a paragraph.
- Every entry should change what Claude does. Drop the rest.
- The newest knowledge wins over older entries.
- Nest folders only where there's a clear hierarchy (such as packages in a monorepo); otherwise keep categories flat.
