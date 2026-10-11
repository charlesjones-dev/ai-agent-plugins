---
name: ado-create
description: "Create a Feature, User Story or Task in Azure DevOps with the project's configured conventions. Stories go under a Feature and Tasks under a User Story."
argument-hint: "[feature|story|task] [parent ID] [title]"
disable-model-invocation: true
---

# Create Azure DevOps Work Item

Interactively create a Feature, User Story or Task work item in Azure DevOps using the organization's configured conventions and guidelines. A User Story is created as a child of an existing Feature, and a Task as a child of an existing User Story.

## Instructions

**BEFORE DOING ANYTHING ELSE**: Read the arguments, validate the Azure DevOps configuration in CLAUDE.md (Phase 1), then gather whatever the arguments didn't supply. Don't skip Phase 1 even when the arguments cover the type, parent and title.

### Arguments

Arguments: $ARGUMENTS

Claude Code replaces the placeholder on the line above with the text typed after the command, and leaves the line empty when there is none.

Read the arguments in this order. Every part is optional, and anything left out is asked for later.

1. **Type** (first word): `feature`, `story` (also `user-story` or `user story`) or `task`, in any letter case.
2. **Parent ID** (story and task only): the next word, when it is a whole number, with or without a leading `#` (`1234` or `#1234`). For a story it's the parent Feature's ID. For a task it's the parent User Story's ID.
3. **Title**: all remaining text, with surrounding quotes removed.

Examples:

- `/ado-create` asks for the type, then everything else.
- `/ado-create feature` creates a Feature and asks for its fields.
- `/ado-create story 1234` creates a User Story under Feature 1234 and asks for its fields.
- `/ado-create task 5678 "Write unit tests for registration"` creates a Task under User Story 5678 with that title and asks only for the hour estimate.

Rules:

- A Feature has no parent, so for a feature all text after the type is the title.
- If the arguments don't start with a type, ask for the type (Phase 2, Step 1), then read the rest of the arguments as the parent ID and title for the chosen type.
- A parent ID or title from the arguments is not asked for again, but it is validated the same way as a typed answer: the parent ID must be a valid number and the title must not be empty. If one fails, ask for it with the normal question.
- Never take a description, persona statement, background, acceptance criteria, Story Points or hour estimate from the arguments. Ask for those as described below.

### Phase 1: Validate Azure DevOps Configuration

Before proceeding with work item creation, verify that Azure DevOps configuration exists:

1. Use the **Read tool** to read `CLAUDE.md` from the project root
2. If the file doesn't exist OR doesn't contain an "## Azure DevOps" section:
   - Display the following error message:
     ```
     ❌ Azure DevOps configuration not found

     CLAUDE.md does not contain Azure DevOps configuration.

     Please run /ado-init first to configure Azure DevOps settings for this project.

     The /ado-init command will:
     - Configure your organization, project, and team
     - Set up Area Path and Iteration Path defaults
     - Define naming conventions and work item guidelines
     - Optionally configure the Azure DevOps MCP server
     ```
   - **STOP** and do not proceed further

3. If the Azure DevOps section exists, extract these values from it. `/ado-init` has written the section in two formats, so accept either:
   - **Current format**, one line per value: `**Organization:**`, `**Project:**`, `**Team:**`, `**Area Path:**`, `**Iteration Path:**` and `**Naming Convention:**`, each followed by its value
   - **Older format**, one sentence: the organization is the text after 'specify the organization as "', the project after 'the project as "', the team after 'the team as "', the Area Path after 'Area Path" set to "' and the Iteration Path after 'Iteration Path" set to "'
   - **Naming convention**: decimal notation when the Naming Convention value starts with "Decimal notation", or when the section says User Stories use decimal notation (1.1, 1.2, 2.1). Simple descriptive names when the value starts with "Simple descriptive names", or when the section says User Stories use descriptive titles without decimal notation. If neither appears, ask which convention to use before you suggest or generate a User Story title.
   - Store these values for use in work item creation

4. Use the **Read tool** to read [references/work-items.md](references/work-items.md) from this skill's folder. It holds the work item guidelines: hierarchy, HTML formatting, Description and Acceptance Criteria templates, Story Points, hour estimation, naming conventions and default field values. Follow it whenever you draft or format a field.

5. Proceed to Phase 2

**IMPORTANT**:
- Use **Read tool** to check CLAUDE.md - DO NOT use bash commands
- The entire command should STOP if Azure DevOps configuration is not found
- Do not prompt the user for configuration values - they must run /ado-init first (the naming convention question above is the only exception)

### Phase 2: Choose the Type and Parent

**Step 1 - Work Item Type** (skip when the arguments gave the type):

Simply output the following text as your response message and STOP (DO NOT call any tools):

"What type of work item would you like to create?

- feature: a top-level Feature
- story: a User Story under an existing Feature
- task: a Task under an existing User Story

Please respond with 'feature', 'story' or 'task'."

Wait for the user's response before proceeding. For a Feature, skip to Phase 3.

**Step 2 - Parent ID** (story and task only; skip when the arguments gave a valid one):

For a **User Story**, simply output the following text as your response message and STOP (DO NOT call any tools):

"What is the ID of the parent Feature for this User Story?

(This is the numeric ID of the Feature work item that will contain this story. You can find this in Azure DevOps or from the output of /ado-create feature)"

For a **Task**, simply output the following text as your response message and STOP (DO NOT call any tools):

"What is the ID of the parent User Story for this Task?

(This is the numeric ID of the User Story work item that will contain this task. You can find this in Azure DevOps or from the output of /ado-create story)"

Wait for the user's next message with the parent ID before proceeding. The parent ID must be a valid number; if it isn't, say so and ask again.

**Step 3 - Look Up the Parent** (story and task only):

Every User Story must belong to a Feature, and every Task to a User Story. Retrieve the parent with the **wit_get_work_item** MCP tool:
- `id`: The parent ID (as number, not string)
- `project`: Use the project name from Phase 1 configuration

Then:
- Store the parent's title. A User Story uses the parent Feature's title for its decimal-notation prefix. A Task uses the parent User Story's title in its description, and its description for context when drafting the title.
- If the work item isn't found, display the error, suggest creating the parent first (/ado-create feature for a story, /ado-create story for a task), and ask for the parent ID again.
- If its type (`System.WorkItemType`) isn't the expected parent type (Feature for a story, User Story for a task), output the following and STOP:

  "Work item [ID] is a [ACTUAL_TYPE], not a [EXPECTED_TYPE]. Every [User Story needs a parent Feature | Task needs a parent User Story].

  Type a different ID, or 'continue' to use [ID] anyway."

  Wait for the response. Look up a new ID the same way, or proceed with this one if the user says 'continue'.

### Phase 3: Gather Work Item Information

Collect the details for the chosen type. The user can choose between AI generation or manual input.

**Step 0 - Choose Input Method:**

Skip this step for a **Task** whose title came from the arguments: a Task's only drafted field is its title, so go straight to the hour estimate (Task, Step 2).

Otherwise, simply output the text for the chosen type as your response message and STOP (DO NOT call any tools).

For a **Feature**:

"Would you like to use AI to generate the Feature details, or provide them manually?

Options:
1. AI: Provide a description and let AI generate the title and description
2. Manual: Provide title and description yourself

Please respond with 'AI' or 'Manual'."

For a **User Story**:

"Would you like to use AI to generate the User Story details, or provide them manually?

Options:
1. AI: Provide a description and let AI generate the title, persona statement, background, and acceptance criteria
2. Manual: Provide each field yourself

Please respond with 'AI' or 'Manual'."

For a **Task**:

"Would you like to use AI to generate the Task title, or provide it manually?

Options:
1. AI: Provide a description and let AI generate an appropriate task title
2. Manual: Provide the task title yourself

Please respond with 'AI' or 'Manual'."

Wait for the user's response, then follow the section for the chosen type. When the title came from the arguments, use it as the title: in AI mode don't generate or confirm a title, and in Manual mode skip the title question.

#### Feature

**If user chooses 'AI' (or similar affirmative response):**

**Step AI-1 - Get Description Prompt:**

Simply output the following text as your response message and STOP:

"Please provide a description or overview of what this Feature should accomplish. I'll use this to generate a title and detailed description.

(Provide as much context as you'd like - the more detail you provide, the better the generated content will be.)"

Wait for the user's description, then:

1. Analyze the naming convention from Phase 1 configuration
2. Generate a Feature title following the naming convention (e.g., "1: Feature Name" for decimal notation)
3. Generate a feature description that:
   - Summarizes the feature's purpose
   - Describes what user stories it will contain
   - Provides an overview without excessive fine details
   - Is clear and suitable for stakeholders

**Step AI-2 - Confirm Generated Title:**

Display the generated title and ask for confirmation:

"I've generated the following title based on your description:

**Title:** [GENERATED_TITLE]

Would you like to use this title, or would you prefer to provide your own?
(Type 'yes' to use this title, or provide an alternative title)"

Wait for response:
- If user approves (says "yes", "ok", "looks good", etc.), store the generated title
- If user provides alternative text, use that as the title instead

**Step AI-3 - Confirm Generated Description:**

Display the generated description and ask for confirmation:

"I've generated the following description:

**Description:**
[GENERATED_DESCRIPTION]

Would you like to use this description, or would you prefer to provide your own?
(Type 'yes' to use this description, or provide an alternative description)"

Wait for response:
- If user approves (says "yes", "ok", "looks good", etc.), store the generated description
- If user provides alternative text, use that as the description instead

Then proceed to Phase 4 with the final values.

**If user chooses 'Manual':**

**Step 1 - Feature Title:**

Simply output the following text as your response message and STOP (DO NOT call any tools):

"What is the title for this Feature?

(Based on your naming convention, use an appropriate format. For decimal notation, use: '1: Feature Name', '2: Feature Name', etc.)"

Wait for the user's next message with the feature title before proceeding.

**Step 2 - Feature Description:**

After receiving the feature title, simply output the following text as your response message and STOP (DO NOT call any tools):

"What is the high-level description for this Feature?

(Provide a summary of the feature's purpose and the user stories it will contain. This should be an overview without fine details.)"

Wait for the user's next message with the feature description before proceeding.

#### User Story

**If user chooses 'AI' (or similar affirmative response):**

**Step AI-1 - Get Description Prompt:**

Simply output the following text as your response message and STOP:

"Please provide a description or overview of what this User Story should accomplish. I'll use this to generate a title, persona statement, background information, and acceptance criteria.

(Provide as much context as you'd like - the more detail you provide, the better the generated content will be.)"

Wait for the user's description, then:

1. Analyze the naming convention from Phase 1 configuration
2. Generate a User Story title following the naming convention (e.g., "1.1: Story Name" for decimal notation, using the parent Feature's number from its title as the prefix)
3. Generate a user persona statement in the format: "As a [role], I want to [action] so that [benefit]"
4. Generate relevant background information with technical details and constraints (formatted as bullet points)
5. Generate acceptance criteria using "Given, When, Then" format with multiple scenarios if appropriate

**Step AI-2 - Confirm Generated Title:**

Display the generated title and ask for confirmation:

"I've generated the following title based on your description:

**Title:** [GENERATED_TITLE]

Would you like to use this title, or would you prefer to provide your own?
(Type 'yes' to use this title, or provide an alternative title)"

Wait for response:
- If user approves (says "yes", "ok", "looks good", etc.), store the generated title
- If user provides alternative text, use that as the title instead

**Step AI-3 - Confirm Generated Persona Statement:**

Display the generated persona statement and ask for confirmation:

"I've generated the following user persona statement:

**Persona Statement:**
[GENERATED_PERSONA]

Would you like to use this persona statement, or would you prefer to provide your own?
(Type 'yes' to use this statement, or provide an alternative)"

Wait for response:
- If user approves, store the generated persona statement
- If user provides alternative text, use that instead

**Step AI-4 - Confirm Generated Background:**

Display the generated background and ask for confirmation:

"I've generated the following background information:

**Background:**
[GENERATED_BACKGROUND]

Would you like to use this background information, or would you prefer to provide your own?
(Type 'yes' to use this background, 'none' to skip background, or provide alternative background information)"

Wait for response:
- If user approves, store the generated background
- If user says 'none', mark background as skipped
- If user provides alternative text, use that instead

**Step AI-5 - Confirm Generated Acceptance Criteria:**

Display the generated acceptance criteria and ask for confirmation:

"I've generated the following acceptance criteria:

**Acceptance Criteria:**
[GENERATED_CRITERIA]

Would you like to use these acceptance criteria, or would you prefer to provide your own?
(Type 'yes' to use these criteria, or provide alternative acceptance criteria)"

Wait for response:
- If user approves, store the generated acceptance criteria
- If user provides alternative text, use that instead

**Step AI-6 - Story Points:**

Simply output the following text as your response message and STOP:

"What is the Story Points estimate for this User Story?

(Use Fibonacci sequence values: 1, 2, 3, 5, 8, 13, 21, etc.)"

Wait for the user's next message with story points before proceeding to Phase 4.

**If user chooses 'Manual':**

**Step 1 - Story Title:**

Simply output the following text as your response message and STOP (DO NOT call any tools):

"What is the title for this User Story?

(Based on your naming convention, use an appropriate format. For decimal notation, use: '1.1: Story Name', '2.1: Story Name', etc.)"

Wait for the user's next message with the story title before proceeding.

**Step 2 - User Persona Statement:**

After receiving the story title, simply output the following text as your response message and STOP (DO NOT call any tools):

"What is the user persona statement for this story?

(Format: 'As a [role], I want to [action] so that [benefit]'
Example: 'As a website visitor, I want to log in with my email and password so that I can access my personalized dashboard.')"

Wait for the user's next message with the persona statement before proceeding.

**Step 3 - Background Information:**

After receiving the persona statement, simply output the following text as your response message and STOP (DO NOT call any tools):

"What background information should be included for this story?

(Provide relevant context, technical details, or constraints. Use bullet points for clarity. Type 'none' to skip.)"

Wait for the user's next message with background information (or 'none') before proceeding.

**Step 4 - Acceptance Criteria:**

After receiving the background information, simply output the following text as your response message and STOP (DO NOT call any tools):

"What are the acceptance criteria for this story?

(Use 'Given, When, Then' format. Provide multiple scenarios if needed. Keep criteria concise for QA testers.
Example:
Given a registered user with valid credentials
When they enter email and password on the login page
Then they should be authenticated and redirected to dashboard)"

Wait for the user's next message with acceptance criteria before proceeding.

**Step 5 - Story Points:**

After receiving the acceptance criteria, simply output the following text as your response message and STOP (DO NOT call any tools):

"What is the Story Points estimate for this User Story?

(Use Fibonacci sequence values: 1, 2, 3, 5, 8, 13, 21, etc.)"

Wait for the user's next message with story points before proceeding.

#### Task

**If user chooses 'AI' (or similar affirmative response):**

**Step AI-1 - Get Description Prompt:**

Simply output the following text as your response message and STOP:

"Please provide a description of what this Task should accomplish. I'll use this to generate an appropriate task title.

(Describe the specific work to be done. Examples: 'implement the login API endpoint', 'test authentication flows', 'create database migration for users table')"

Wait for the user's description, then:

1. Use the parent User Story details from Phase 2 to understand context
2. Generate a Task title that is:
   - Simple and descriptive
   - Focused on the work to be done
   - Follows common patterns like: 'Development for [feature]', 'QA testing for [feature]', 'Deploy [component]'
   - Clear and actionable

**Step AI-2 - Confirm Generated Title:**

Display the generated title and ask for confirmation:

"I've generated the following title based on your description:

**Title:** [GENERATED_TITLE]

Would you like to use this title, or would you prefer to provide your own?
(Type 'yes' to use this title, or provide an alternative title)"

Wait for response:
- If user approves (says "yes", "ok", "looks good", etc.), store the generated title
- If user provides alternative text, use that as the title instead

**Step AI-3 - Hour Estimate:**

Simply output the following text as your response message and STOP:

"What is the hour estimate for this Task?

(This value will be set for both 'Original Estimate' and 'Remaining Work' fields. Provide a numeric value in hours.)"

Wait for the user's next message with the hour estimate before proceeding to Phase 4.

**If user chooses 'Manual':**

**Step 1 - Task Title:**

Simply output the following text as your response message and STOP (DO NOT call any tools):

"What is the title for this Task?

(Use a simple, descriptive title focused on the work to be done.
Examples: 'Development for user login functionality', 'QA testing for authentication', 'Deploy to staging environment')"

Wait for the user's next message with the task title before proceeding.

**Step 2 - Hour Estimate:**

After receiving the task title, simply output the following text as your response message and STOP (DO NOT call any tools):

"What is the hour estimate for this Task?

(This value will be set for both 'Original Estimate' and 'Remaining Work' fields. Provide a numeric value in hours.)"

Wait for the user's next message with the hour estimate before proceeding.

**IMPORTANT** (all types):
- Simply output the question text in your response message and STOP - do NOT call ANY tools (except the parent lookup in Phase 2 and when generating AI content)
- DO NOT use the AskUserQuestion tool for any of these steps
- After outputting each question, wait for the user's next message before proceeding
- For AI mode: Generate content based on the user's description, the naming convention and, for stories and tasks, the parent work item
- For AI mode: Always confirm generated content and allow user to override
- For AI mode: The parent ID is still required (Phase 2) before generating content for a story or task
- Validate that required fields are provided (not empty): title and description for a Feature; title, persona statement, acceptance criteria and Story Points for a User Story; title and hour estimate for a Task
- Parent Feature ID and parent User Story ID must be valid numbers
- Story Points and the hour estimate must be valid numbers

### Phase 4: Create the Work Item

Using the configuration from Phase 1 and the information from Phases 2 and 3, create the work item for the chosen type.

#### Feature

1. Format the description as HTML for proper Azure DevOps display:
   - Wrap the description in `<p>` tags
   - Convert line breaks to `<br/>` tags
   - If the description contains bullet points (lines starting with `-` or `*`), wrap them in `<ul>` and `<li>` tags

2. Use the **wit_create_work_item** MCP tool with the following parameters:
   - `project`: Use the project name from Phase 1 configuration
   - `workItemType`: "Feature"
   - `fields`: Array containing these field objects:
     - Title field: `{"name": "System.Title", "value": "[USER_PROVIDED_TITLE]"}`
     - Description field: `{"name": "System.Description", "value": "[HTML_FORMATTED_DESCRIPTION]", "format": "Html"}`
     - Area Path field: `{"name": "System.AreaPath", "value": "[AREA_PATH_FROM_CONFIG]"}`
     - Iteration Path field: `{"name": "System.IterationPath", "value": "[ITERATION_PATH_FROM_CONFIG]"}`
     - State field: `{"name": "System.State", "value": "New"}`

3. Wait for the MCP tool response

**IMPORTANT**:
- Use the exact field names shown above (e.g., "System.Title", "System.Description")
- Ensure HTML formatting is applied to the description for readability
- Use configuration values from Phase 1, not hardcoded values
- The format parameter for Description must be "Html"

#### User Story

1. Build the description in HTML format (WITHOUT acceptance criteria):
   - Start with the persona statement wrapped in `<p>` tags
   - If background information was provided (not 'none'):
     - Add a blank line and `<p><strong>Background:</strong></p>`
     - Format background as bullet list with `<ul>` and `<li>` tags
   - **DO NOT include acceptance criteria in the description** - they go in a separate field

2. Format the acceptance criteria in HTML format:
   - Use proper line breaks with `<br/>` tags or bullet list format with `<ul>` and `<li>` tags
   - This will be set in the separate Acceptance Criteria field

3. Use the **wit_add_child_work_items** MCP tool with the following parameters:
   - `parentId`: The parent feature ID (as number, not string)
   - `project`: Use the project name from Phase 1 configuration
   - `workItemType`: "User Story"
   - `items`: Array containing a single item object with:
     - `title`: User-provided title
     - `description`: HTML-formatted description from step 1 (persona + background only)
     - `format`: "Html"
     - `areaPath`: Area Path from configuration
     - `iterationPath`: Iteration Path from configuration

4. After the user story is created, use the **wit_update_work_item** MCP tool to set both Story Points AND Acceptance Criteria:
   - `id`: The ID of the newly created user story (from the response of wit_add_child_work_items)
   - `updates`: Array containing two update operations:
     - `{"op": "add", "path": "/fields/Microsoft.VSTS.Scheduling.StoryPoints", "value": "[STORY_POINTS_VALUE]"}`
     - `{"op": "add", "path": "/fields/Microsoft.VSTS.Common.AcceptanceCriteria", "value": "[HTML_FORMATTED_ACCEPTANCE_CRITERIA]"}`

5. Wait for both MCP tool responses

**IMPORTANT**:
- Use the exact field names and paths shown above
- Ensure HTML formatting is applied to both description and acceptance criteria
- **DO NOT include acceptance criteria in the description field** - use the separate AcceptanceCriteria field
- Parent ID must be converted to a number (not a string)
- Use configuration values from Phase 1, not hardcoded values
- Story Points and Acceptance Criteria must be set in a separate update operation after creation
- Both Story Points and Acceptance Criteria can be set in a single wit_update_work_item call with multiple update operations

#### Task

1. Tasks should have minimal description as per Azure DevOps conventions:
   - Use a simple description: "Task for [STORY_TITLE]. See parent User Story for details."
   - Format as HTML: `<p>Task for [STORY_TITLE]. See parent User Story for details.</p>`
   - `[STORY_TITLE]` is the parent User Story's title from the Phase 2 lookup. If you don't have it, retrieve the parent with **wit_get_work_item** (`id`: the parent story ID, `project`: the project name from Phase 1 configuration) before creating the task.

2. Use the **wit_add_child_work_items** MCP tool with the following parameters:
   - `parentId`: The parent story ID (as number, not string)
   - `project`: Use the project name from Phase 1 configuration
   - `workItemType`: "Task"
   - `items`: Array containing a single item object with:
     - `title`: User-provided title
     - `description`: HTML-formatted description referencing parent story
     - `format`: "Html"
     - `areaPath`: Area Path from configuration
     - `iterationPath`: Iteration Path from configuration

3. After the task is created, use the **wit_update_work_item** MCP tool to set hour estimates:
   - `id`: The ID of the newly created task (from the response of wit_add_child_work_items)
   - `updates`: Array containing:
     - `{"op": "add", "path": "/fields/Microsoft.VSTS.Scheduling.OriginalEstimate", "value": "[HOUR_ESTIMATE]"}`
     - `{"op": "add", "path": "/fields/Microsoft.VSTS.Scheduling.RemainingWork", "value": "[HOUR_ESTIMATE]"}`

4. Wait for all MCP tool responses

**IMPORTANT**:
- Use the exact field names and paths shown above
- Use the parent story's title in the task description
- Ensure HTML formatting is applied to the description
- Parent ID must be converted to a number (not a string)
- Use configuration values from Phase 1, not hardcoded values
- Hour estimates must be set in a separate update operation after creation
- Both Original Estimate and Remaining Work should have identical values
- DO NOT set Completed Work field (leave empty initially)

### Phase 5: Display Success Message

After the work item is created, display the success message for its type. Replace placeholders with actual values from the created work item and configuration.

#### Feature

```
✓ Feature created successfully!

Feature Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 ID: [FEATURE_ID]
📋 Title: [FEATURE_TITLE]
📂 Project: [PROJECT_NAME]
📍 Area Path: [AREA_PATH]
🔄 Iteration Path: [ITERATION_PATH]
✨ State: New
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next Steps:
1. Create User Stories under this Feature using /ado-create story
2. Review the feature in Azure DevOps web interface
3. Add additional details or attachments as needed

💡 To create a user story for this feature:
   /ado-create story [FEATURE_ID]

🔗 View in Azure DevOps:
   https://dev.azure.com/[ORGANIZATION]/[PROJECT]/_workitems/edit/[FEATURE_ID]
```

#### User Story

```
✓ User Story created successfully!

User Story Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 ID: [STORY_ID]
📋 Title: [STORY_TITLE]
👤 Parent Feature: [PARENT_FEATURE_ID]
📂 Project: [PROJECT_NAME]
📍 Area Path: [AREA_PATH]
🔄 Iteration Path: [ITERATION_PATH]
⭐ Story Points: [STORY_POINTS]
✨ State: New
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next Steps:
1. Create Task work items under this User Story using /ado-create task
2. Review the story in Azure DevOps web interface
3. Assign team members and refine estimates as needed

💡 To create a task for this story:
   /ado-create task [STORY_ID]

🔗 View in Azure DevOps:
   https://dev.azure.com/[ORGANIZATION]/[PROJECT]/_workitems/edit/[STORY_ID]
```

#### Task

```
✓ Task created successfully!

Task Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 ID: [TASK_ID]
📋 Title: [TASK_TITLE]
📖 Parent User Story: [PARENT_STORY_ID]
📂 Project: [PROJECT_NAME]
📍 Area Path: [AREA_PATH]
🔄 Iteration Path: [ITERATION_PATH]
⏱️  Original Estimate: [HOURS] hours
⏱️  Remaining Work: [HOURS] hours
✨ State: New
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next Steps:
1. Assign the task to a team member in Azure DevOps
2. Update progress and completed work as the task progresses
3. Create additional tasks for the story if needed

💡 To create another task for the same story:
   /ado-create task [PARENT_STORY_ID]

🔗 View in Azure DevOps:
   https://dev.azure.com/[ORGANIZATION]/[PROJECT]/_workitems/edit/[TASK_ID]
```

### Important Constraints

**DO NOT:**
- Proceed without Azure DevOps configuration in CLAUDE.md
- Use bash commands for file operations
- Create the work item without user-provided information
- Use placeholder or empty values
- Call tools during the question steps (questions should be simple text output), apart from the parent lookup
- Include Description or Acceptance Criteria in the work item title
- Include Acceptance Criteria in a User Story's Description field
- Add detailed Description or Acceptance Criteria to tasks (tasks should reference parent story)
- Set different values for a Task's Original Estimate and Remaining Work
- Set a Task's Completed Work field (should remain empty initially)

**DO:**
- Use **Read tool** to check CLAUDE.md for Azure DevOps configuration and to read references/work-items.md
- Simply output question text and STOP for the question steps
- Wait for user's response after each question before proceeding
- Use **wit_get_work_item** to retrieve and check the parent work item for a story or task
- Use **wit_create_work_item** MCP tool to create a Feature
- Use **wit_add_child_work_items** MCP tool to create a User Story as a child of the Feature, or a Task as a child of the User Story
- Use **wit_update_work_item** MCP tool to set Story Points and Acceptance Criteria on a User Story, or the hour estimates on a Task, after creation
- Apply proper HTML formatting to description and acceptance criteria fields
- Set Acceptance Criteria in the Microsoft.VSTS.Common.AcceptanceCriteria field (NOT in Description)
- Keep task descriptions lightweight and reference parent story
- Use configuration values from CLAUDE.md
- Show clear success message with work item details
- Provide helpful next steps and links

### Error Handling

If the MCP tool returns an error:
- Display the error message to the user
- Suggest possible solutions:
  - Verify the parent Feature ID or parent User Story ID exists and is valid (story and task)
  - Verify Azure DevOps MCP server is configured and running
  - Check that project and team names are correct
  - Ensure user has permissions to create work items
  - Verify Node.js 20+ is installed for MCP server
  - Check that the hour estimate is a valid numeric value (task)
- Recommend running /ado-init if configuration seems incorrect
- If a story's parent ID is invalid, suggest using /ado-create feature first
- If a task's parent ID is invalid, suggest using /ado-create story first
