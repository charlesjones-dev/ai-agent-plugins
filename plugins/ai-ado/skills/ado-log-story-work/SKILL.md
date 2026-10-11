---
name: ado-log-story-work
description: "Log completed work to a User Story by creating a Task with completed hours already set."
disable-model-invocation: true
---

# Log Completed Work to User Story

Rapidly log completed work to a User Story by creating a new Task work item with completed hours already set. This command is designed for quick logging of work done multiple times per day.

## Instructions

**CRITICAL**: This command MUST NOT accept any arguments. If the user provided any text, work descriptions, hours, IDs, or other arguments after this command (e.g., `/ado-log-story-work "Fixed bug" 2` or `/ado-log-story-work 123`), you MUST COMPLETELY IGNORE them. Do NOT use any work descriptions, hours, IDs, or other arguments that appear in the user's message. You MUST ONLY gather requirements through the interactive prompts as specified below.

**BEFORE DOING ANYTHING ELSE**: Validate Azure DevOps configuration in CLAUDE.md, then begin gathering task information. DO NOT skip these steps even if the user provided arguments after the command.

This command creates a Task work item to record completed work, following the organization's Azure DevOps conventions defined in CLAUDE.md.

### Phase 1: Validate Azure DevOps Configuration

Before proceeding with task creation, verify that Azure DevOps configuration exists:

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

3. If Azure DevOps section exists, extract these values from it. `/ado-init` has written the section in two formats, so accept either:
   - **Current format**, one line per value: `**Organization:**`, `**Project:**`, `**Team:**`, `**Area Path:**` and `**Iteration Path:**`, each followed by its value
   - **Older format**, one sentence: the organization is the text after 'specify the organization as "', the project after 'the project as "', the team after 'the team as "', the Area Path after 'Area Path" set to "' and the Iteration Path after 'Iteration Path" set to "'
   - Store these values for use in task creation
   - Proceed to Phase 2

**IMPORTANT**:
- Use **Read tool** to check CLAUDE.md - DO NOT use bash commands
- The entire command should STOP if Azure DevOps configuration is not found
- Do not prompt the user for configuration values - they must run /ado-init first

### Phase 2: Gather Task Information

Collect task details from the user. The user can choose between AI-powered generation or manual input.

**Step 1 - Get Parent User Story ID:**

Simply output the following text as your response message and STOP (DO NOT call any tools):

"What is the ID of the parent User Story for logging this completed work?

(This is the numeric ID of the User Story work item. You can find this in Azure DevOps or from the output of /ado-create story)"

Wait for the user's next message with the parent story ID before proceeding.

**Step 2 - Choose Input Method:**

Simply output the following text as your response message and STOP (DO NOT call any tools):

"Would you like to use AI to generate the Task details, or provide them manually?

Options:
1. AI-powered: Provide a description (optionally including a git commit hash) and let AI generate an appropriate task title and description
2. Manual: Provide the task details yourself

Please respond with 'AI' or 'Manual'."

Wait for the user's response before proceeding.

**If user chooses 'AI' (or similar affirmative response):**

**Step AI-1 - Get Prompt:**

Simply output the following text as your response message and STOP:

"Please describe the work that was completed. You can optionally include a git commit hash (full or short SHA) and I'll look up the commit details to enhance the task description.

(Examples:
- 'Implemented user authentication endpoints'
- 'Fixed bug in payment processing - commit abc123def'
- 'Added validation to registration form, see commit 1a2b3c4d5e6f7890')"

Wait for the user's prompt, then perform the following steps to generate content:

1. **Detect git commit hash** in the prompt:
   - Look for patterns like: 7-40 character hexadecimal strings that could be commit hashes
   - Common patterns: standalone hex strings, after words like "commit", "hash", "sha"

2. **If commit hash detected**:
   - Use **Bash tool** to run: `git show [COMMIT_HASH] --stat --pretty=format:"%H%n%h%n%s%n%b"`
     - This will show: full SHA, short SHA, subject, body, and file changes
   - Parse the git output to extract:
     - Full SHA (first line)
     - Short SHA (second line)
     - Commit message (subject + body)
     - Changed files list
   - Store this information for use in generation

3. **Generate a concise, action-oriented task title** (5-10 words) that describes what was completed
   - Examples: "Implement user authentication API endpoints", "Fix payment processing validation bug", "Add email verification to registration"

4. **Generate a detailed task description** (2-4 sentences) explaining what was accomplished:

   **If NO commit hash was found:**
   - Expand on the user's description with more detail about what was tested, implemented, fixed, or added
   - Include relevant technical details or context
   - Make it informative enough that someone reading the task understands what was done
   - Example generation:
     - User input: "Tested CMS functionality"
     - Generated description: "Completed comprehensive testing of the CMS functionality. Verified that content authors can edit page components inline, preview changes in real-time, and publish updates successfully. All core editing features are working as expected."

   **If commit hash WAS found:**
   - Start with what was accomplished (based on user description)
   - Reference the git commit with both full and short SHA
   - Include relevant parts of the commit message
   - List key files that were changed (if significant)
   - Example generation:
     - User input: "Implemented JWT auth - commit abc123def4567890"
     - Generated description: "Implemented JWT token authentication for the login API endpoints. This work is captured in commit abc123def4567890 (abc123d). The commit adds token generation, validation middleware, and refresh token logic. Key changes include: src/auth/jwt.ts, src/middleware/auth.ts, src/routes/login.ts."

   **Important**: Format the description as HTML with `<p>` tags for paragraphs and `<br/>` for line breaks. Keep it professional, clear, and informative.

**Step AI-2 - Confirm Generated Title:**

Display the generated title and ask for confirmation:

"I've generated the following title: [GENERATED_TITLE]

Would you like to use this title, or would you prefer to provide your own?
(Type 'yes' to use this title, or provide an alternative title)"

Wait for response:
- If user approves (says "yes", "ok", "looks good", etc.), store the generated title
- If user provides alternative text, use that as the title instead

**Step AI-3 - Confirm Generated Description:**

Display the generated description and ask for confirmation:

"I've generated the following description: [GENERATED_DESCRIPTION]

Would you like to use this description, or would you prefer to provide your own?
(Type 'yes' to use this description, or provide an alternative description)"

Wait for response:
- If user approves (says "yes", "ok", "looks good", etc.), store the generated description
- If user provides alternative text, use that as the description instead

**If user chooses 'Manual':**

**Step M-1 - Task Title:**

Simply output the following text as your response message and STOP (DO NOT call any tools):

"What is the title for this completed task?

(Provide a concise description of the work that was completed)"

Wait for the user's next message with the task title before proceeding.

**Step M-2 - Task Description:**

After receiving the task title, simply output the following text as your response message and STOP (DO NOT call any tools):

"What is the description for this completed task?

(Provide enough detail to understand what was accomplished. You can include commit hashes, file names, or other relevant details.)"

Wait for the user's next message with the task description before proceeding.

**Step 3 - Completed Hours:**

Simply output the following text as your response message and STOP:

"How many hours were completed on this task?

(Provide a numeric value in hours. This will be set for both 'Original Estimate' and 'Completed Work' fields, with 'Remaining Work' left empty.)"

Wait for the user's next message with the completed hours before proceeding.

**Step 4 - Placeholder Task Subtraction:**

Simply output the following text as your response message and STOP:

"Would you like to subtract these hours from a placeholder task?

(This is useful if you have a bucket of hours allocated to a placeholder task that you want to draw down as work is completed. Type 'yes' or 'no')"

Wait for the user's response.

**If user says 'yes' (or similar affirmative):**

**Step 4a - Placeholder Task ID:**

Simply output the following text as your response message and STOP:

"What is the ID of the placeholder task to subtract hours from?

(This is the numeric ID of the existing Task work item that contains your hour bucket)"

Wait for the user's next message with the placeholder task ID before proceeding to Phase 3.

**If user says 'no' (or similar negative):**

Proceed directly to Phase 3.

**IMPORTANT**:
- Simply output the question text in your response message and STOP - do NOT call ANY tools (except when looking up git commits or generating AI content)
- DO NOT use the AskUserQuestion tool for any of these steps
- After outputting each question, wait for the user's next message before proceeding
- **For AI mode**: In Step AI-1, you MUST actually generate BOTH the title AND description content (steps 4 and 5) before proceeding to Step AI-2
- **For AI mode**: Steps AI-2 and AI-3 display the ALREADY GENERATED content for user confirmation
- **For AI mode**: The description MUST be actual content (2-4 sentences), NOT empty, NOT just placeholder text
- For AI mode: Detect git commit hashes automatically and look them up
- For AI mode: Always confirm generated content and allow user to override
- For Manual mode: Use provided text directly without modification
- Validate that required fields are provided (not empty)
- Parent User Story ID must be a valid number
- Completed hours must be a valid number
- Placeholder task ID (if provided) must be a valid number

### Phase 3: Create Task Work Item

Using the configuration from Phase 1 and the information from Phase 2, create the task work item:

1. Format the task description as HTML:
   - If AI-generated: Use the generated HTML-formatted description
   - If manual: Wrap the user's description in `<p>` tags, replacing line breaks with `<br/>`

2. Use the **wit_add_child_work_items** MCP tool with the following parameters:
   - `parentId`: The parent story ID provided by user (as number, not string)
   - `project`: Use the project name from Phase 1 configuration
   - `workItemType`: "Task"
   - `items`: Array containing a single item object with:
     - `title`: Generated or user-provided title
     - `description`: HTML-formatted description
     - `format`: "Html"
     - `areaPath`: Area Path from configuration
     - `iterationPath`: Iteration Path from configuration

3. After the task is created, use the **wit_update_work_item** MCP tool to set hour fields:
   - `id`: The ID of the newly created task (from the response of wit_add_child_work_items)
   - `updates`: Array containing:
     - `{"op": "add", "path": "/fields/Microsoft.VSTS.Scheduling.OriginalEstimate", "value": "[COMPLETED_HOURS]"}`
     - `{"op": "add", "path": "/fields/Microsoft.VSTS.Scheduling.CompletedWork", "value": "[COMPLETED_HOURS]"}`

4. Wait for both MCP tool responses

**IMPORTANT**:
- Use the exact field names and paths shown above
- Ensure HTML formatting is applied to the description
- Parent ID must be converted to a number (not a string)
- Use configuration values from Phase 1, not hardcoded values
- Set both Original Estimate and Completed Work to the same value (completed hours)
- DO NOT set Remaining Work field (leave empty)
- Completed Work field is critical - this marks the task as having completed work logged

### Phase 4: Update Placeholder Task (If Requested)

If the user requested placeholder task hour subtraction in Phase 2:

1. First, retrieve the current placeholder task details using **wit_get_work_item** MCP tool:
   - `id`: The placeholder task ID provided by user
   - `project`: Use the project name from Phase 1 configuration
   - Extract current values for:
     - Original Estimate (field: Microsoft.VSTS.Scheduling.OriginalEstimate)
     - Remaining Work (field: Microsoft.VSTS.Scheduling.RemainingWork)

2. Calculate new values:
   - New Original Estimate = Current Original Estimate - Completed Hours
   - New Remaining Work = Current Remaining Work - Completed Hours
   - Ensure values don't go below 0

3. Use the **wit_update_work_item** MCP tool to update the placeholder task:
   - `id`: The placeholder task ID
   - `updates`: Array containing:
     - `{"op": "replace", "path": "/fields/Microsoft.VSTS.Scheduling.OriginalEstimate", "value": "[NEW_ORIGINAL_ESTIMATE]"}`
     - `{"op": "replace", "path": "/fields/Microsoft.VSTS.Scheduling.RemainingWork", "value": "[NEW_REMAINING_WORK]"}`

4. Wait for the MCP tool response

**IMPORTANT**:
- Use "replace" operation (not "add") for updating existing field values
- Calculate new values correctly by subtracting completed hours
- Ensure values don't become negative (minimum value is 0)
- Store the old and new values to display in the success message

### Phase 5: Display Success Message

After successful task creation (and optional placeholder update), display a comprehensive success message:

**If placeholder task was NOT updated:**

```
✓ Completed work logged successfully!

Task Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 ID: [TASK_ID]
📋 Title: [TASK_TITLE]
📖 Parent User Story: [PARENT_STORY_ID] - [PARENT_STORY_TITLE]
📂 Project: [PROJECT_NAME]
📍 Area Path: [AREA_PATH]
🔄 Iteration Path: [ITERATION_PATH]
⏱️  Original Estimate: [HOURS] hours
✅ Completed Work: [HOURS] hours
✨ State: New
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next Steps:
1. Update task state to "Closed" in Azure DevOps if fully complete
2. Log additional work to the same story using /ado-log-story-work
3. Review overall story progress

💡 To log more work to this story:
   /ado-log-story-work
   (Parent User Story ID: [PARENT_STORY_ID])

🔗 View in Azure DevOps:
   https://dev.azure.com/[ORGANIZATION]/[PROJECT]/_workitems/edit/[TASK_ID]
```

**If placeholder task WAS updated:**

```
✓ Completed work logged successfully!

Task Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 ID: [TASK_ID]
📋 Title: [TASK_TITLE]
📖 Parent User Story: [PARENT_STORY_ID] - [PARENT_STORY_TITLE]
📂 Project: [PROJECT_NAME]
📍 Area Path: [AREA_PATH]
🔄 Iteration Path: [ITERATION_PATH]
⏱️  Original Estimate: [HOURS] hours
✅ Completed Work: [HOURS] hours
✨ State: New
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Placeholder Task Updated:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔖 Placeholder Task ID: [PLACEHOLDER_TASK_ID]
⏱️  Original Estimate: [OLD_ORIGINAL_ESTIMATE] hours → [NEW_ORIGINAL_ESTIMATE] hours (-[HOURS] hours)
⏳ Remaining Work: [OLD_REMAINING_WORK] hours → [NEW_REMAINING_WORK] hours (-[HOURS] hours)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next Steps:
1. Update task state to "Closed" in Azure DevOps if fully complete
2. Log additional work to the same story using /ado-log-story-work
3. Review overall story progress and remaining placeholder hours

💡 To log more work to this story:
   /ado-log-story-work
   (Parent User Story ID: [PARENT_STORY_ID])

🔗 View task in Azure DevOps:
   https://dev.azure.com/[ORGANIZATION]/[PROJECT]/_workitems/edit/[TASK_ID]

🔗 View placeholder task in Azure DevOps:
   https://dev.azure.com/[ORGANIZATION]/[PROJECT]/_workitems/edit/[PLACEHOLDER_TASK_ID]
```

Replace placeholders with actual values from the created task, placeholder task, and configuration.

### Important Constraints

**DO NOT:**
- Proceed without Azure DevOps configuration in CLAUDE.md
- Use bash commands for file operations (except git show for commit lookup)
- Create the task without user-provided information
- Use placeholder or empty values
- Call tools during question steps (questions should be simple text output)
- Set Remaining Work field (must be left empty)
- Use "add" operation when updating placeholder task values (use "replace")
- Allow placeholder task hours to become negative

**DO:**
- Use **Read tool** to check CLAUDE.md for Azure DevOps configuration
- Simply output question text and STOP for question steps (no tool calls except for git and AI generation)
- Wait for user's response after each question before proceeding
- Use **Bash tool** with `git show` to look up commit details if hash detected
- Use **wit_get_work_item** to retrieve placeholder task details
- Use **wit_add_child_work_items** MCP tool to create the task as a child of the story
- Use **wit_update_work_item** MCP tool to set hour fields after creation
- Apply proper HTML formatting to description field
- Set both Original Estimate and Completed Work to the completed hours value
- Leave Remaining Work empty (do not set)
- Auto-generate title and description in AI mode
- Always confirm AI-generated content before using
- Use manual input directly without modification in Manual mode
- Calculate placeholder task updates correctly
- Show clear success message with all relevant details
- Provide helpful next steps and links

### Error Handling

If the MCP tool returns an error:
- Display the error message to the user
- Suggest possible solutions:
  - Verify the parent User Story ID is a valid number
  - Verify the placeholder Task ID exists and is valid (if applicable)
  - Verify Azure DevOps MCP server is configured and running
  - Check that project and team names are correct
  - Ensure user has permissions to create and update work items
  - Verify Node.js 20+ is installed for MCP server
  - Check that hour values are valid numeric values
  - Ensure git repository is accessible if commit hash was provided
- Recommend running /ado-init if configuration seems incorrect
- If parent ID is invalid, suggest using /ado-create story first
- If git command fails, suggest verifying the commit hash is valid

If git commit lookup fails:
- Display a warning that commit could not be found
- Continue with task generation using only the user's description (without commit context)
- Do not stop the entire command flow
