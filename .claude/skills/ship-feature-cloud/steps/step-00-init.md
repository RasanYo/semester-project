---
name: step-00-init
description: Parse feature description from $ARGUMENTS, extract title and slug, confirm current branch
prev_step: null
next_step: steps/step-01-ralph-import.md
---

# Step 0: Initialize - Parse Description and Confirm Branch

## MANDATORY EXECUTION RULES:

- NEVER ask for confirmation - this is fully automated
- NEVER modify the description - use exactly what user provided
- NEVER create or switch branches - use the current session branch
- ALWAYS extract a short title (max 50 chars) from description
- ALWAYS generate a URL-safe slug (max 40 chars)
- ALWAYS confirm the current branch before proceeding
- ALWAYS proceed immediately to next step

## YOUR TASK:

Parse the feature description from `$ARGUMENTS`, extract a title and slug, and confirm the current session branch.

---

## EXECUTION SEQUENCE:

### 1. Capture Feature Description

The full input is provided in `$ARGUMENTS`. Use it directly as the feature description (no flag parsing needed — cloud variant has no `--local` flag).

```yaml
{feature_description}: "$ARGUMENTS"
```

### 2. Extract Short Title (max 50 chars)

Generate a concise title from the description:

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

```yaml
{slug}: "<url-safe-slug, max 40 chars>"
```

### 4. Confirm Current Branch

Verify the current branch exists and is the session's working branch. Do NOT switch away from it.

```bash
git branch --show-current
```

Record the branch name:

```yaml
{current_branch}: "<output of git branch --show-current>"
```

### 5. Set State Variables

```yaml
{feature_description}: "$ARGUMENTS"
{short_title}: "<extracted, max 50 chars>"
{slug}: "<generated, max 40 chars>"
{current_branch}: "<current branch name>"
```

### 6. Proceed to Next Step

Immediately load `steps/step-01-ralph-import.md` with these variables.

---

## SUCCESS METRICS:

Feature description captured from $ARGUMENTS
Short title extracted (<=50 chars)
Slug generated (<=40 chars, lowercase, hyphens only)
Current branch confirmed (not switched)
State variables set
Proceeding to step-01

## FAILURE MODES:

$ARGUMENTS is empty or not provided -> Stop with error message
Cannot extract meaningful title -> Use first 50 chars of description
Not on any branch (detached HEAD) -> Stop with error: "Not on a branch. Cloud sessions require a working branch."

## NEXT STEP:

Load `steps/step-01-ralph-import.md`

<critical>
This is a no-confirmation skill. Parse and proceed immediately.
Do not ask the user anything - just extract and continue.
Do NOT create or switch branches.
</critical>
