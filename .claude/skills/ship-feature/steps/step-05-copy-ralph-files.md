---
name: step-05-copy-ralph-files
description: Copy generated Ralph files into project .ralph/ and clean up temp directory
prev_step: steps/step-04-ralph-import.md
next_step: steps/step-06-show-and-launch.md
---

# Step 5: Copy Ralph Files and Clean Up

## MANDATORY EXECUTION RULES:

- 🛑 NEVER ask for confirmation - execute immediately
- 🛑 NEVER overwrite .ralphrc or AGENT.md - those are project-level configs
- 🛑 NEVER leave the temp directory behind
- ✅ ALWAYS overwrite PROMPT.md and fix_plan.md (they are feature-specific)
- ✅ ALWAYS merge specs/ contents (don't wipe existing specs)
- ✅ ALWAYS clean up temp directory and temp file
- ✅ ALWAYS proceed immediately to next step

## YOUR TASK:

Copy the generated PROMPT.md, fix_plan.md, and specs/ from the temp import directory into the project's `.ralph/` directory, then clean up.

---

## EXECUTION SEQUENCE:

### 1. Verify State Variables

Confirm you have these from previous steps:

```yaml
{issue_number}: # Number from created issue
{temp_import_dir}: # e.g., "temp-ralph-import-27"
```

### 2. Copy PROMPT.md

Overwrite the generic PROMPT.md with the feature-specific one:

```bash
cp {temp_import_dir}/.ralph/PROMPT.md .ralph/PROMPT.md
```

### 3. Copy fix_plan.md

Overwrite the generic fix_plan.md with the feature-specific one:

```bash
cp {temp_import_dir}/.ralph/fix_plan.md .ralph/fix_plan.md
```

### 4. Copy specs/

Merge specs from the import into the project's specs directory:

```bash
cp -r {temp_import_dir}/.ralph/specs/* .ralph/specs/ 2>/dev/null || true
```

**Note:** Using `|| true` in case specs/ is empty in the import (unlikely but safe).

### 5. Verify Files Were Copied

```bash
ls -la .ralph/PROMPT.md .ralph/fix_plan.md .ralph/specs/
```

Confirm PROMPT.md and fix_plan.md have recent timestamps (just copied).

### 6. Clean Up Temp Directory

Remove the temporary import directory:

```bash
rm -rf {temp_import_dir}
```

**This is safe to rm -rf because:**
- It's a temp directory we just created
- It contains only generated files
- The useful files have already been copied to .ralph/

### 7. Clean Up Temp File

Remove the exported issue body:

```bash
rm -f /tmp/ralph-feature-{issue_number}.md
```

### 8. Proceed to Next Step

Immediately load `steps/step-06-show-and-launch.md` with all state variables.

---

## SUCCESS METRICS:

✅ .ralph/PROMPT.md overwritten with feature-specific content
✅ .ralph/fix_plan.md overwritten with feature-specific content
✅ .ralph/specs/ populated with generated specs
✅ .ralphrc NOT modified (project config preserved)
✅ .ralph/AGENT.md NOT modified (build config preserved)
✅ Temp import directory deleted
✅ Temp issue file deleted
✅ Proceeding to step-06

## FAILURE MODES:

❌ .ralph/ doesn't exist → Error: "Ralph not enabled in this project. Run: ralph-enable-ci"
❌ Copy fails (permissions) → Check filesystem permissions on .ralph/
❌ Temp directory already deleted → Skip cleanup, proceed

## ERROR HANDLING:

If copy fails:
1. Check if .ralph/ directory exists
2. If not: run `ralph-enable-ci` to create it, then retry copies
3. If permissions issue: stop and report error

## EXAMPLE EXECUTION:

**Input state:**
```yaml
{issue_number}: "27"
{temp_import_dir}: "temp-ralph-import-27"
```

**Commands executed:**
```bash
cp temp-ralph-import-27/.ralph/PROMPT.md .ralph/PROMPT.md
cp temp-ralph-import-27/.ralph/fix_plan.md .ralph/fix_plan.md
cp -r temp-ralph-import-27/.ralph/specs/* .ralph/specs/ 2>/dev/null || true
rm -rf temp-ralph-import-27
rm -f /tmp/ralph-feature-27.md
```

**Verification:**
```bash
ls -la .ralph/PROMPT.md .ralph/fix_plan.md .ralph/specs/
```

## NEXT STEP:

Load `steps/step-06-show-and-launch.md`

<critical>
This is a no-confirmation skill. Copy files, clean up, and proceed immediately.
Do not ask the user for approval - just execute and continue.
Do NOT touch .ralphrc or AGENT.md - only PROMPT.md, fix_plan.md, and specs/.
</critical>
