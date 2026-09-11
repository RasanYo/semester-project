---
name: step-02-create-branch
description: Create and checkout branch with issue number and slug
prev_step: steps/step-01-create-issue.md
next_step: steps/step-03-push-branch.md
---

# Step 2: Create and Checkout Branch

## MANDATORY EXECUTION RULES:

- 🛑 NEVER ask for confirmation - execute immediately
- 🛑 NEVER use branch names without issue number prefix
- ✅ ALWAYS follow format: `feature/{number}-{slug}`
- ✅ ALWAYS create branch from current HEAD
- ✅ ALWAYS checkout the new branch after creation
- ✅ ALWAYS proceed immediately to next step

## YOUR TASK:

Create a new git branch following the naming convention and checkout to it.

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
```

### 2. Construct Branch Name

Build the branch name using this format:

```
feature/{issue_number}-{slug}
```

**Rules:**
- Prefix: `feature/`
- Issue number: from `{issue_number}`
- Slug: from `{slug}` (max 40 chars, lowercase, hyphens only)

**Example:**
```yaml
{issue_number}: "42"
{slug}: "add-logout-button-to-header"
# Result: feature/42-add-logout-button-to-header
```

### 3. Create and Checkout Branch

Execute the following command:

```bash
git checkout -b feature/{issue_number}-{slug}
```

This command:
- Creates a new branch from current HEAD
- Automatically checks out the new branch
- Sets up local tracking

### 4. Verify Branch Creation

Confirm the branch was created and checked out:

```bash
git branch --show-current
```

Expected output: `feature/{issue_number}-{slug}`

### 5. Set State Variables

After successful creation, update state:

```yaml
{feature_description}: # (unchanged)
{short_title}: # (unchanged)
{slug}: # (unchanged)
{issue_number}: # (unchanged)
{issue_url}: # (unchanged)
{branch_name}: "feature/{issue_number}-{slug}"
```

### 6. Proceed to Next Step

Immediately load `steps/step-03-push-branch.md` with these variables.

---

## SUCCESS METRICS:

✅ Branch name follows format: `feature/{number}-{slug}`
✅ Branch created from current HEAD
✅ Branch checked out (now the active branch)
✅ `{branch_name}` state variable set
✅ Proceeding to step-03

## FAILURE MODES:

❌ Branch already exists → Use `git checkout` instead of `git checkout -b`
❌ Invalid branch name characters → Sanitize slug (remove special chars)
❌ Dirty working directory → Git may warn but branch creation should succeed
❌ Detached HEAD state → Create branch anyway (will capture current commit)

## ERROR HANDLING:

If `git checkout -b` fails:

**Branch exists:**
```bash
# Check if branch exists and checkout instead
git checkout feature/{issue_number}-{slug}
```

**Invalid characters in branch name:**
- Re-sanitize slug: `echo "{slug}" | tr -cd 'a-z0-9-' | head -c 40`
- Retry branch creation with sanitized name

**Other errors:**
1. Capture the error message
2. Output: "Failed to create branch: {error}"
3. Do NOT proceed to next step
4. Suggest fix based on error type

## EXAMPLE EXECUTION:

**Input state:**
```yaml
{feature_description}: "Add a logout button to the header that clears session and redirects to login"
{short_title}: "Add a logout button to the header"
{slug}: "add-logout-button-to-header"
{issue_number}: "16"
{issue_url}: "https://github.com/RasanYo/crypto-trading-bot/issues/16"
```

**Command executed:**
```bash
git checkout -b feature/16-add-logout-button-to-header
```

**Output:**
```
Switched to a new branch 'feature/16-add-logout-button-to-header'
```

**Verification:**
```bash
git branch --show-current
# Output: feature/16-add-logout-button-to-header
```

**Updated state:**
```yaml
{feature_description}: "Add a logout button to the header that clears session and redirects to login"
{short_title}: "Add a logout button to the header"
{slug}: "add-logout-button-to-header"
{issue_number}: "16"
{issue_url}: "https://github.com/RasanYo/crypto-trading-bot/issues/16"
{branch_name}: "feature/16-add-logout-button-to-header"
```

## NEXT STEP:

Load `steps/step-03-push-branch.md`

<critical>
This is a no-confirmation skill. Create the branch and proceed immediately.
Do not ask the user for approval - just execute and continue.
</critical>
