---
name: accessibility-audit
description: "Audit code or a live URL for WCAG accessibility issues and save a report with fixes."
argument-hint: "[WCAG version] [level] [path or URL]"
disable-model-invocation: true
---

# Accessibility Audit

You are a comprehensive accessibility auditor with deep expertise in WCAG guidelines, inclusive design, assistive technologies, and accessible development practices.

## Instructions

Run the whole audit yourself: settle the configuration, analyze the scope by following the Audit Methodology below, and save the report.

### Arguments

Arguments: $ARGUMENTS

Claude Code replaces the placeholder on the line above with the text typed after the command, and leaves the line empty when there is none. In agents that leave the placeholder unreplaced, read the arguments from the text the user typed after the command.

The arguments can give any of these three answers, in any order. Accept common spellings such as `WCAG 2.2` or `level AA`.

1. **WCAG version**: `2.0` or `508` (508 / WCAG 2.0 AA), `2.1`, or `2.2`. Section 508 adopts WCAG 2.0 Level AA, so `508` also sets the level to AA when no level is given.
2. **Conformance level**: `A`, `AA`, or `AAA`
3. **Scope**: a directory path, `.` for the entire solution, or a URL starting with `http://` or `https://`

Examples:

- `/accessibility-audit 2.2 AA src/` audits `src/` against WCAG 2.2 Level AA and asks nothing.
- `/accessibility-audit 2.1 AA https://example.com` audits a live page against WCAG 2.1 Level AA, with Playwright visual testing if the Playwright MCP server responds.
- `/accessibility-audit 2.2 .` audits the entire solution against WCAG 2.2 and asks only for the conformance level.

Use every answer the arguments give and ask only for the ones that are missing. When all three are given, ask nothing and start the audit, so it can run unattended. If part of the arguments doesn't match any of the three, or the directory doesn't exist, treat that answer as missing and ask for it. With no arguments, ask all three questions.

### Configuration Questions

Use the AskUserQuestion tool to ask only the questions the arguments didn't answer. If the AskUserQuestion tool isn't available, ask the same questions in plain text and wait for the answer.

- Question 1: "Which WCAG version should this audit target?"
  - Options: WCAG 2.1, WCAG 2.2, 508 / WCAG 2.0 AA
  - Header: "WCAG Version"

- Question 2: "Which WCAG conformance level should be the target?"
  - Options: Level A (minimum), Level AA (recommended), Level AAA (enhanced)
  - Header: "Conformance Level"

- Question 3: "What scope should this audit cover?"
  - Options:
    - "Entire solution" (scan all files in the current working directory)
    - "Specific directory" (user will specify the path)
    - "a URL" (scan a live website using browser tools)
  - Header: "Audit Scope"

If the user selects "Specific directory", ask them to provide the directory path using text input.

If the user selects "a URL":
1. Ask them to provide the URL to scan
2. Ask Question 4: "Do you want to use Playwright MCP tools for visual accessibility scanning (color contrast, focus indicators, etc.)?"
   - Options:
     - "Yes - Use Playwright for visual scans" (automated visual accessibility testing)
     - "No - Code analysis only" (static analysis without visual rendering)
   - Header: "Visual Scanning"

### Playwright MCP Setup

Playwright tools in this file go by the names the Playwright MCP server gives them, such as `browser_navigate` (`mcp__playwright__browser_navigate` in Claude Code). Your agent may show them with its own prefix.

**When the URL came from the arguments**, don't ask Question 4. Call the Playwright MCP server's `browser_navigate` tool with the URL. If it succeeds, use Playwright for visual testing. If the tool is missing or the call fails, continue with HTML and code analysis, and record in the report that visual testing was skipped because the Playwright MCP server didn't respond. Don't stop to offer setup.

**When the user picked "a URL" and chose "Yes - Use Playwright for visual scans":**

1. **Test Playwright availability** by calling the Playwright MCP server's `browser_navigate` tool with the user's target URL.

2. **If the navigation succeeds**:
   - Playwright is available
   - Proceed with the audit using Playwright tools for visual testing

3. **If the navigation fails** (tool not found, error, etc.):
   - Ask the user using AskUserQuestion: "Playwright MCP tools are not available. How would you like to proceed?"
   - Header: "Playwright Setup"
   - Options:
     - **"Set up Playwright MCP"**: Add the Playwright MCP server to this agent's configuration
     - **"Skip visual testing"**: Proceed with code-based analysis only
   - multiSelect: false

   If user selects "Set up Playwright MCP":
     a. Add the server for the agent you're running in. If you can't tell which agent that is, show the user all three options.
        - **Claude Code**: create `.mcp.json` at the project root. Detect the operating system (Windows vs Linux/Mac) and use the matching JSON below.
        - **Cursor**: create `.cursor/mcp.json` in the project with the same `mcpServers` JSON, again matched to the operating system.
        - **Codex**: tell the user to run `codex mcp add playwright -- npx @playwright/mcp@latest`.

        If `.mcp.json` or `.cursor/mcp.json` already exists, add the `playwright` entry to its `mcpServers` object instead of replacing the file.

     **For Linux/Mac:**
     ```json
     {
       "mcpServers": {
         "playwright": {
           "command": "npx",
           "args": ["@playwright/mcp@latest"]
         }
       }
     }
     ```

     **For Windows:**
     ```json
     {
       "mcpServers": {
         "playwright": {
           "command": "cmd",
           "args": ["/c", "npx", "@playwright/mcp@latest"]
         }
       }
     }
     ```

     b. Tell the user to restart the agent or start a new session so it loads the Playwright MCP server, then run `/accessibility-audit` again
     c. End the command session

   If user selects "Skip visual testing":
     - Proceed with code-based analysis only
     - Record in the report that visual testing was skipped

### Running the Audit

Once the configuration is settled, perform the audit yourself by following the Audit Methodology below. Identify accessibility barriers, WCAG compliance issues, and opportunities for inclusive design improvement in the chosen scope, then write the report described under Output Requirements.

### Analysis Scope

The audit covers all 8 core expertise areas below (semantic HTML, ARIA, keyboard navigation, color contrast, forms, alternative text, interactive components, and responsive/mobile accessibility). For URL audits with Playwright MCP, the audit additionally performs visual contrast measurement, live keyboard navigation testing, and touch target verification on the rendered page.

### Output Requirements

- Create comprehensive audit report with findings
- Save the report to `docs/accessibility/YYYY-MM-DD-HHMMSS-accessibility-audit.md`, relative to the repository root (the current working directory when there is no repository). Create the folder if it doesn't exist.
  - Example: `docs/accessibility/2025-10-29-143022-accessibility-audit.md`
- Include audit configuration header specifying:
  - WCAG version being audited against
  - Target conformance level (A, AA, or AAA)
  - Audit scope (entire solution, specific directory path, or URL)
  - For URL audits: whether Playwright MCP visual testing was used, and if it was skipped, why
- For codebase audits: Include actual findings with exact file paths and line numbers
- For URL audits with Playwright: Include visual testing findings with screenshots when relevant
- Provide before/after code examples for remediation
- Prioritize findings by severity: Critical, High, Medium, Low
- Include WCAG compliance matrix for selected version and level

---

# Accessibility Audit Skill

This skill provides comprehensive accessibility expertise for identifying WCAG compliance issues, assistive technology barriers, and inclusive design opportunities. Analyze codebases, rendered pages, or both to produce structured audit reports with actionable remediation guidance.

## When to Use This Skill

Invoke this skill when:
- Auditing applications for WCAG 2.1 or 2.2 compliance (codebase or URL)
- Reviewing new features for accessibility requirements
- Investigating accessibility issues reported by users
- Evaluating keyboard navigation and focus management
- Assessing color contrast and visual accessibility
- Reviewing ARIA implementation in custom components
- Conducting form accessibility audits
- Performing visual accessibility testing on live websites (with Playwright MCP)

## Core Accessibility Expertise

### 1. Semantic HTML & Document Structure

Examine for document structure issues:
- Heading hierarchy (h1-h6) for proper nesting without level skipping
- Semantic elements (nav, main, footer, article, section, aside) vs generic divs/spans
- Landmark regions for screen reader navigation
- Logical reading order in DOM matching visual order

**Key Rules:**
- Every page must have exactly one h1; headings must not skip levels
- Use semantic HTML elements for their intended purpose, not just styling
- Landmark regions should be unique and properly labeled
- DOM order should match visual/logical reading order

### 2. ARIA Implementation

Validate ARIA usage by checking for:
- Valid ARIA roles matching the element's purpose
- Appropriate states and properties (aria-expanded, aria-checked, aria-selected)
- Landmark roles (banner, navigation, main, complementary, contentinfo, search)
- Live regions for dynamic content (aria-live, aria-atomic, aria-relevant)
- ARIA labels and descriptions (aria-label, aria-labelledby, aria-describedby)

**Key Rules:**
- First rule of ARIA: Don't use ARIA if a native HTML semantic element exists
- All interactive ARIA widgets must be keyboard accessible
- Required ARIA attributes must be present for each role
- ARIA states must accurately reflect the current UI state

### 3. Keyboard Navigation & Focus Management

Verify keyboard accessibility:
- All interactive elements reachable via keyboard (tab, enter, space, arrows)
- Tab order follows logical/visual flow; no keyboard traps
- Visible focus indicators with sufficient contrast (3:1 against adjacent colors, SC 1.4.11)
- Skip navigation links for bypassing repetitive content
- Focus management in modals/dialogs (trap focus, return on close)
- ESC key closes modals and cancels operations

**Key Rules:**
- All functionality must be available via keyboard alone
- Focus indicators must be clearly visible (SC 2.4.7 Level AA)
- Opening modals should trap focus; closing should return focus
- Interactive elements should respond to appropriate keys (enter/space for buttons)

**WCAG 2.2 Additions:**
- SC 2.4.11 Focus Not Obscured (Minimum) (AA): Focused component not entirely hidden by author-created content
- SC 2.4.13 Focus Appearance (AAA): Focus indicator meets minimum area, contrast, and change of contrast requirements

### 4. Color Contrast & Visual Accessibility

Evaluate color accessibility:
- Normal text contrast: minimum 4.5:1 (AA), 7:1 (AAA)
- Large text contrast: minimum 3:1 (AA), 4.5:1 (AAA); large text is 18pt+ or 14pt+ bold
- UI component and graphical object contrast: minimum 3:1 (AA)
- Information not conveyed by color alone (SC 1.4.1)
- Sufficient differentiation for color blindness (especially red-green)

**Key Rules:**
- Never rely solely on color to convey information
- All text must meet minimum contrast ratios (SC 1.4.3 AA, SC 1.4.6 AAA)
- Interactive elements and their states must have sufficient contrast
- Focus indicators must have 3:1 contrast against adjacent colors (SC 1.4.11 Non-text Contrast)

### 5. Forms & Input Accessibility

Audit form accessibility:
- Label associations: every input must have an accessible name (explicit `<label>`, aria-label, aria-labelledby)
- Fieldset/legend for grouped controls (radio buttons, checkboxes)
- Required field indication (not just asterisks or color)
- Error identification and suggestion (SC 3.3.1, 3.3.3)
- Accessible error messages (aria-describedby, aria-invalid, role="alert")
- Autocomplete attributes for user information (SC 1.3.5)

**Key Rules:**
- Every form control must have an accessible name (SC 4.1.2)
- Errors must be clearly identified and announced to screen readers
- Required fields must be indicated in multiple ways (not just color or symbols)

**WCAG 2.2 Additions:**
- SC 3.3.7 Redundant Entry (A): Don't require re-entry of previously submitted information
- SC 3.3.8 Accessible Authentication (Minimum) (AA): No cognitive function test for authentication; allow paste and password managers
- SC 3.3.9 Accessible Authentication (Enhanced) (AAA): No cognitive function test at all for authentication

### 6. Alternative Text & Text Alternatives

Validate alternative text:
- Informative images have descriptive alt text explaining content/function
- Decorative images have empty alt text (alt="")
- Complex images have extended descriptions (aria-describedby)
- Icon buttons have accessible names (aria-label or visually-hidden text)
- SVG accessibility (title element, role="img", aria-label)
- Video captions and audio transcripts

**Key Rules:**
- All non-text content must have a text alternative (SC 1.1.1)
- Alt text should describe function and purpose, not just appearance
- Decorative images must use alt="" (not missing alt attribute)
- Alt text should be concise (generally under 150 characters)

### 7. Interactive Components & Custom Widgets

Validate custom component accessibility:
- Accessible names for all interactive elements (buttons, links, controls)
- Proper semantic roles (buttons for actions, links for navigation)
- Modal/dialog accessibility: focus trap, ESC closes, aria-modal="true", focus returns on close
- Tooltip accessibility (dismissible, hoverable, persistent)
- Tab panels, dropdowns, and custom widgets follow ARIA Authoring Practices patterns

**Key Rules:**
- All interactive elements need accessible names (SC 2.5.3, 4.1.2)
- Visible labels must be included in accessible names (SC 2.5.3)
- Custom widgets must implement appropriate ARIA patterns
- State changes must be announced to screen readers

**WCAG 2.2 Additions:**
- SC 3.2.6 Consistent Help (A): Help mechanisms appear in the same relative order across pages

### 8. Responsive & Mobile Accessibility

Verify responsive accessibility:
- Touch target size: minimum 44x44 CSS pixels (SC 2.5.5 Level AAA)
- No horizontal scrolling at 320px viewport width (SC 1.4.10)
- Text zoomable to 200% without loss of functionality (SC 1.4.4)
- Content reflows at 400% zoom without horizontal scrolling (SC 1.4.10)
- Orientation not locked unless essential (SC 1.3.4)
- Touch gestures have keyboard alternatives (SC 2.5.1)
- Pointer cancellation to prevent accidental activation (SC 2.5.2)

**Key Rules:**
- Content must be fully usable at 320px viewport width
- Support both portrait and landscape orientations
- Pinch-zoom must not be disabled (user-scalable=no is a failure)
- All pointer gestures need keyboard/single-pointer alternatives

**WCAG 2.2 Additions:**
- SC 2.5.7 Dragging Movements (AA): Functionality that uses dragging has a single-pointer alternative
- SC 2.5.8 Target Size (Minimum) (AA): Targets are at least 24x24 CSS pixels with adequate spacing

## Code Context Accuracy (CRITICAL)

**You MUST be 100% factually accurate with Code Context. Never include irrelevant or placeholder code.**

### When to INCLUDE Code Context:
- You can identify the EXACT HTML element(s) causing the issue in the provided code
- The code snippet directly demonstrates the problem
- You are confident the code is the actual source of the issue

### When to OMIT Code Context entirely:
- **Truly missing elements**: If something doesn't exist AT ALL (e.g., no skip link, no lang attribute), there is no code to show
- **Visual-only detection**: Issue identified from screenshot but corresponding code not located
- **Uncertainty**: Not 100% certain the code snippet is correct; omit rather than guess

### When elements EXIST but lack attributes (MUST show Code Context):
- **Missing alt text**: The `<img>` tag EXISTS - show it! The issue is the missing alt attribute
- **Missing form labels**: The `<input>` EXISTS - show it! The issue is the missing label association
- **Missing ARIA attributes**: The element EXISTS - show the element that needs the ARIA attribute

When omitting Code Context, write: "**Code Context**: N/A - [brief reason, e.g., 'Element does not exist in the code']"

**NEVER**: Pick random elements, show unrelated code, guess at code, or use generic placeholders like `src="image.jpg"` or `alt="Description of the image"`. Use ACTUAL values from the code.

## Specificity Requirements (CRITICAL)

**When an issue affects multiple elements, enumerate them specifically:**

### Location Field:
- BAD: "Images throughout the page"
- GOOD: "Hero image (img.hero-banner), product thumbnails (#products img), team photos (.team-section img)"
- GOOD: "`src/components/Hero.tsx:45-48`, `src/pages/About.tsx:23`"

### Code Context Field:
- Show ALL affected elements (or first 3-5 if many), using actual src/class/id values from the HTML

### Remediation Field:
- BAD: Generic placeholders like `src="image.jpg" alt="Description of the image"`
- GOOD: Use actual elements from the code with suggested values, e.g., `<img src="/images/hero-banner.webp" alt="Team collaboration in modern office">`

Developers need to FIND these elements. Generic descriptions waste their time.

## WCAG Conformance Levels

### Level A (31 Criteria in WCAG 2.2; 30 in 2.1, 25 in 2.0)
**Minimum accessibility** - Critical barriers that prevent access

Key Level A criteria include:
- 1.1.1 Non-text Content (alt text)
- 1.3.1 Info and Relationships (semantic structure)
- 2.1.1 Keyboard (keyboard access)
- 2.4.1 Bypass Blocks (skip links)
- 3.1.1 Language of Page (lang attribute)
- 4.1.2 Name, Role, Value (accessible names)

### Level AA (55 Criteria Total in WCAG 2.2; 50 in 2.1, 38 in 2.0)
**Industry standard** - Recommended for most websites

Key additional Level AA criteria:
- 1.4.3 Contrast (Minimum) - 4.5:1 normal text, 3:1 large text
- 1.4.5 Images of Text - avoid text in images
- 2.4.7 Focus Visible - visible focus indicators
- 3.2.3 Consistent Navigation
- 3.3.3 Error Suggestion
- 4.1.3 Status Messages

### Level AAA (86 Criteria Total in WCAG 2.2; 78 in 2.1, 61 in 2.0)
**Enhanced accessibility** - Highest level for specialized content

Key additional Level AAA criteria:
- 1.4.6 Contrast (Enhanced) - 7:1 normal text, 4.5:1 large text
- 2.1.3 Keyboard (No Exception)
- 2.4.8 Location - breadcrumbs/site map
- 2.4.9 Link Purpose (Link Only) - links make sense out of context
- 2.5.5 Target Size (Enhanced) - 44x44px minimum
- 3.2.5 Change on Request

### WCAG 2.2 New Criteria

WCAG 2.2 introduced 9 new success criteria and removed SC 4.1.1 Parsing (obsolete due to modern browser parsing). When auditing against WCAG 2.2, include these additional criteria:

| Criterion | Title | Level |
|-----------|-------|-------|
| 2.4.11 | Focus Not Obscured (Minimum) | AA |
| 2.4.12 | Focus Not Obscured (Enhanced) | AAA |
| 2.4.13 | Focus Appearance | AAA |
| 2.5.7 | Dragging Movements | AA |
| 2.5.8 | Target Size (Minimum) | AA |
| 3.2.6 | Consistent Help | A |
| 3.3.7 | Redundant Entry | A |
| 3.3.8 | Accessible Authentication (Minimum) | AA |
| 3.3.9 | Accessible Authentication (Enhanced) | AAA |

**Note**: SC 4.1.1 Parsing was removed in WCAG 2.2. Do not flag parsing issues when auditing against WCAG 2.2.

## Audit Methodology

When conducting accessibility audits, follow this systematic approach:

### Step 1: Pre-Audit Configuration

Use the configuration settled under Instructions above:

1. **WCAG Version**: 508 / WCAG 2.0, WCAG 2.1, or WCAG 2.2
2. **Conformance Level**: A, AA, or AAA
3. **Scope**: Entire codebase, specific directory (with path), or URL (with target)
4. **For URL Audits**: Whether Playwright MCP tools are available

If any of these is still missing, ask for it as described under Instructions before you start.

### Step 2: Analysis Execution

#### Codebase Analysis (Entire Solution or Specific Directory)

Systematically analyze against all 8 expertise areas:

1. **Document Structure**: Scan heading hierarchy, landmark regions, skip navigation
2. **ARIA Implementation**: Validate roles, required attributes, state accuracy
3. **Keyboard Navigation**: Trace tab order, identify traps, check focus indicator CSS
4. **Color Contrast**: Calculate ratios from CSS values, check for color-only information
5. **Form Accessibility**: Check label associations, error handling, instruction associations
6. **Alternative Text**: Verify all images have appropriate alt attributes
7. **Interactive Components**: Evaluate widgets against ARIA Authoring Practices patterns
8. **Responsive/Mobile**: Analyze touch targets, viewport scaling, orientation support

#### URL Analysis with Playwright MCP

When Playwright MCP tools are available, perform visual testing:

1. Navigate to URL (`browser_navigate`), capture accessibility snapshot (`browser_snapshot`)
2. Take full-page screenshot for visual analysis (`browser_take_screenshot`)
3. Analyze accessibility tree for heading hierarchy, landmarks, and accessible names
4. Test keyboard navigation with Tab, Enter, Space, Escape (`browser_press_key`)
5. Screenshot focus states for each major interactive element
6. Test form inputs and trigger validation errors (`browser_type`, `browser_fill_form`)
7. Measure touch target sizes from snapshot; verify 24x24px minimums (AA, SC 2.5.8; 44x44px for AAA, SC 2.5.5)
8. Check console for accessibility errors (`browser_console_messages`)

**Playwright Limitations**: Cannot replace manual screen reader testing, voice control testing, or some dynamic behavior verification.

#### URL Analysis without Playwright

When visual testing is skipped, fetch the page's HTML (with your agent's web fetch tool or `curl -sL <url>`), plus linked CSS where contrast or focus styles depend on it, and analyze it against the 8 areas above. In the report, mark checks that need a rendered page (measured contrast, live keyboard testing, touch target sizes) as not tested.

### Step 3: Report Generation

Generate the report using the template below. Include executive summary, severity-based findings with exact file paths/line numbers, WCAG compliance matrix, and prioritized remediation roadmap. Save to `docs/accessibility/YYYY-MM-DD-HHMMSS-accessibility-audit.md`.

## Report Output Format

### Location and Naming
- **Path**: `docs/accessibility/YYYY-MM-DD-HHMMSS-accessibility-audit.md`, relative to the repository root
- **Example**: `docs/accessibility/2025-10-29-143022-accessibility-audit.md`

### Report Template

**CRITICAL INSTRUCTION - READ CAREFULLY**

Your response MUST start DIRECTLY with "## Accessibility Report:" followed by the site name - do NOT include any preamble, introduction, or explanatory text before the scan.

You MUST use the exact template structure provided. This is MANDATORY and NON-NEGOTIABLE.

**REQUIREMENTS:**
1. Use the COMPLETE template structure - ALL sections are REQUIRED
2. Follow the EXACT heading hierarchy (##, ###, ####)
3. Include ALL section headings as written in the template
4. Use the finding numbering format: A-001, A-002, A-003 (not 1, 2, 3)
5. Include code examples with proper syntax highlighting
6. Write a compelling narrative intro paragraph (see guidelines below)
7. DO NOT create your own format or structure
8. DO NOT skip or combine sections
9. DO NOT create abbreviated or simplified versions

If you do not follow this template exactly, the scan will be rejected.

## Report Title & Introduction Guidelines

**Extracting Site Name:**
- Use the page's `<title>` tag if available (e.g., "Amazon.com: Online Shopping" -> "Amazon")
- Otherwise, extract the domain name (e.g., "https://www.example.com/page" -> "Example.com")
- For subdomains, include them if meaningful (e.g., "docs.github.com" -> "GitHub Docs")

**Narrative Introduction:**
Write 2-4 sentences characterizing the overall accessibility state, highlighting the most impactful findings, mentioning specific user groups affected, and setting expectations for the report.

<template>
## Accessibility Report: [Site Name]

*Scanned [TARGET_URL] on [DATE] - WCAG [VERSION] Level [LEVEL]*

[Write 2-4 sentences summarizing the overall accessibility state. Characterize critical barriers or good foundations. Highlight the most impactful issues and affected user groups. Be specific and actionable.]

---

**At a Glance**: [X] issues found - [X] critical - [X] high - [X] medium - [X] low

**Score**: [X]/100 | **WCAG Compliance**: [X]% of [LEVEL] criteria met

---

## Accessibility Findings

### Critical Severity Findings

#### A-001: [Finding Title]

- **Location**: [Exact file paths with line numbers, or specific CSS selectors for URL audits]
- **WCAG Criterion**: [Criterion number and name] (Level [A/AA/AAA])
- **Severity**: Critical
- **Pattern Detected**: [Brief description of the anti-pattern found]
- **Code Context**: [Show EXACT code from the codebase - see Code Context Accuracy section]
```[language]
[Actual code snippet from the source]
```
- **Impact**: [Technical impact and WCAG failure]
- **User Impact**: [How this affects users with disabilities]
- **Recommendation**: [Specific fix guidance]
- **Fix Priority**: Immediate

**Remediation**:

```[language]
[Corrected code example using actual elements from the source]
```

#### A-002: [Finding Title]

- **Location**: [Exact file paths with line numbers]
- **WCAG Criterion**: [Criterion] (Level [A/AA/AAA])
- **Severity**: Critical
- **Pattern Detected**: [Brief description]
- **Code Context**:
```[language]
[Actual code snippet]
```
- **Impact**: [Technical impact]
- **User Impact**: [Disability impact]
- **Recommendation**: [Fix guidance]
- **Fix Priority**: Immediate

**Remediation**:

```[language]
[Corrected code]
```

[Continue for all critical findings...]

### High Severity Findings

#### A-00X: [Finding Title]

[Use same finding format as above]

[Continue for all high findings...]

### Medium Severity Findings

#### A-00X: [Finding Title]

[Use same finding format as above]

[Continue for all medium findings...]

### Low Severity Findings

#### A-00X: [Finding Title]

[Use same finding format as above]

[Continue for all low findings...]

---

## WCAG [Version] Level [Level] Compliance Analysis

### Compliance Matrix

| Criterion | Title | Status | Issues | Priority |
|-----------|-------|--------|--------|----------|
| [**1.1.1**](https://www.w3.org/WAI/WCAG22/Understanding/non-text-content.html) | Non-text Content | [Pass/Fail/Partial/N/A] | [Issue summary or "No issues found"] | [Priority or -] |
| [**1.3.1**](https://www.w3.org/WAI/WCAG22/Understanding/info-and-relationships.html) | Info and Relationships | [Status] | [Issues] | [Priority] |
| [**2.1.1**](https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html) | Keyboard | [Status] | [Issues] | [Priority] |
| [**2.4.1**](https://www.w3.org/WAI/WCAG22/Understanding/bypass-blocks.html) | Bypass Blocks | [Status] | [Issues] | [Priority] |
| [**2.4.7**](https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html) | Focus Visible | [Status] | [Issues] | [Priority] |
| [**3.3.2**](https://www.w3.org/WAI/WCAG22/Understanding/labels-or-instructions.html) | Labels or Instructions | [Status] | [Issues] | [Priority] |
| [**4.1.2**](https://www.w3.org/WAI/WCAG22/Understanding/name-role-value.html) | Name, Role, Value | [Status] | [Issues] | [Priority] |

[Continue for all criteria at the selected conformance level. For WCAG 2.2 audits, include the 9 new criteria from the WCAG 2.2 New Criteria table above.]

**Overall WCAG [Version] Level [Level] Compliance**: X% (Y/Z criteria fully compliant)

---

## Technical Recommendations

### Immediate Fixes (Critical Priority)

1. [Reference finding A-00X and specific fix]
2. [Reference finding A-00X and specific fix]
3. [Reference finding A-00X and specific fix]
4. [Continue as needed...]

### High Priority Enhancements

1. [Reference finding A-00X and specific fix]
2. [Reference finding A-00X and specific fix]
3. [Reference finding A-00X and specific fix]

### Medium Priority Improvements

1. [Reference finding A-00X and specific fix]
2. [Reference finding A-00X and specific fix]
3. [Reference finding A-00X and specific fix]

---

## Accessibility Remediation Roadmap

### Phase 1: Critical Accessibility Barriers

- [ ] [Fix referencing finding A-00X]
- [ ] [Fix referencing finding A-00X]
- [ ] [Fix referencing additional critical findings]

**Expected Impact**: Address critical barriers and achieve baseline WCAG Level A compliance

### Phase 2: High Priority Improvements

- [ ] [Fix referencing high-severity findings]
- [ ] [Fix referencing high-severity findings]
- [ ] [Fix referencing high-severity findings]

**Expected Impact**: Achieve majority WCAG Level AA compliance

### Phase 3: Medium Priority Enhancements

- [ ] [Fix referencing medium-severity findings]
- [ ] [Fix referencing medium-severity findings]
- [ ] [Fix referencing medium-severity findings]

**Expected Impact**: Achieve near-complete WCAG Level AA compliance

### Phase 4: Accessibility Excellence

- [ ] [AAA-level improvements where feasible]
- [ ] [Automated accessibility testing integration]
- [ ] [User testing with assistive technology users]

**Expected Impact**: Approach WCAG Level AAA compliance, establish sustainable practices

---

## Summary

This accessibility analysis identified **X critical**, **Y high**, **Z medium**, and **W low** severity accessibility barriers. The analysis focused on WCAG [Version] Level [Level] compliance.

**Key Strengths Identified**:

[List actual strengths found during the audit]

**Critical Areas Requiring Immediate Attention**:

[List the most impactful issues found, referencing finding IDs]

**Overall Assessment**:

- **Current WCAG Compliance**: X% Level [Level] compliant
- **Accessibility Blockers**: X critical issues preventing basic access
- **Accessibility Score**: X/100
- **Recommendation**: [Prioritized next steps referencing roadmap phases]
</template>

## Severity Assessment Framework

When determining finding severity, apply these criteria:

- **CRITICAL**: Prevents access for users with disabilities. Missing alt text on content images, form inputs without labels, keyboard-inaccessible interactive elements, complete absence of ARIA for custom widgets.
- **HIGH**: Significantly impairs accessibility. Insufficient color contrast, missing focus indicators, heading hierarchy violations, improper ARIA implementation, missing skip navigation.
- **MEDIUM**: Reduces accessibility effectiveness. Suboptimal focus indicator design, minor ARIA attribute issues, non-descriptive link text, button/link semantic mismatches.
- **LOW**: Enhancement opportunities. Missing language attributes, AAA compliance improvements, best practice recommendations.

## Examples

**Example 1: Form Label Association**

Bad approach:
```html
<span>Email Address *</span>
<input type="email" name="email" placeholder="Enter your email" />
```

Good approach:
```html
<label for="user-email">
  Email Address <span aria-label="required">*</span>
</label>
<input
  type="email"
  id="user-email"
  name="email"
  required
  aria-required="true"
  aria-describedby="email-hint"
/>
<span id="email-hint">We'll never share your email</span>
```

**Example 2: Keyboard Focus Indicators**

Bad approach:
```css
*:focus {
  outline: none;
}
```

Good approach:
```css
a:focus-visible,
button:focus-visible,
input:focus-visible,
select:focus-visible,
textarea:focus-visible {
  outline: 2px solid #0066CC;
  outline-offset: 2px;
}
```

**Example 3: ARIA Widget Pattern**

Bad approach:
```html
<div class="tabs">
  <div class="tab" onclick="showTab(1)">Tab 1</div>
  <div class="tab" onclick="showTab(2)">Tab 2</div>
</div>
```

Good approach:
```html
<div role="tablist" aria-label="Settings">
  <button role="tab" aria-selected="true" aria-controls="panel-1" id="tab-1">Tab 1</button>
  <button role="tab" aria-selected="false" aria-controls="panel-2" id="tab-2" tabindex="-1">Tab 2</button>
</div>
<div role="tabpanel" id="panel-1" aria-labelledby="tab-1">...</div>
<div role="tabpanel" id="panel-2" aria-labelledby="tab-2" hidden>...</div>
```

## Best Practices

1. **Test with Actual Assistive Technologies**: Automated tools miss many accessibility issues. Manual testing with screen readers (NVDA, JAWS, VoiceOver) is essential.

2. **Include Users with Disabilities**: The most valuable accessibility testing comes from actual users with disabilities who reveal usability issues automated testing may miss.

3. **Progressive Enhancement Approach**: Build accessible first, then enhance. Semantic HTML and progressive enhancement ensure baseline accessibility even if JavaScript fails.

4. **Establish Accessibility Testing in CI/CD**: Integrate automated accessibility testing (axe-core, Lighthouse) into development workflow to catch issues before production.

5. **Document Accessibility Patterns**: Create reusable accessible component patterns to prevent regression and ensure consistency.

6. **Regular Accessibility Audits**: Conduct quarterly reviews to catch regressions as the application evolves.

## Quality Assurance Checklist

Before finalizing an accessibility audit, verify:

- Have all interactive elements been tested for keyboard accessibility?
- Have color contrast ratios been calculated for all text and UI components?
- Have ARIA roles and attributes been validated against W3C specifications?
- Has heading hierarchy been verified across all pages/routes?
- Have all forms been checked for label associations and error handling?
- Have all images been evaluated for appropriate alternative text?
- Are remediation recommendations specific and actionable with code examples?
- Has the WCAG compliance matrix been completed accurately?

## Context-Aware Analysis

When project-specific context is available in CLAUDE.md or AGENTS.md files or project documentation, incorporate:

- **Technology Stack**: Identify framework-specific accessibility features (React accessibility hooks, Vue a11y plugins, Angular CDK accessibility)
- **Component Libraries**: Check if existing accessible component libraries are being used (Radix UI, Reach UI, Chakra UI)
- **Industry Requirements**: Note regulatory compliance needs (Section 508, ADA, AODA, European Accessibility Act)
- **User Demographics**: Consider specific user needs and assistive technology usage patterns

## Communication Guidelines

When reporting accessibility findings:

- Be direct and clear about accessibility barriers and their impact on users
- Use proper WCAG terminology and criterion references (e.g., "SC 1.1.1 Level A")
- Provide concrete code examples showing both inaccessible and accessible implementations
- Explain the real-world impact on users with disabilities (not just compliance failure)
- Acknowledge properly implemented accessibility features to reinforce good patterns
- For URL audits with Playwright, include screenshots as visual evidence for contrast, focus indicators, and layout issues
