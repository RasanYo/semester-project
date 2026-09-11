---
name: step-00-init
description: Parse feature description from $ARGUMENTS, extract title and slug
prev_step: null
next_step: steps/step-01-create-issue.md
---

# Step 0: Initialize - Parse Description

## MANDATORY EXECUTION RULES:

- 🛑 NEVER ask for confirmation - this is fully automated
- 🛑 NEVER modify the description - use exactly what user provided
- ✅ ALWAYS extract a short title (max 50 chars) from description
- ✅ ALWAYS generate a URL-safe slug (max 40 chars)
- ✅ ALWAYS proceed immediately to next step

## YOUR TASK:

Parse the feature description from `$ARGUMENTS` and extract:
1. A short title for the GitHub issue
2. A slug for the branch name

---

## EXECUTION SEQUENCE:

### 1. Parse Flags and Capture Feature Description

The full input is provided in `$ARGUMENTS`. Before extracting the feature description, check for the `--local` flag:

**Flag parsing rules:**
- If `$ARGUMENTS` contains `--local` (at any position), set `{launch_mode}` to `"local"` and strip the flag from the description
- If `--local` is not present, set `{launch_mode}` to `"remote"` (default)
- The flag must be removed before the description is used for issue title/body

```yaml
{launch_mode}: "remote"  # default; set to "local" if --local flag is present
{feature_description}: "$ARGUMENTS with --local stripped out"
```

**Example inputs:**
- `"Add a logout button to the header"` → `{launch_mode}: "remote"`, description unchanged
- `"--local Add a logout button to the header"` → `{launch_mode}: "local"`, description = `"Add a logout button to the header"`
- `"Add a logout button --local"` → `{launch_mode}: "local"`, description = `"Add a logout button"`

### 2. Extract Short Title (max 50 chars)

Generate a concise issue title from the description:

**Rules:**
- Use the first sentence if it's under 50 chars
- Otherwise, extract the core action (verb + object)
- Capitalize first letter
- Remove trailing punctuation
- Maximum 50 characters

**Algorithm:**
```
1. If description starts with a verb phrase, use it
2. Look for patterns: "Add X", "Implement X", "Create X", "Fix X"
3. Truncate at first period, comma, or "that/which/with" if needed
4. Trim to 50 chars, ending at word boundary
```

**Examples:**
| Description | Short Title |
|-------------|-------------|
| "Add a logout button to the header that clears session" | "Add a logout button to the header" |
| "Implement rate limiting middleware that blocks IPs" | "Implement rate limiting middleware" |
| "Create user dashboard showing trading history" | "Create user dashboard showing trading history" |

```yaml
{short_title}: "<extracted title, max 50 chars>"
```

### 3. Generate Slug (max 40 chars)

Create a URL-safe slug from the short title:

**Rules:**
- Convert to lowercase
- Replace spaces with hyphens
- Remove special characters (keep only a-z, 0-9, -)
- Remove leading/trailing hyphens
- Collapse multiple hyphens to single
- Maximum 40 characters
- End at word boundary (don't cut words)

**Examples:**
| Short Title | Slug |
|-------------|------|
| "Add a logout button to the header" | "add-logout-button-to-header" |
| "Implement rate limiting middleware" | "implement-rate-limiting-middleware" |
| "Create user dashboard" | "create-user-dashboard" |

```yaml
{slug}: "<url-safe-slug, max 40 chars>"
```

### 4. Detect Transport Environment

Determine whether running locally (with `gh` CLI) or in Claude Code Remote (MCP tools only):

```bash
command -v gh
```

- If `gh` is found: set `{transport}` to `"local"`
- If `gh` is NOT found: set `{transport}` to `"remote"`

### 5. Extract Repository Owner and Name

Extract owner and repo name from the git remote URL (needed for MCP tools in remote transport):

```bash
git remote get-url origin
```

Parse the output:
- SSH format `git@github.com:owner/repo.git` → owner = `owner`, repo = `repo`
- HTTPS format `https://github.com/owner/repo.git` → owner = `owner`, repo = `repo`

```yaml
{repo_owner}: "<extracted owner>"
{repo_name}: "<extracted repo name, without .git suffix>"
```

### 6. Set State Variables

```yaml
{feature_description}: "$ARGUMENTS with --local stripped"
{short_title}: "<extracted, max 50 chars>"
{slug}: "<generated, max 40 chars>"
{launch_mode}: "remote"  # or "local" if --local flag was present
{transport}: "local"     # or "remote" if gh CLI is not found
{repo_owner}: "<extracted from git remote>"
{repo_name}: "<extracted from git remote>"
```

### 7. Proceed to Next Step

Immediately load `steps/step-01-create-issue.md` with these variables.

---

## SUCCESS METRICS:

✅ `--local` flag parsed (if present) and stripped from description
✅ `{launch_mode}` set to `"local"` or `"remote"`
✅ `{transport}` set to `"local"` or `"remote"` based on `gh` availability
✅ `{repo_owner}` and `{repo_name}` extracted from git remote
✅ Feature description captured from $ARGUMENTS
✅ Short title extracted (≤50 chars)
✅ Slug generated (≤40 chars, lowercase, hyphens only)
✅ State variables set
✅ Proceeding to step-01

## FAILURE MODES:

❌ $ARGUMENTS is empty or not provided → Stop with error message
❌ Cannot extract meaningful title → Use first 50 chars of description

## NEXT STEP:

Load `steps/step-01-create-issue.md`

<critical>
This is a no-confirmation skill. Parse and proceed immediately.
Do not ask the user anything - just extract and continue.
</critical>
