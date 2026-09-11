---
name: ship-feature-cloud
description: Automated feature shipping for Claude Code tab (cloud) sessions - generates Ralph files via ralph-import, launches Ralph on the pre-existing session branch. No branch creation or PR — use the web UI's "Create PR" button when done.
argument-hint: "<feature description>"
---

<objective>
Ship a feature from description to Ralph implementation within a Claude Code tab (cloud) session. Pass a feature description as an argument, and this skill will:

1. Parse the description and extract a title/slug
2. Confirm the current session branch (do NOT create or switch branches)
3. Export the description, run ralph-import to generate PROMPT.md, fix_plan.md, and specs/
4. Copy generated files into the project's .ralph/ directory
5. Launch Ralph to implement the feature
6. Stop — commits accumulate on the session branch; open a PR via the web UI

**Usage:**
```bash
/ship-feature-cloud "Add a logout button to the header that clears session and redirects to login page"
```
</objective>

<quick_start>
**Ship a feature in a cloud session:**
```bash
/ship-feature-cloud "Your feature description here - be detailed about what you want"
```

**What happens:**
1. Description parsed, title and slug extracted
2. Current session branch confirmed (no branch creation)
3. Description exported and fed to `ralph-import`
4. Generated PROMPT.md, fix_plan.md, specs/ copied into .ralph/
5. Ralph launched (plain `ralph`, no `--monitor`)
6. Done — use the web UI "Create PR" button when ready
</quick_start>

<critical_rule>
NEVER ask for confirmation - run everything automatically
NEVER create branches - the session already has one
NEVER push branches - the GitHub proxy handles this
NEVER create PRs - the user does this via the web UI
NEVER use ralph --monitor - no tmux in cloud VMs
ALWAYS extract a short title from the description
ALWAYS wait for ralph-import to complete before copying files
ALWAYS launch ralph (plain, never --monitor)
ALWAYS stop after Ralph finishes with a summary pointing to the UI's PR button
</critical_rule>

<when_to_use>
**Use this skill when:**
- You are in a Claude Code tab (cloud/web) session
- You have a clear feature description ready
- Ralph and ralph-import are pre-installed on the cloud VM
- Project has `.ralph/` directory

**Don't use for:**
- Local CLI sessions (use `/ship-feature` instead — it handles branches and PRs)
- Simple one-file changes (just ask Claude directly)
- Projects without Ralph set up
</when_to_use>

<parameters>
| Parameter | Description |
|-----------|-------------|
| `$ARGUMENTS` | Full feature description (required) |

**Examples:**
```bash
/ship-feature-cloud "Add dark mode toggle to settings page with system preference detection"
/ship-feature-cloud "Implement rate limiting middleware that blocks IPs after 100 requests per minute"
```
</parameters>

<state_variables>
| Variable | Type | Description |
|----------|------|-------------|
| `{feature_description}` | string | Full description from $ARGUMENTS |
| `{short_title}` | string | Extracted title (max 50 chars) for display |
| `{slug}` | string | URL-safe slug (max 40 chars) for temp dir naming |
| `{current_branch}` | string | The pre-existing session branch name |
| `{temp_import_dir}` | string | Temporary directory from ralph-import |
</state_variables>

<entry_point>
Load `steps/step-00-init.md`
</entry_point>

<step_files>
| Step | File | Purpose |
|------|------|---------|
| 00 | `step-00-init.md` | Parse $ARGUMENTS, extract title and slug, confirm current branch |
| 01 | `step-01-ralph-import.md` | Export description, run ralph-import |
| 02 | `step-02-copy-ralph-files.md` | Copy generated files into .ralph/, clean up |
| 03 | `step-03-show-and-launch.md` | Display files, launch Ralph, stop with summary |
</step_files>

<execution_rules>
1. **No Confirmation**: Execute all steps without asking user
2. **No Branch Ops**: Never create, switch, or push branches
3. **No PR Creation**: Never attempt to create a PR
4. **Progressive Loading**: Load one step at a time
5. **Error Handling**: If any step fails, stop and report error
6. **Wait for Import**: ralph-import takes ~2 minutes - wait for completion
7. **Preserve Project Config**: Never overwrite .ralphrc or AGENT.md
8. **Auto-Launch**: Ralph starts automatically after files are copied
9. **Stop After Ralph**: Do not attempt post-Ralph git operations
</execution_rules>

<success_criteria>
ralph-import generated PROMPT.md, fix_plan.md, and specs/
Generated files copied into project's .ralph/ directory
Temp import directory cleaned up
Ralph launched and completed
Summary displayed pointing user to web UI's "Create PR" button
</success_criteria>
