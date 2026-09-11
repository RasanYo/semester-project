---
name: step-04-ralph-import
description: Export issue body and run ralph-import to generate Ralph files
prev_step: steps/step-03-push-branch.md
next_step: steps/step-05-copy-ralph-files.md
---

# Step 4: Export Issue and Run Ralph Import

## MANDATORY EXECUTION RULES:

- 🛑 NEVER ask for confirmation - execute immediately
- 🛑 NEVER skip the ralph-import step - it generates critical files
- ✅ ALWAYS export the full issue body (not just the title)
- ✅ ALWAYS wait for ralph-import to complete before proceeding
- ✅ ALWAYS proceed immediately to next step

## YOUR TASK:

Export the GitHub issue body to a temp file and run `ralph-import` to generate PROMPT.md, fix_plan.md, and specs/ from the issue description.

---

## EXECUTION SEQUENCE:

### 1. Verify State Variables

Confirm you have these from previous steps:

```yaml
{feature_description}: # Full description from user
{short_title}: # Extracted title (max 50 chars)
{slug}: # URL-safe slug (max 40 chars)
{issue_number}: # Number from created issue
{issue_url}: # Full URL of created issue
{branch_name}: # Full branch name (feature/{number}-{slug})
```

### 2. Ensure Working Directory is Repo Root

Navigate to the repository root so all relative paths (`.ralph/`, temp directories) resolve correctly. This is critical for Claude Code Remote where the session cwd may not be the repo root.

```bash
cd "$(git rev-parse --show-toplevel)"
```

### 3. Export Issue Body to Temp File

**If `{transport}` is `"local"`:**

```bash
gh issue view {issue_number} --json body --jq '.body' > /tmp/ralph-feature-{issue_number}.md
```

**If `{transport}` is `"remote"`:**

Write `{feature_description}` directly to the temp file (we already have the issue body — no need to re-fetch from GitHub):

```bash
cat <<'ISSUE_EOF' > /tmp/ralph-feature-{issue_number}.md
{feature_description}
ISSUE_EOF
```

This extracts the full issue description (which was generated from the user's feature description in step-01).

### 4. Run Ralph Import

Execute the following command:

```bash
ralph-import /tmp/ralph-feature-{issue_number}.md temp-ralph-import-{issue_number}
```

**What this does:**
- Creates a new directory `temp-ralph-import-{issue_number}/` in the current working directory
- Uses Claude to intelligently convert the issue description into:
  - `.ralph/PROMPT.md` — Ralph development instructions with full context
  - `.ralph/fix_plan.md` — Prioritized task breakdown
  - `.ralph/specs/requirements.md` — Detailed technical specifications
- This command takes ~2 minutes as it invokes Claude internally

**Important:** Wait for the command to complete. Do not proceed until ralph-import has finished.

### 5. Verify Import Success

Check that the generated files exist:

```bash
ls -la temp-ralph-import-{issue_number}/.ralph/PROMPT.md
ls -la temp-ralph-import-{issue_number}/.ralph/fix_plan.md
ls -la temp-ralph-import-{issue_number}/.ralph/specs/
```

All three must exist before proceeding.

### 6. Set State Variables

```yaml
{temp_import_dir}: "temp-ralph-import-{issue_number}"
```

### 7. Proceed to Next Step

Immediately load `steps/step-05-copy-ralph-files.md` with all state variables.

---

## SUCCESS METRICS:

✅ Issue body exported to /tmp/ralph-feature-{issue_number}.md
✅ ralph-import completed successfully
✅ PROMPT.md exists in temp directory
✅ fix_plan.md exists in temp directory
✅ specs/ directory exists in temp directory
✅ {temp_import_dir} state variable set
✅ Proceeding to step-05

## FAILURE MODES:

❌ `gh` command fails → Check authentication with `gh auth status`
❌ Issue body is empty → Stop with error: "Issue #{issue_number} has no description"
❌ `ralph-import` not found → Error: "ralph-import not installed. Run: git clone https://github.com/frankbria/ralph-claude-code.git && cd ralph-claude-code && ./install.sh"
❌ `ralph-import` fails → Capture error output and stop. Do not proceed with empty files.
❌ Generated files missing → ralph-import may have partially failed. Check logs and stop.

## ERROR HANDLING:

If ralph-import fails:
1. Capture the error output
2. Output: "Failed to generate Ralph files: {error}"
3. Clean up temp directory if it was created
4. Do NOT proceed to next step
5. Do NOT launch Ralph with generic/empty files

## EXAMPLE EXECUTION:

**Input state:**
```yaml
{issue_number}: "27"
{slug}: "add-portfolio-dashboard"
```

**Commands executed:**
```bash
gh issue view 27 --json body --jq '.body' > /tmp/ralph-feature-27.md
ralph-import /tmp/ralph-feature-27.md temp-ralph-import-27
```

**Verification:**
```bash
ls -la temp-ralph-import-27/.ralph/PROMPT.md
ls -la temp-ralph-import-27/.ralph/fix_plan.md
ls -la temp-ralph-import-27/.ralph/specs/
```

**Updated state:**
```yaml
{temp_import_dir}: "temp-ralph-import-27"
```

## NEXT STEP:

Load `steps/step-05-copy-ralph-files.md`

<critical>
This is a no-confirmation skill. Export, import, and proceed immediately.
Do not ask the user for approval - just execute and continue.
ralph-import takes ~2 minutes — wait for it to finish, do not proceed early.
</critical>
