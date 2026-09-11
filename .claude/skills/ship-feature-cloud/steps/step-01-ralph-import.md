---
name: step-01-ralph-import
description: Export feature description and run ralph-import to generate Ralph files
prev_step: steps/step-00-init.md
next_step: steps/step-02-copy-ralph-files.md
---

# Step 1: Export Description and Run Ralph Import

## MANDATORY EXECUTION RULES:

- NEVER ask for confirmation - execute immediately
- NEVER skip the ralph-import step - it generates critical files
- ALWAYS export the full feature description
- ALWAYS wait for ralph-import to complete before proceeding
- ALWAYS proceed immediately to next step

## YOUR TASK:

Export the feature description to a temp file and run `ralph-import` to generate PROMPT.md, fix_plan.md, and specs/.

---

## EXECUTION SEQUENCE:

### 1. Verify State Variables

Confirm you have these from step-00:

```yaml
{feature_description}: # Full description from user
{short_title}: # Extracted title (max 50 chars)
{slug}: # URL-safe slug (max 40 chars)
{current_branch}: # Current session branch
```

### 2. Ensure Working Directory is Repo Root

Navigate to the repository root so all relative paths resolve correctly:

```bash
cd "$(git rev-parse --show-toplevel)"
```

### 3. Export Description to Temp File

Write the feature description directly to a temp file:

```bash
cat <<'DESC_EOF' > /tmp/ralph-cloud-{slug}.md
{feature_description}
DESC_EOF
```

### 4. Run Ralph Import

Execute the following command:

```bash
ralph-import /tmp/ralph-cloud-{slug}.md temp-ralph-cloud-{slug}
```

**What this does:**
- Creates a new directory `temp-ralph-cloud-{slug}/` in the current working directory
- Uses Claude to convert the description into:
  - `.ralph/PROMPT.md` — Ralph development instructions with full context
  - `.ralph/fix_plan.md` — Prioritized task breakdown
  - `.ralph/specs/requirements.md` — Detailed technical specifications
- This command takes ~2 minutes as it invokes Claude internally

**Important:** Wait for the command to complete. Do not proceed until ralph-import has finished.

### 5. Verify Import Success

Check that the generated files exist:

```bash
ls -la temp-ralph-cloud-{slug}/.ralph/PROMPT.md
ls -la temp-ralph-cloud-{slug}/.ralph/fix_plan.md
ls -la temp-ralph-cloud-{slug}/.ralph/specs/
```

All three must exist before proceeding.

### 6. Set State Variables

```yaml
{temp_import_dir}: "temp-ralph-cloud-{slug}"
```

### 7. Proceed to Next Step

Immediately load `steps/step-02-copy-ralph-files.md` with all state variables.

---

## SUCCESS METRICS:

Description exported to /tmp/ralph-cloud-{slug}.md
ralph-import completed successfully
PROMPT.md exists in temp directory
fix_plan.md exists in temp directory
specs/ directory exists in temp directory
{temp_import_dir} state variable set
Proceeding to step-02

## FAILURE MODES:

`ralph-import` not found -> Error: "ralph-import not installed. Ensure environment setup script has run."
`ralph-import` fails -> Capture error output and stop. Do not proceed with empty files.
Generated files missing -> ralph-import may have partially failed. Check logs and stop.

## ERROR HANDLING:

If ralph-import fails:
1. Capture the error output
2. Output: "Failed to generate Ralph files: {error}"
3. Clean up temp directory if it was created
4. Do NOT proceed to next step
5. Do NOT launch Ralph with generic/empty files

## NEXT STEP:

Load `steps/step-02-copy-ralph-files.md`

<critical>
This is a no-confirmation skill. Export, import, and proceed immediately.
Do not ask the user for approval - just execute and continue.
ralph-import takes ~2 minutes — wait for it to finish, do not proceed early.
</critical>
