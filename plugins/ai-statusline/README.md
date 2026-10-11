# AI-Statusline Plugin

**Status line customization for Claude Code.** Interactive setup and edit wizards for configuring a custom status line with progress bars and customizable display options.

> **How this relates to the native `/statusline` command:** Claude Code ships a built-in `/statusline` command that covers baseline setup (describe what you want, or auto-configure from your shell prompt). This plugin goes further with richer, opinionated widgets: a Unicode progress bar with color thresholds, 5-hour/7-day rate-limit percentages with color coding, a month-to-date spend budget for Enterprise/API seats that have no rate limits, a reasoning-effort indicator with `/effort`-matched colors (including ultracode detection), a sandbox indicator that appears while the Bash sandbox is on, session cost and duration segments, granular per-segment toggles, and a matching `/statusline-edit` flow for reconfiguring later without regenerating the script.

---

## Example Status Line

```
Opus 5 (1M context) · high · 420k/1000k ▓▓▓▓░░░░░░ 42% · 5h:12% 7d:4% · my-project · main · 5m 23s · 2:45pm · v2.1.80
```

On an Enterprise or API seat with a monthly spend cap (no 5h/7d rate limits), with the optional spend budget enabled:

```
Opus 5 (1M context) · high · 71k/1000k ░░░░░░░░░░ 7% · mo:$47.20/$2000 2.4% · my-project · main · 7m 48s · 4:52pm · v2.1.267
```

With the optional sandbox indicator enabled, `Sandbox` appears in orange after the effort level while the Bash sandbox is on:

```
Opus 5 (1M context) · high · Sandbox · 420k/1000k ▓▓▓▓░░░░░░ 42% · 5h:12% 7d:4% · my-project · main · 5m 23s · 2:45pm · v2.1.293
```

---

## Available Skills

### `/statusline-wizard`

Interactive setup wizard for configuring Claude Code's custom status line from scratch.

**What it does:**

- Detects your operating system (Mac/Linux/Windows)
- Checks for existing configuration and offers to back up if present
- Runs an interactive wizard using grouped questions
- Creates the appropriate script file (`statusline.sh` or `statusline.ps1`)
- Updates `~/.claude/settings.json` with the statusLine configuration
- Makes the script executable on Mac/Linux

**Usage:**

```
/statusline-wizard
```

**Wizard Questions:**

The wizard asks about four categories of display options:

1. **Context Display** (what to show about your Claude session)
   - Token count (e.g., "420k/1000k")
   - Progress bar (visual percentage indicator)
   - Model name (e.g., "Opus 5 (1M context)")
   - Effort level (e.g., "high", with `/effort`-matched colors)

2. **Project Display** (what to show about your project)
   - Current directory name
   - Git branch name
   - Sandbox indicator (Mac/Linux; disabled by default, and shown only while the Bash sandbox is on)

3. **Session Display** (what to show about timing/costs)
   - Session duration
   - Current time
   - Claude Code version
   - Session cost (disabled by default)

4. **Usage Limits** (how close you are to your plan's limits)
   - Rate limit usage - 5h and 7d windows (Pro/Max plans)
   - Monthly spend budget - month-to-date spend across sessions on this machine (disabled by default; prompts for your monthly cap in USD and when it resets)

### `/statusline-edit`

Edit your existing status line configuration.

**What it does:**

- Detects your OS and locates the existing script file
- Reads current configuration values from the script
- Asks the same questions as the wizard
- Updates only the configuration variables (preserves the rest of the script)

**Usage:**

```
/statusline-edit
```

**Note:** If no status line script exists, you'll be prompted to run `/statusline-wizard` first.

---

## Quick Start

### Installation

```
/plugin marketplace add charlesjones-dev/ai-agent-plugins
/plugin install ai-statusline@ai-agent-plugins
```

### Usage

```
# Step 1: Run the setup wizard
/statusline-wizard

# Step 2: Answer the interactive questions
# Select which elements you want displayed

# Step 3: The new status line appears right away

# Later: Edit your configuration
/statusline-edit
```

---

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| Model name | On | Display model name (e.g., "Opus 5 (1M context)") |
| Effort level | On | Display reasoning effort level with `/effort`-matched colors |
| Sandbox indicator | Off | Display `Sandbox` in orange after the effort level while the Bash sandbox is on (Mac/Linux only) |
| Token count | On | Display token usage (e.g., "420k/1000k") |
| Progress bar | On | Display visual progress bar with percentage |
| Current directory | On | Display current working directory name |
| Git branch | On | Display current git branch |
| Session duration | On | Display how long the session has been running |
| Current time | On | Display current time |
| Claude Code version | On | Display Claude Code version number |
| Session cost | Off | Display session cost in USD |
| Rate limit usage | On | Display 5-hour and 7-day rate limit percentages (hidden on accounts without rolling windows) |
| Monthly spend budget | Off | Display month-to-date spend across all sessions on this machine, e.g. `mo:$47.20/$2000 2.4%` |
| Monthly spend cap | 0 (none) | USD cap used for the spend budget percentage and colors; `0` shows the bare total |
| Spend cap reset | 1st, 00:00 UTC | Day of month (1-28) and time (UTC) the cap resets; the wizard converts what the console shows into UTC |

---

## Features

### Visual Progress Bar

The progress bar uses Unicode block characters to show context usage:

```
▓▓▓▓░░░░░░ 42%  (Green - under 70%)
▓▓▓▓▓▓▓░░░ 74%  (Yellow - 70-79%)
▓▓▓▓▓▓▓▓░░ 85%  (Red - 80%+)
```

### Rate Limit Display

Shows your 5-hour and 7-day rate limit usage with color coding:

```
5h:12% 7d:4%    (Green - under 50%)
5h:65% 7d:42%   (Yellow - 50-79%)
5h:92% 7d:85%   (Red - 80%+)
```

**Not on every plan:** Claude Code only sends `rate_limits` for plans with rolling usage windows (Pro/Max). Enterprise seats and API-billed accounts on a monthly spend cap receive no rate-limit data at all, so this segment stays hidden even when enabled. Use the Monthly Spend Budget segment below instead.

### Monthly Spend Budget

For accounts with no rolling rate limits, the optional spend segment shows month-to-date spend across all Claude Code sessions on this machine, colored on the same thresholds as the rate-limit segment:

```
mo:$47.20/$2000 2.4%    (Green - under 50% of cap)
mo:$1240.00/$2000 62.0% (Yellow - 50-79%)
mo:$1700.00/$2000 85.0% (Red - 80%+)
mo:$47.20               (No cap configured - bare total)
```

Enable it with `SHOW_SPEND_BUDGET=true` and set `SPEND_LIMIT_USD` to your seat's monthly cap (the "$0.96 of $2,000.00 spent" figure on the Anthropic console usage page). Leave the cap at `0` to show the bare total.

**Reset day and time:** the payload doesn't tell us when your cap resets, so you provide it. `SPEND_RESET_DAY` (1-28) and `SPEND_RESET_TIME` (HH:MM, 24-hour) are both in UTC and default to the 1st at 00:00 UTC, which is what the Anthropic console uses. The console shows that same instant in your local time ("Resets Wed, Sep 30, 8:00 PM EDT" is Oct 1 00:00 UTC), and the wizard does the conversion when you paste it. Invalid values fall back to the default rather than breaking the status line.

**How it works:** Claude Code only reports the current session's cost, so each render writes it to `~/.claude/statusline-spend/<period-start>/<session_id>` and the segment sums every file for the current billing period, where the period starts at the most recent reset day/time. One file per session means concurrent sessions never contend for a shared file. Previous periods are pruned automatically. If the directory can't be created or written (read-only home, missing `HOME`), the segment silently falls back to the current session's cost.

**Caveats to know before relying on it:**

- **It's a local estimate and won't match your bill.** The figure is Claude Code's own `cost.total_cost_usd` estimate and won't match the Anthropic console (in one observed case the console showed $0.96 spent while a single live session already reported $1.11). The authoritative sources are the console usage page and the Admin API cost report, which needs an org admin key most seat users don't have.
- **No historical backfill.** Only sessions rendered after you enable the segment are counted.
- **This machine only.** It doesn't include claude.ai web/desktop usage or sessions on other machines.

### Effort Level Display

Shows the session's reasoning effort level, colored to match Claude Code's `/effort` picker:

| Level | Color |
|-------|-------|
| `low` | Yellow |
| `medium` | Green |
| `high` | Light purple |
| `xhigh` | Dark purple |
| `max` | Per-character rainbow |
| `ultracode` | Purple explosion (`✦ultracode✦`, cycling purple shades) |

The segment reflects live `/effort` changes and is hidden entirely when the current model doesn't support the effort parameter.

**Ultracode detection:** Claude Code reports ultracode as plain `xhigh` in the status line payload, so the scripts scan the session transcript for the most recent `/effort` command output to tell them apart. If a session never ran `/effort`, the payload value is shown as-is.

### Sandbox Indicator

Shows `Sandbox` in orange, right after the effort level, while Claude Code's [Bash sandbox](https://code.claude.com/docs/en/sandboxing) is on for the session. It's hidden while the sandbox is off. It's disabled by default: select it in the wizard, or set `SHOW_SANDBOX=true`.

The status line payload doesn't say whether the sandbox is on, so the script works it out from your settings the way Claude Code does. The first of these that sets `sandbox.enabled` wins:

1. Managed settings: `managed-settings.json` and `managed-settings.d/` in `/Library/Application Support/ClaudeCode/` (macOS) or `/etc/claude-code/` (Linux, WSL2)
2. `--settings` on the `claude` command line, as inline JSON or a file path, such as `claude --settings '{"sandbox": {"enabled": true}}'`
3. `.claude/settings.local.json`, where `/sandbox` saves its choices (at the repository root, or the main checkout's root in a worktree)
4. `.claude/settings.json` in the directory Claude Code started in
5. `~/.claude/settings.json`

Turning the sandbox on or off with `/sandbox` shows up on the next refresh.

The indicator reflects your settings. It can't confirm that the sandbox started, and it can't read MDM profiles or server-managed settings. On Linux and WSL2 it stays hidden when `bwrap` or `socat` is missing, because the sandbox can't start without them, but other startup failures go unnoticed. When it matters, such as before a security audit, ask Claude to run `touch ~/sandbox-probe` and check that it fails. The sandbox doesn't run on native Windows, so the PowerShell script has no sandbox indicator.

---

## How It Works

1. **Script Generation**: The wizard writes one script for your OS (Bash on Mac/Linux, PowerShell on Windows) and adds it to your `settings.json` (paths below). The script reads JSON input from stdin (provided by Claude Code)

2. **JSON Parsing**:
   - Mac/Linux: Uses `jq` to parse the JSON data
   - Windows: Uses PowerShell's `ConvertFrom-Json`

3. **Dynamic Output**: The script builds output segments based on enabled options, joining them with separators

4. **ANSI Colors**: Uses standard ANSI escape codes for cross-terminal color support

### Script Location

| OS | Script Path | Settings Path |
|----|-------------|---------------|
| Mac/Linux | `~/.claude/statusline.sh` | `~/.claude/settings.json` |
| Windows | `C:/Users/USERNAME/.claude/statusline.ps1` | `C:/Users/USERNAME/.claude/settings.json` |

---

## Requirements

### Mac/Linux

- **jq**: Required for JSON parsing
  ```bash
  # macOS
  brew install jq

  # Ubuntu/Debian
  sudo apt install jq

  # Fedora
  sudo dnf install jq
  ```

### Windows

- PowerShell 5.1+ (included with Windows 10/11) or PowerShell Core 7+
- No additional dependencies required

### Terminal Support

- Unicode support for progress bar characters (`▓` and `░`)
- ANSI color code support (most modern terminals)

---

## Customization

### Manual Configuration

After running the wizard, you can manually edit the configuration variables at the top of the script file:

**Bash (`~/.claude/statusline.sh`):**
```bash
SHOW_MODEL=true           # Show model name
SHOW_EFFORT=true          # Show reasoning effort level
SHOW_SANDBOX=false        # Show "Sandbox" while the Bash sandbox is on
SHOW_TOKEN_COUNT=true     # Show token usage count
SHOW_PROGRESS_BAR=true    # Show visual progress bar
SHOW_DIRECTORY=true       # Show current directory name
SHOW_GIT_BRANCH=true      # Show current git branch
SHOW_COST=false           # Show session cost
SHOW_DURATION=true        # Show session duration
SHOW_TIME=true            # Show current time
SHOW_VERSION=true         # Show Claude Code version
SHOW_RATE_LIMITS=true     # Show rate limit usage (5h/7d windows)
SHOW_SPEND_BUDGET=false   # Show month-to-date spend across sessions on this machine
SPEND_LIMIT_USD=0         # Monthly spend cap in USD (0 = no cap, show bare total)
SPEND_RESET_DAY=1         # Day of the month (1-28) the cap resets, UTC
SPEND_RESET_TIME=00:00    # Time (HH:MM, 24h, UTC) the cap resets
```

**PowerShell (`C:/Users/USERNAME/.claude/statusline.ps1`):**
```powershell
$SHOW_MODEL = $true
$SHOW_EFFORT = $true
$SHOW_TOKEN_COUNT = $true
$SHOW_PROGRESS_BAR = $true
$SHOW_DIRECTORY = $true
$SHOW_GIT_BRANCH = $true
$SHOW_COST = $false
$SHOW_DURATION = $true
$SHOW_TIME = $true
$SHOW_VERSION = $true
$SHOW_RATE_LIMITS = $true
$SHOW_SPEND_BUDGET = $false
$SPEND_LIMIT_USD = 0
$SPEND_RESET_DAY = 1
$SPEND_RESET_TIME = '00:00'
```

---

## Troubleshooting

### Status line not appearing

1. Verify the script exists at the expected location
2. Check that `~/.claude/settings.json` contains the `statusLine` configuration
3. Restart Claude Code if it still doesn't appear

### Colors not displaying

- Ensure your terminal supports ANSI escape codes
- Try a different terminal emulator if colors don't appear

### Progress bar characters look wrong

- Ensure your terminal font supports Unicode block characters
- Try a font like "Fira Code", "JetBrains Mono", or "Cascadia Code"

### jq not found (Mac/Linux)

Install jq using your package manager (see Requirements section above).

### Rate limits (5h/7d) never appear

Your account has no rolling rate-limit windows, so Claude Code doesn't send `rate_limits` in the status line payload. This is expected for Enterprise seats and API-billed accounts on a monthly spend cap. Enable the Monthly Spend Budget segment (`SHOW_SPEND_BUDGET=true`) for a comparable month-to-date view.

### Spend budget only shows the current session

The script couldn't write to `~/.claude/statusline-spend/` (read-only home directory or `HOME` not set), so it fell back to the current session's cost. Make that directory writable to restore cross-session totals.

---

## Plugin Details

- **Name:** AI-Statusline
- **Version:** 1.5.1
- **Type:** UI Customization
- **Features:**
  - Skills: `/statusline-wizard`, `/statusline-edit`
- **License:** MIT
- **Author:** Charles Jones

---

## Contributing

Bug reports and fixes are welcome. See [CONTRIBUTING.md](../../CONTRIBUTING.md).

---

## License

MIT License - See [LICENSE](LICENSE) file for details.
