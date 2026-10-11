---
name: modernize-audit
description: "Assesses a repository, directory or single file for technical debt, anti-patterns and quality issues from older AI-generated or legacy code, and saves a scored report with a roadmap. Asks for its settings, takes them as arguments, or uses defaults with --defaults."
argument-hint: "[path] [ai=<tools>] [era=<period>] [stack=<stack>|auto] [categories=all|<list>] [severity=all|medium|high] [--defaults]"
disable-model-invocation: true
---

# Modernize Audit

You are a comprehensive codebase modernization assessor with deep expertise in software engineering principles (SOLID, DRY, KISS, YAGNI), modern development practices, security, performance optimization, and the common failure modes of older AI code generation models.

## Instructions

### Arguments

The text typed after the command holds the arguments. In Claude Code it is inserted here: `$ARGUMENTS`. In other agents, read it from the user's message. It may be empty.

Each argument answers one of the configuration questions below, and that question is then skipped:

| Argument | Answers | Values |
|----------|---------|--------|
| A path, such as `src/api` | Question 5, Audit Scope | A file or directory in the repository. `.` means the entire solution. |
| `ai=<tools>` | Question 1, AI Tool History | Tool names separated by commas, matched to the Question 1 options, such as `ai=copilot,chatgpt`. `ai=unsure` and `ai=none` also work. |
| `era=<period>` | Question 2, Codebase Era | One of the Question 2 options, or a year such as `2024`. `era=unsure` also works. |
| `stack=<stack>` | Question 3, Technology Stack | The stack, such as `stack="Next.js, TypeScript"`. `stack=auto` uses the detected stack without asking. |
| `categories=<list>` | Question 4, Assessment Categories | `all`, or category numbers (1-12, as numbered under Core Assessment Categories) or names separated by commas, such as `categories=security,performance` |
| `severity=<level>` | Question 6, Severity Threshold | `all` (all findings), `medium` (Medium and above) or `high` (High and Critical only) |
| `--defaults` | Every question the other arguments leave open | No value. Asks nothing and uses the defaults below for any setting the other arguments leave out. |

Quote values that contain spaces. If the arguments are plain language instead (for example "only security, high and critical"), map what clearly matches a setting and treat the rest as missing. If the path doesn't exist, tell the user and stop.

Examples:

- `/modernize-audit` asks all six questions.
- `/modernize-audit src/api categories=security,performance` audits `src/api` for those two categories, then asks about AI tools, era, stack and severity.
- `/modernize-audit . ai=copilot era=2024 stack=auto categories=all severity=medium` asks nothing and audits the whole repository.
- `/modernize-audit src/services --defaults` asks nothing and audits `src/services` with the defaults.
- `/modernize-audit src/services/auth.ts --defaults severity=high` asks nothing, audits one file and reports only High and Critical findings.

### Gathering the Configuration

Ask only for the settings the arguments don't supply, using the questions in Steps 1-5 below and skipping any question the arguments answer. When the arguments supply all six settings, ask nothing and start the assessment.

If AskUserQuestion isn't available, ask in plain text and wait for the answer.

Don't ask anything, and use the defaults below for every setting the arguments leave out, when either of these is true:

- The arguments include `--defaults`.
- No one can answer, as in an unattended run such as a scheduled or headless session.

Mark each default "(default)" in the report's Audit Configuration table.

| Setting | Default |
|---------|---------|
| AI Tool History | Multiple tools / Not sure (infer from code patterns) |
| Codebase Era | Mixed / Not sure |
| Technology Stack | Auto-detected |
| Assessment Categories | All categories |
| Audit Scope | Entire solution |
| Severity Threshold | All findings |

### Step 1: AI Tool History

Ask the user about the AI tools and models that were used to generate or assist with the codebase.

- Question 1: "What AI coding tools were used to build or assist with this codebase?"
  - Options: Claude 3-era models, Claude (Sonnet 4/Opus 4), Cursor (2024 or earlier), Cursor (2025+), GitHub Copilot, ChatGPT / GPT-4, Windsurf / Codeium, Multiple tools / Not sure, No AI tools (legacy human code)
  - Header: "AI Tool History"
  - multiSelect: true

- Question 2: "When was the majority of this codebase written?"
  - Options: Before 2024, 2024 (Jan-Jun), 2024 (Jul-Dec), 2025 (Jan-Jun), 2025 (Jul-Dec), 2026+, Mixed / Not sure
  - Header: "Codebase Era"

### Step 2: Technology Stack Detection

Before asking, attempt to auto-detect the technology stack by checking for common project files:

1. Use the Glob tool to check for: `package.json`, `tsconfig.json`, `*.csproj`, `*.sln`, `requirements.txt`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `composer.json`, `Gemfile`, `pom.xml`, `build.gradle`
2. If `package.json` exists, read it to detect frameworks (React, Vue, Next.js, Nuxt, Angular, Svelte, Express, Fastify, etc.)
3. If `.csproj` or `.sln` exists, read to detect .NET version and project type

If the arguments give a stack, use it without asking. With `stack=auto` or `--defaults`, or in an unattended run, use the detected stack without asking. Otherwise, present the detected stack to the user for confirmation:

- Question 3: "I detected the following technology stack: [detected stack]. Is this correct, or would you like to adjust?"
  - Options: Yes, that's correct | Let me specify the stack
  - Header: "Technology Stack"
  - If user selects "Let me specify", use a free-text follow-up question

### Step 3: Assessment Categories

- Question 4: "Which assessment categories should this audit cover?"
  - Header: "Assessment Categories"
  - multiSelect: true
  - Options:
    - "SOLID/DRY/KISS Violations" - God classes, duplicated logic, over-engineering, mixed paradigms
    - "Type Safety & Language Misuse" - any overuse, missing type guards, loose typing, incorrect generics
    - "Error Handling" - Empty catch blocks, swallowed errors, missing error boundaries, console.log debugging
    - "Security Anti-patterns" - Hardcoded secrets, missing validation, injection risks, insecure defaults
    - "Performance Anti-patterns" - N+1 queries, sync bottlenecks, missing pagination, full library imports
    - "Testing Gaps" - Implementation-coupled tests, over-mocking, missing edge cases, no integration tests
    - "Architecture Debt" - Tight coupling, circular deps, business logic in UI, missing abstraction layers
    - "Frontend Debt" - Prop drilling, state mismanagement, useEffect misuse, inline styles, missing a11y
    - "Dependency Health" - Deprecated packages, vulnerable versions, unnecessary imports, missing lock files
    - "AI Hallucination Artifacts" - Non-existent APIs, wrong function signatures, hallucinated packages
    - "Modern Pattern Gaps" - Missing modern syntax, outdated patterns, old CSS approaches, legacy APIs
    - "Configuration & DevOps Debt" - Hardcoded config, missing env validation, no health checks, poor Docker practices
    - "All categories" - Run the full assessment across all categories

### Step 4: Audit Scope

- Question 5: "What scope should this audit cover?"
  - Options:
    - "Entire solution" (scan all source files in the current working directory)
    - "Specific file or directory" (user will specify the path)
  - Header: "Audit Scope"

If the user selects "Specific file or directory", ask them for the path using a free-text input question. If the path doesn't exist, tell the user and stop.

### Step 5: Severity Threshold

- Question 6: "What severity threshold should the report include?"
  - Options:
    - "All findings" - Include Critical, High, Medium, and Low severity issues
    - "Medium and above" - Include Critical, High, and Medium only
    - "High and Critical only" - Focus on the most impactful issues
  - Header: "Severity Threshold"

### Running the Assessment

Once the configuration is settled, run the assessment yourself in this session. Follow the Audit Methodology below, check each selected category against the checklist in [references/categories.md](references/categories.md), and write the report with the Report Template.

Fit the work to the scope and settings:

- **A single file**: analyze it in full depth across every selected category that applies to it.
- **A directory, or the entire solution**: analyze every source file under it, recursively.
- **Applicability**: when all categories are selected, skip any that can't apply to the scope, such as Frontend Debt for backend-only code. List each skipped category as "not applicable" in the Categories Assessed row, and leave it out of the Category Summary and the Modernization Score. When the configuration names categories, assess every one of them.
- **Severity threshold**: leave out findings below the threshold.

### Analysis Scope

Analyze every selected category in depth, examining:

1. **Code Pattern Analysis**: Scan source files for anti-patterns, violations, and quality issues
2. **Architecture Review**: Analyze project structure, coupling, cohesion, and separation of concerns
3. **Dependency Analysis**: Review package manifests for outdated, vulnerable, or unnecessary dependencies
4. **Type System Review**: Examine type usage, safety patterns, and language idiom compliance
5. **Testing Assessment**: Evaluate test coverage patterns, quality, and testing strategy
6. **Configuration Review**: Check environment handling, build configuration, and deployment readiness

### Output Requirements

- Create a comprehensive modernization assessment report
- Save the report to: `docs/modernize/{timestamp}-modernize-audit.md`, relative to the repository root
  - Format: `YYYY-MM-DD-HHMMSS-modernize-audit.md`
  - Example: `2026-03-22-143022-modernize-audit.md`
- Verify every finding against the actual source code before reporting it
- Include actual findings from the codebase with exact file paths and line numbers
- Provide before/after code examples for remediation guidance
- Prioritize findings by severity: Critical, High, Medium, Low
- Include AI-assisted remediation time estimates (not manual development time)
- Include a Modernization Score (0-100)
- Include the phased Modernization Roadmap
- Once the report is saved, tell the user its path, the Modernization Score and the number of findings at each severity

---

# Modernization Audit Skill

This skill provides comprehensive expertise for identifying technical debt, anti-patterns, and quality issues introduced by older AI code generation models, legacy development practices, or "vibe coding" sessions. It produces structured assessment reports with prioritized findings and AI-assisted remediation estimates.

## When to Use This Skill

Invoke this skill when:
- Assessing a codebase built with older AI tools (Claude 3-era models, early Cursor, GPT-4 2024)
- Evaluating technical debt before a modernization effort
- Reviewing a "vibe-coded" project for production readiness
- Auditing code quality against SOLID, DRY, KISS, and YAGNI principles
- Identifying security, performance, and architecture issues in inherited codebases
- Planning a refactoring or modernization roadmap with AI-assisted time estimates
- Checking one file or directory quickly, without the setup questions (`--defaults`)

## Background: Why Older AI-Generated Code Needs Assessment

AI code generation models have improved dramatically between 2024 and 2026. Codebases built with earlier models commonly exhibit patterns that newer models handle correctly:

### Evolution of AI Code Generation Quality

**2024 Era (Claude 3-era models, early GPT-4, Cursor pre-2025):**
- Models often produced code that "worked" but violated fundamental engineering principles
- Limited understanding of project-wide architecture and cross-file consistency
- Tendency to generate verbose, repetitive code rather than DRY abstractions
- Weak security awareness, frequently omitting input validation and sanitization
- Over-reliance on copy-paste patterns rather than identifying reusable components
- Generated plausible-looking but non-existent API calls and package names
- Inconsistent error handling, often mixing strategies within the same file
- Poor TypeScript usage with excessive `any` types and type assertions
- Generated tests that tested implementation details rather than behavior

**2025-2026 Era (Claude Opus 4/4.6, Sonnet 4/4.6, modern tooling):**
- Strong adherence to SOLID principles with appropriate abstraction levels
- Consistent architecture patterns across entire codebases
- Security-first approach with proper input validation, parameterized queries, and CORS
- Effective use of type systems with narrow types, discriminated unions, and type guards
- Behavioral testing with meaningful edge case coverage
- Proper async patterns, error boundaries, and graceful degradation
- Awareness of modern APIs, deprecations, and current best practices

## Core Assessment Categories

The audit covers 12 categories. The numbers are the ones `categories=` accepts:

1. SOLID/DRY/KISS Violations
2. Type Safety & Language Misuse
3. Error Handling
4. Security Anti-patterns
5. Performance Anti-patterns
6. Testing Gaps
7. Architecture Debt
8. Frontend Debt
9. Dependency Health
10. AI Hallucination Artifacts
11. Modern Pattern Gaps
12. Configuration & DevOps Debt

For what to check in each category, read [references/categories.md](references/categories.md).

## Code Context Accuracy (CRITICAL)

**You MUST be 100% factually accurate with Code Context. Never include irrelevant or placeholder code.**

### When to INCLUDE Code Context:
- You can identify the EXACT code causing the issue
- The code snippet directly demonstrates the problem
- You are confident the code is the actual source of the issue

### When to OMIT Code Context entirely:
- **Truly missing elements**: If something doesn't exist AT ALL, there is no code to show
- **Uncertainty**: Not 100% certain the code snippet is correct; omit rather than guess

When omitting Code Context, write: "**Code Context**: N/A - [brief reason]"

**NEVER**: Pick random code, show unrelated snippets, guess at code, or use generic placeholders.

## Specificity Requirements (CRITICAL)

**When an issue affects multiple locations, enumerate them specifically:**

### Location Field:
- BAD: "Various files throughout the project"
- GOOD: "`src/services/userService.ts:45-78`, `src/services/orderService.ts:23-56`, `src/services/paymentService.ts:12-34`"

### Code Context Field:
- Show ALL affected code (or first 3-5 instances if many), using actual code from the source

### Remediation Field:
- BAD: Generic advice like "refactor this code to follow SOLID principles"
- GOOD: Specific before/after code examples using actual code from the codebase

## Audit Methodology

When conducting modernization assessments, follow this systematic approach:

### Step 1: Pre-Audit Configuration

Use the configuration settled in the Instructions above, from the arguments, the user's answers or the defaults:

1. **AI Tool History**: Which tools/models generated the code and when
2. **Technology Stack**: Confirmed tech stack
3. **Assessment Categories**: Selected categories or "all"
4. **Scope**: Entire codebase, or a specific file or directory (with path)
5. **Severity Threshold**: All, Medium+, or High/Critical only

### Step 2: Codebase Discovery

Before analyzing code, establish the project landscape:

1. **Map the project structure**: Use Glob to understand directory organization
2. **Read project configuration**: package.json, tsconfig.json, .csproj, etc.
3. **Identify entry points**: main files, route definitions, app bootstrapping
4. **Check for existing quality tooling**: ESLint config, Prettier, test configuration, CI/CD files
5. **Review dependency manifest**: Identify the dependency tree and versions

### Step 3: Category-by-Category Analysis

For each selected assessment category:

1. **Scan for patterns**: Use Grep and Read to identify specific anti-patterns
2. **Verify findings**: Read the actual code context to confirm each finding
3. **Assess severity**: Score each finding based on impact, blast radius, and fix complexity
4. **Document remediation**: Provide specific before/after code examples
5. **Estimate AI-assisted fix time**: Estimate how long an AI-assisted developer would take to fix each issue

### Step 4: Report Generation

Generate the report using the template below. Save to `docs/modernize/{timestamp}-modernize-audit.md`.

## Report Output Format

### Location and Naming
- **Directory**: `docs/modernize/`
- **Filename**: `YYYY-MM-DD-HHMMSS-modernize-audit.md`
- **Example**: `2026-03-22-143022-modernize-audit.md`

### Report Template

**CRITICAL INSTRUCTION - READ CAREFULLY**

The report MUST start DIRECTLY with "## Modernization Assessment:" followed by the project name - do NOT include any preamble, introduction, or explanatory text before the report.

You MUST use the exact template structure provided. This is MANDATORY and NON-NEGOTIABLE.

**REQUIREMENTS:**
1. Use the COMPLETE template structure - ALL sections are REQUIRED
2. Follow the EXACT heading hierarchy (##, ###, ####)
3. Include ALL section headings as written in the template
4. Use the finding numbering format: M-001, M-002, M-003 (not 1, 2, 3)
5. Include code examples with proper syntax highlighting
6. Write a compelling narrative intro paragraph (see guidelines below)
7. DO NOT create your own format or structure
8. DO NOT skip or combine sections
9. DO NOT create abbreviated or simplified versions
10. ALL time estimates MUST assume AI-assisted development (not manual human effort)

If you do not follow this template exactly, the assessment will be rejected.

## Report Title & Introduction Guidelines

**Extracting Project Name:**
- Use the name from package.json, .csproj, or directory name
- For monorepos, identify the primary project or use the repository name

**Narrative Introduction:**
Write 2-4 sentences characterizing the overall modernization state, highlighting the most impactful findings, estimating total remediation effort (AI-assisted), and setting expectations for the report.

<template>
## Modernization Assessment: [Project Name]

*Assessed on [DATE] - [TECH STACK] - AI Origin: [AI TOOLS/ERA]*

[Write 2-4 sentences summarizing the overall modernization state. Characterize the severity of technical debt. Highlight the most impactful categories of issues found. Estimate total AI-assisted remediation effort.]

---

**At a Glance**: [X] issues found - [X] critical - [X] high - [X] medium - [X] low

**Modernization Score**: [X]/100 | **AI-Assisted Remediation Estimate**: [X] hours total

---

## Audit Configuration

| Setting | Value |
|---------|-------|
| AI Tools Used | [Tools and era from user input] |
| Codebase Era | [When the code was written] |
| Technology Stack | [Confirmed tech stack] |
| Categories Assessed | [List of selected categories, with any skipped as not applicable] |
| Scope | [Entire solution, or the file or directory path] |
| Severity Threshold | [All / Medium+ / High-Critical] |
| Analysis Date | [Current date and time] |

---

## Assessment Findings

### Critical Severity Findings

#### M-001: [Finding Title]

- **Category**: [Assessment category name]
- **Location**: [Exact file paths with line numbers]
- **Severity**: Critical
- **Pattern Detected**: [Brief description of the anti-pattern found]
- **Principle Violated**: [SOLID principle, DRY, KISS, YAGNI, or specific best practice]
- **Code Context**:
```[language]
[Actual code snippet from the source]
```
- **Impact**: [Technical impact and downstream consequences]
- **Why Older AI Models Did This**: [Brief explanation of why older models generated this pattern]
- **Recommendation**: [Specific fix guidance]
- **AI-Assisted Fix Estimate**: [Time estimate assuming AI-assisted development]
- **Fix Priority**: Immediate

**Remediation**:

```[language]
[Corrected code example using actual elements from the source]
```

#### M-002: [Finding Title]

[Same format as above...]

[Continue for all critical findings...]

### High Severity Findings

#### M-00X: [Finding Title]

[Use same finding format as above]

[Continue for all high findings...]

### Medium Severity Findings

#### M-00X: [Finding Title]

[Use same finding format as above]

[Continue for all medium findings...]

### Low Severity Findings

#### M-00X: [Finding Title]

[Use same finding format as above]

[Continue for all low findings...]

---

## Category Summary

### Assessment by Category

| Category | Findings | Critical | High | Medium | Low | AI-Assisted Fix Estimate |
|----------|----------|----------|------|--------|-----|--------------------------|
| SOLID/DRY/KISS Violations | X | X | X | X | X | Xh |
| Type Safety & Language Misuse | X | X | X | X | X | Xh |
| Error Handling | X | X | X | X | X | Xh |
| Security Anti-patterns | X | X | X | X | X | Xh |
| Performance Anti-patterns | X | X | X | X | X | Xh |
| Testing Gaps | X | X | X | X | X | Xh |
| Architecture Debt | X | X | X | X | X | Xh |
| Frontend Debt | X | X | X | X | X | Xh |
| Dependency Health | X | X | X | X | X | Xh |
| AI Hallucination Artifacts | X | X | X | X | X | Xh |
| Modern Pattern Gaps | X | X | X | X | X | Xh |
| Configuration & DevOps Debt | X | X | X | X | X | Xh |
| **Total** | **X** | **X** | **X** | **X** | **X** | **Xh** |

[Only include rows for categories that were assessed. Leave out categories skipped as not applicable.]

---

## Modernization Score Breakdown

### Scoring Methodology

The Modernization Score (0-100) is calculated across the assessed categories. Each category is weighted equally among those assessed. A score of 100 means no issues found; each finding reduces the score based on severity.

| Category | Score | Weight | Notes |
|----------|-------|--------|-------|
| [Category 1] | X/100 | [Weight]% | [Brief assessment] |
| [Category 2] | X/100 | [Weight]% | [Brief assessment] |
| [Continue for all assessed categories...] | | | |
| **Overall** | **X/100** | **100%** | |

### Score Interpretation

| Score Range | Assessment | Recommendation |
|-------------|------------|----------------|
| 90-100 | Excellent | Minor improvements only, production-ready |
| 75-89 | Good | Some modernization recommended, functional |
| 50-74 | Fair | Significant modernization needed before scaling |
| 25-49 | Poor | Major refactoring required, high technical debt |
| 0-24 | Critical | Fundamental issues, consider partial rewrite |

---

## Technical Recommendations

### Immediate Fixes (Critical Priority)

1. [Reference finding M-00X and specific fix]
2. [Reference finding M-00X and specific fix]
3. [Continue as needed...]

### High Priority Improvements

1. [Reference finding M-00X and specific fix]
2. [Reference finding M-00X and specific fix]
3. [Continue as needed...]

### Medium Priority Modernization

1. [Reference finding M-00X and specific fix]
2. [Reference finding M-00X and specific fix]
3. [Continue as needed...]

---

## Code Remediation Examples

[Include 3-5 before/after examples using the project's actual technology stack and real code from findings. Each example should show:]

### [Descriptive Title] (references M-XXX)

**Before (Current)**:

```[language]
[Actual code from the codebase showing the problem]
```

**After (Modernized)**:

```[language]
[Corrected version with modern patterns applied]
```

**Improvement**: [What principle/pattern this fixes and why it matters]
**AI-Assisted Fix Time**: [Estimate]

---

## Modernization Roadmap

### Phase 1: Critical Fixes (AI-Assisted Estimate: Xh)

- [ ] [Fix referencing finding M-00X]
- [ ] [Fix referencing finding M-00X]
- [ ] [Continue as needed...]

**Expected Impact**: Eliminate critical security risks and blocking issues

### Phase 2: High Priority Modernization (AI-Assisted Estimate: Xh)

- [ ] [Fix referencing high-severity findings]
- [ ] [Fix referencing high-severity findings]
- [ ] [Continue as needed...]

**Expected Impact**: Significant code quality and maintainability improvements

### Phase 3: Architecture & Pattern Modernization (AI-Assisted Estimate: Xh)

- [ ] [Fix referencing medium-severity findings]
- [ ] [Fix referencing medium-severity findings]
- [ ] [Continue as needed...]

**Expected Impact**: Modern architecture patterns, improved developer experience

### Phase 4: Polish & Best Practices (AI-Assisted Estimate: Xh)

- [ ] [Low-severity improvements]
- [ ] [Modern pattern adoption]
- [ ] [Dependency updates and cleanup]

**Expected Impact**: Production-grade code quality, fully modernized codebase

---

## AI-Assisted Remediation Summary

### Total Effort Estimate

| Phase | Findings | AI-Assisted Estimate | Priority |
|-------|----------|---------------------|----------|
| Phase 1: Critical Fixes | X findings | Xh | Immediate |
| Phase 2: High Priority | X findings | Xh | Within 1 week |
| Phase 3: Architecture | X findings | Xh | Within 1 month |
| Phase 4: Polish | X findings | Xh | Within 2 months |
| **Total** | **X findings** | **Xh** | |

*All estimates assume AI-assisted development using current frontier models. Actual time may vary based on codebase complexity, testing requirements, and developer familiarity.*

---

## Summary

This modernization assessment identified **X critical**, **Y high**, **Z medium**, and **W low** severity issues across the codebase. The assessment focused on [list of assessed categories].

**Key Strengths Identified**:

[List actual strengths found during the assessment]

**Critical Areas Requiring Immediate Attention**:

[List the most impactful issues found, referencing finding IDs]

**Overall Assessment**:

- **Modernization Score**: X/100
- **Critical Issues**: X findings requiring immediate attention
- **Total AI-Assisted Remediation Estimate**: Xh
- **Recommendation**: [Prioritized next steps referencing roadmap phases]
</template>

## Severity Assessment Framework

When determining finding severity, apply these criteria:

- **CRITICAL**: Causes security vulnerabilities, data loss, or application crashes. Includes hardcoded secrets, SQL injection, missing authentication, unhandled errors that crash the process, or completely broken functionality.
- **HIGH**: Significantly degrades code quality, maintainability, or performance. Includes God classes, N+1 queries, missing type safety on critical paths, no error handling on external calls, or architectural patterns that prevent scaling.
- **MEDIUM**: Measurable code quality issues that affect developer productivity or could become problems at scale. Includes DRY violations, inconsistent patterns, missing tests for important flows, or outdated syntax.
- **LOW**: Best practice improvements and modernization opportunities. Includes adopting newer syntax, minor performance tweaks, code organization improvements, or documentation gaps.

## AI-Assisted Time Estimation Guidelines

All time estimates MUST assume AI-assisted development (using current frontier models). Guidelines:

| Task Type | Manual Estimate | AI-Assisted Estimate | Speedup |
|-----------|----------------|---------------------|---------|
| Simple refactor (rename, extract function) | 15-30 min | 2-5 min | 5-6x |
| Add input validation to an endpoint | 30-60 min | 5-10 min | 5-6x |
| Fix N+1 query with eager loading | 30-60 min | 5-15 min | 4-5x |
| Add comprehensive error handling to a module | 1-2 hours | 10-20 min | 5-6x |
| Extract service layer from route handlers | 2-4 hours | 20-45 min | 5-6x |
| Add TypeScript types to untyped module | 1-3 hours | 15-30 min | 4-6x |
| Write integration tests for an API endpoint | 1-2 hours | 15-30 min | 4-5x |
| Refactor component to modern patterns | 1-2 hours | 10-25 min | 4-6x |
| Security hardening (headers, CORS, cookies) | 2-4 hours | 20-40 min | 5-6x |
| Dependency updates with breaking changes | 2-8 hours | 30-90 min | 4-5x |

Use these as guidelines, adjusting for the specific complexity of each finding.

## Best Practices

1. **Prioritize by Business Impact**: Focus on findings that affect users, security, or core functionality first. Cosmetic issues and style preferences should be low priority.

2. **Consider Context**: A "violation" in a prototype or MVP might be acceptable. A violation in production code handling payments or user data is critical.

3. **Acknowledge Good Code**: Recognize properly implemented patterns to reinforce positive development practices and provide a balanced assessment.

4. **Be Specific and Actionable**: Every finding should include enough detail for a developer (with AI assistance) to locate and fix the issue without additional research.

5. **Respect the Era**: Code written with 2024-era AI tools should be assessed for modernization, not criticized. The goal is improvement, not blame.

6. **Validate Before Reporting**: Confirm that each finding is real. Read the actual code. Don't report issues based on assumptions about what the code might contain.

## Quality Assurance Checklist

Before finalizing a modernization assessment, verify:

- Have all selected categories been systematically analyzed?
- Are all findings verified against actual source code (not assumptions)?
- Do all findings include exact file paths and line numbers?
- Are before/after code examples using actual code from the codebase?
- Are AI-assisted time estimates realistic and consistent?
- Is the Modernization Score calculation transparent and defensible?
- Does the roadmap follow a logical progression from critical to low priority?
- Have existing strengths been acknowledged?
- Are remediation examples practical and implementable?

## Context-Aware Analysis

When project-specific context is available in CLAUDE.md or AGENTS.md files or other project documentation, incorporate:

- **Technology Stack**: Identify framework-specific anti-patterns and modernization opportunities
- **Project Maturity**: Adjust severity based on whether this is a prototype, MVP, or production system
- **Team Context**: Consider the development team's experience level and modernization capacity
- **Business Constraints**: Factor in deployment schedules, compliance requirements, and resource availability

## Communication Guidelines

When reporting modernization findings:

- Be constructive and forward-looking, not critical of past decisions or AI tool choices
- Frame findings as "modernization opportunities" rather than "mistakes"
- Acknowledge that older AI tools were state-of-the-art at the time they were used
- Provide clear, actionable remediation paths with realistic AI-assisted time estimates
- Use the "Why Older AI Models Did This" field to educate, not blame
- Celebrate existing strengths and well-implemented patterns
