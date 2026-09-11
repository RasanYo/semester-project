---
name: step-07-push-and-pr
description: Push Ralph's commits and open a pull request
prev_step: steps/step-06-show-and-launch.md
next_step: null
---

# Step 7: Push Commits and Open PR

## MANDATORY EXECUTION RULES:

- 🛑 NEVER ask for confirmation - execute immediately
- 🛑 NEVER abort on PR creation failure - warn and continue
- ✅ ALWAYS check for commits before pushing
- ✅ ALWAYS check for existing PR before creating one
- ✅ ALWAYS use the correct transport (gh CLI or MCP tool)
- ✅ ALWAYS display completion summary with PR link
- ✅ ALWAYS handle "no changes" gracefully

## YOUR TASK:

After Ralph finishes implementing, push all commits to origin and open a pull request. Use `gh` CLI locally or GitHub MCP tools in Remote.

---

## EXECUTION SEQUENCE:

### 1. Verify State Variables

Confirm you have these from previous steps:

```yaml
{branch_name}: # Full branch name (feature/{number}-{slug})
{issue_number}: # Number from created issue
{short_title}: # Extracted title (max 50 chars)
{issue_url}: # Full URL of created issue
{transport}: # "local" or "remote"
{repo_owner}: # GitHub repo owner
{repo_name}: # GitHub repo name
```

### 2. Check for Commits to Push

Check if there are any new commits beyond what's already on the remote:

```bash
git log origin/{branch_name}..HEAD --oneline
```

**If output is empty:** Ralph made no changes. Skip to the completion summary and output:
```
⚠️ Ralph made no changes — nothing to push or PR.
```
Do NOT attempt to push or create a PR. Proceed to the completion summary.

### 3. Push Commits

Push Ralph's commits to the remote:

```bash
git push origin {branch_name}
```

**If push fails:** Retry once:

```bash
git push origin {branch_name}
```

**If push still fails:** Output error prominently with manual command:
```
❌ Failed to push commits. Run manually:
   git push origin {branch_name}
```
Do NOT abort — still attempt PR creation.

### 4. Check for Existing PR

**If `{transport}` is `"local"`:**

```bash
gh pr list --head {branch_name} --json number,url --jq '.[0]'
```

**If `{transport}` is `"remote"`:**

```
Tool: mcp__github__list_pull_requests
Parameters:
  owner: "{repo_owner}"
  repo: "{repo_name}"
  head: "{repo_owner}:{branch_name}"
  state: "open"
```

**If a PR already exists:** Extract the URL, set `{pr_url}`, and skip to the completion summary.

### 5. Create Pull Request

**If `{transport}` is `"local"`:**

```bash
gh pr create --title "{short_title}" --body "Automated implementation of #{issue_number} via Ralph.

Closes #{issue_number}"
```

**If `{transport}` is `"remote"`:**

```
Tool: mcp__github__create_pull_request
Parameters:
  owner: "{repo_owner}"
  repo: "{repo_name}"
  title: "{short_title}"
  body: "Automated implementation of #{issue_number} via Ralph.\n\nCloses #{issue_number}"
  head: "{branch_name}"
  base: "main"
```

Capture the URL from the output:

```yaml
{pr_url}: "<URL from gh or MCP output>"
```

**If PR creation fails:** Output warning with manual command:
```
⚠️ Failed to create PR. Run manually:
   gh pr create --fill
```
Set `{pr_url}` to "N/A" and proceed to the completion summary.

### 6. Display Completion Summary

Output the following:

```
╔════════════════════════════════════════════════════════════╗
║                    ✅ SHIP-FEATURE COMPLETE                ║
╠════════════════════════════════════════════════════════════╣
║ Issue: #{issue_number} - {short_title}
║ Branch: {branch_name}
║ PR: {pr_url}
╚════════════════════════════════════════════════════════════╝
```

---

## SUCCESS METRICS:

✅ Commits pushed to origin (or "no changes" detected)
✅ Existing PR detected OR new PR created via correct transport
✅ `{pr_url}` state variable set
✅ Completion summary displayed
✅ Ship-feature skill complete

## FAILURE MODES:

❌ No commits to push → Skip push and PR, display "no changes" message
❌ `git push` fails → Retry once, then warn with manual command
❌ `gh pr create` fails (local) → Warn with manual command
❌ MCP tool fails (remote) → Warn with manual command
❌ PR already exists → Extract existing PR URL, treat as success

## ERROR HANDLING:

**Philosophy: warn, don't abort.** At this point Ralph's work is done and committed locally. A failed push or PR is recoverable — the user can run the commands manually. The skill should always reach the completion summary.

## NEXT STEP:

None — this is the final step. Ship-feature is complete.

<critical>
This is a no-confirmation skill. Push, create PR, and display summary immediately.
Do not ask the user for approval - just execute and complete.
If push or PR creation fails, WARN but do NOT abort - always show the completion summary.
</critical>
