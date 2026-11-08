# Security policy

## Supported versions

Only the latest marketplace release gets security fixes. Update to it before you report a problem.

## Reporting a vulnerability

Report it privately through the contact form at [charlesjones.dev/contact](https://charlesjones.dev/contact), not in a public issue. I reply within one business day.

Please include:

- What the problem is and how to reproduce it
- The affected plugin and version
- The impact you expect
- A suggested fix, if you have one

Once it's fixed, the release notes credit you unless you'd rather stay anonymous.

## Scope

This policy covers the marketplace catalogs, the plugins in `plugins/`, and the docs and examples in this repository.

## Using these plugins safely

1. **Read before you install.** Skills and subagents are Markdown files. ai-knowledge also ships a session-start hook, and ai-performance, ai-rules, ai-security, ai-seo and ai-workflow ship scripts. You can read all of them in the plugin folder before you install.
2. **Stay on the latest release.**
3. **Block reads of secrets.** The ai-security plugin's `/security-init` adds Claude Code deny rules for credential and secret files. See the [ai-security README](plugins/ai-security/README.md) for its other skills.
4. **Check what you commit.** The git skills skip common secret files, but review the staged files before you push.
5. **Review what an unattended run changed.** Some skills read web pages, PRs, CI logs or work items that other people wrote. They treat that text as data and don't follow instructions in it. Review what an unattended run changed before you merge.

## Contact

For questions that aren't sensitive, [open a GitHub issue](https://github.com/charlesjones-dev/ai-agent-plugins/issues).
