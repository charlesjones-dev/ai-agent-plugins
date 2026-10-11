# Azure DevOps Work Item Guidelines

`/ado-create` reads this file before it drafts or formats a work item. It covers the Feature, User Story and Task hierarchy, HTML formatting, acceptance criteria, Story Points, hour estimation, naming conventions and default field values. The project's CLAUDE.md, written by `/ado-init`, supplies the organization, project, team, Area Path, Iteration Path and naming convention.

## Work Item Hierarchy

Azure DevOps uses a three-level structure for Agile projects:

1. **Features** (top level) - High-level capabilities or business objectives
2. **User Stories** (child of Features) - Specific functionality from a user perspective
3. **Tasks** (child of User Stories) - Individual work items for implementation

**Key Rules:**
- Every User Story must belong to a Feature (parent-child relationship)
- Every Task must belong to a User Story (parent-child relationship)
- Features contain one or more User Stories
- User Stories contain one or more Tasks

## HTML Formatting Requirement

**CRITICAL:** All text fields (Description, Acceptance Criteria) must use proper HTML formatting for correct rendering in Azure DevOps.

**Examples:**

```html
<!-- Good: Proper HTML -->
<p>As a developer, I need to implement user authentication.</p>
<p><strong>Background:</strong></p>
<ul>
  <li>Current system has no authentication</li>
  <li>Users need secure login</li>
</ul>

<!-- Bad: Plain text -->
As a developer, I need to implement user authentication.

Background:
- Current system has no authentication
- Users need secure login
```

**HTML Formatting Guidelines:**
- Use `<p>` tags for paragraphs
- Use `<ul>` and `<li>` for bullet lists
- Use `<ol>` and `<li>` for numbered lists
- Use `<strong>` for bold text
- Use `<em>` for italic text
- Use `<h3>`, `<h4>` for section headers (if needed)

## Feature Requirements

**Purpose:** High-level business capability or objective containing related User Stories.

**Description Field:**
- Provide a simple, high-level summary of the feature
- Explain the business value or objective
- Avoid fine implementation details (those belong in User Stories)
- Use HTML formatting with `<p>` tags and lists

**Example Feature:**
```
Title: 1: User Authentication System
Description:
<p>Implement a complete user authentication system with login, registration, and password reset capabilities.</p>
<p><strong>Business Value:</strong></p>
<ul>
  <li>Enable secure access to the application</li>
  <li>Support personalized user experiences</li>
  <li>Meet security compliance requirements</li>
</ul>
```

**Field Settings:**
- Area Path: Set to appropriate team area
- Iteration Path: Set to target sprint/iteration
- State: "New" (default for new work items)
- Assigned To: Leave unassigned (team members assign themselves)

## User Story Requirements

**Purpose:** Specific functionality described from a user perspective, containing implementation Tasks.

### Structure

- Each User Story belongs to exactly one parent Feature
- Each User Story contains one or more child Tasks
- User Stories remain unassigned until team members pick them up

### Description Field Format

Use HTML formatting with this structure:

```html
<p><strong>As a</strong> [user persona], <strong>I want to</strong> [capability], <strong>so that</strong> [benefit].</p>

<p><strong>Background:</strong></p>
<ul>
  <li>[Context point 1]</li>
  <li>[Context point 2]</li>
  <li>[Context point 3]</li>
</ul>

<p><strong>Additional Information:</strong></p>
<ul>
  <li>[Implementation detail 1]</li>
  <li>[Implementation detail 2]</li>
</ul>
```

**Example:**
```html
<p><strong>As a</strong> website visitor, <strong>I want to</strong> register for an account, <strong>so that</strong> I can access personalized features.</p>

<p><strong>Background:</strong></p>
<ul>
  <li>Current system has no user accounts</li>
  <li>Marketing team requires user tracking</li>
  <li>Future features depend on user identity</li>
</ul>

<p><strong>Additional Information:</strong></p>
<ul>
  <li>Email should be the unique identifier</li>
  <li>Password strength validation required</li>
  <li>Email verification recommended but not required for MVP</li>
</ul>
```

### Acceptance Criteria Format

Use the "Given, When, Then" format with HTML:

```html
<p><strong>Scenario 1: Successful Registration</strong></p>
<ul>
  <li><strong>Given</strong> I am on the registration page</li>
  <li><strong>When</strong> I enter valid email and password</li>
  <li><strong>Then</strong> my account is created and I am logged in</li>
</ul>

<p><strong>Scenario 2: Invalid Email</strong></p>
<ul>
  <li><strong>Given</strong> I am on the registration page</li>
  <li><strong>When</strong> I enter an invalid email format</li>
  <li><strong>Then</strong> I see an error message and cannot submit</li>
</ul>
```

**Guidelines:**
- Keep criteria concise and testable
- Focus on observable behavior, not implementation
- Use bullet points for readability
- Structure for QA testers to execute

### Story Points

Apply Fibonacci sequence values to the "Story Points" field to estimate relative complexity:

- **1** - Trivial change, very well understood
- **2** - Simple change, clear requirements
- **3** - Moderate complexity, some uncertainty
- **5** - Complex change, multiple components
- **8** - Very complex, significant uncertainty
- **13** - Epic-level work (consider breaking down)

**Field Settings:**
- Area Path: Set to appropriate team area
- Iteration Path: Set to target sprint/iteration
- State: "New"
- Assigned To: Leave unassigned
- Story Points: Fibonacci value (1, 2, 3, 5, 8, 13)

## Task Requirements

**Purpose:** Lightweight work tracking items representing individual implementation activities.

### Structure

- Each Task belongs to exactly one parent User Story
- Tasks do NOT get a detailed Description or Acceptance Criteria. Their description is one line pointing to the parent User Story: `<p>Task for [STORY_TITLE]. See parent User Story for details.</p>`
- Tasks reference the parent User Story for all context
- Tasks remain unassigned until developers pick them up

### Title Format

Keep Task titles simple and descriptive, focused on the work activity:

**Good Task Titles:**
- "Implement registration API endpoint"
- "Create registration form UI"
- "Write unit tests for registration flow"
- "Add email validation logic"
- "Update database schema for users table"

**Bad Task Titles:**
- "Do the registration stuff" (too vague)
- "As a user I want to register..." (that's the User Story, not a Task)
- "Registration" (not specific enough)

### Hour Estimation

Tasks are the **primary container** for hour tracking. Set both fields to the same estimated value:

- **Original Estimate**: Total hours estimated to complete the work
- **Remaining Work**: Same value as Original Estimate (initially)
- **Completed Work**: Leave empty (will be filled during work)

**Example:**
```
Original Estimate: 4
Remaining Work: 4
Completed Work: (empty)
```

**Estimation Guidelines:**
- Break tasks into 2-8 hour chunks when possible
- Tasks over 16 hours should be split into smaller tasks
- Be realistic and include testing/debugging time
- Consider code review and documentation time

**Field Settings:**
- Area Path: Inherited from parent User Story (or set explicitly)
- Iteration Path: Inherited from parent User Story (or set explicitly)
- State: "New"
- Assigned To: Leave unassigned
- Original Estimate: Hours (e.g., 4)
- Remaining Work: Same as Original Estimate

## Naming Convention Standards

Azure DevOps lacks robust priority sorting, so naming conventions ensure proper organization in the backlog.

### Features Naming

**Format:** `[NUMBER]: [DESCRIPTION]`

- Prefix with a single digit from 1-99
- Use the number to indicate priority/sequence
- Keep description concise and business-focused

**Examples:**
- "1: User Authentication System"
- "2: Product Catalog Management"
- "3: Shopping Cart and Checkout"

### User Stories Naming

There are two supported naming conventions. **Check the project's CLAUDE.md file for the configured convention, or ask which convention to use before creating User Stories**.

#### Convention 1: Decimal Notation

**Format:** `[FEATURE_NUMBER].[STORY_NUMBER]: [DESCRIPTION]`

- Use decimal notation incorporating the parent Feature number
- Stories under Feature 1 are numbered 1.1, 1.2, 1.3...
- Stories under Feature 2 are numbered 2.1, 2.2, 2.3...

**Examples:**
- "1.1: User Registration"
- "1.2: User Login"
- "1.3: Password Reset"
- "2.1: Product Listing Page"
- "2.2: Product Detail View"

**Benefits:**
- Clear parent-child relationship visible in title
- Automatic sorting keeps stories grouped by feature
- Easy to identify which feature a story belongs to

#### Convention 2: Simple Descriptive Names

**Format:** `[DESCRIPTION]`

- Use clear, descriptive titles without numbering
- Focus on the capability being delivered
- No decimal notation or prefixes

**Examples:**
- "Create user registration system"
- "Implement user login flow"
- "Add password reset functionality"
- "Build product listing page"
- "Develop product detail view"

**Benefits:**
- More flexible and natural language
- Easier to read and understand
- Less maintenance when reorganizing features

### Tasks Naming

**Format:** `[DESCRIPTION]`

- Always use simple, descriptive titles without numbering
- Focus on the implementation activity
- Keep concise and action-oriented

**Examples:**
- "Implement user registration API endpoint"
- "Create login UI components"
- "Write authentication unit tests"
- "Design product listing page layout"
- "Add product search functionality"

## Default Field Values

When creating work items, apply these defaults unless explicitly specified otherwise:

**All Work Item Types:**
- **State:** "New"
- **Assigned To:** Unassigned (leave blank)

**Project-Specific Values:**
These are typically configured in the project's CLAUDE.md file:
- **Organization:** (from configuration)
- **Project:** (from configuration)
- **Team:** (from configuration)
- **Area Path:** (from configuration, e.g., "ProjectName\\Team\\TeamName")
- **Iteration Path:** (from configuration, e.g., "ProjectName\\Sprint 1")

## Best Practices

1. **Check Configuration First:** Before creating work items, check if the project has Azure DevOps configuration in CLAUDE.md that specifies organization, project, team, area path, iteration path, and naming convention preferences.

2. **Always Use HTML:** Never use plain text or markdown in Description or Acceptance Criteria fields - always use proper HTML formatting.

3. **Maintain Hierarchy:** Never create orphaned work items. Every User Story needs a parent Feature, every Task needs a parent User Story.

4. **Check Naming Convention:** If not specified in CLAUDE.md, ask which naming convention is preferred (decimal notation like 1.1, 1.2 or simple descriptive names) before creating User Stories.

5. **Keep Tasks Lightweight:** Tasks should not duplicate the User Story's description or acceptance criteria. They should be simple work containers with just a title and hour estimates.

6. **Leave Assignments Blank:** Let team members assign themselves to work items during sprint planning or daily standups.

7. **Estimate Realistically:** Include time for testing, code review, documentation, and debugging in task hour estimates.

8. **Use Story Points Consistently:** Apply Fibonacci sequence values to User Stories based on relative complexity, not absolute time.

9. **Progressive Disclosure:** Create Features first, then User Stories, then Tasks. This allows for iterative refinement of scope and estimation.

10. **Validate Before Creating:** Review the work item hierarchy and ensure all required fields are populated before calling MCP tools to create items.

## Common Patterns

### Pattern: Creating a Complete Feature with Stories and Tasks

When asked to create a new feature with full breakdown:

1. **Create the Feature** with high-level description
2. **Create User Stories** as children of the Feature with proper descriptions and acceptance criteria
3. **Create Tasks** as children of each User Story with hour estimates
4. **Review the hierarchy** to ensure proper parent-child relationships
5. **Confirm total estimated hours** across all tasks align with story points

### Pattern: Adding Tasks to Existing User Story

When asked to add tasks to an existing story:

1. **Fetch the User Story** to understand context
2. **Review existing tasks** to avoid duplication
3. **Create new Tasks** with appropriate titles and hour estimates
4. **Link Tasks to the User Story** as parent

### Pattern: Breaking Down a Large User Story

When a User Story is too large (Story Points 13+):

1. **Review the original User Story** description and acceptance criteria
2. **Identify natural breakpoints** in functionality
3. **Create multiple smaller User Stories** under the same Feature
4. **Distribute acceptance criteria** across the new stories
5. **Update or close the original story** as appropriate
6. **Create Tasks** for each new User Story

## Example Work Item Hierarchy

```
Feature: 1: User Authentication System
  Description: <p>Implement complete user authentication...</p>

  User Story: 1.1: User Registration
    Description: <p><strong>As a</strong> website visitor...</p>
    Acceptance Criteria: <p><strong>Scenario 1...</strong></p>
    Story Points: 5

    Task: Implement registration API endpoint
      Original Estimate: 4
      Remaining Work: 4

    Task: Create registration form UI
      Original Estimate: 3
      Remaining Work: 3

    Task: Write unit tests for registration
      Original Estimate: 2
      Remaining Work: 2

  User Story: 1.2: User Login
    Description: <p><strong>As a</strong> registered user...</p>
    Acceptance Criteria: <p><strong>Scenario 1...</strong></p>
    Story Points: 3

    Task: Implement login API endpoint
      Original Estimate: 3
      Remaining Work: 3

    Task: Create login form UI
      Original Estimate: 2
      Remaining Work: 2
```

## Troubleshooting

**Problem:** Work items not appearing in the correct order in backlog

**Solution:** Ensure Features are numbered 1-99, and User Stories follow the configured naming convention (decimal notation or descriptive names).

**Problem:** Acceptance criteria rendering incorrectly in Azure DevOps

**Solution:** Verify all text fields use proper HTML formatting with `<p>`, `<ul>`, `<li>` tags.

**Problem:** Tasks showing as orphaned in queries

**Solution:** Verify each Task has a parent User Story link set correctly when created.

**Problem:** Story Points not summing correctly at Feature level

**Solution:** Ensure Story Points are only set on User Stories, not on Features or Tasks.
