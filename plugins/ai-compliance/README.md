# AI-Compliance plugin

Audits the licenses of your open-source dependencies, flags copyleft and missing-license risks, and generates NOTICE or ATTRIBUTION files.

Open-source licenses carry legal obligations. A GPL-licensed dependency in a proprietary project can require you to disclose your source code. AGPL can do the same for a SaaS application, because network use triggers its copyleft. A dependency with no license is legally "all rights reserved", and you can't use it without explicit permission. This plugin scans your dependency tree, identifies licenses and flags conflicts with your project's license. It also generates a file with the copyright and license notices that licenses such as MIT, BSD and Apache 2.0 require you to keep.

## Installation

Claude Code:

```
/plugin marketplace add charlesjones-dev/ai-agent-plugins
/plugin install ai-compliance@ai-agent-plugins
```

Codex:

```
codex plugin marketplace add charlesjones-dev/ai-agent-plugins
codex plugin add ai-compliance@ai-agent-plugins
```

Cursor: add this repository as a team marketplace, or copy this folder to `~/.cursor/plugins/local/ai-compliance`. See the [Cursor install steps](../../README.md#cursor).

## Skills

### `/compliance-license-audit`

Audits the open-source licenses in your dependency tree, and asks a few questions first.

#### What it checks
- Detects your project's license and asks you to confirm it
- Scans dependency manifests (package.json, requirements.txt, .csproj, go.mod, Cargo.toml, etc.)
- Identifies the licenses of direct and transitive dependencies
- Scans source code for license headers and vendored or copied code
- Classifies licenses as Permissive, Weak Copyleft, Strong Copyleft, Non-Open-Source / Restrictive, or Unknown / No License
- Flags conflicts with your project's license
- Identifies dependencies with no license (highest legal risk)
- Gives a License Compliance Score (0-100)
- Lists unmet license obligations (missing NOTICE files, attribution, etc.)
- Suggests alternatives for problem dependencies

#### Usage
```
/compliance-license-audit
```

The skill asks about:
1. Your project's license (auto-detected with confirmation)
2. Audit scope (full, dependencies only, or source code only)
3. Risk tolerance (strict, moderate, permissive only, or informational)
4. Whether to include transitive dependencies

It saves the report to `docs/compliance/YYYY-MM-DD-HHMMSS-license-audit.md`.

### `/compliance-notice-generate`

Generates NOTICE, ATTRIBUTION, or THIRD-PARTY-NOTICES files from your dependency tree.

#### What it does
- Writes one of four formats: NOTICE, THIRD-PARTY-NOTICES.md, ATTRIBUTION.md, licenses.json
- Covers production dependencies only, all of them, or custom dependency groups
- Includes the full license text always, never, or only when the license requires it
- Extracts copyright notices from LICENSE files
- Handles dual-licensed packages
- Reads the package ecosystems listed below
- Finds existing attribution files and asks how to handle them

#### Usage
```
/compliance-notice-generate
```

The skill asks about:
1. Output format (NOTICE, THIRD-PARTY-NOTICES.md, ATTRIBUTION.md, or licenses.json)
2. Content scope (production only, all, or custom)
3. Whether to include full license texts (yes, no, or only when required)
4. How to handle existing attribution files (if any)

It saves the file to the project root.

## License classifications

| Classification | Examples | Risk Level |
|---------------|----------|------------|
| Permissive | MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, Unlicense | Low |
| Weak Copyleft | LGPL-2.1, LGPL-3.0, MPL-2.0, EPL-2.0 | Moderate |
| Strong Copyleft | GPL-2.0, GPL-3.0, AGPL-3.0, SSPL-1.0 | High-Critical |
| Non-Open-Source / Restrictive | BUSL-1.1, Elastic-2.0, Commons Clause | Critical |
| Unknown / No License | Unidentified license, or all rights reserved by default | Critical |

## Supported package ecosystems

| Ecosystem | Manifest | Lock File |
|-----------|----------|-----------|
| Node.js | package.json | package-lock.json, yarn.lock, pnpm-lock.yaml |
| Python | requirements.txt, pyproject.toml, Pipfile | Pipfile.lock, poetry.lock |
| .NET | *.csproj, packages.config | packages.lock.json |
| Go | go.mod | go.sum |
| Rust | Cargo.toml | Cargo.lock |
| Ruby | Gemfile | Gemfile.lock |
| PHP | composer.json | composer.lock |
| Java/Kotlin | pom.xml, build.gradle | - |

## What the common licenses require

- MIT: "The above copyright notice and this permission notice shall be included in all copies"
- Apache 2.0: reproduce the NOTICE file in any distribution, if the project ships one
- BSD 3-Clause: "Redistributions in binary form must reproduce the above copyright notice"

## Recommended workflow

1. Run `/compliance-license-audit` to see which licenses your dependencies use
2. Fix the critical findings (conflicting or missing licenses)
3. Run `/compliance-notice-generate` to create the attribution files your licenses require
4. Add the attribution file to your release checklist

## Plugin details

| Field | Value |
|-------|-------|
| Version | 1.1.1 |
| Author | [Charles Jones](https://charlesjones.dev) |
| License | MIT |
| Repository | [ai-agent-plugins](https://github.com/charlesjones-dev/ai-agent-plugins) |

## Contributing

Bug reports and fixes are welcome. See [CONTRIBUTING.md](../../CONTRIBUTING.md).
