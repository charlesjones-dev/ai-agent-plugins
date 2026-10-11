# Contributing

Bug reports and fixes are welcome. Pull requests are for fixes only; new plugins, skills and features start as an issue.

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).

## Reporting a Bug

[Open an issue](https://github.com/charlesjones-dev/ai-agent-plugins/issues) with:

- The plugin and its version
- The agent you used (Claude Code, Codex or Cursor), the command you ran and what you expected
- What happened instead, including any error text

Security problems go through [SECURITY.md](SECURITY.md), not a public issue.

## Sending a Fix

1. Fork the repository and create a branch.

2. Make the fix. Each plugin is self-contained:

   ```
   plugins/{plugin-name}/
     .claude-plugin/plugin.json             # Claude Code manifest: name, version, description, author, keywords
     plugin.json                            # Agent Plugins manifest, only in plugins that run in Codex and Cursor
     skills/{skill-name}/SKILL.md           # one folder per command
     skills/{skill-name}/agents/openai.yaml # command-only skills: stops Codex running them unprompted
     agents/{agent-name}.md                 # optional Claude Code subagents; use `model: inherit`
     README.md
     LICENSE
   ```

   The root `.claude-plugin/marketplace.json` lists every plugin. Its entry and the plugin's own `.claude-plugin/plugin.json` must keep the same name, version, description, author and keywords. Plugins that run in Codex and Cursor also have a root `plugin.json` with the same fields, and are listed in `.agents/plugins/marketplace.json` (Codex) and `.cursor-plugin/marketplace.json` (Cursor).

   A skill with `disable-model-invocation: true` needs an `agents/openai.yaml` next to its `SKILL.md`. Codex ignores the Claude Code field and reads this file instead:

   ```yaml
   policy:
     allow_implicit_invocation: false
   ```

3. Test it. Validate the manifests:

   ```
   claude plugin validate plugins/{plugin-name}
   claude plugin validate .
   python3 scripts/check-manifests.py
   ```

   The last command checks that the catalogs, both manifest formats and the Codex policy files agree.

   Then, from a project to try it on, start Claude Code with the plugin loaded from your clone and run the skill you changed as `/{plugin-name}:{skill-name}`:

   ```
   claude --plugin-dir /path/to/your/clone/plugins/{plugin-name}
   ```

   The plugin loads for that session only, and nothing is installed or written to your settings. If you already installed the plugin from this marketplace, your clone's copy replaces it for the session. After more edits, run `/reload-plugins`.

4. Leave version numbers and `CHANGELOG.md` alone. They're updated at release.

5. Commit with a conventional prefix such as `fix:` or `docs:`, and leave Claude Code attribution out of the message.

6. Open a pull request that says what was broken, how you fixed it and how you tested it. Link the issue if there is one.

If you edit a README, keep it plain: no emoji in headings, no "AI-powered", and no figures you haven't measured. For the plugin formats, see the [Claude Code plugin docs](https://code.claude.com/docs/en/plugins) and the [Agent Plugins specification](https://agent-plugins.org/).

## License

By contributing, you agree that your contributions are licensed under the [MIT License](LICENSE).
