---
name: step-03-show-and-launch
description: Display generated Ralph files, launch Ralph (plain only), stop with summary pointing to web UI PR button
prev_step: steps/step-02-copy-ralph-files.md
next_step: null
---

# Step 3: Show Files, Launch Ralph, and Stop

## MANDATORY EXECUTION RULES:

- NEVER ask for confirmation - launch Ralph automatically
- NEVER skip showing the generated files
- NEVER use ralph --monitor or --live - plain ralph only (no tmux in cloud)
- NEVER create a PR or push branches after Ralph finishes
- ALWAYS display PROMPT.md and fix_plan.md content before launching
- ALWAYS show current branch name in summary
- ALWAYS stop after Ralph with a summary pointing to the web UI's PR button

## YOUR TASK:

Display the generated Ralph files, launch Ralph, and stop with a summary. Do NOT attempt any post-Ralph git operations (no push, no PR creation).

---

## EXECUTION SEQUENCE:

### 1. Display Summary Banner

Output the following:

```
========================================================
              SHIP-FEATURE-CLOUD READY
========================================================
 Branch: {current_branch}
 Feature: {short_title}
========================================================
```

### 2. Display Generated PROMPT.md

Read and display the contents of `.ralph/PROMPT.md`:

```bash
cat .ralph/PROMPT.md
```

### 3. Display Generated fix_plan.md

Read and display the contents of `.ralph/fix_plan.md`:

```bash
cat .ralph/fix_plan.md
```

### 4. Display specs/ Contents

List the specs directory and show file names:

```bash
ls .ralph/specs/
```

### 5. Launch Ralph

Always use plain `ralph` — never `--monitor` or `--live` (no tmux in cloud VMs):

```bash
ralph
```

This call blocks until Ralph finishes. Ralph's commits accumulate on the current session branch.

### 6. Display Completion Summary

After Ralph returns, output:

```
========================================================
              SHIP-FEATURE-CLOUD COMPLETE
========================================================
 Branch: {current_branch}
 Feature: {short_title}
 Status: Ralph has finished. Commits are on the session branch.

 NEXT STEP: Use the web UI's "Create PR" button to open
 a pull request when you're ready.
========================================================
```

**STOP HERE.** Do not attempt to push, create PRs, or perform any further git operations.

---

## SUCCESS METRICS:

Summary banner displayed with branch and feature info
PROMPT.md content shown
fix_plan.md content shown
specs/ listing shown
Ralph launched (plain) and completed
Completion summary displayed with PR button guidance
No post-Ralph git operations attempted

## FAILURE MODES:

`ralph` command not found -> Error: "Ralph not installed. Ensure environment setup script has run."
.ralph/PROMPT.md is empty/generic -> Warning but proceed
.ralph/fix_plan.md has no tasks -> Warning: "No tasks generated. Review .ralph/fix_plan.md."

## ERROR HANDLING:

If `ralph` fails:
1. Capture the error output
2. Report the error
3. Still display the completion summary — partial commits may exist on the branch

If ralph is not installed:
1. Output: "ralph command not found. Ensure the environment setup script has installed ralph."
2. Stop

<critical>
This is a no-confirmation skill. Show files and launch Ralph immediately.
Do not ask the user if they want to review first - just show and launch.
After Ralph completes, STOP. Do NOT push, do NOT create a PR.
The user will use the web UI's "Create PR" button.
</critical>
