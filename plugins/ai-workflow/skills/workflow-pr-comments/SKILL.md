---
name: workflow-pr-comments
description: "Formats every GitHub comment the agent posts on the user's behalf: a note callout that names the model and the user, then a short, direct reply. Use whenever you post a comment on a pull request or issue for the user, including inline review comments, replies to people and review bots, and the reason for resolving or dismissing a finding."
---

# Leaving PR comments

A reader should see at once that an agent wrote the comment, and for whom. Use this format for every comment you post on GitHub on the user's behalf.

## Format

Start the comment with this GitHub note callout, then a blank line, then the reply:

```md
> [!NOTE]
> 🤖 **<model> responding on behalf of <user>**

<the reply>
```

- `<model>` is the public name of the model that wrote the comment, as the harness reports it, such as "Claude Opus 5.5". If the harness doesn't report the model, use the harness name, such as "Claude Code". Never guess a model name.
- `<user>` is the user's GitHub login, from `gh api user --jq .login`.
- Keep the attribution inside the callout and the reply below it. Don't add a horizontal rule, a heading, a signature or a second attribution.

## Where it applies

Use it for top-level PR and issue comments, inline review comments, replies to people and review bots, and the written reason before you resolve or dismiss a finding.

Don't use it for:

- PR descriptions and commit messages.
- Text the user asked you to post word for word without attribution.
- Commands to review bots, such as `@codex review ...` or `bugbot run`. A bot reads these only as a bare command, so post each one by itself with no callout.

## Writing the reply

- Lead with the conclusion: fixed, by design, won't fix, or a question.
- Cite what backs it up: the commit SHA, the file and line, a check, a test or a reproduction.
- Keep it short. Leave out thanks, filler and status narration.
- Say which parts you verified and which are your judgment.

## Posting

1. Check the whole comment for secrets, tokens, internal URLs and other private details. This includes quoted text and attachments.
2. Write the body to a file and post it from there, so the shell doesn't change quotes or blank lines: `gh pr comment <N> --body-file <file>`, or `-F body=@<file>` with `gh api`.
3. Check that GitHub returned the URL of the comment or review.
4. Resolve a review thread only after the reply to it posted.

---

Adapted from `leaving-pr-comments` in [tstack](https://github.com/t3dotgg/tstack) by Theo Browne (MIT). See THIRD-PARTY-NOTICES.md in this plugin.
