# Third-party notices

This plugin is adapted from [improve](https://github.com/shadcn/improve), shadcn's agent skill that audits a codebase and writes implementation plans for other agents to carry out. It is used under the MIT License below. The adapted versions differ from the original: its one skill is split into four commands, its text is rewritten, and some behavior is added or changed. The table lists what came from where.

Source: https://github.com/shadcn/improve at commit `cac56e1ebd3c279aa9153616cfeac7b174ab90f9`.

| File in this plugin | Adapted from (improve `skills/improve/`) |
|---------------------|------------------------------------------|
| `skills/improve-audit/SKILL.md` | `SKILL.md` (the recon, audit, vet and plan phases, and the `quick`, `deep`, focus, `branch` and `next` variants) |
| `skills/improve-audit/references/audit-playbook.md` | `references/audit-playbook.md` |
| `skills/improve-plan/SKILL.md` | `SKILL.md` (the `plan` and `review-plan` variants) |
| `skills/improve-execute/SKILL.md` | `SKILL.md` (the `execute` variant) and `references/closing-the-loop.md` |
| `skills/improve-reconcile/SKILL.md` | `SKILL.md` (the `reconcile` variant) and `references/closing-the-loop.md` |
| `skills/*/references/plan-template.md` | `references/plan-template.md` |
| `skills/*/references/publish-issues.md` | `references/closing-the-loop.md` (the `--issues` flow) |

## improve license

```text
MIT License

Copyright (c) 2026 shadcn

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
