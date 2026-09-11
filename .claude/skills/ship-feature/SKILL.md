---
name: ship-feature
description: Fully automated feature shipping - creates issue, branch, generates Ralph files via ralph-import, launches Ralph to implement, and opens a PR
argument-hint: "[--local] <feature description>"
---

<objective>
Ship a feature from description to implementation with zero manual steps. Pass a feature description as an argument, and this skill will:

1. Create a GitHub issue from your description
2. Create and checkout a feature branch
3. Push branch to origin
4. Run ralph-import to generate PROMPT.md, fix_plan.md, and specs/ from the issue
5. Copy generated files into the project's .ralph/ directory
6. Launch Ralph to implement the feature
7. Push commits and open a pull request

**Usage:**
```bash
/ship-feature "Add a logout button to the header that clears session and redirects to login page"
/ship-feature --local "Add dark mode toggle with system preference detection"
```
</objective>

<quick_start>
**Ship a feature (fully automated):**
```bash
/ship-feature "Your feature description here - be detailed about what you want"
```

**What happens:**
1. GitHub issue created with title extracted from description
2. Branch created: `feature/{number}-{slug}`
3. Branch pushed to origin with tracking
4. Issue body exported and fed to `ralph-import`
5. Generated PROMPT.md, fix_plan.md, specs/ copied into .ralph/
6. Ralph launched (plain `ralph` for Remote, `ralph --monitor` with `--local`)
7. Commits pushed and PR opened
</quick_start>

<critical_rule>
🛑 NEVER ask for confirmation - run everything automatically
🛑 NEVER wait for user input after starting
🛑 NEVER overwrite .ralphrc or AGENT.md - those are project-level configs
✅ ALWAYS extract a short title from the description
✅ ALWAYS capture the issue number from gh output
✅ ALWAYS wait for ralph-import to complete before copying files
✅ ALWAYS launch ralph (use --monitor only when --local flag is passed)
✅ ALWAYS push commits and open a PR after Ralph finishes
</critical_rule>

<when_to_use>
**Use this skill when:**
- You have a clear feature description ready
- You want hands-off implementation
- Ralph is installed globally (`ralph` command available)
- Project has `.ralph/` directory (run `ralph-enable-ci` first if not)

**Don't use for:**
- Simple one-file changes (just ask Claude directly)
- Features requiring constant user feedback
- Projects without Ralph set up
</when_to_use>

<parameters>
| Parameter | Description |
|-----------|-------------|
| `$ARGUMENTS` | Full feature description (required) |
| `--local` | Launch Ralph with `--monitor` (tmux dashboard) instead of plain `ralph` |

**Examples:**
```bash
/ship-feature "Add dark mode toggle to settings page with system preference detection"
/ship-feature --local "Implement rate limiting middleware that blocks IPs after 100 requests per minute"
/ship-feature "Create user dashboard showing trading history with pagination and CSV export"
```
</parameters>

<state_variables>
| Variable | Type | Description |
|----------|------|-------------|
| `{feature_description}` | string | Full description from $ARGUMENTS (with --local stripped) |
| `{short_title}` | string | Extracted title (max 50 chars) for issue |
| `{slug}` | string | URL-safe slug for branch name (max 40 chars) |
| `{launch_mode}` | string | `"local"` or `"remote"` — controls Ralph launch behavior |
| `{transport}` | string | `"local"` (gh CLI) or `"remote"` (MCP tools) — auto-detected |
| `{repo_owner}` | string | GitHub repository owner (extracted from git remote) |
| `{repo_name}` | string | GitHub repository name (extracted from git remote) |
| `{issue_number}` | number | GitHub issue number from creation |
| `{issue_url}` | string | Full GitHub issue URL |
| `{branch_name}` | string | Full branch name: feature/{number}-{slug} |
| `{temp_import_dir}` | string | Temp directory from ralph-import |
| `{pr_url}` | string | GitHub pull request URL |
</state_variables>

<entry_point>
Load `steps/step-00-init.md`
</entry_point>

<step_files>
| Step | File | Purpose |
|------|------|---------|
| 00 | `step-00-init.md` | Parse $ARGUMENTS, extract title, slug, --local flag; detect transport |
| 01 | `step-01-create-issue.md` | Create GitHub issue (gh or MCP), capture number |
| 02 | `step-02-create-branch.md` | Create and checkout feature branch |
| 03 | `step-03-push-branch.md` | Push branch to origin with tracking |
| 04 | `step-04-ralph-import.md` | cd to repo root, export issue body, run ralph-import |
| 05 | `step-05-copy-ralph-files.md` | Copy generated files into .ralph/, clean up |
| 06 | `step-06-show-and-launch.md` | Display files, launch Ralph (blocks until done) |
| 07 | `step-07-push-and-pr.md` | Push commits and open a pull request (gh or MCP) |
</step_files>

<execution_rules>
1. **No Confirmation**: Execute all steps without asking user
2. **Progressive Loading**: Load one step at a time
3. **Error Handling**: If any step fails, stop and report error
4. **Wait for Import**: ralph-import takes ~2 minutes - wait for completion
5. **Preserve Project Config**: Never overwrite .ralphrc or AGENT.md
6. **Auto-Launch**: Ralph starts automatically after files are copied
7. **Wait for Ralph**: Ralph blocks until complete, then proceed to push/PR
</execution_rules>

<success_criteria>
✅ GitHub issue created with descriptive title
✅ Feature branch created, checked out, and pushed
✅ ralph-import generated PROMPT.md, fix_plan.md, and specs/
✅ Generated files copied into project's .ralph/ directory
✅ Temp import directory cleaned up
✅ Ralph launched and completed
✅ Commits pushed and PR created on GitHub
</success_criteria>
