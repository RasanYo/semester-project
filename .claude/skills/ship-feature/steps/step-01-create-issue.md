---
name: step-01-create-issue
description: Create GitHub issue from feature description without confirmation
prev_step: steps/step-00-init.md
next_step: steps/step-02-create-branch.md
---

# Step 1: Create GitHub Issue

## MANDATORY EXECUTION RULES:

- 🛑 NEVER ask for confirmation - execute immediately
- 🛑 NEVER modify user's description - use as issue body
- ✅ ALWAYS use the correct transport (gh CLI or MCP tool)
- ✅ ALWAYS capture issue number from output
- ✅ ALWAYS proceed immediately to next step

## YOUR TASK:

Create a GitHub issue using the extracted title and full description. Use `gh` CLI locally or GitHub MCP tools in Remote.

---

## EXECUTION SEQUENCE:

### 1. Verify State Variables

Confirm you have these from step-00:

```yaml
{feature_description}: # Full description from user
{short_title}: # Extracted title (max 50 chars)
{slug}: # URL-safe slug (max 40 chars)
{transport}: # "local" or "remote"
{repo_owner}: # GitHub repo owner
{repo_name}: # GitHub repo name
```

### 2. Create GitHub Issue

**If `{transport}` is `"local"`:**

```bash
gh issue create --title "{short_title}" --body "{feature_description}"
```

The command outputs a URL like: `https://github.com/owner/repo/issues/42`

Extract the issue number from the trailing path segment.

**If `{transport}` is `"remote"`:**

Use the GitHub MCP tool to create the issue:

```
Tool: mcp__github__create_issue
Parameters:
  owner: "{repo_owner}"
  repo: "{repo_name}"
  title: "{short_title}"
  body: "{feature_description}"
```

Extract the issue number and URL from the MCP tool response.

### 3. Capture Issue Number

```yaml
{issue_number}: # Extracted from URL or MCP response (e.g., "42")
{issue_url}: # Full GitHub issue URL
```

### 4. Set State Variables

After successful creation, update state:

```yaml
{feature_description}: # (unchanged)
{short_title}: # (unchanged)
{slug}: # (unchanged)
{transport}: # (unchanged)
{repo_owner}: # (unchanged)
{repo_name}: # (unchanged)
{issue_number}: "<number from issue creation>"
{issue_url}: "<full URL of created issue>"
```

### 5. Proceed to Next Step

Immediately load `steps/step-02-create-branch.md` with these variables.

---

## SUCCESS METRICS:

✅ Issue created via correct transport (gh or MCP)
✅ Issue URL captured from output
✅ Issue number extracted (numeric value)
✅ State variables updated with issue_number and issue_url
✅ Proceeding to step-02

## FAILURE MODES:

❌ `gh` not installed (local transport) → Error: "GitHub CLI (gh) not installed. Run: brew install gh"
❌ `gh` not authenticated → Error: "Not authenticated. Run: gh auth login"
❌ MCP tool not available (remote transport) → Error: "GitHub MCP tools not available in this environment"
❌ No remote repository → Error: "No git remote found. Push to GitHub first."
❌ API error → Capture error message and stop

## ERROR HANDLING:

If issue creation fails:
1. Capture the error message
2. Output: "Failed to create issue: {error}"
3. Do NOT proceed to next step
4. Suggest fix based on error type

## NEXT STEP:

Load `steps/step-02-create-branch.md`

<critical>
This is a no-confirmation skill. Create the issue and proceed immediately.
Do not ask the user for approval - just execute and continue.
</critical>
