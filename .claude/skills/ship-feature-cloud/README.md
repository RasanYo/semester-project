# ship-feature-cloud

Automated feature shipping for Claude Code tab (cloud/web) sessions. Takes a feature description and runs Ralph on the pre-existing session branch — no branch creation, no PR creation.

## Why?

The original `ship-feature` skill owns the full git lifecycle: creating branches, pushing, and opening PRs. In a Claude Code tab session, the branch is pre-scoped by the system and PRs are created via the web UI. This cloud variant strips the git lifecycle steps and focuses on what matters: generating Ralph files and launching implementation.

## Architecture

- `SKILL.md` — skill metadata, parameters, state variables, and execution rules
- `steps/step-00-init.md` — parses the feature description, extracts title and slug, confirms current branch
- `steps/step-01-ralph-import.md` — exports description to temp file, runs `ralph-import` to generate PROMPT.md, fix_plan.md, and specs/
- `steps/step-02-copy-ralph-files.md` — copies generated files into `.ralph/`, preserves .ralphrc and AGENT.md, cleans up temp dir
- `steps/step-03-show-and-launch.md` — displays generated files, launches Ralph (plain, never `--monitor`), stops with summary

Steps execute sequentially with no user confirmation.

## Usage

```bash
# In a Claude Code tab (cloud) session:
/ship-feature-cloud "Add dark mode toggle to settings page with system preference detection"
```

After Ralph finishes, use the web UI's "Create PR" button to open a pull request.

Requires: `ralph` and `ralph-import` installed on the cloud VM (handled by environment setup script), `.ralph/` directory initialized.

## When to use which variant

| Environment | Skill | Why |
|-------------|-------|-----|
| Local CLI (`claude` in terminal) | `/ship-feature` | Owns full git lifecycle: branch, push, PR |
| Cloud Code tab (web UI) | `/ship-feature-cloud` | Uses session branch, no PR creation |
