---
name: statusline-wizard
description: "Interactive setup wizard for configuring Claude Code's custom status line with progress bars and customizable display options."
disable-model-invocation: true
---

# Status Line Wizard

Set up a custom status line for Claude Code with visual progress bars and configurable display options.

## Instructions

**CRITICAL**: This command MUST NOT accept any arguments. If the user provided any text after this command, COMPLETELY IGNORE it.

Follow the Setup Workflow defined in this skill (see the "Status Line Setup Skill" section below) to:

1. Detect the operating system (Mac/Linux/Windows)
2. Check for existing statusLine configuration and offer to back up if present
3. Run the configuration wizard using AskUserQuestion to gather preferences
4. Create the appropriate script file (`.sh` for Mac/Linux, `.ps1` for Windows)
5. Update `~/.claude/settings.json` with the statusLine configuration
6. Make the script executable on Mac/Linux using `chmod +x`

### Wizard Questions

Use AskUserQuestion with these grouped questions:

**Question 1 - Context Display** (multiSelect: true):
- Token count (50k/100k) - default selected
- Progress bar - default selected
- Model name - default selected
- Effort level (low/medium/high/xhigh/max/ultracode) - default selected

**Question 2 - Project Display** (multiSelect: true):
- Current directory - default selected
- Git branch - default selected
- Sandbox indicator - NOT selected by default. Description: "Shows 'Sandbox' in orange after the effort level while Claude Code's Bash sandbox is on for this session, whether /sandbox, a settings file or claude --settings turned it on. Hidden when it's off."

On Windows, leave out the Sandbox indicator option. The sandbox doesn't run on native Windows, so the PowerShell script has no sandbox segment.

**Question 3 - Session Display** (multiSelect: true):
- Session duration - default selected
- Current time - default selected
- Claude Code version - default selected
- Session cost - NOT selected by default

**Question 4 - Usage Limits** (multiSelect: true):
- Rate limit usage (5h/7d) - default selected. Description: "Only shown on plans with rolling rate-limit windows (Pro, Max and Ultra). Each window shows only when your plan has it, so an account without a 5-hour limit shows 7d alone. Enterprise and API seats billed against a monthly spend cap have no rate limits, so the segment stays hidden. Pick Monthly spend budget instead."
- Monthly spend budget (mo:$47.20/$2000 2.4%) - NOT selected by default. Description: "Month-to-date spend across all Claude Code sessions on this machine, as estimated locally by Claude Code. Counts only sessions rendered after setup."

AskUserQuestion allows at most 4 options per question, so rate limits and spend budget live in their own question rather than in Session Display.

**Questions 5 and 6 - Spend cap and reset** (only ask if "Monthly spend budget" was selected; send both in one AskUserQuestion call, single select each):

Question 5 - Monthly spend cap (USD):
- "No cap - show bare total" (Recommended if the user has no known cap) → `SPEND_LIMIT_USD=0`
- "$500" → `SPEND_LIMIT_USD=500`
- "$1000" → `SPEND_LIMIT_USD=1000`
- "$2000" → `SPEND_LIMIT_USD=2000`

The user can pick "Other" and type any amount; write the numeric value (digits and optional decimal point only, no currency symbol or thousands separators) into `SPEND_LIMIT_USD`. The cap is the seat's monthly spend limit shown on the Anthropic console usage page (e.g., "$0.96 of $2,000.00 spent").

Question 6 - When does the spend cap reset?
- "1st of the month at 00:00 UTC" (Recommended - what the Anthropic console uses) → `SPEND_RESET_DAY=1`, `SPEND_RESET_TIME=00:00`
- "1st of the month at midnight in my local time zone" → `SPEND_RESET_DAY=1` and `SPEND_RESET_TIME` set to local midnight converted to UTC using the machine's current offset (e.g., EDT is UTC-4, so `04:00`). Warn that daylight-saving changes shift this by an hour twice a year. If the local offset is ahead of UTC (e.g., UTC+2), local midnight on the 1st falls on the last day of the previous month in UTC, which `SPEND_RESET_DAY` (1-28) cannot express - explain this and use the UTC option instead.
- "A different day or time" → the user picks "Other" and types what the console shows, e.g. "Resets Wed, Sep 30, 8:00 PM EDT"

For "Other", convert the user's day and time to UTC before writing the variables. Example: "Sep 30, 8:00 PM EDT" is Oct 1 00:00 UTC, so write `SPEND_RESET_DAY=1` and `SPEND_RESET_TIME=00:00`. `SPEND_RESET_DAY` must be 1-28 (days 29-31 do not exist in every month) and `SPEND_RESET_TIME` must be `HH:MM` in 24-hour UTC. The script falls back to the 1st at 00:00 UTC if either value is invalid. Tell the user the UTC values you wrote so they can confirm.

### Success Message

After successful setup, display:

```
Status line configured successfully!

Script: ~/.claude/statusline.sh (or .ps1)
Settings: ~/.claude/settings.json

You should see your new status line below!

To customize later, run /statusline-edit or edit the SHOW_* variables at the top of the script file.
```

If the user enabled the monthly spend budget, append:

```
Monthly spend note: the "mo:" segment is Claude Code's local cost estimate for sessions
on this machine rendered from now on. It will not match the Anthropic console exactly;
use the console usage page for the authoritative figure.
```

---

# Status Line Setup Skill

This skill provides guidance for configuring Claude Code's status line with customizable display options, progress bars, and cross-platform support.

## When to Use This Skill

Invoke this skill when:
- Setting up a custom status line for Claude Code
- Configuring which elements to show/hide in the status line
- Adding a visual progress bar for context usage
- Setting up cross-platform status line scripts (bash/PowerShell)

## Setup Workflow

### Phase 1: Check Existing Configuration

1. Detect the operating system using Bash: `uname -s` (returns "Darwin" for macOS, "Linux" for Linux)
   - If command fails or returns "MINGW"/"MSYS"/"CYGWIN", assume Windows
2. Read the user's settings file:
   - **Mac/Linux**: `~/.claude/settings.json`
   - **Windows**: `C:/Users/USERNAME/.claude/settings.json` (get USERNAME from environment)
3. Check if `statusLine` section already exists
4. If exists, ask user using AskUserQuestion:
   - **Replace**: Back up existing file and create new configuration
   - **Cancel**: Stop the setup process

### Phase 2: Configuration Wizard

Use the AskUserQuestion tool to gather user preferences. Group questions logically:

**Question 1: Context Information**
- Show model name (default: yes)
- Show token count e.g. "50k/100k" (default: yes)
- Show progress bar (default: yes)
- Show effort level e.g. "high" (default: yes)

**Question 2: Project Information**
- Show current directory (default: yes)
- Show git branch (default: yes)
- Show sandbox indicator (default: no; Mac/Linux only, hidden while the sandbox is off)

**Question 3: Session Information**
- Show session cost (default: no)
- Show session duration (default: yes)
- Show current time (default: yes)
- Show Claude Code version (default: yes)

**Question 4: Usage Limits**
- Show rate limit usage - 5h and 7d windows (default: yes; each window is hidden automatically when the account doesn't have it, such as the 5h window on an Ultra account without a 5-hour limit)
- Show monthly spend budget - month-to-date spend across all sessions on this machine (default: no)

**Questions 5-6: Monthly spend cap and reset** (only when monthly spend budget was selected)
- Ask for the monthly cap in USD and write it to `SPEND_LIMIT_USD`; `0` means no cap (bare total)
- Ask when the cap resets and write the day of month (1-28, UTC) to `SPEND_RESET_DAY` and the time (HH:MM, 24h, UTC) to `SPEND_RESET_TIME`; convert whatever the user pastes from the console into UTC first

### Phase 3: Create Script File

Based on OS, create the appropriate script file:

**Mac/Linux**: `~/.claude/statusline.sh`
**Windows**: `C:/Users/USERNAME/.claude/statusline.ps1`

If script file already exists, back it up first with `.backup` extension.

### Phase 4: Update Settings

Update the settings.json file with the statusLine configuration:

**Mac/Linux**:
```json
{
  "statusLine": {
    "type": "command",
    "command": "/Users/USERNAME/.claude/statusline.sh",
    "padding": 0
  }
}
```

**Windows**:
```json
{
  "statusLine": {
    "type": "command",
    "command": "powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:/Users/USERNAME/.claude/statusline.ps1",
    "padding": 0
  }
}
```

### Phase 5: Make Executable (Mac/Linux only)

Run `chmod +x ~/.claude/statusline.sh` to make the script executable.

## Script Templates

### Bash Script Template (Mac/Linux)

```bash
#!/bin/bash

# =============================================================================
# Claude Code Status Line
# =============================================================================
# Configuration - Set these to customize your status line
# =============================================================================

SHOW_MODEL=true           # Show model name (e.g., "Claude Opus 4.8")
SHOW_EFFORT=true          # Show reasoning effort level (e.g., "high")
SHOW_SANDBOX=false        # Show "Sandbox" when Claude Code's Bash sandbox is enabled for this session
SHOW_TOKEN_COUNT=true     # Show token usage count (e.g., "50k/100k")
SHOW_PROGRESS_BAR=true    # Show visual progress bar
SHOW_DIRECTORY=true       # Show current directory name
SHOW_GIT_BRANCH=true      # Show current git branch
SHOW_COST=false           # Show session cost (useful for API/Pro users)
SHOW_DURATION=true        # Show session duration
SHOW_TIME=true            # Show current time
SHOW_VERSION=true         # Show Claude Code version
SHOW_RATE_LIMITS=true     # Show rate limit usage (5h/7d windows; a window the account doesn't have is hidden)
SHOW_SPEND_BUDGET=false   # Show month-to-date spend across all sessions on this machine (e.g., "mo:$47.20/$2000 2.4%")
SPEND_LIMIT_USD=0         # Monthly spend cap in USD for the spend segment (0 = no cap, show bare total)
SPEND_RESET_DAY=1         # Day of the month (1-28) the spend cap resets, in UTC
SPEND_RESET_TIME=00:00    # Time of day (HH:MM, 24h, UTC) the spend cap resets

# =============================================================================

input=$(cat)
model_name=$(echo "$input" | jq -r '.model.display_name')
effort_level=$(echo "$input" | jq -r '.effort.level // empty')
transcript_path=$(echo "$input" | jq -r '.transcript_path // empty')
current_dir=$(basename "$(echo "$input" | jq -r '.workspace.current_dir')")
version=$(echo "$input" | jq -r '.version')
usage=$(echo "$input" | jq '.context_window.current_usage')
host_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
cost=$(echo "$input" | jq -r '.cost.total_cost_usd')
duration_ms=$(echo "$input" | jq -r '.cost.total_duration_ms')
current_time=$(date +"%I:%M%p" | tr '[:upper:]' '[:lower:]')

# Ultracode reports as plain "xhigh" in the payload; detect it from the session
# transcript (the /effort command's stdout records the actual level chosen).
if [ "$effort_level" = "xhigh" ] && [ -n "$transcript_path" ] && [ -f "$transcript_path" ]; then
  last_effort_set=$(grep -ho '<local-command-stdout>Set effort level to [a-z]*' "$transcript_path" 2>/dev/null | tail -1 | awk '{print $NF}')
  [ "$last_effort_set" = "ultracode" ] && effort_level="ultracode"
fi

# Format cost
if [ "$cost" != "null" ] && [ -n "$cost" ]; then
  cost_fmt=$(printf '$%.2f' "$cost")
else
  cost_fmt='$0.00'
fi

# Format duration (ms to human readable)
if [ "$duration_ms" != "null" ] && [ -n "$duration_ms" ]; then
  duration_s=$((duration_ms / 1000))
  if [ $duration_s -lt 60 ]; then
    duration_fmt="${duration_s}s"
  elif [ $duration_s -lt 3600 ]; then
    mins=$((duration_s / 60))
    secs=$((duration_s % 60))
    duration_fmt="${mins}m ${secs}s"
  else
    hours=$((duration_s / 3600))
    mins=$(((duration_s % 3600) / 60))
    duration_fmt="${hours}h ${mins}m"
  fi
else
  duration_fmt='0s'
fi

# Get git branch
git_branch=$(git -C "$(echo "$input" | jq -r '.workspace.current_dir')" branch --show-current 2>/dev/null)
if [ -z "$git_branch" ]; then
  git_branch='-'
fi

# Build progress bar
build_progress_bar() {
  local pct=$1
  local color=$2
  local bar_width=10
  local filled=$((pct * bar_width / 100))
  local empty=$((bar_width - filled))

  local bar=""
  for ((i=0; i<filled; i++)); do bar+="▓"; done
  for ((i=0; i<empty; i++)); do bar+="░"; done

  printf '\033[%sm%s %d%%\033[0m' "$color" "$bar" "$pct"
}

# Color each character of a string, cycling through the given 256-color codes
colorize_chars() {
  local text=$1
  shift
  local palette=("$@")
  local out="" i ch
  for ((i=0; i<${#text}; i++)); do
    ch=${text:i:1}
    out+="\033[38;5;${palette[i % ${#palette[@]}]}m${ch}"
  done
  printf '%s\033[0m' "$out"
}

# ANSI color codes
reset='\033[0m'
white='\033[97m'
green='\033[32m'
yellow='\033[33m'
red='\033[31m'
blue='\033[94m'
magenta='\033[35m'
cyan='\033[36m'
gray='\033[90m'
orange='\033[38;5;208m'

# Build output segments
output=""

# Model name
if [ "$SHOW_MODEL" = true ]; then
  output="${white}${model_name}${reset}"
fi

# Effort level (absent when the model doesn't support effort)
# Colors match the /effort picker: yellow/green/light purple/dark purple/rainbow/purple explosion
if [ "$SHOW_EFFORT" = true ] && [ -n "$effort_level" ]; then
  case "$effort_level" in
    low) effort_fmt="${yellow}${effort_level}${reset}" ;;
    medium) effort_fmt="${green}${effort_level}${reset}" ;;
    high) effort_fmt="\033[38;5;141m${effort_level}${reset}" ;;
    xhigh) effort_fmt="\033[38;5;93m${effort_level}${reset}" ;;
    max) effort_fmt=$(colorize_chars "$effort_level" 196 208 226 46 39 129) ;;
    ultracode) effort_fmt=$(colorize_chars "✦${effort_level}✦" 93 129 135 141 171 177) ;;
    *) effort_fmt="${white}${effort_level}${reset}" ;;
  esac
  [ -n "$output" ] && output="$output · "
  output="$output${effort_fmt}"
fi

# Sandbox (shown when Claude Code's Bash sandbox is enabled for this session)
# The payload has no sandbox field, so this resolves sandbox.enabled the way Claude
# Code does. The first source that sets it wins: managed settings, --settings on the
# claude command line, .claude/settings.local.json, .claude/settings.json, then user
# settings. MDM profiles and server-managed settings can't be read from here.
sandbox_value() { jq -r '.sandbox.enabled | select(type == "boolean")' 2>/dev/null; }

if [ "$SHOW_SANDBOX" = true ]; then
  os_name=$(uname -s)
  project_dir=$(echo "$input" | jq -r '.workspace.project_dir // .workspace.current_dir // empty')
  sandbox_on=""

  # Managed settings: later managed-settings.d drop-ins override earlier ones and managed-settings.json
  if [ "$os_name" = Darwin ]; then managed_dir="/Library/Application Support/ClaudeCode"; else managed_dir=/etc/claude-code; fi
  managed_files=("$managed_dir/managed-settings.json" "$managed_dir"/managed-settings.d/*.json)
  for ((i=${#managed_files[@]}-1; i>=0; i--)); do
    [ -z "$sandbox_on" ] && [ -f "${managed_files[i]}" ] && sandbox_on=$(sandbox_value < "${managed_files[i]}")
  done

  # --settings on the claude command line, as inline JSON or a file path
  if [ -z "$sandbox_on" ]; then
    claude_pid=${CLAUDE_PID:-}
    if [ -z "$claude_pid" ]; then
      pid=$PPID
      for _ in 1 2 3 4; do
        [ "${pid:-0}" -gt 1 ] 2>/dev/null || break
        case "$(ps -o comm= -p "$pid" 2>/dev/null)" in
          claude|*/claude) claude_pid=$pid; break ;;
        esac
        pid=$(ps -o ppid= -p "$pid" 2>/dev/null | tr -d ' ')
      done
    fi
    if [ -n "$claude_pid" ]; then
      cli_settings=$(ps -ww -o args= -p "$claude_pid" 2>/dev/null | awk '{
        line = " " $0
        if (!match(line, / --settings[ =]/)) exit
        s = substr(line, RSTART + RLENGTH)
        if (substr(s, 1, 1) != "{") { split(s, parts, " "); print parts[1]; exit }
        for (j = 1; j <= length(s); j++) {
          c = substr(s, j, 1)
          if (q) { if (e) e = 0; else if (c == "\\") e = 1; else if (c == "\"") q = 0 }
          else if (c == "\"") q = 1
          else if (c == "{") d++
          else if (c == "}" && --d == 0) { print substr(s, 1, j); exit }
        }
      }')
      case "$cli_settings" in
        "") ;;
        "{"*) sandbox_on=$(printf '%s' "$cli_settings" | sandbox_value) ;;
        /*) [ -f "$cli_settings" ] && sandbox_on=$(sandbox_value < "$cli_settings") ;;
        *) [ -f "$project_dir/$cli_settings" ] && sandbox_on=$(sandbox_value < "$project_dir/$cli_settings") ;;
      esac
    fi
  fi

  # Project settings. In a git repo Claude Code keeps settings.local.json at the
  # repository root (the main checkout's root in a worktree), and that copy wins over
  # one left in the starting directory.
  if [ -z "$sandbox_on" ] && [ -n "$project_dir" ]; then
    project_files=()
    git_common=$(git -C "$project_dir" rev-parse --git-common-dir 2>/dev/null)
    if [ -n "$git_common" ]; then
      case "$git_common" in /*) ;; *) git_common="$project_dir/$git_common" ;; esac
      repo_root=$(cd "$git_common/.." 2>/dev/null && pwd -P)
      if [ -n "$repo_root" ] && [ "$repo_root" != "$(cd "$HOME" 2>/dev/null && pwd -P)" ]; then
        project_files+=("$repo_root/.claude/settings.local.json")
      fi
    fi
    project_files+=("$project_dir/.claude/settings.local.json" "$project_dir/.claude/settings.json")
    for f in "${project_files[@]}"; do
      [ -z "$sandbox_on" ] && [ -f "$f" ] && sandbox_on=$(sandbox_value < "$f")
    done
  fi

  # User settings
  user_settings="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/settings.json"
  [ -z "$sandbox_on" ] && [ -f "$user_settings" ] && sandbox_on=$(sandbox_value < "$user_settings")

  # On Linux and WSL2 the sandbox can't start without bubblewrap and socat
  if [ "$sandbox_on" = true ] && [ "$os_name" = Linux ]; then
    { command -v bwrap && command -v socat; } >/dev/null 2>&1 || sandbox_on=false
  fi

  if [ "$sandbox_on" = true ]; then
    [ -n "$output" ] && output="$output · "
    output="$output${orange}Sandbox${reset}"
  fi
fi

# Token count and progress bar
size=$(echo "$input" | jq '.context_window.context_window_size // 0')
if [ "$usage" != "null" ] && [ "$size" -gt 0 ]; then
  current=$(echo "$usage" | jq '(.input_tokens // 0) + (.cache_creation_input_tokens // 0) + (.cache_read_input_tokens // 0)')
  # Prefer the host-provided percentage (newer Claude Code); fall back to computing it
  if [ -n "$host_pct" ]; then
    pct=${host_pct%%.*}
  else
    pct=$((current * 100 / size))
  fi
  [ $pct -gt 100 ] && pct=100
  current_k=$((current / 1000))
  size_k=$((size / 1000))

  if [ $pct -lt 70 ]; then
    color='32'
  elif [ $pct -lt 80 ]; then
    color='33'
  else
    color='31'
  fi

  if [ "$SHOW_TOKEN_COUNT" = true ] || [ "$SHOW_PROGRESS_BAR" = true ]; then
    [ -n "$output" ] && output="$output · "

    if [ "$SHOW_TOKEN_COUNT" = true ]; then
      output="$output\033[${color}m${current_k}k/${size_k}k\033[0m"
    fi

    if [ "$SHOW_PROGRESS_BAR" = true ]; then
      progress_bar=$(build_progress_bar "$pct" "$color")
      [ "$SHOW_TOKEN_COUNT" = true ] && output="$output "
      output="$output${progress_bar}"
    fi
  fi
else
  if [ "$SHOW_TOKEN_COUNT" = true ] || [ "$SHOW_PROGRESS_BAR" = true ]; then
    [ -n "$output" ] && output="$output · "
    if [ "$SHOW_TOKEN_COUNT" = true ]; then
      output="$output${green}0k/0k${reset}"
    fi
    if [ "$SHOW_PROGRESS_BAR" = true ]; then
      progress_bar=$(build_progress_bar 0 '32')
      [ "$SHOW_TOKEN_COUNT" = true ] && output="$output "
      output="$output${progress_bar}"
    fi
  fi
fi

# Rate limits (5h/7d windows)
# Prints a window's used percentage, capped at 100, or nothing when the window is
# missing, null or malformed. A window counts only with a numeric used_percentage and
# a positive resets_at, so an account without a 5-hour limit shows 7d alone, not 5h:0%.
rate_limit_pct() {
  echo "$input" | jq -r --arg w "$1" '
    .rate_limits | objects | .[$w] | objects
    | select((.used_percentage | type) == "number" and .used_percentage >= 0
        and (.resets_at | type) == "number" and .resets_at > 0)
    | [.used_percentage, 100] | min | (. * 100 | round) / 100' 2>/dev/null
}

if [ "$SHOW_RATE_LIMITS" = true ]; then
  rl_5h=$(rate_limit_pct five_hour)
  rl_7d=$(rate_limit_pct seven_day)

  rl_segment=""

  if [ -n "$rl_5h" ]; then
    rl_5h_int=${rl_5h%%.*}
    if [ "$rl_5h_int" -lt 50 ]; then rl_5h_color='32'
    elif [ "$rl_5h_int" -lt 80 ]; then rl_5h_color='33'
    else rl_5h_color='31'; fi
    rl_segment="\033[${rl_5h_color}m5h:${rl_5h}%\033[0m"
  fi

  if [ -n "$rl_7d" ]; then
    rl_7d_int=${rl_7d%%.*}
    if [ "$rl_7d_int" -lt 50 ]; then rl_7d_color='32'
    elif [ "$rl_7d_int" -lt 80 ]; then rl_7d_color='33'
    else rl_7d_color='31'; fi
    [ -n "$rl_segment" ] && rl_segment="$rl_segment "
    rl_segment="$rl_segment\033[${rl_7d_color}m7d:${rl_7d}%\033[0m"
  fi

  if [ -n "$rl_segment" ]; then
    [ -n "$output" ] && output="$output · "
    output="$output${rl_segment}"
  fi
fi

# Monthly spend budget (period-to-date across all sessions on this machine)
# The host only reports the current session's cost, so each render records it to
# ~/.claude/statusline-spend/<period-start>/<session_id> (one file per session avoids
# write contention) and the segment sums every file for the current billing period.
# The period starts at the most recent SPEND_RESET_DAY/SPEND_RESET_TIME (UTC).
# Any filesystem failure degrades to the current session's cost only.
if [ "$SHOW_SPEND_BUDGET" = true ]; then
  num_re='^[0-9]+(\.[0-9]+)?$'
  int_re='^[0-9]+$'
  hm_re='^([01][0-9]|2[0-3]):[0-5][0-9]$'
  period_re='^[0-9]{4}-[0-9]{2}-[0-9]{2}$'
  session_id=$(echo "$input" | jq -r '.session_id // empty' | tr -cd 'A-Za-z0-9._-')

  # Resolve the current period start from the configured reset day/time (UTC);
  # invalid values fall back to the 1st of the month at 00:00 UTC
  reset_day=$SPEND_RESET_DAY
  { [[ "$reset_day" =~ $int_re ]] && [ "$reset_day" -ge 1 ] && [ "$reset_day" -le 28 ]; } || reset_day=1
  reset_hm=$SPEND_RESET_TIME
  [[ "$reset_hm" =~ $hm_re ]] || reset_hm="00:00"
  read -r now_y now_m now_d now_hm <<< "$(date -u '+%Y %m %d %H:%M')"
  p_y=$((10#$now_y)); p_m=$((10#$now_m)); now_d=$((10#$now_d))
  if [ "$now_d" -lt "$reset_day" ] || { [ "$now_d" -eq "$reset_day" ] && [[ "$now_hm" < "$reset_hm" ]]; }; then
    p_m=$((p_m - 1))
    [ "$p_m" -eq 0 ] && { p_m=12; p_y=$((p_y - 1)); }
  fi
  spend_period=$(printf '%04d-%02d-%02d' "$p_y" "$p_m" "$reset_day")

  spend_root="${HOME:-}/.claude/statusline-spend"
  period_dir="$spend_root/$spend_period"
  period_total=""

  if [ -n "$HOME" ] && [ -n "$session_id" ] && [[ "$cost" =~ $num_re ]]; then
    if mkdir -p "$period_dir" 2>/dev/null \
      && printf '%s\n' "$cost" > "$period_dir/.$session_id.tmp" 2>/dev/null \
      && mv -f "$period_dir/.$session_id.tmp" "$period_dir/$session_id" 2>/dev/null; then
      period_total=$(awk '$1 ~ /^[0-9]+(\.[0-9]+)?$/ { s += $1 } END { printf "%.2f", s }' "$period_dir"/* 2>/dev/null)
      # Prune previous periods
      for d in "$spend_root"/*/; do
        d=${d%/}
        d_name=${d##*/}
        if [[ "$d_name" =~ $period_re ]] && [[ "$d_name" < "$spend_period" ]]; then
          rm -rf "$d" 2>/dev/null
        fi
      done
    fi
  fi

  if [ -z "$period_total" ]; then
    if [[ "$cost" =~ $num_re ]]; then period_total=$cost; else period_total=0; fi
  fi

  spend_fmt=$(printf '$%.2f' "$period_total")
  if awk -v c="$SPEND_LIMIT_USD" 'BEGIN { exit !(c + 0 > 0) }' 2>/dev/null; then
    spend_pct=$(awk -v t="$period_total" -v c="$SPEND_LIMIT_USD" 'BEGIN { printf "%.1f", t * 100 / c }')
    cap_fmt=$(awk -v c="$SPEND_LIMIT_USD" 'BEGIN { if (c == int(c)) printf "%d", c; else printf "%.2f", c }')
    spend_int=${spend_pct%%.*}
    if [ "$spend_int" -lt 50 ]; then spend_color='32'
    elif [ "$spend_int" -lt 80 ]; then spend_color='33'
    else spend_color='31'; fi
    spend_segment="\033[${spend_color}mmo:${spend_fmt}/\$${cap_fmt} ${spend_pct}%\033[0m"
  else
    spend_segment="${yellow}mo:${spend_fmt}${reset}"
  fi

  [ -n "$output" ] && output="$output · "
  output="$output${spend_segment}"
fi

# Directory
if [ "$SHOW_DIRECTORY" = true ]; then
  [ -n "$output" ] && output="$output · "
  output="$output${blue}${current_dir}${reset}"
fi

# Git branch
if [ "$SHOW_GIT_BRANCH" = true ]; then
  [ -n "$output" ] && output="$output · "
  output="$output${magenta}${git_branch}${reset}"
fi

# Cost
if [ "$SHOW_COST" = true ]; then
  [ -n "$output" ] && output="$output · "
  output="$output${yellow}${cost_fmt}${reset}"
fi

# Duration
if [ "$SHOW_DURATION" = true ]; then
  [ -n "$output" ] && output="$output · "
  output="$output${cyan}${duration_fmt}${reset}"
fi

# Time
if [ "$SHOW_TIME" = true ]; then
  [ -n "$output" ] && output="$output · "
  output="$output${white}${current_time}${reset}"
fi

# Version
if [ "$SHOW_VERSION" = true ]; then
  [ -n "$output" ] && output="$output · "
  output="$output${gray}v${version}${reset}"
fi

printf '%b' "$output"
```

### PowerShell Script Template (Windows)

```powershell
# =============================================================================
# Claude Code Status Line (PowerShell)
# =============================================================================
# Configuration - Set these to customize your status line
# =============================================================================

$SHOW_MODEL = $true           # Show model name (e.g., "Claude Opus 4.8")
$SHOW_EFFORT = $true          # Show reasoning effort level (e.g., "high")
$SHOW_TOKEN_COUNT = $true     # Show token usage count (e.g., "50k/100k")
$SHOW_PROGRESS_BAR = $true    # Show visual progress bar
$SHOW_DIRECTORY = $true       # Show current directory name
$SHOW_GIT_BRANCH = $true      # Show current git branch
$SHOW_COST = $false           # Show session cost (useful for API/Pro users)
$SHOW_DURATION = $true        # Show session duration
$SHOW_TIME = $true            # Show current time
$SHOW_VERSION = $true         # Show Claude Code version
$SHOW_RATE_LIMITS = $true     # Show rate limit usage (5h/7d windows; a window the account doesn't have is hidden)
$SHOW_SPEND_BUDGET = $false   # Show month-to-date spend across all sessions on this machine (e.g., "mo:$47.20/$2000 2.4%")
$SPEND_LIMIT_USD = 0          # Monthly spend cap in USD for the spend segment (0 = no cap, show bare total)
$SPEND_RESET_DAY = 1          # Day of the month (1-28) the spend cap resets, in UTC
$SPEND_RESET_TIME = '00:00'   # Time of day (HH:MM, 24h, UTC) the spend cap resets

# =============================================================================

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Read JSON from stdin
$inputJson = [System.Console]::In.ReadToEnd()
$data = $inputJson | ConvertFrom-Json

$model_name = $data.model.display_name
$effort_level = $data.effort.level
$transcript_path = $data.transcript_path
$current_dir = Split-Path -Leaf "$($data.workspace.current_dir)"
$version = $data.version
$usage = $data.context_window.current_usage
$host_pct = $data.context_window.used_percentage
$cost = $data.cost.total_cost_usd
$duration_ms = $data.cost.total_duration_ms
$current_time = (Get-Date -Format "h:mmtt").ToLower()

# Ultracode reports as plain "xhigh" in the payload; detect it from the session
# transcript (the /effort command's stdout records the actual level chosen).
if ($effort_level -eq 'xhigh' -and $transcript_path -and (Test-Path $transcript_path)) {
    $effort_matches = Select-String -Path $transcript_path -Pattern '<local-command-stdout>Set effort level to ([a-z]+)' -AllMatches |
        ForEach-Object { $_.Matches }
    if ($effort_matches -and ($effort_matches | Select-Object -Last 1).Groups[1].Value -eq 'ultracode') {
        $effort_level = 'ultracode'
    }
}

# Format cost
if ($null -ne $cost) {
    $cost_fmt = '$' + ('{0:F2}' -f $cost)
} else {
    $cost_fmt = '$0.00'
}

# Format duration (ms to human readable)
if ($null -ne $duration_ms) {
    $duration_s = [math]::Floor($duration_ms / 1000)
    if ($duration_s -lt 60) {
        $duration_fmt = "${duration_s}s"
    } elseif ($duration_s -lt 3600) {
        $mins = [math]::Floor($duration_s / 60)
        $secs = $duration_s % 60
        $duration_fmt = "${mins}m ${secs}s"
    } else {
        $hours = [math]::Floor($duration_s / 3600)
        $mins = [math]::Floor(($duration_s % 3600) / 60)
        $duration_fmt = "${hours}h ${mins}m"
    }
} else {
    $duration_fmt = '0s'
}

# Get git branch
$git_branch = try {
    git -C "$($data.workspace.current_dir)" branch --show-current 2>$null
} catch { $null }
if ([string]::IsNullOrEmpty($git_branch)) {
    $git_branch = '-'
}

# ANSI color codes
$esc = [char]27
$reset = "$esc[0m"
$white = "$esc[97m"
$cyan = "$esc[36m"
$green = "$esc[32m"
$yellow = "$esc[33m"
$red = "$esc[31m"
$blue = "$esc[94m"
$magenta = "$esc[35m"
$gray = "$esc[90m"

# Build progress bar
function Build-ProgressBar {
    param (
        [int]$Percent,
        [string]$Color
    )
    $bar_width = 10
    $filled = [math]::Floor($Percent * $bar_width / 100)
    $empty = $bar_width - $filled

    $bar = ([string][char]0x2593) * $filled + ([string][char]0x2591) * $empty
    return "$Color$bar $Percent%$reset"
}

# Color each character of a string, cycling through the given 256-color codes
function Set-CharColors {
    param (
        [string]$Text,
        [int[]]$Palette
    )
    $out = ""
    for ($i = 0; $i -lt $Text.Length; $i++) {
        $code = $Palette[$i % $Palette.Count]
        $out += "$esc[38;5;${code}m$($Text[$i])"
    }
    return "$out$reset"
}

# Build output segments
$segments = @()

# Model name
if ($SHOW_MODEL) {
    $segments += "$white$model_name$reset"
}

# Effort level (absent when the model doesn't support effort)
# Colors match the /effort picker: yellow/green/light purple/dark purple/rainbow/purple explosion
if ($SHOW_EFFORT -and $effort_level) {
    switch ($effort_level) {
        'low'       { $effort_fmt = "$yellow$effort_level$reset" }
        'medium'    { $effort_fmt = "$green$effort_level$reset" }
        'high'      { $effort_fmt = "$esc[38;5;141m$effort_level$reset" }
        'xhigh'     { $effort_fmt = "$esc[38;5;93m$effort_level$reset" }
        'max'       { $effort_fmt = Set-CharColors -Text $effort_level -Palette 196, 208, 226, 46, 39, 129 }
        'ultracode' { $effort_fmt = Set-CharColors -Text ([string][char]0x2726 + $effort_level + [char]0x2726) -Palette 93, 129, 135, 141, 171, 177 }
        default     { $effort_fmt = "$white$effort_level$reset" }
    }
    $segments += $effort_fmt
}

# Token count and progress bar
$size = [long]$data.context_window.context_window_size
if ($null -ne $usage -and $size -gt 0) {
    $current = [long]$usage.input_tokens + [long]$usage.cache_creation_input_tokens + [long]$usage.cache_read_input_tokens
    # Prefer the host-provided percentage (newer Claude Code); fall back to computing it
    if ($null -ne $host_pct) {
        $pct = [math]::Min(100, [math]::Floor([double]$host_pct))
    } else {
        $pct = [math]::Min(100, [math]::Floor($current * 100 / $size))
    }
    $current_k = [math]::Floor($current / 1000)
    $size_k = [math]::Floor($size / 1000)

    if ($pct -lt 70) {
        $token_color = $green
    } elseif ($pct -lt 80) {
        $token_color = $yellow
    } else {
        $token_color = $red
    }

    $token_segment = ""
    if ($SHOW_TOKEN_COUNT) {
        $token_segment = "$token_color${current_k}k/${size_k}k$reset"
    }
    if ($SHOW_PROGRESS_BAR) {
        $progress_bar = Build-ProgressBar -Percent $pct -Color $token_color
        if ($SHOW_TOKEN_COUNT) {
            $token_segment += " $progress_bar"
        } else {
            $token_segment = $progress_bar
        }
    }
    if ($token_segment) {
        $segments += $token_segment
    }
} else {
    $token_segment = ""
    if ($SHOW_TOKEN_COUNT) {
        $token_segment = "${green}0k/0k$reset"
    }
    if ($SHOW_PROGRESS_BAR) {
        $progress_bar = Build-ProgressBar -Percent 0 -Color $green
        if ($SHOW_TOKEN_COUNT) {
            $token_segment += " $progress_bar"
        } else {
            $token_segment = $progress_bar
        }
    }
    if ($token_segment) {
        $segments += $token_segment
    }
}

# Rate limits (5h/7d windows)
# Returns a window's used percentage, capped at 100, or $null when the window is
# missing, null or malformed. A window counts only with a numeric used_percentage and
# a positive resets_at, so an account without a 5-hour limit shows 7d alone, not 5h:0%.
function Get-RateLimitPercent {
    param ($Window)
    if ($Window -isnot [System.Management.Automation.PSCustomObject]) { return $null }
    $used = $Window.used_percentage
    $resets_at = $Window.resets_at
    foreach ($value in $used, $resets_at) {
        if (-not ($value -is [int] -or $value -is [long] -or $value -is [double] -or $value -is [decimal])) { return $null }
    }
    if ([double]::IsNaN([double]$used) -or $used -lt 0 -or $resets_at -le 0) { return $null }
    return [math]::Round([math]::Min([double]$used, 100), 2)
}

if ($SHOW_RATE_LIMITS) {
    $rl = $data.rate_limits
    if ($rl -is [System.Management.Automation.PSCustomObject]) {
        $rl_parts = @()

        $rl_5h = Get-RateLimitPercent $rl.five_hour
        if ($null -ne $rl_5h) {
            if ($rl_5h -lt 50) { $rl_5h_color = $green }
            elseif ($rl_5h -lt 80) { $rl_5h_color = $yellow }
            else { $rl_5h_color = $red }
            $rl_parts += "${rl_5h_color}5h:${rl_5h}%$reset"
        }

        $rl_7d = Get-RateLimitPercent $rl.seven_day
        if ($null -ne $rl_7d) {
            if ($rl_7d -lt 50) { $rl_7d_color = $green }
            elseif ($rl_7d -lt 80) { $rl_7d_color = $yellow }
            else { $rl_7d_color = $red }
            $rl_parts += "${rl_7d_color}7d:${rl_7d}%$reset"
        }

        if ($rl_parts.Count -gt 0) {
            $segments += ($rl_parts -join " ")
        }
    }
}

# Monthly spend budget (period-to-date across all sessions on this machine)
# The host only reports the current session's cost, so each render records it to
# ~/.claude/statusline-spend/<period-start>/<session_id> (one file per session avoids
# write contention) and the segment sums every file for the current billing period.
# The period starts at the most recent SPEND_RESET_DAY/SPEND_RESET_TIME (UTC).
# Any filesystem failure degrades to the current session's cost only.
if ($SHOW_SPEND_BUDGET) {
    $inv = [System.Globalization.CultureInfo]::InvariantCulture
    $session_id = ([string]$data.session_id) -replace '[^A-Za-z0-9._-]', ''

    # Resolve the current period start from the configured reset day/time (UTC);
    # invalid values fall back to the 1st of the month at 00:00 UTC
    $reset_day = 1
    $parsed_day = 0
    if ([int]::TryParse([string]$SPEND_RESET_DAY, [ref]$parsed_day) -and $parsed_day -ge 1 -and $parsed_day -le 28) { $reset_day = $parsed_day }
    $reset_h = 0
    $reset_min = 0
    if ([string]$SPEND_RESET_TIME -match '^([01][0-9]|2[0-3]):([0-5][0-9])$') { $reset_h = [int]$Matches[1]; $reset_min = [int]$Matches[2] }
    $now_utc = [DateTime]::UtcNow
    $period_start = New-Object DateTime ($now_utc.Year, $now_utc.Month, $reset_day, $reset_h, $reset_min, 0, [DateTimeKind]::Utc)
    if ($period_start -gt $now_utc) { $period_start = $period_start.AddMonths(-1) }
    $spend_period = $period_start.ToString('yyyy-MM-dd', $inv)

    $home_dir = if ($HOME) { $HOME } else { $env:USERPROFILE }
    $period_total = $null

    if ($home_dir -and $session_id -and $null -ne $cost) {
        try {
            $spend_root = Join-Path (Join-Path $home_dir '.claude') 'statusline-spend'
            $period_dir = Join-Path $spend_root $spend_period
            New-Item -ItemType Directory -Path $period_dir -Force -ErrorAction Stop | Out-Null
            $tmp_file = Join-Path $period_dir ".$session_id.tmp"
            [System.IO.File]::WriteAllText($tmp_file, ([double]$cost).ToString('R', $inv) + "`n")
            Move-Item -LiteralPath $tmp_file -Destination (Join-Path $period_dir $session_id) -Force -ErrorAction Stop

            $sum = 0.0
            foreach ($f in Get-ChildItem -LiteralPath $period_dir -File -ErrorAction Stop | Where-Object { $_.Name -notlike '*.tmp' }) {
                try {
                    $v = 0.0
                    $txt = [System.IO.File]::ReadAllText($f.FullName).Trim()
                    if ([double]::TryParse($txt, [System.Globalization.NumberStyles]::Float, $inv, [ref]$v)) { $sum += $v }
                } catch { }
            }
            $period_total = $sum

            # Prune previous periods
            foreach ($d in Get-ChildItem -LiteralPath $spend_root -Directory -ErrorAction SilentlyContinue) {
                if ($d.Name -match '^\d{4}-\d{2}-\d{2}$' -and [string]::CompareOrdinal($d.Name, $spend_period) -lt 0) {
                    try { Remove-Item -LiteralPath $d.FullName -Recurse -Force -ErrorAction SilentlyContinue } catch { }
                }
            }
        } catch {
            $period_total = $null
        }
    }

    if ($null -eq $period_total) {
        $period_total = if ($null -ne $cost) { [double]$cost } else { 0.0 }
    }

    $spend_fmt = '$' + ('{0:F2}' -f $period_total)
    $cap = 0.0
    if ([double]::TryParse([string]$SPEND_LIMIT_USD, [System.Globalization.NumberStyles]::Float, $inv, [ref]$cap) -and $cap -gt 0) {
        $spend_pct = $period_total * 100 / $cap
        $spend_pct_fmt = '{0:F1}' -f $spend_pct
        $cap_fmt = if ($cap -eq [math]::Floor($cap)) { '{0:F0}' -f $cap } else { '{0:F2}' -f $cap }
        if ($spend_pct -lt 50) { $spend_color = $green }
        elseif ($spend_pct -lt 80) { $spend_color = $yellow }
        else { $spend_color = $red }
        $segments += "${spend_color}mo:${spend_fmt}/`$${cap_fmt} ${spend_pct_fmt}%$reset"
    } else {
        $segments += "${yellow}mo:${spend_fmt}$reset"
    }
}

# Directory
if ($SHOW_DIRECTORY) {
    $segments += "$blue$current_dir$reset"
}

# Git branch
if ($SHOW_GIT_BRANCH) {
    $segments += "$magenta$git_branch$reset"
}

# Cost
if ($SHOW_COST) {
    $segments += "$yellow$cost_fmt$reset"
}

# Duration
if ($SHOW_DURATION) {
    $segments += "$cyan$duration_fmt$reset"
}

# Time
if ($SHOW_TIME) {
    $segments += "$white$current_time$reset"
}

# Version
if ($SHOW_VERSION) {
    $segments += "${gray}v$version$reset"
}

$sep = " " + [char]0x00B7 + " "
Write-Host -NoNewline ($segments -join $sep)
```

## Configuration Variables

| Variable | Default | Description |
|----------|---------|-------------|
| SHOW_MODEL | true | Display model name (e.g., "Claude Opus 4.8") |
| SHOW_EFFORT | true | Display reasoning effort level with /effort-matched colors |
| SHOW_SANDBOX | false | Display "Sandbox" in orange after the effort level while Claude Code's Bash sandbox is on (Bash script only) |
| SHOW_TOKEN_COUNT | true | Display token usage (e.g., "50k/100k") |
| SHOW_PROGRESS_BAR | true | Display visual progress bar with percentage |
| SHOW_DIRECTORY | true | Display current working directory name |
| SHOW_GIT_BRANCH | true | Display current git branch |
| SHOW_COST | false | Display session cost in USD |
| SHOW_DURATION | true | Display session duration |
| SHOW_TIME | true | Display current time |
| SHOW_VERSION | true | Display Claude Code version |
| SHOW_RATE_LIMITS | true | Display rate limit usage (5h/7d windows). Each window is hidden when the payload has no usable one, so an account without a 5-hour limit shows `7d` alone. The whole segment is hidden when the payload has no `rate_limits` |
| SHOW_SPEND_BUDGET | false | Display month-to-date spend across all sessions on this machine (e.g., "mo:$47.20/$2000 2.4%") |
| SPEND_LIMIT_USD | 0 | Monthly spend cap in USD for the spend segment; `0` = no cap, show the bare total |
| SPEND_RESET_DAY | 1 | Day of the month (1-28) the spend cap resets, in UTC; invalid values fall back to 1 |
| SPEND_RESET_TIME | 00:00 | Time of day (HH:MM, 24-hour, UTC) the spend cap resets; invalid values fall back to 00:00 |

### Monthly spend budget caveats

The spend segment exists for accounts that have no rolling rate limits (Enterprise seats and API-billed usage with a monthly spend cap). Make sure the user sees these caveats when they enable it:

- **Local estimate only.** The figure is Claude Code's own `cost.total_cost_usd` estimate and will NOT match the Anthropic console (in one observed case the console showed $0.96 spent while a single live session already reported $1.11). The authoritative sources are the console usage page or the Admin API cost report, which requires an org admin key most seat users do not have.
- **No historical backfill.** Only sessions rendered after the segment was enabled are counted.
- **This machine only.** Counts Claude Code sessions on this machine, not claude.ai web/desktop usage or other machines.
- **How it works.** Each render writes the current session's cost to `~/.claude/statusline-spend/<period-start>/<session_id>` (one file per session so concurrent sessions never contend). The period starts at the most recent `SPEND_RESET_DAY` / `SPEND_RESET_TIME` in UTC, so the directory is named for that date (e.g., `2026-09-01`). The segment sums every file in the current period's directory and prunes older period directories. If the directory cannot be created or written (read-only home, missing `HOME`), the segment silently falls back to showing the current session's cost.
- **Reset timing.** The reset is not in the status line payload for accounts without `rate_limits`, so the user supplies it. The default (1st of the month, 00:00 UTC) matches the Anthropic console, which displays the same instant in local time (e.g., "Resets Wed, Sep 30, 8:00 PM EDT" is Oct 1 00:00 UTC). The total rolls over at that moment; sessions that span the reset count toward the new period in full, since only their latest cumulative cost is recorded.

## Important Notes

- The scripts require `jq` to be installed on Mac/Linux for JSON parsing
- PowerShell scripts work on Windows PowerShell 5.1+ and PowerShell Core 7+
- Unicode progress bar characters should work on modern terminals
- Colors use ANSI escape codes which work on most modern terminals
- Status line updates appear immediately after setup
- The effort segment reads `.effort.level` from the status line payload and is hidden entirely when the current model doesn't support the effort parameter (the field is absent)
- Effort colors match the `/effort` picker: yellow (low), green (medium), light purple (high), dark purple (xhigh), per-character rainbow (max), and a purple-explosion `✦ultracode✦` treatment
- Ultracode reports as plain `xhigh` in the payload, so the scripts detect it by grepping the session transcript (`.transcript_path`) for the most recent `/effort` command output ("Set effort level to …"); if a session starts in ultracode without `/effort` ever being run, it displays as `xhigh`
- The rate-limit segment reads `.rate_limits.five_hour` / `.rate_limits.seven_day`, which the host only sends for plans with rolling usage windows (Pro, Max and Ultra). Enterprise seats and API-billed accounts on a monthly spend cap receive no `rate_limits` key at all, so with `SHOW_RATE_LIMITS=true` the segment is hidden rather than showing zeros. Those users should enable `SHOW_SPEND_BUDGET` (and set `SPEND_LIMIT_USD` to their cap) to get a comparable month-to-date view
- Each rate-limit window renders on its own, and only when it has a numeric `used_percentage` and a positive `resets_at` (Unix epoch seconds). Verified Ultra accounts have no 5-hour limit, so the host sends no `five_hour` window and the segment shows `7d:` alone. Newer Ultra accounts keep a 5-hour limit until they're verified. A window that is missing, null, empty or malformed is left out, never shown as `0%` or `N/A`, and leaves no extra separator or space. Values above 100 are capped at 100
- The context percentage prefers the host-provided `.context_window.used_percentage` (newer Claude Code versions) and falls back to computing it from `current_usage` for older versions
- The status line payload has no sandbox field, so the sandbox segment resolves `sandbox.enabled` from the settings layers in Claude Code's order, where the first layer that sets it wins: managed settings (`managed-settings.json` and `managed-settings.d/` in `/Library/Application Support/ClaudeCode/` or `/etc/claude-code/`), `--settings` on the `claude` command line (inline JSON or a file path, read from the process found through `$CLAUDE_PID` or by walking up the process tree), `.claude/settings.local.json` (at the repository root, or the main checkout's root in a worktree, then the starting directory), `.claude/settings.json` in `workspace.project_dir`, and `~/.claude/settings.json` (or `$CLAUDE_CONFIG_DIR/settings.json`). A `/sandbox` change shows up on the next render
- The sandbox segment shows the configured state. It can't read MDM profiles or server-managed settings, and on Linux and WSL2 it stays hidden when `bwrap` or `socat` is missing, because the sandbox can't start without them. Other startup failures, such as an AppArmor rule that blocks bubblewrap, aren't detected, so for an audit, confirm with a probe such as `touch ~/sandbox-probe`, which should fail
- The PowerShell script has no sandbox segment, because the sandbox doesn't run on native Windows
