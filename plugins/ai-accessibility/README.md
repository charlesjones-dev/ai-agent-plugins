# AI-Accessibility Plugin

**Accessibility audits for Claude Code, Codex and Cursor.** `/accessibility-audit` checks your code or a live URL against WCAG 2.1, WCAG 2.2 or 508 / WCAG 2.0 AA and saves a report with before/after fixes. URL audits can use Playwright MCP for visual checks.

---

## What This Plugin Does

The plugin ships one skill, which runs in Claude Code, Codex and Cursor. Run the audit during development to catch accessibility barriers in code or on a rendered page before they reach production.

## Limits

An audit doesn't certify WCAG or legal compliance. It also doesn't replace manual screen reader testing or testing with people with disabilities.

## Available Skills

### `/accessibility-audit`

**Arguments:**

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

The skill uses whatever the arguments supply and asks only for what's missing. With all three it asks nothing, so the audit can run unattended. With none, it asks:

1. **WCAG Version**: Choose WCAG 2.1, WCAG 2.2, or 508 / WCAG 2.0 AA
2. **Conformance Level**: Choose A (minimum), AA (industry standard), or AAA (enhanced)
3. **Scope**: Choose entire codebase, specific directory, or a URL
4. **Visual Scanning** (if URL selected): Choose whether to use Playwright MCP tools for visual accessibility testing

When the URL comes from the arguments, the skill uses Playwright if the Playwright MCP server responds. If it doesn't, the audit falls back to HTML and code analysis and the report notes that visual testing was skipped.

**What it analyzes:** the areas listed under [Features](#features). URL audits with Playwright MCP also check:

- **Visual Color Contrast Testing** - Contrast measurements of rendered elements
- **Actual Focus Indicator Visibility** - Visual verification of focus states
- **Rendered DOM Structure** - Accessibility tree as perceived by assistive technologies
- **Interactive Element Testing** - Keyboard navigation testing on live page
- **Touch Target Size Verification** - Actual pixel measurements of interactive elements
- **Screenshot-based Analysis** - Visual accessibility assessment with evidence

---

## Quick Start

### Installation

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

### Usage

**Codebase Analysis:**
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

**URL Analysis with Playwright MCP:**
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

---

## Features

### Configurable WCAG Assessment

**WCAG 2.1 vs 2.2:**
- **WCAG 2.1**: 78 success criteria across 13 guidelines (Level A 30, AA 20, AAA 28)
- **WCAG 2.2**: 86 success criteria (adds 9 and removes SC 4.1.1 Parsing; Level A 31, AA 24, AAA 31)
  - New criteria: Focus Not Obscured (AA/AAA), Focus Appearance (AAA), Dragging Movements (AA), Target Size Minimum (AA), Consistent Help (A), Redundant Entry (A), Accessible Authentication (AA/AAA)

**Conformance Levels** (WCAG 2.2, cumulative):
- **Level A** (31 criteria) - Minimum accessibility, critical barriers
- **Level AA** (55 criteria, A plus AA) - Industry standard
- **Level AAA** (86 criteria) - Enhanced accessibility, highest level

### Analysis Areas

#### Semantic HTML & Structure
- Heading hierarchy validation (h1-h6 without skipping levels)
- Semantic element usage (nav, main, footer, article, section)
- Landmark regions for screen reader navigation
- Logical reading order assessment

#### ARIA Implementation
- Valid ARIA roles, states, and properties
- Landmark roles (banner, navigation, main, complementary)
- Widget roles (button, checkbox, tab, dialog)
- Live regions for dynamic content
- ARIA labels and descriptions

#### Keyboard Accessibility
- Tab order follows logical flow
- All interactive elements keyboard accessible
- No keyboard traps detected
- Visible focus indicators
- Skip navigation links
- Focus management in modals/dialogs
- WCAG 2.2: Focus Not Obscured (SC 2.4.11), Focus Appearance (SC 2.4.13)

#### Color Contrast
- Normal text: 4.5:1 minimum (AA), 7:1 (AAA)
- Large text: 3:1 minimum (AA), 4.5:1 (AAA)
- UI components: 3:1 minimum
- Information not conveyed by color alone
- Color blindness considerations

#### Form Accessibility
- Label associations (explicit/implicit)
- Fieldset/legend for grouped controls
- Required field indication
- Error identification and suggestions
- Accessible error messages (aria-describedby, aria-invalid)
- Autocomplete attributes
- WCAG 2.2: Redundant Entry (SC 3.3.7), Accessible Authentication (SC 3.3.8/3.3.9)

#### Alternative Text
- Descriptive alt text for informative images
- Empty alt for decorative images
- Complex image descriptions
- Icon button accessible names
- SVG accessibility
- Video captions and audio transcripts

#### Interactive Components
- Accessible names for all interactive elements
- Proper button vs link semantics
- Modal/dialog accessibility (focus trap, ESC key, aria-modal)
- Tooltip accessibility
- Dropdown/select accessibility
- Custom widget ARIA patterns
- WCAG 2.2: Consistent Help (SC 3.2.6)

#### Mobile & Responsive
- Touch target size: 24×24px minimum (AA, SC 2.5.8); 44×44px (AAA, SC 2.5.5)
- No horizontal scrolling at 320px width
- Text can be zoomed to 200%
- Orientation not locked
- Content reflows at 400% zoom
- WCAG 2.2: Dragging Movements (SC 2.5.7), Target Size Minimum (SC 2.5.8)

---

## Plugin Details

- **Name:** AI-Accessibility
- **Version:** 2.0.0
- **License:** MIT
- **Author:** Charles Jones

---

## Contributing

Bug reports and fixes are welcome. See [CONTRIBUTING.md](../../CONTRIBUTING.md).

---

## License

MIT License. See [LICENSE](LICENSE).
