# ship-feature (Local/CLI)

Fully automated skill for **local CLI sessions** that takes a feature description and ships it — creating the GitHub issue, branch, Ralph PRD files, launching autonomous implementation, and opening a PR. For cloud Code tab sessions, use `/ship-feature-cloud` instead.

## Why?

Shipping a feature normally requires several manual steps: writing an issue, creating a branch, drafting a PRD, configuring Ralph, launching it, pushing commits, and opening a PR. This skill collapses the entire workflow into a single command so features can be dispatched in seconds. With Claude Code Remote, features run in Anthropic's cloud environment in the background, enabling parallel feature shipping — even from a phone.

## Architecture

- `SKILL.md` — skill metadata, parameters, state variables, and execution rules
- `steps/step-00-init.md` — parses the feature description and `--local` flag, extracts a short title and URL-safe slug
- `steps/step-01-create-issue.md` — creates a GitHub issue via `gh issue create`
- `steps/step-02-create-branch.md` — creates and checks out `feature/{number}-{slug}`
- `steps/step-03-push-branch.md` — pushes branch to origin with upstream tracking
- `steps/step-04-ralph-import.md` — cds to repo root, exports issue body, runs `ralph-import` to generate PROMPT.md, fix_plan.md, and specs/
- `steps/step-05-copy-ralph-files.md` — copies generated files into `.ralph/`, preserves .ralphrc and AGENT.md, cleans up temp dir
- `steps/step-06-show-and-launch.md` — displays generated files and launches Ralph (plain `ralph` or `ralph --monitor` based on mode)
- `steps/step-07-push-and-pr.md` — pushes Ralph's commits and opens a pull request

Steps execute sequentially with no user confirmation. Each step passes state variables to the next.

## Usage

```bash
# Remote execution (default) — plain ralph, auto-push, auto-PR
/ship-feature "Add dark mode toggle to settings page with system preference detection"

# Local execution — tmux monitoring dashboard
/ship-feature --local "Add rate limiting middleware"

# Via Claude Code Remote — runs in background on Anthropic's infrastructure
# Dispatch multiple features in parallel from any device
```

Requires: `gh` CLI authenticated, `ralph` and `ralph-import` installed globally, `.ralph/` directory initialized.

## When to use which variant

| Environment | Skill | Why |
|-------------|-------|-----|
| Local CLI (`claude` in terminal) | `/ship-feature` | Owns full git lifecycle: branch, push, PR |
| Cloud Code tab (web UI) | `/ship-feature-cloud` | Uses session branch, no PR creation |
