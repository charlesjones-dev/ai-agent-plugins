---
name: ado-init
description: "Initialize Azure DevOps configuration in CLAUDE.md with organization, project, and team settings."
disable-model-invocation: true
---

# Azure DevOps Init

Initialize Azure DevOps configuration by creating or updating `CLAUDE.md` with your organization, project, and team settings, and optionally configuring the Azure DevOps MCP server.

## Instructions

**CRITICAL**: This command MUST NOT accept any arguments. If the user provided any text, organization names, project names, or other arguments after this command (e.g., `/ado-init myorg` or `/ado-init myorg/myproject`), you MUST COMPLETELY IGNORE them. Do NOT use any organization names, project names, or other arguments that appear in the user's message. You MUST ONLY gather requirements through the interactive sequential prompts as specified below.

**BEFORE DOING ANYTHING ELSE**: Begin with Phase 1 by asking for the organization name. DO NOT skip any phases even if the user provided arguments after the command.

Configure CLAUDE.md with Azure DevOps-specific settings that guide Claude Code when working with the Microsoft Azure DevOps MCP server tools. The CLAUDE.md section holds the configuration and the few work item rules Claude needs when it uses the MCP tools directly. The detailed work item creation guidelines live in the `/ado-create` command, which only the user can start.

### Phase 1: Gather Azure DevOps Configuration

Collect Azure DevOps settings from the user in a sequential flow. Ask for each value and wait for the user's response before proceeding to the next.

**Step 1 - Organization:**

Simply output the following text as your response message and STOP (DO NOT call any tools, especially not AskUserQuestion):

"What is your Azure DevOps organization name? (This is the organization URL segment, e.g., 'contoso' in dev.azure.com/contoso)"

Wait for the user's next message with their organization name before proceeding.

**Step 2 - Project:**

After receiving the organization name, simply output the following text as your response message and STOP (DO NOT call any tools):

"What is your Azure DevOps project name?"

Wait for the user's next message with their project name before proceeding.

**Step 3 - Team:**

After receiving the project name, simply output the following text as your response message and STOP (DO NOT call any tools):

"What is your Azure DevOps team name?"

Wait for the user's next message with their team name before proceeding.

**Step 4 - Area Path:**

After receiving the team name, simply output the following text as your response message and STOP (DO NOT call any tools):

"What is your default Area Path for work items? (This determines where work items are organized. Suggested format: `[PROJECT]\\Team\\[TEAM]`, or leave blank to use the default)"

Wait for the user's next message with their area path (or blank) before proceeding.

**Step 5 - Iteration Path:**

After receiving the area path, simply output the following text as your response message and STOP (DO NOT call any tools):

"What is your default Iteration Path for work items? (This determines which sprint/iteration work items belong to. Suggested format: `[PROJECT]\\Sprint 1`, or leave blank to use the default)"

Wait for the user's next message with their iteration path (or blank) before proceeding.

**Step 6 - Naming Convention:**

After receiving the iteration path, simply output the following text as your response message and STOP (DO NOT call any tools):

"Do you want to use decimal notation for User Story naming? (e.g., 1.1, 1.2, 2.1 for Stories under numbered Features)

Type 'yes' for decimal notation (1, 2, 3 for Features; 1.1, 1.2, 2.1 for Stories)
Type 'no' for simple descriptive names (numbered Features only, descriptive names for Stories and Tasks)"

Wait for the user's next message with their choice (yes/no) before proceeding.

**Step 7 - MCP Configuration:**

After receiving the naming convention choice, simply output the following text as your response message and STOP (DO NOT call any tools):

"Do you want to create a .mcp.json file for Azure DevOps MCP server configuration?

Type 'yes' to configure the Azure DevOps MCP server
Type 'no' to skip MCP configuration"

Wait for the user's next message with their choice (yes/no) before proceeding.

**Step 8 - Operating System (only if Step 7 was "yes"):**

If the user answered "yes" to Step 7, simply output the following text as your response message and STOP (DO NOT call any tools):

"Are you using Windows or Linux/Mac?

Type 'windows' for Windows
Type 'linux' for Linux or Mac

Note: Node.js 20+ is required for npx to work. Check your version with: node --version"

Wait for the user's next message with their choice (windows/linux) before proceeding.

If the user answered "no" to Step 7, skip Step 8 entirely and proceed to Phase 2A.

**IMPORTANT**:
- For Steps 1-8: Simply output the question text in your response message and STOP - do NOT call ANY tools
- DO NOT use the AskUserQuestion tool (or any other tool) for any of the steps 1-8
- After outputting each question, wait for the user's next message before proceeding to the next step
- For Steps 6 and 7, expect the user to type "yes" or "no"
- For Step 8 (if applicable), expect the user to type "windows" or "linux"
- Validate that organization, project, and team names are provided (not empty)
- If Area Path or Iteration Path are empty, apply defaults:
  - Area Path default: `[PROJECT]\\Team\\[TEAM]`
  - Iteration Path default: `[PROJECT]\\Sprint 1`
- Store all collected values (including OS choice) for use in Phase 2A and Phase 3

### Phase 2A: Handle MCP Configuration

If the user answered "yes" to Step 7 (MCP configuration):

1. Check if `.mcp.json` exists in the project root using the **Read tool**
2. If `.mcp.json` already exists (Read succeeds):
   - Display the appropriate message based on the OS choice from Step 8:

   **For Windows:**
     ```
     ⚠️  .mcp.json file already exists

     For security reasons, we cannot read or modify existing .mcp.json files.

     Please manually add the following configuration to your .mcp.json file:

     {
       "mcpServers": {
         "ado": {
           "command": "cmd",
           "args": ["/c", "npx", "-y", "@azure-devops/mcp", "[ORGANIZATION]"]
         }
       }
     }

     Replace [ORGANIZATION] with: [organization_value]

     💡 Tip: If you already have mcpServers configured, add the "ado" entry
        to your existing mcpServers object.

     📖 Authentication Setup: Visit https://github.com/microsoft/azure-devops-mcp
        for instructions on configuring authentication with your Azure DevOps account.
     ```

   **For Linux/Mac:**
     ```
     ⚠️  .mcp.json file already exists

     For security reasons, we cannot read or modify existing .mcp.json files.

     Please manually add the following configuration to your .mcp.json file:

     {
       "mcpServers": {
         "ado": {
           "command": "npx",
           "args": ["-y", "@azure-devops/mcp", "[ORGANIZATION]"]
         }
       }
     }

     Replace [ORGANIZATION] with: [organization_value]

     💡 Tip: If you already have mcpServers configured, add the "ado" entry
        to your existing mcpServers object.

     📖 Authentication Setup: Visit https://github.com/microsoft/azure-devops-mcp
        for instructions on configuring authentication with your Azure DevOps account.
     ```

   - Replace `[ORGANIZATION]` and `[organization_value]` with the actual organization name
   - Proceed to Phase 2B

3. If `.mcp.json` doesn't exist (Read returns error):
   - Create `.mcp.json` with the appropriate content based on the OS choice from Step 8 using the **Write tool**:

   **For Windows:**
     ```json
     {
       "mcpServers": {
         "ado": {
           "command": "cmd",
           "args": ["/c", "npx", "-y", "@azure-devops/mcp", "[ORGANIZATION]"]
         }
       }
     }
     ```

   **For Linux/Mac:**
     ```json
     {
       "mcpServers": {
         "ado": {
           "command": "npx",
           "args": ["-y", "@azure-devops/mcp", "[ORGANIZATION]"]
         }
       }
     }
     ```

   - Replace `[ORGANIZATION]` with the actual organization name
   - Display success message:
     ```
     ✓ Created .mcp.json with Azure DevOps MCP server configuration

     📖 Authentication Setup Required:
        Visit https://github.com/microsoft/azure-devops-mcp for instructions on
        configuring authentication with your Azure DevOps account.

        You'll need to set up a Personal Access Token (PAT) with appropriate
        permissions for the MCP server to connect to your ADO account.
     ```
   - Proceed to Phase 2B

If the user answered "no" to Step 7 (skip MCP configuration):
- Skip all MCP configuration steps
- Proceed directly to Phase 2B

**IMPORTANT for Phase 2A**:
- Use **Read tool** to check if .mcp.json exists - DO NOT use bash commands
- For security reasons, NEVER read the contents of an existing .mcp.json file
- If .mcp.json exists, only show the snippet - do NOT attempt to merge or modify
- Use **Write tool** only when creating a new .mcp.json file
- Use the correct command format based on user's OS choice (Windows vs Linux/Mac)
- Ensure proper JSON formatting with correct indentation

### Phase 2B: Check Existing CLAUDE.md

Check if `CLAUDE.md` already exists and contains an Azure DevOps section using the **Read tool**:

1. Try to read `CLAUDE.md` using the Read tool from the project root
2. If the file exists and Read succeeds:
   - Parse the content
   - Search for "## Azure DevOps" section header
   - If Azure DevOps section exists and mentions `ado-work-items`:
     - This section was written by an earlier version of /ado-init. It says the `ado-work-items` skill loads automatically with the Azure DevOps MCP tools, which stopped being true when the skill became command-only, and ai-ado 2.0 replaced the skill with `/ado-create`.
     - Use the **Edit tool** to replace the paragraph that mentions `ado-work-items` (it starts with `**Work Item Guidelines:**` unless the user edited it) with the work item rules block from the Phase 3 template: every line from `**Work Item Rules:**` through the line that mentions `/ado-create`.
     - If the section also contains the sentence `All work items (Features, User Stories, and Tasks) should have the "State" set to "New" unless otherwise specified.`, remove that sentence, since the first rule covers it.
     - Leave everything else unchanged, including the configuration values and the rest of CLAUDE.md
     - Display:
       ```
       ✓ Updated the Azure DevOps section in CLAUDE.md

       It referred to the ado-work-items skill, which ai-ado 2.0 replaced with
       /ado-create. In its place, the section now lists the work item rules Claude
       follows with the Azure DevOps MCP tools and points to /ado-create.

       Your organization, project, team, paths and naming convention are unchanged.
       To change them, edit the Azure DevOps section of CLAUDE.md.
       ```
     - Return early without making other changes
   - If Azure DevOps section exists (and doesn't mention `ado-work-items`):
     - **STOP** and display a warning message:
       ```
       ⚠️  Azure DevOps section already exists in CLAUDE.md

       The CLAUDE.md file already contains Azure DevOps configuration.

       To update the configuration:
       1. Manually edit CLAUDE.md to update the Azure DevOps section
       2. Or remove the Azure DevOps section and run /ado-init again

       Current Azure DevOps section found at line: [line_number]
       ```
     - Return early without making changes
   - If no Azure DevOps section exists:
     - Proceed to Phase 3 to append the section
3. If the file doesn't exist (Read returns error):
   - Proceed to Phase 3 to create new CLAUDE.md with Azure DevOps section

**IMPORTANT**:
- Use **Read tool** to check file existence - DO NOT use bash test commands
- The Read tool will gracefully handle non-existent files by returning an error
- Only proceed with writing if no Azure DevOps section currently exists. The one exception is the `ado-work-items` replacement above, which edits only that paragraph
- Preserve all existing content when appending

### Phase 3: Build Azure DevOps Configuration Section

Using the values collected in Phase 1, build a simplified Azure DevOps configuration section:

```markdown
## Azure DevOps

Azure DevOps MCP tools are authorized for use in this project. When utilizing Azure DevOps MCP tools, use the following configuration:

**Organization:** [ORGANIZATION]
**Project:** [PROJECT]
**Team:** [TEAM]
**Area Path:** [AREA_PATH]
**Iteration Path:** [ITERATION_PATH]
**Naming Convention:** [NAMING_CONVENTION_DESCRIPTION]

**Work Item Rules:**

- Set "State" to "New" on new work items unless otherwise specified, and leave them unassigned.
- Every User Story has a parent Feature, and every Task has a parent User Story.
- Write Description and Acceptance Criteria as HTML (`<p>`, `<ul>`, `<li>`, `<strong>`), not Markdown. Acceptance criteria use Given/When/Then and go in the Acceptance Criteria field, not the Description.
- Story Points (Fibonacci: 1, 2, 3, 5, 8, 13) go on User Stories only. A new Task gets the same hours in Original Estimate and Remaining Work, and Completed Work stays empty.

For the full guidelines, the user can run `/ado-create feature`, `/ado-create story` or `/ado-create task` from the ai-ado plugin. Claude can't start that command itself, so suggest it instead of trying to load it.
```

**Naming Convention Description Values:**

If user selected "Yes, use decimals":
```
Decimal notation (Features: 1, 2, 3; User Stories: 1.1, 1.2, 2.1; Tasks: descriptive names)
```

If user selected "No, simple names":
```
Simple descriptive names (Features: numbered 1-99; User Stories and Tasks: descriptive names)
```

**Template Variable Replacements:**
- `[ORGANIZATION]` → User's organization name
- `[PROJECT]` → User's project name
- `[TEAM]` → User's team name
- `[AREA_PATH]` → User's area path
- `[ITERATION_PATH]` → User's iteration path
- `[NAMING_CONVENTION_DESCRIPTION]` → Appropriate description based on user choice

### Phase 4: Write or Update CLAUDE.md

After building the Azure DevOps configuration section:

**If CLAUDE.md exists (no Azure DevOps section):**
1. Read the existing content
2. Append two newlines and the Azure DevOps section to the end
3. Use the **Write tool** to update CLAUDE.md with combined content
4. Show success message with "updated" status

**If CLAUDE.md doesn't exist:**
1. Create a new CLAUDE.md with the Azure DevOps section
2. Add a header explaining this is project-specific configuration for Claude Code
3. Use the **Write tool** to create CLAUDE.md
4. Show success message with "created" status

**File Header for New CLAUDE.md:**
```markdown
# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

```

**IMPORTANT**:
- Use **Write tool** to create/update the CLAUDE.md file
- DO NOT use bash commands for writing the file
- Preserve all existing content when updating
- Add proper spacing (two newlines) before the Azure DevOps section
- Ensure proper markdown formatting

### Phase 5: Display Success Message

Show a comprehensive success message with configuration summary:

```
✓ Azure DevOps configuration successfully added to CLAUDE.md!

Configuration Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Organization: [organization]
📂 Project: [project]
👥 Team: [team]
📍 Area Path: [area_path]
🔄 Iteration Path: [iteration_path]
📝 Naming Convention: [Decimal notation | Simple descriptive names]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Work Item Rules:
The section also lists the rules Claude follows when it uses the Azure DevOps
MCP tools directly:
✓ State "New" and unassigned for new work items
✓ Three-level hierarchy (Features → User Stories → Tasks)
✓ HTML formatting for Description and Acceptance Criteria
✓ Story Points on User Stories, hour fields on Tasks

To create work items with the full guidelines (Description and Acceptance
Criteria templates, naming conventions, estimation), run:
   /ado-create feature
   /ado-create story [parent Feature ID]
   /ado-create task [parent User Story ID]

Next Steps:
1. Review the generated CLAUDE.md Azure DevOps section
2. [If MCP was configured] Ensure Node.js 20+ is installed (check: node --version)
3. [If MCP was configured] Set up authentication for Azure DevOps MCP server:
   📖 Visit https://github.com/microsoft/azure-devops-mcp for detailed instructions
   You'll need to create a Personal Access Token (PAT) with appropriate permissions
4. [If MCP was configured] Restart Claude Code for the MCP server to take effect
5. Create work items with /ado-create, or log hours to a story with /ado-log-story-work

💡 Azure DevOps MCP Server: https://github.com/microsoft/azure-devops-mcp
💡 Node.js Download: https://nodejs.org/

💡 Tip: All Azure DevOps MCP work item operations will now automatically
   use these organization, project, and team settings unless explicitly
   overridden.
```

### Important Constraints

**DO NOT:**
- Modify or remove existing content from CLAUDE.md, apart from replacing the stale `ado-work-items` paragraph in Phase 2B
- Proceed if Azure DevOps section already exists, beyond that Phase 2B replacement
- Use bash commands for file operations
- Create the Azure DevOps section without user confirmation
- Include empty or placeholder values in the configuration
- Include the full work item guidelines in CLAUDE.md (they live in /ado-create)
- Tell the user or write in CLAUDE.md that a command loads automatically

**DO:**
- Use **Read tool** to check if CLAUDE.md exists and for Azure DevOps section
- For Steps 1-8: Simply output the question text in your message and STOP (no tool calls)
- Wait for the user's next message after each question before proceeding
- For Steps 6 and 7, expect the user to type "yes" or "no"
- Use **Write tool** to create/update CLAUDE.md
- Preserve all existing CLAUDE.md content when appending
- Validate that required fields are provided
- Show clear success message with configuration summary
- Provide helpful next steps for using the configuration
- Replace all template placeholders with actual user values
- Use proper markdown formatting with appropriate spacing
- Point to /ado-create for creating work items

### Additional Features

**Default Values:**
- If user doesn't provide Area Path, use: `[PROJECT]\\Team\\[TEAM]`
- If user doesn't provide Iteration Path, use: `[PROJECT]\\Sprint 1`

**Validation:**
- Ensure organization name doesn't contain special characters
- Ensure project and team names are valid (no leading/trailing spaces)
- Warn if Area Path or Iteration Path format seems incorrect

**MCP Integration Note:**
If the user chose to configure MCP (.mcp.json was created or snippet was shown), include a reminder in the success message to restart Claude Code for the MCP server configuration to take effect.

**Work Item Guidelines:**
The full work item guidelines are in `/ado-create`, which reads them when the user runs it. The ai-ado commands are command-only, so none of them load on their own when Claude uses the Azure DevOps MCP tools. That's why the CLAUDE.md section carries the short work item rules itself and points to `/ado-create` for the rest.
