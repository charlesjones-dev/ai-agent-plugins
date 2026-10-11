# Workflow Rules Library

This file is the source of truth for `/workflow-rules`. Each rule is parsed by ID and rendered into the target CLAUDE.md wrapped in HTML comment markers (`<!-- workflow-rules:id=... -->`).

Schema:

```markdown
## Section: <Section Name>

### rule: <kebab-case-id>
**Title:** <Short title shown in pickers and as the H3 inside CLAUDE.md>
**Body:**
- <bullet 1>
- <bullet 2>
```

Rules are intentionally short (1-3 sentences each), because every rule is loaded into every conversation.

Retired rules are listed in `SKILL.md`, not here, so they can't be installed.

---

## Section: PR and Commit Hygiene

### rule: pr-scope-current-session
**Title:** PR/commit descriptions cover only current-session changes
**Body:**
- Describe ONLY what changed in the commits authored in the current session. Do not describe prior commits on the branch, even if the PR will include them. If the branch carries unrelated prior commits, mention that in one line ("Branch also carries N prior commits not from this session") and stop. Do not summarize them.

### rule: no-fabricated-test-plans
**Title:** Don't invent test plans
**Body:**
- Do not invent test plans, checklists, or verification steps that were not actually performed. If no testing was done, omit the test plan section entirely, or write a single line like "Not tested locally" with one sentence on what would need verification.

### rule: no-speculative-deploy-steps
**Title:** Don't add speculative deploy/rollout steps
**Body:**
- Do not add speculative deploy, rollout, or post-merge steps unless asked.

### rule: short-pr-bodies
**Title:** Keep PR bodies short
**Body:**
- Keep PR bodies short. A 1-3 bullet summary of the actual diff is usually enough. No filler sections, no headers for the sake of structure.

### rule: scoped-commit-messages
**Title:** Scope commit messages to the diff
**Body:**
- Commit messages: describe what the diff does, not surrounding context, future plans, or unrelated work.
