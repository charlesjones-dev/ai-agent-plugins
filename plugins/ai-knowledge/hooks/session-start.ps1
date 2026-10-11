# ai-knowledge SessionStart hook for Windows without Git Bash, where Claude Code runs hooks in PowerShell.
# Same logic as session-start.sh: prints the auto-capture instruction when the project has a 2.x
# knowledge base and this developer turned auto-capture on. Otherwise it prints nothing.
# hooks.json loads this file as a script block, so the execution policy doesn't block it.

$kbDir = if ($env:CLAUDE_PROJECT_DIR) { $env:CLAUDE_PROJECT_DIR } else { (Get-Location).Path }
if (-not (Test-Path -LiteralPath (Join-Path $kbDir '.claude/rules/kb/_index.md'))) { exit 0 }

$kbSetting = $env:AI_KNOWLEDGE_AUTO_CAPTURE
if (-not $kbSetting -and (Get-Command git -ErrorAction SilentlyContinue)) {
  $kbSetting = (& git -C $kbDir config --get ai-knowledge.autoCapture 2>$null) -join ''
}
if ("$kbSetting".Trim() -notmatch '^(1|true|on|yes)$') { exit 0 }

$kbRoot = if ($env:CLAUDE_PLUGIN_ROOT) { $env:CLAUDE_PLUGIN_ROOT } else { Split-Path -Parent $PSScriptRoot }
$kbText = Join-Path $kbRoot 'hooks/auto-capture.txt'
if (Test-Path -LiteralPath $kbText) { Get-Content -Raw -LiteralPath $kbText }
exit 0
