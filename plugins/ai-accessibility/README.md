# AI-Accessibility plugin

Audits code, or a live URL, for Section 508/WCAG 2.0, WCAG 2.1 or WCAG 2.2 issues and saves a report with before/after fixes. URL audits can use Playwright MCP for visual checks. The plugin has one skill, `/accessibility-audit`, and it runs in Claude Code, Codex and Cursor.

## Limits

An audit doesn't certify WCAG or legal compliance. It also doesn't replace manual screen reader testing or testing with people with disabilities.

## Available skills

### `/accessibility-audit`

#### Arguments

```
/accessibility-audit [WCAG version] [level] [path or URL]
```

1. **WCAG version**: `2.0` or `508` (508 / WCAG 2.0 AA), `2.1`, or `2.2`. `508` also sets the level to AA.
2. **Conformance level**: `A`, `AA`, or `AAA`
3. **Scope**: a directory path, `.` for the entire solution, or a URL

Examples:

```
/accessibility-audit 2.2 AA src/
/accessibility-audit 2.1 AA https://example.com
/accessibility-audit 2.2 .
```

The skill uses whatever the arguments supply and asks only for what's missing. With all three it asks nothing, so the audit can run unattended. With none, it asks for:

1. The WCAG version: WCAG 2.1, WCAG 2.2, or 508 / WCAG 2.0 AA.
2. The conformance level: A (minimum), AA (recommended) or AAA (enhanced).
3. The scope: the entire codebase, one directory, or a URL.
4. For a URL, whether to use Playwright MCP for visual testing.

When the URL comes from the arguments, the skill uses Playwright if the Playwright MCP server responds. If it doesn't, the audit falls back to HTML and code analysis, and the report says that visual testing was skipped.

#### What it analyzes

The audit covers the areas under [Features](#features). URL audits with Playwright MCP also measure contrast on rendered elements, check that focus states are visible, read the accessibility tree that assistive technologies get, test keyboard navigation on the live page, measure touch targets in pixels, and keep screenshots as evidence.

## Installation

Claude Code:

```
/plugin marketplace add charlesjones-dev/ai-agent-plugins
/plugin install ai-accessibility@ai-agent-plugins
```

Codex:

```
codex plugin marketplace add charlesjones-dev/ai-agent-plugins
codex plugin add ai-accessibility@ai-agent-plugins
```

Cursor: add this repository as a team marketplace, or copy this folder to `~/.cursor/plugins/local/ai-accessibility`. See the [Cursor install steps](../../README.md#cursor).

## Usage

### Codebase analysis

```
# Step 1: Run an accessibility audit
/accessibility-audit
# Or skip the questions: /accessibility-audit 2.2 AA src/

# Step 2: Answer configuration questions (only those the arguments didn't cover)
# - WCAG Version: 2.1, 2.2, or 508 / WCAG 2.0 AA
# - Conformance Level: A, AA, or AAA
# - Scope: Entire solution or specific directory

# Step 3: Review the generated report
# Located at: docs/accessibility/YYYY-MM-DD-HHMMSS-accessibility-audit.md
# Example: docs/accessibility/2025-10-29-143022-accessibility-audit.md

# Step 4: Implement recommended fixes
# Follow the prioritized remediation roadmap (Phase 1-4)
```

### URL analysis with Playwright MCP

```
# Step 1: Run an accessibility audit
/accessibility-audit
# Or skip the questions: /accessibility-audit 2.1 AA https://example.com

# Step 2: Answer configuration questions (only those the arguments didn't cover)
# - WCAG Version: 2.1, 2.2, or 508 / WCAG 2.0 AA
# - Conformance Level: A, AA, or AAA
# - Scope: a URL
# - Provide the URL to scan
# - Visual Scanning: Yes - Use Playwright for visual scans

# Step 3: If you picked the URL interactively and Playwright MCP is not installed, the skill will:
# - Offer to set up the Playwright MCP server for your agent
#   (.mcp.json in Claude Code, .cursor/mcp.json in Cursor, `codex mcp add` in Codex)
# - Ask you to restart the agent or start a new session
# - After restart, run /accessibility-audit again
# With the URL in the arguments, it skips visual testing instead and says so in the report

# Step 4: Review the generated report with visual evidence
# Located at: docs/accessibility/YYYY-MM-DD-HHMMSS-accessibility-audit.md

# Step 5: Implement recommended fixes
# Follow the prioritized remediation roadmap
```

## Features

### WCAG versions and levels

- WCAG 2.1 has 78 success criteria across 13 guidelines: Level A 30, AA 20, AAA 28.
- WCAG 2.2 has 86 success criteria. It adds 9 and removes SC 4.1.1 Parsing: Level A 31, AA 24, AAA 31.
  - The new criteria are Focus Not Obscured (AA/AAA), Focus Appearance (AAA), Dragging Movements (AA), Target Size Minimum (AA), Consistent Help (A), Redundant Entry (A) and Accessible Authentication (AA/AAA).

The conformance levels are cumulative. In WCAG 2.2:

- Level A has 31 criteria and covers the critical barriers.
- Level AA has 55 criteria (A plus AA). It's the recommended level.
- Level AAA has 86 criteria and is the highest level.

### Analysis areas

#### Semantic HTML and structure
- Heading hierarchy (h1-h6 without skipping levels)
- Semantic elements (nav, main, footer, article, section)
- Landmark regions for screen reader navigation
- Logical reading order

#### ARIA
- Valid ARIA roles, states, and properties
- Landmark roles (banner, navigation, main, complementary)
- Widget roles (button, checkbox, tab, dialog)
- Live regions for dynamic content
- ARIA labels and descriptions

#### Keyboard access
- Tab order that follows the layout
- Keyboard access to every control
- Keyboard traps
- Visible focus indicators
- Skip navigation links
- Focus management in modals and dialogs
- WCAG 2.2: Focus Not Obscured (SC 2.4.11), Focus Appearance (SC 2.4.13)

#### Color contrast
- Normal text: 4.5:1 minimum (AA), 7:1 (AAA)
- Large text: 3:1 minimum (AA), 4.5:1 (AAA)
- UI components: 3:1 minimum
- Information not conveyed by color alone
- Color blindness

#### Forms
- Label associations (explicit and implicit)
- Fieldset and legend for grouped controls
- Required field indication
- Error identification and suggestions
- Accessible error messages (aria-describedby, aria-invalid)
- Autocomplete attributes
- WCAG 2.2: Redundant Entry (SC 3.3.7), Accessible Authentication (SC 3.3.8/3.3.9)

#### Alternative text
- Descriptive alt text for informative images
- Empty alt for decorative images
- Descriptions for complex images
- Accessible names for icon buttons
- SVG names and roles
- Video captions and audio transcripts

#### Interactive components
- Accessible names for every control
- Button vs link semantics
- Modals and dialogs (focus trap, ESC key, aria-modal)
- Tooltips
- Dropdowns and selects
- ARIA patterns for custom widgets
- WCAG 2.2: Consistent Help (SC 3.2.6)

#### Mobile and responsive
- Touch target size: 24×24px minimum (AA, SC 2.5.8); 44×44px (AAA, SC 2.5.5)
- No horizontal scrolling at 320px width
- Text can be zoomed to 200%
- Orientation not locked
- Content reflows at 400% zoom
- WCAG 2.2: Dragging Movements (SC 2.5.7), Target Size Minimum (SC 2.5.8)

## Plugin details

- **Name:** AI-Accessibility
- **Version:** 2.0.1
- **License:** MIT
- **Author:** Charles Jones

## Contributing

Bug reports and fixes are welcome. See [CONTRIBUTING.md](../../CONTRIBUTING.md).

## License

MIT License. See [LICENSE](LICENSE).
