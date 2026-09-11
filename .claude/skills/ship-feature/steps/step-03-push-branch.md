---
name: step-03-push-branch
description: Push branch to origin with upstream tracking
prev_step: steps/step-02-create-branch.md
next_step: steps/step-04-ralph-import.md
---

# Step 3: Push Branch to Origin

## MANDATORY EXECUTION RULES:

- 🛑 NEVER ask for confirmation - execute immediately
- 🛑 NEVER push without setting upstream tracking
- ✅ ALWAYS use the -u flag to set up remote tracking
- ✅ ALWAYS push to origin remote
- ✅ ALWAYS verify push succeeded before proceeding
- ✅ ALWAYS proceed immediately to next step

## YOUR TASK:

Push the newly created branch to the origin remote and set up upstream tracking.

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

### 2. Push Branch with Upstream Tracking

Execute the following command:

```bash
git push -u origin {branch_name}
```

**Flags explained:**
- `-u` (or `--set-upstream`): Sets up tracking relationship with remote branch
- `origin`: The default remote repository
- `{branch_name}`: The branch to push

This command:
- Pushes local branch to origin
- Creates the remote branch if it doesn't exist
- Sets up local branch to track the remote branch
- Enables `git pull` and `git push` without specifying remote/branch

### 3. Verify Push Success

The push is successful if:
- Command exits with code 0
- Output shows branch pushed to origin
- Remote tracking is established

**Expected output pattern:**
```
Branch '{branch_name}' set up to track remote branch '{branch_name}' from 'origin'.
```

Or:
```
To github.com:owner/repo.git
 * [new branch]      {branch_name} -> {branch_name}
branch '{branch_name}' set up to track 'origin/{branch_name}'.
```

### 4. Verify Remote Tracking (Optional)

To confirm tracking is set up:

```bash
git branch -vv
```

Expected: Current branch shows `[origin/{branch_name}]` tracking info.

### 5. Proceed to Next Step

Immediately load `steps/step-04-ralph-import.md` with current state variables.

---

## SUCCESS METRICS:

✅ Branch pushed to origin remote
✅ Upstream tracking set up (`-u` flag used)
✅ Remote branch exists on GitHub
✅ Local branch tracks remote branch
✅ Proceeding to step-04

## FAILURE MODES:

❌ No remote named 'origin' → Check `git remote -v`, add origin if missing
❌ Authentication failed → User needs to configure git credentials
❌ Permission denied → User lacks push access to repository
❌ Remote branch already exists → May need to force push or use different name
❌ Network error → Retry the push command

## ERROR HANDLING:

If `git push -u origin` fails:

**No remote 'origin':**
```bash
# Check available remotes
git remote -v

# If no origin, cannot push - fail with message
# "No 'origin' remote configured. Please add a remote first."
```

**Authentication failure:**
```
# Output: "Authentication failed"
# Cannot auto-fix - user must configure credentials
# Fail with message: "Git authentication failed. Please configure your credentials."
```

**Permission denied:**
```
# Output: "Permission denied" or "403"
# Cannot auto-fix - user lacks repo access
# Fail with message: "Permission denied. Check your repository access."
```

**Branch already exists on remote:**
```bash
# If branch exists and diverged, this is unusual for a new feature
# Output warning but proceed since our branch should be correct
git push -u origin {branch_name} --force-with-lease
```

**Network errors:**
```bash
# Retry once after short delay
sleep 2
git push -u origin {branch_name}
```

## EXAMPLE EXECUTION:

**Input state:**
```yaml
{feature_description}: "Add a logout button to the header that clears session and redirects to login"
{short_title}: "Add a logout button to the header"
{slug}: "add-logout-button-to-header"
{issue_number}: "16"
{issue_url}: "https://github.com/RasanYo/crypto-trading-bot/issues/16"
{branch_name}: "feature/16-add-logout-button-to-header"
```

**Command executed:**
```bash
git push -u origin feature/16-add-logout-button-to-header
```

**Output:**
```
Enumerating objects: 5, done.
Counting objects: 100% (5/5), done.
Delta compression using up to 8 threads
Compressing objects: 100% (3/3), done.
Writing objects: 100% (3/3), 1.23 KiB | 1.23 MiB/s, done.
Total 3 (delta 2), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (2/2), completed with 2 local objects.
To github.com:RasanYo/crypto-trading-bot.git
 * [new branch]      feature/16-add-logout-button-to-header -> feature/16-add-logout-button-to-header
branch 'feature/16-add-logout-button-to-header' set up to track 'origin/feature/16-add-logout-button-to-header'.
```

**State unchanged - proceed to next step.**

## NEXT STEP:

Load `steps/step-04-ralph-import.md`

<critical>
This is a no-confirmation skill. Push the branch and proceed immediately.
Do not ask the user for approval - just execute and continue.
</critical>
