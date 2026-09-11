#!/usr/bin/env bash
# PostToolUse(Bash) — after a merge, remind Claude to record the work in DEVLOG.md.
#
# The harness runs this, so it does not depend on Claude remembering a rule. It
# only *reminds*: the decision to write an entry (and whether the work even
# deserves one) stays with the model, which is why this injects context rather
# than blocking anything.
set -uo pipefail

command=$(jq -r '.tool_input.command // ""' 2>/dev/null) || exit 0

case "$command" in
  *"gh pr merge"*|*"git merge"*) ;;
  *) exit 0 ;;
esac

cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"A merge just ran. If it brought a substantial piece of work into `develop` — a layer reworked, a module added, a new capability, a result established — write a DEVLOG.md entry for it now, following `.claude/commands/devlog.md`: gather the range with git log, draft the entry in French, show it, and commit DEVLOG.md on its own once approved. Skip it for a config sync, a typo, a one-file fix, or a merge into anything other than develop — say in one line that you are skipping and why, then carry on. Do not ask the user whether to write it; decide, and act."}}
JSON
