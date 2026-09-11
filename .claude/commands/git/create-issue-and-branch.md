# Generate AI-Friendly Issue and Branch

When I ask you to "create an issue for [feature description]", follow this workflow:

## Step 1: Generate Issue

Create a GitHub issue draft with:

**Issue Title:**
A clear, action-oriented title (max 30 chars) starting with a verb

**Issue Description:**
```
## Overview
Brief 3-4 sentence summary of what needs to be built and why it matters

## Requirements
- Bullet points of core functionality (3-7 items)
- Focus on WHAT, not HOW

## Technical Context
- Relevant libraries or tools to consider
- Documentation references if applicable
- Integration points with existing system

## Acceptance Criteria
- Clear, testable conditions for completion (2-4 items)
- User-facing outcomes

## Notes
- Any constraints, dependencies, or architectural considerations
```

## Step 2: Review

After generating the issue, ask me:
"Does this look good? Reply with:
- 'yes' or 'create' to create the GitHub issue and branch
- 'edit [feedback]' to revise
- 'cancel' to abort"

## Step 3: Create Issue

If I approve, use the GitHub CLI to create the issue:
```bash
gh issue create --title "TITLE" --body "DESCRIPTION"
```

Capture the issue number from the output.

If I provide feedback, revise the issue and show it again for review.

## Step 4: Create Branch

After issue creation, automatically create and switch to a feature branch:

1. Generate branch name from issue number and title:
   - Format: `feature/{number}-{slug}`
   - Slug: lowercase title, spaces to hyphens, remove special chars, max 40 chars
   - Example: Issue #5 "Add user authentication" → `feature/5-add-user-authentication`

2. Create and checkout the branch:
```bash
git checkout -b feature/{number}-{slug}
```

3. Confirm completion with:
   - Issue URL
   - Branch name
   - Ready to start working message

## Guidelines:
- Keep description under 20 lines total
- Use clear, jargon-free language
- Focus on outcomes, not implementation
- Assume the reader is an AI agent that needs context, not code
- Include links to official docs for suggested libraries
- Mention relevant files/components by name if they exist

## Example Workflow:

**Me:** "Create an issue for adding video preview thumbnails"

**You:**
```
**Title:** Add video thumbnail previews

**Description:**
## Overview
Display video thumbnails when users share YouTube links. This provides visual context for shared videos without requiring users to click the link.

## Requirements
- Extract video ID from YouTube URLs
- Fetch thumbnail from YouTube API or oEmbed
- Show thumbnail as a card in the message
- Handle loading and error states

## Technical Context
- Use YouTube oEmbed API (no key required)
- Integrate with existing message components

## Acceptance Criteria
- Thumbnails appear for valid YouTube URLs
- Broken/invalid links show graceful fallback

## Notes
- Should work with both youtube.com and youtu.be URLs
```
---
Does this look good? Reply with 'yes'/'create' to create the issue and branch, 'edit [feedback]' to revise, or 'cancel' to abort.

**Me:** "yes"

**You:**
- Creates issue #5 via `gh issue create`
- Creates branch `feature/5-add-video-thumbnail-previews`
- Confirms: "Issue #5 created. Switched to branch `feature/5-add-video-thumbnail-previews`. Ready to start working!"

---

## Prerequisites:
- GitHub CLI (`gh`) installed and authenticated
- Git repository initialized with remote
