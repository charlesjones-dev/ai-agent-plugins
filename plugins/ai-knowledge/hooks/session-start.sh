#!/bin/sh
# ai-knowledge SessionStart hook (macOS, Linux, and Windows with Git Bash).
# Prints the auto-capture instruction when the project has a 2.x knowledge base
# and this developer turned auto-capture on. Otherwise it prints nothing.
# Setting: AI_KNOWLEDGE_AUTO_CAPTURE in the environment, else git config ai-knowledge.autoCapture.

dir=${CLAUDE_PROJECT_DIR:-$PWD}
[ -f "$dir/.claude/rules/kb/_index.md" ] || exit 0

setting=${AI_KNOWLEDGE_AUTO_CAPTURE-}
if [ -z "$setting" ] && command -v git >/dev/null 2>&1; then
  setting=$(git -C "$dir" config --get ai-knowledge.autoCapture 2>/dev/null)
fi

case $setting in
  1|[Tt][Rr][Uu][Ee]|[Oo][Nn]|[Yy][Ee][Ss]) ;;
  *) exit 0 ;;
esac

root=${CLAUDE_PLUGIN_ROOT:-$(dirname "$0")/..}
cat "$root/hooks/auto-capture.txt" 2>/dev/null
exit 0
