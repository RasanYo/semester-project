# Playwright CLI Skill

Browser automation for testing via Playwright CLI. Optimized for token efficiency in coding agents.

## Installation

Ensure Playwright CLI and Chrome are installed:
```bash
npm install -g @playwright/cli@latest
# Chrome must be installed at /opt/google/chrome/chrome
```

## Config Files

Two config files are available for different testing contexts:

### Desktop (CMS Testing)
```bash
playwright-cli --config=playwright-cli.desktop.json --session=cms-test <command>
```
- Viewport: 1280x720
- Use for: CMS admin interface testing

### Mobile (Webapp Testing)
```bash
playwright-cli --config=playwright-cli.mobile.json --session=webapp-test <command>
```
- Device: iPhone 14 emulation
- Use for: Visitor webapp testing (mobile-first)

## Quick Reference

### Navigation
```bash
playwright-cli open <url>                    # Open URL in browser
playwright-cli go-back                       # Navigate back
playwright-cli go-forward                    # Navigate forward
playwright-cli reload                        # Reload page
```

### Element Interaction
```bash
playwright-cli click <ref>                   # Click element
playwright-cli fill <ref> <text>             # Fill input field
playwright-cli select <ref> <value>          # Select dropdown option
playwright-cli check <ref>                   # Check checkbox
playwright-cli uncheck <ref>                 # Uncheck checkbox
playwright-cli hover <ref>                   # Hover over element
```

### Keyboard & Input
```bash
playwright-cli press <key>                   # Press key (Enter, Tab, Escape)
playwright-cli type <text>                   # Type text with key events
```

### Page Inspection
```bash
playwright-cli snapshot                      # Get accessibility snapshot
playwright-cli screenshot                    # Take screenshot
playwright-cli pdf                           # Generate PDF
playwright-cli console                       # Get console logs
```

### Waiting
```bash
playwright-cli wait <ms>                     # Wait milliseconds
playwright-cli wait-for <ref>                # Wait for element
playwright-cli wait-for-url <pattern>        # Wait for URL match
```

## Element References

Elements are referenced by their accessibility properties:

- **By role**: `button[name="Submit"]`, `link[name="Home"]`
- **By test-id**: `[data-testid="login-form"]`
- **By text**: `text="Click me"`
- **By placeholder**: `[placeholder="Email"]`

## Session Management

Use sessions to isolate browser state per project:
```bash
playwright-cli --session=melior-test open http://localhost:3000
```

Sessions persist cookies and storage between commands.

## Headless Mode

Default is visible browser. For CI/testing:
```bash
playwright-cli --headless open <url>
```

## Common Testing Patterns

### Login Flow
```bash
playwright-cli open http://localhost:3000/login
playwright-cli fill "[placeholder='Email']" "test@example.com"
playwright-cli fill "[placeholder='Password']" "password123"
playwright-cli click "button[name='Sign in']"
playwright-cli wait-for-url "**/dashboard**"
playwright-cli snapshot  # Verify dashboard loaded
```

### Form Submission
```bash
playwright-cli open http://localhost:3000/audioguides/new
playwright-cli fill "[name='title']" "Test Audioguide"
playwright-cli fill "[name='description']" "A test description"
playwright-cli click "button[name='Save']"
playwright-cli wait 1000
playwright-cli snapshot  # Verify success state
```

### Dialog Interaction
```bash
playwright-cli click "button[name='Create Audioguide']"
playwright-cli wait-for "[role='dialog']"
playwright-cli snapshot  # Get dialog content
playwright-cli fill "[name='title']" "New Guide"
playwright-cli click "button[name='Submit']"
```

### Verification
```bash
playwright-cli snapshot | grep "My Audioguide"  # Check text exists
playwright-cli screenshot --path=test-result.png  # Visual capture
```

## Error Handling

If a command fails, the CLI returns non-zero exit code with error message.
Common issues:
- Element not found: Check selector, use `snapshot` to see current state
- Timeout: Increase wait time or check if page is loading
- Navigation failed: Verify URL and server is running
