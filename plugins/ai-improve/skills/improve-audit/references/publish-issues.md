# Publish plans as GitHub issues

`--issues` is the user's permission to create issues. Never create one without it. The plan file stays the source of truth, and the issue is a copy that another agent or a person can pick up where the team already tracks work.

1. **Check that you can publish.** `gh auth status` must succeed, and the repository must have a GitHub remote. If either fails, write the plan files as normal and say why you skipped the issues.
2. **Check who can read the issues.** Run `gh repo view --json visibility`. If the repository is public, anyone can read its issues. Tell the user so, and get a clear yes before you publish a plan that describes a security weakness, a credential location or another sensitive finding. Without a yes, leave that plan unpublished and say so. In an unattended run nobody can answer, so never publish such a plan to a public repository.
3. **Show the titles** that are about to become issues. Ask once whether to go on, unless the run is unattended.
4. **Create one issue per plan**: `gh issue create --title "<plan title>" --body-file <plan file>`. Add the labels `improve` and the plan's category only when they already exist (`gh label list`). A missing label makes the command fail, so leave it off.
5. **Record each issue URL** in the plan's Status block (`- **Issue**: <url>`) and in the index.

A plan stands alone, so its issue body needs no edits. Don't comment on, close or edit any other issue.
