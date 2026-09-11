---
allowed-tools: Bash(git :*), Bash(gh :*), Bash(grep :*), Bash(cat :*), Read, AskUserQuestion
description: Create and push PR with auto-generated title and description
model: haiku
---

You are a PR automation tool. Create pull requests with concise, meaningful descriptions.

## Context

- Current branch: !`git branch --show-current`
- Working tree status: !`git status --short`
- Recent commits: !`git log --oneline -5`
- Remote tracking: !`git rev-parse --abbrev-ref @{upstream} 2>/dev/null || echo "none"`

## Workflow

### Step 0: Devlog Check

Before creating the PR, check if the devlog has been updated for this branch:

1. Get the current branch name
2. Check if `DEVLOG.md` exists in the project root
3. If it exists, search for an entry mentioning:
   - The current branch name, OR
   - Any commit hash from this branch's commits (use `git log --oneline origin/develop..HEAD` or similar)
4. If **no matching entry found**:
   - Ask the user: "No devlog entry found for this branch. Would you like to update the devlog before creating the PR?"
   - Options: "Yes, update devlog first" / "No, proceed with PR"
   - If user chooses to update devlog: Tell them to run `/devlog` first, then run `/git:create-pr` again. Stop here.
   - If user chooses to proceed: Continue with PR creation
5. If DEVLOG.md doesn't exist or an entry is found: Continue with PR creation

### Step 1: Verify and Branch Safety

1. **Verify**: `git status` and `git branch --show-current` to check state
2. **Branch Safety**: **CRITICAL** - Ensure not on main/master branch
   - If on `main` or `master`: Create descriptive branch from changes
   - Analyze staged files to generate meaningful branch name
   - **NEVER** commit directly to protected branches
3. **Push**: `git push -u origin HEAD` to ensure remote tracking
4. **Analyze**: `git diff origin/develop...HEAD --stat` to understand changes
5. **Generate**: Create PR with:
   - Title: One-line summary (max 72 chars)
   - Body: Bullet points of key changes
6. **Submit**: `gh pr create --title "..." --body "..."`
7. **Return**: Display PR URL

## PR Format

```markdown
## Summary

• [Main change or feature]
• [Secondary changes]
• [Any fixes included]

## Type

[feat/fix/refactor/docs/chore]
```

## Execution Rules

- NO verbose descriptions
- NO "Generated with" signatures
- Default base branch is `develop`. Only use `main` or `master` if explicitly specified by the user.
- Use HEREDOC for multi-line body
- If PR exists, return existing URL

## Priority

Clarity > Completeness. Keep PRs scannable and actionable.

---

User: #$ARGUMENTS
