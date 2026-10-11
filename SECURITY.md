# Security Policy

## Supported Versions

Only the latest marketplace release gets security fixes. Update to it before you report a problem.

## Reporting a Vulnerability

Report it privately through the contact form at [charlesjones.dev/contact](https://charlesjones.dev/contact), not in a public issue. I reply within one business day.

Please include:

- What the problem is and how to reproduce it
- The affected plugin and version
- The impact you expect
- A suggested fix, if you have one

Once it's fixed, the release notes credit you unless you'd rather stay anonymous.

## Scope

This policy covers the marketplace catalogs, the plugins in `plugins/`, and the docs and examples in this repository.

## Using These Plugins Safely

1. **Read before you install.** Skills and subagents are plain Markdown files, so you can see exactly what a plugin tells Claude Code, Codex or Cursor to do.
2. **Stay on the latest release.** Fixes only go into the newest version.
3. **Block reads of secrets.** The ai-security plugin's `/security-init` adds Claude Code deny rules for credential and secret files. See the [ai-security README](plugins/ai-security/README.md) for its other skills.
4. **Check what you commit.** The git skills skip common secret files, but review the staged files before you push.

## Contact

For questions that aren't sensitive, [open a GitHub issue](https://github.com/charlesjones-dev/ai-agent-plugins/issues).
