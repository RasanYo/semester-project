# Generate Directory README

Generate or update a README.md for a directory by analyzing its contents.

**Target directory:** $ARGUMENTS (defaults to current directory if empty)

## Instructions

### Step 1: Validate the path

If `$ARGUMENTS` is provided, verify the directory exists. If it doesn't exist, print a clear error message and stop. If `$ARGUMENTS` is empty, use the current working directory.

### Step 2: Scan the directory

List all files and subdirectories in the target directory (non-recursive, one level only).

Identify source files by extension: `.py`, `.ts`, `.js`, `.sh`, `.go`, `.rs`, `.java`

### Step 3: Read source files

Read each source file in full. Modern context windows handle this easily, and full file content produces better documentation by capturing all public functions and classes.

If no source files are found, warn the user but continue - attempt to generate documentation based on file names, folder names, and any config files present.

### Step 4: Check for existing README

If a `README.md` already exists in the target directory:
- Read its current content
- Preserve any valuable context while updating to match the current code state
- Do not start from scratch - treat it as an update

### Step 5: Generate the README

Write a README.md following this exact structure:

```markdown
# [module name]

[One sentence: what this module does]

## Why?

[2–4 sentences: what problem this solves, why it exists as a separate module]

## Architecture

[Short description of how files/components fit together. One line per file if the module has multiple files.]

## Usage

[Minimal code example showing the most common use case]
```

**Hard constraints:**
- Maximum **60 lines** total
- Maximum **20 lines** for the Architecture section
- **No table of contents**
- **No badges**
- **No license or author sections**
- **Present tense** throughout ("handles", "fetches", not "will handle")
- Focus on **surface area** (what it does, how to use it), not implementation details
- Only include sections that are relevant - if the module is a single simple script, skip Architecture

### Step 6: Write the file

Write the generated content to `[target_directory]/README.md`.

Confirm completion by stating:
- The path where README was written
- A brief summary of what was documented
