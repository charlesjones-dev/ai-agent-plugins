# AI Compliance Plugin

Software compliance auditing for open-source license detection, risk assessment, and attribution file generation.

## Overview

Open-source license compliance is a legal obligation. Using a GPL-licensed dependency in a proprietary project could require disclosing your source code. A dependency with no license at all is legally "all rights reserved" and can't be used without explicit permission. This plugin scans your dependency tree, identifies licenses, flags incompatibilities with your project's license, and generates a file carrying the copyright and license notices that licenses like MIT, BSD, and Apache 2.0 require you to keep.

## Quick Start

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

### `/compliance-license-audit` - License Compliance Audit

Interactive audit of the open-source licenses in your dependency tree.

**Features:**
- Auto-detects your project's license with confirmation
- Scans dependency manifests (package.json, requirements.txt, .csproj, go.mod, Cargo.toml, etc.)
- Identifies direct and transitive dependency licenses
- Scans source code for license headers and vendored/copied code
- Classifies licenses: Permissive, Weak Copyleft, Strong Copyleft, Unknown / No License
- Flags incompatibilities with your project's license
- Identifies dependencies with no license (highest legal risk)
- Produces a License Compliance Score (0-100)
- Lists unfulfilled license obligations (missing NOTICE files, attribution, etc.)
- Provides specific alternatives for problematic dependencies

**Usage:**
```
/compliance-license-audit
```

The skill asks about:
1. Your project's license (auto-detected with confirmation)
2. Audit scope (full, dependencies only, or source code only)
3. Risk tolerance (strict, moderate, permissive only, or informational)
4. Whether to include transitive dependencies

**Report output:** `/docs/compliance/YYYY-MM-DD-HHMMSS-license-audit.md`

### `/compliance-notice-generate` - Generate NOTICE / Attribution File

Generates NOTICE, ATTRIBUTION, or THIRD-PARTY-NOTICES files from your dependency tree.

**Features:**
- Four output formats: NOTICE, THIRD-PARTY-NOTICES.md, ATTRIBUTION.md, licenses.json
- Configurable scope (production only, all, or custom dependency groups)
- Optional full license text inclusion
- Extracts copyright notices from LICENSE files
- Handles dual-licensed packages
- Supports the package ecosystems listed below
- Detects and handles existing attribution files

**Usage:**
```
/compliance-notice-generate
```

The skill asks about:
1. Output format (NOTICE, THIRD-PARTY-NOTICES.md, ATTRIBUTION.md, or licenses.json)
2. Content scope (production only, all, or custom)
3. Whether to include full license texts
4. How to handle existing attribution files (if any)

**Output:** Saved to the project root.

## License Classifications

| Classification | Examples | Risk Level |
|---------------|----------|------------|
| Permissive | MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, Unlicense | Low |
| Weak Copyleft | LGPL-2.1, LGPL-3.0, MPL-2.0, EPL-2.0 | Moderate |
| Strong Copyleft | GPL-2.0, GPL-3.0, AGPL-3.0, SSPL-1.0 | High-Critical |
| Unknown / No License | Unidentified license, or all rights reserved by default | Critical |

## Supported Package Ecosystems

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

## Why This Matters

- **MIT License** requires: "The above copyright notice and this permission notice shall be included in all copies"
- **Apache 2.0** requires: Reproducing the NOTICE file in any distribution, if the project ships one
- **BSD 3-Clause** requires: "Redistributions in binary form must reproduce the above copyright notice"
- **AGPL in a SaaS application** can require releasing your source, since network use triggers its copyleft

## Recommended Workflow

1. Run `/compliance-license-audit` to see which licenses your dependencies use
2. Address any critical findings (incompatible licenses, missing licenses)
3. Run `/compliance-notice-generate` to create attribution files fulfilling your obligations
4. Add attribution file maintenance to your release checklist

## Plugin Details

| Field | Value |
|-------|-------|
| Version | 1.1.0 |
| Author | [Charles Jones](https://charlesjones.dev) |
| License | MIT |
| Repository | [ai-agent-plugins](https://github.com/charlesjones-dev/ai-agent-plugins) |

## Contributing

Bug reports and fixes are welcome. See [CONTRIBUTING.md](../../CONTRIBUTING.md).
