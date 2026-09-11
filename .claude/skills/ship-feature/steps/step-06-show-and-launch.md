---
name: step-06-show-and-launch
description: Display generated Ralph files and launch Ralph (plain or --monitor based on launch_mode)
prev_step: steps/step-05-copy-ralph-files.md
next_step: steps/step-07-push-and-pr.md
---

# Step 6: Show Files and Launch Ralph

## MANDATORY EXECUTION RULES:

- 🛑 NEVER ask for confirmation - launch Ralph automatically
- 🛑 NEVER skip showing the generated files
- ✅ ALWAYS display PROMPT.md and fix_plan.md content before launching
- ✅ ALWAYS launch Ralph (plain `ralph` for remote, `ralph --monitor` for local)
- ✅ ALWAYS show issue URL and branch name in summary
- ✅ ALWAYS proceed to step-07 after Ralph returns

## YOUR TASK:

Display the generated Ralph files so the user can see them in the output, then launch Ralph. After Ralph completes, proceed to step-07.

---

## EXECUTION SEQUENCE:

### 1. Display Summary Banner

Output the following:

```
╔════════════════════════════════════════════════════════════╗
║                    🚀 SHIP-FEATURE READY                   ║
╠════════════════════════════════════════════════════════════╣
║ Issue: #{issue_number} - {short_title}
║ Branch: {branch_name}
║ URL: {issue_url}
║ Mode: {launch_mode}
╚════════════════════════════════════════════════════════════╝
```

### 2. Display Generated PROMPT.md

Read and display the contents of `.ralph/PROMPT.md`:

```bash
cat .ralph/PROMPT.md
```

Show this to the user so they can see what Ralph will work from.

### 3. Display Generated fix_plan.md

Read and display the contents of `.ralph/fix_plan.md`:

```bash
cat .ralph/fix_plan.md
```

Show this to the user so they can see the task breakdown.

### 4. Display specs/ Contents

List the specs directory and show file names:

```bash
ls .ralph/specs/
```

### 5. Launch Ralph

Branch on `{transport}` and `{launch_mode}`:

**If `{transport}` is `"remote"`:**

```bash
ralph
```

Plain `ralph` runs in the foreground. The Claude Code Remote session captures stdout naturally. Never use `--monitor` in remote (no tmux). This call blocks until Ralph finishes.

**If `{transport}` is `"local"` and `{launch_mode}` is `"local"`:**

```bash
ralph --monitor
```

If tmux is not installed, fall back to:

```bash
ralph --live
```

`ralph --monitor` opens a tmux session with a live monitoring dashboard. `ralph --live` runs in the foreground with streaming output.

**If `{transport}` is `"local"` and `{launch_mode}` is `"remote"` (default):**

```bash
ralph
```

Plain `ralph` runs in the foreground with stdout output.

### 6. Proceed to Next Step

After Ralph returns (the blocking call completes), immediately load `steps/step-07-push-and-pr.md` with all state variables.

---

## SUCCESS METRICS:

✅ Summary banner displayed with issue/branch info and launch mode
✅ PROMPT.md content shown to user
✅ fix_plan.md content shown to user
✅ specs/ listing shown
✅ Ralph launched and completed
✅ Proceeding to step-07

## FAILURE MODES:

❌ `ralph` command not found → Error: "Ralph not installed. Run: git clone https://github.com/frankbria/ralph-claude-code.git && cd ralph-claude-code && ./install.sh"
❌ tmux not installed (local mode) → Fall back to `ralph --live`
❌ .ralph/PROMPT.md is empty/generic → Warning but proceed (ralph-import may have partially failed)
❌ .ralph/fix_plan.md has no tasks → Warning: "No tasks generated. Review .ralph/fix_plan.md before Ralph starts."

## ERROR HANDLING:

If `ralph` fails (any mode):
1. Capture the error output
2. Report the error
3. Still proceed to step-07 — commits made before the failure should still be pushed

If `ralph --monitor` fails (local mode only):
1. Check if tmux is installed: `which tmux`
2. If not installed, run `ralph --live` instead
3. If ralph itself fails, capture error and report

If ralph is not installed:
1. Output installation instructions
2. Stop - do not attempt to install automatically

## NEXT STEP:

Load `steps/step-07-push-and-pr.md`

<critical>
This is a no-confirmation skill. Show files and launch Ralph immediately.
Do not ask the user if they want to review first - just show and launch.
After Ralph completes, proceed to step-07 to push commits and open a PR.
</critical>
