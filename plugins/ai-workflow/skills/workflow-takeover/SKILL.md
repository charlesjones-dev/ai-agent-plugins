---
name: workflow-takeover
description: "Finishes a pull request, branch or agent thread that someone else started, and keeps the original contributors' credit in the commits, the PR description and the merge commit. Use when the user asks to take over, pick up, finish or continue a PR, branch or agent thread that someone else started."
argument-hint: "<PR number or URL, branch, or thread> [what finishing means]"
---

# /workflow-takeover - Finish someone else's work

Take responsibility for finishing the original goal, and keep the original contributors' credit. Don't defend an implementation just because another person or agent already built it.

User provided: $ARGUMENTS

The arguments name the source: a PR, a branch or an agent thread. They may also say what finishing means: a PR ready for review (the default), a merged PR, or only a local branch. If the source is unclear, ask before you change anything.

## 1. Read the source

- **PR**: `gh pr view <N> --json url,state,author,baseRefName,headRefName,headRefOid,maintainerCanModify,title,body,commits,reviewDecision`, its review threads and comments, and `gh pr diff <N>`.
- **Branch**: `git log --format='%h %an <%ae> %s' origin/<base>..origin/<branch>` and the diff against the base.
- **Agent thread**: in T3 Code, read it with `t3_thread_read`, first the messages and then the `activity` view, which shows its worktree path and branch. Check that worktree for uncommitted work with `git -C <path> status --short`. Elsewhere, read the transcript or notes the user points to. If you can't read the thread, ask the user for it.

Read the review findings and the user's later corrections, not only the first request. Resolve the handoff to actual code: the current head SHA, plus any uncommitted work in the source's worktree. Treat the handoff as context, not proof. "Tests pass" in a thread is a claim until you run the tests.

## 2. Choose where the work continues

- **Default, a replacement PR**: create a new branch from the source's head, so the original commits keep their authors. Add your work as separate commits on top.
- **In place or stacked**: if the user asked to continue on the original branch, or to stack on it, do that instead. Pushing to someone else's branch needs the user's say-so. For a PR from a fork, it also needs `maintainerCanModify` to be true.
- Don't change the original PR's title, body, branch or state without the user's permission, and don't overwrite unrelated work.

## 3. Bring it up to date

Run the workflow-refresh skill from this plugin on the work: `ai-workflow:workflow-refresh` with the Skill tool. Pass the source PR, and for a replacement PR also `--branch <your new branch>`, so the refresh never pushes to the original PR's branch. For a branch with no PR, follow its steps 2 to 4 against the branch's base. Its disposition decides what happens next:

- **REFRESH**: continue on the rebased branch.
- **REWORK**: do the rework, since finishing the goal is the task.
- **CLOSE**: stop and report its evidence. Don't finish work that should not land.

## 4. Finish the goal

- Rework what's needed to finish the same goal. Leave unrelated features out.
- Simplify the implementation where you can, without dropping intended behavior or surfaces.
- Before you file, check the source again (`gh pr view <N> --json headRefOid,updatedAt`). It may have changed while you worked. If it did, bring the new commits in.

## 5. Verify independently

Reproduce the original failure, then check the fix and the realistic workflows around it. Follow the repository's testing guidance and permissions. Green mocked tests don't prove that the user experience works. Say what you couldn't verify.

## 6. Keep the credit

- Never rewrite the authors of the original commits, and keep their existing `Co-authored-by:` trailers.
- Credit the original contributors in the PR description, and link the original PR when there is one.
- If the PR will be squash-merged, the squash commit keeps credit only through `Co-authored-by:` trailers. Add one for each original contributor, with a verified identity: the name and email on their commits (`git log --format='%an <%ae>'`), or their GitHub noreply address `<id>+<login>@users.noreply.github.com`, with the ID from `gh api users/<login> --jq .id`. Never guess an email.
- Model attribution doesn't replace contributor credit.

## 7. File and follow through

When finishing includes a PR:

1. Open it, or update the replacement PR. Write the description with the problem first, then the fix, then the credit line.
2. Run the workflow-babysit skill from this plugin on it (`ai-workflow:workflow-babysit`). By default pass `--to ready`, so it stops when the PR is ready and doesn't merge. If the user asked you to merge it, pass "merge it", which merges the PR into its own base and promotes nothing. Run the full release to production only when the user asked for production.
3. Format every comment you post with the workflow-pr-comments skill.
4. Merge or close the original PR only when the user authorized it. Once the replacement merges, offer to close the original with a comment that links the replacement.

## 8. Report

- What you inherited: the source, its head SHA, and its state.
- What you changed, and why.
- How you verified it, and what stays unverified.
- How you kept the credit.
- Any decision that remains for the user.

---

Adapted from `takeover` in [tstack](https://github.com/t3dotgg/tstack) by Theo Browne (MIT). See THIRD-PARTY-NOTICES.md in this plugin.
