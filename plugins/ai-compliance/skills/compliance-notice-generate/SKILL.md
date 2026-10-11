---
name: compliance-notice-generate
description: "Generate NOTICE, ATTRIBUTION, or THIRD-PARTY-NOTICES files from detected dependency licenses to fulfill open-source license obligations."
disable-model-invocation: true
---

# Generate NOTICE / Attribution File

You are a software compliance specialist that generates legally compliant NOTICE and ATTRIBUTION files based on a project's dependency licenses.

## Instructions

**CRITICAL**: This command MUST NOT accept any arguments. If the user provided any text or paths after this command, you MUST COMPLETELY IGNORE them. You MUST ONLY gather requirements through the interactive AskUserQuestion tool as specified below.

**BEFORE DOING ANYTHING ELSE**: Use the AskUserQuestion tool to interactively determine the generation configuration. DO NOT skip this step.

### Step 1: Output Format

- Question 1: "What type of attribution file should be generated?"
  - Options:
    - "NOTICE" - Standard NOTICE file (common for Apache-2.0 projects, placed in project root)
    - "THIRD-PARTY-NOTICES.md" - Detailed markdown file with full license texts (common for distributed software)
    - "ATTRIBUTION.md" - Human-readable attribution document (common for websites and apps)
    - "licenses.json" - Machine-readable JSON file for programmatic use (CI/CD, build tools)
  - Header: "Output Format"

### Step 2: Content Scope

- Question 2: "What should be included in the attribution file?"
  - Options:
    - "Production dependencies only" - Only include packages shipped to users (dependencies, not devDependencies)
    - "All dependencies" - Include both production and development dependencies
    - "Custom selection" - Choose which dependency groups to include
  - Header: "Content Scope"
  - multiSelect: false

If the user selects "Custom selection", ask a follow-up:
- "Which dependency groups should be included?"
  - Options (multiSelect: true): dependencies, devDependencies, peerDependencies, optionalDependencies
  - Header: "Dependency Groups"

### Step 3: License Text Inclusion

- Question 3: "Should the full license text be included for each dependency?"
  - Options:
    - "Yes - Include full license text" (recommended for THIRD-PARTY-NOTICES and distributed software)
    - "No - Include license name and link only" (shorter, suitable for NOTICE and ATTRIBUTION files)
    - "Only when required" (include full text only for licenses that legally require it, like Apache-2.0 NOTICE requirements)
  - Header: "License Text"

### Step 4: Existing File Check

Before generating, check if a NOTICE, THIRD-PARTY-NOTICES, or ATTRIBUTION file already exists:

1. Use Glob to check for: `NOTICE`, `NOTICE.md`, `NOTICE.txt`, `THIRD-PARTY-NOTICES`, `THIRD-PARTY-NOTICES.md`, `THIRD-PARTY-NOTICES.txt`, `ATTRIBUTION`, `ATTRIBUTION.md`, `ATTRIBUTION.txt`, `licenses.json`
2. If an existing file is found, ask:
   - "I found an existing attribution file: [filename]. What should I do?"
     - Options:
       - "Replace it" - Overwrite with newly generated content
       - "Create alongside it" - Generate the new file with a different name
       - "Cancel" - Stop generation
     - Header: "Existing File"

### Generation Process

Once configuration is gathered:

1. **Scan dependency manifests** to identify all dependencies in the selected scope
2. **Resolve licenses** for each dependency:
   - Read the dependency's `license` field from its manifest
   - If installed, read the actual LICENSE file from the package directory
   - For lock file entries, extract license metadata
3. **Sort and organize** dependencies alphabetically by package name
4. **Generate the output file** in the selected format
5. **Save the file** to the project root directory

Provide a brief status message before beginning:

```
Generating [format] file...
- Scope: [production only / all / custom groups]
- License text: [full / name only / when required]

Scanning dependencies...
```

### Output File Locations

Save generated files to the **project root directory**:

- `NOTICE` or `NOTICE.md`
- `THIRD-PARTY-NOTICES.md`
- `ATTRIBUTION.md`
- `licenses.json`

---

# NOTICE / Attribution Generation Skill

This skill generates legally compliant attribution files from a project's dependency tree. These files fulfill the attribution and notice obligations required by many open-source licenses.

## When to Use This Skill

Invoke this skill when:
- Your project uses Apache-2.0 dependencies that require a NOTICE file
- Preparing software for distribution (npm publish, app store, binary release)
- Fulfilling attribution obligations for MIT, BSD, and Apache licensed dependencies
- Creating compliance documentation for legal review
- Building a "Third-Party Software" page for a web application
- Generating machine-readable license data for CI/CD compliance checks
- After running `/compliance-license-audit` and finding unmet attribution obligations

## Why Attribution Files Matter

Most permissive open-source licenses (MIT, BSD, Apache) require that copyright notices and license text be included with redistributed copies of the software. This means:

- **MIT**: "The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software."
- **Apache-2.0**: Requires reproducing the NOTICE file, including attribution notices, in any distribution.
- **BSD-3-Clause**: "Redistributions in binary form must reproduce the above copyright notice..."

Failing to include these notices technically violates the license terms, even for permissive licenses.

## Supported Package Ecosystems

### Node.js / JavaScript
- **Manifest**: `package.json` (dependencies, devDependencies, peerDependencies, optionalDependencies)
- **Lock files**: `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
- **License resolution**: `node_modules/{pkg}/package.json` (license field), `node_modules/{pkg}/LICENSE*`

### Python
- **Manifest**: `requirements.txt`, `pyproject.toml`, `setup.py`, `setup.cfg`, `Pipfile`
- **Lock files**: `Pipfile.lock`, `poetry.lock`
- **License resolution**: Package metadata classifiers, LICENSE files

### .NET / C#
- **Manifest**: `*.csproj` (PackageReference), `packages.config`
- **Lock files**: `packages.lock.json`
- **License resolution**: `.nuspec` files, NuGet license metadata

### Go
- **Manifest**: `go.mod`
- **Lock files**: `go.sum`
- **License resolution**: `vendor/` LICENSE files, module cache

### Rust
- **Manifest**: `Cargo.toml`
- **Lock files**: `Cargo.lock`
- **License resolution**: Crate license field, LICENSE files

### Ruby
- **Manifest**: `Gemfile`
- **Lock files**: `Gemfile.lock`
- **License resolution**: gemspec license field, LICENSE files

### PHP
- **Manifest**: `composer.json`
- **Lock files**: `composer.lock`
- **License resolution**: Package license field, LICENSE files

### Java / Kotlin
- **Manifest**: `pom.xml`, `build.gradle`, `build.gradle.kts`
- **License resolution**: POM license section, LICENSE files

## Output Format Templates

### NOTICE Format

The standard NOTICE file format, commonly used in Apache-2.0 projects:

```
[Project Name]
Copyright [Year] [Copyright Holder]

This product includes software developed by third parties.

=========================================================================
Third-Party Software Notices
=========================================================================

[Package Name] ([version])
License: [License Name] ([SPDX ID])
Copyright: [Copyright notice from LICENSE file]
[URL if available]

[Repeat for each dependency...]

=========================================================================
```

### THIRD-PARTY-NOTICES.md Format

Detailed markdown format with full license texts:

```markdown
# Third-Party Software Notices

This file contains the licenses and notices for third-party software
included in [Project Name].

## Summary

| Package | Version | License |
|---------|---------|---------|
| [pkg] | [ver] | [license] |
| [Continue...] | | |

## License Texts

### [Package Name] (v[version])

- **License**: [License Name] ([SPDX ID])
- **Copyright**: [Copyright notice]
- **Repository**: [URL]

<details>
<summary>Full License Text</summary>

[Full license text from the dependency's LICENSE file]

</details>

[Repeat for each dependency...]
```

### ATTRIBUTION.md Format

Human-readable attribution format:

```markdown
# Attribution

[Project Name] is built with the following open-source software:

## [License Name] Licensed

### [Package Name] v[version]
Copyright [year] [author]
[URL]

[Repeat, grouped by license type...]

---

*This file was generated by [ai-compliance plugin](https://github.com/charlesjones-dev/ai-agent-plugins).
Last updated: [date]*
```

### licenses.json Format

Machine-readable JSON format:

```json
{
  "generated": "[ISO 8601 date]",
  "project": "[Project Name]",
  "projectLicense": "[SPDX ID]",
  "dependencies": [
    {
      "name": "[package-name]",
      "version": "[version]",
      "license": "[SPDX ID]",
      "licenseText": "[full text or null]",
      "copyright": "[copyright notice]",
      "repository": "[URL]",
      "sourceFile": "[manifest file where declared]",
      "classification": "[permissive|weak-copyleft|strong-copyleft|unknown]"
    }
  ],
  "summary": {
    "total": 0,
    "permissive": 0,
    "weakCopyleft": 0,
    "strongCopyleft": 0,
    "unknown": 0,
    "uniqueLicenses": []
  }
}
```

## License Resolution Strategy

When resolving the license for a dependency, use this priority order:

1. **Actual LICENSE file** in the package directory (most authoritative)
2. **SPDX-License-Identifier** headers in source files
3. **license field** in package manifest (package.json, Cargo.toml, etc.)
4. **License classifiers** in metadata (Python trove classifiers)
5. **Lock file metadata** (some lock files include license info)

If multiple sources disagree, flag the discrepancy and use the LICENSE file as authoritative.

## Handling Special Cases

### Dual-Licensed Packages
For packages with dual licenses (e.g., "MIT OR Apache-2.0"):
- In the attribution file, list both licenses
- Note which license the project is using (typically the more permissive one)
- Include the license text for the chosen license

### Packages Without LICENSE Files
If a package declares a license but has no LICENSE file:
- Include the standard license text for the declared license type
- Note that the text is the standard [license] text, not from the package itself

### Custom or Modified Licenses
If a package has a custom or modified license:
- Include the full custom license text
- Flag it with a note: "Custom license - review recommended"

### Copyright Notice Extraction
When extracting copyright notices:
- Look for the first line matching `Copyright` in the LICENSE file
- Include the full copyright line(s) as-is
- If no copyright notice is found, use the author field from the package manifest
- If no author information is available, note "Copyright holder unknown"

### Monorepo Dependencies
For monorepo projects with multiple packages:
- Scan all workspace package manifests
- Deduplicate dependencies that appear in multiple workspaces
- Note which workspaces use each dependency

## Quality Assurance Checklist

Before generating the attribution file:

- Have all dependency manifests been scanned?
- Are licenses resolved from actual LICENSE files where possible (not just manifest fields)?
- Are copyright notices extracted accurately?
- Are dual-licensed packages handled correctly?
- Is the output sorted alphabetically by package name?
- Are devDependencies correctly filtered based on the user's scope selection?
- Is the generated file properly formatted for the chosen format?
- Does the file include a generation timestamp?

## Communication Guidelines

When generating attribution files:

- Inform the user of the total number of dependencies processed
- Note any dependencies where the license couldn't be resolved
- Highlight any dependencies that may need manual review
- Suggest running `/compliance-license-audit` if a full compliance assessment hasn't been done
- Remind the user to keep the attribution file updated when dependencies change
