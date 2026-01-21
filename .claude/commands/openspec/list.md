# OpenSpec: List Changes and Specs

List OpenSpec changes and specifications.

## Instructions

Display the current state of OpenSpec in this project.

### Step 1: Check OpenSpec Structure

First, verify OpenSpec is initialized:
```bash
ls -la openspec/
```

If `openspec/` doesn't exist, inform the user:
```
OpenSpec is not initialized in this project.
Run /openspec:init to set up OpenSpec.
```

### Step 2: List Active Changes

List all pending changes in `openspec/changes/` (excluding archive):

```bash
ls openspec/changes/ | grep -v archive
```

For each change, show:
- Change ID (directory name)
- Status (has proposal.md, tasks.md, etc.)
- Brief description (from proposal.md first line)

### Step 3: List Specifications

List all current specs in `openspec/specs/`:

```bash
ls openspec/specs/
```

For each spec, show:
- Capability name (directory name)
- Number of requirements
- Brief description

### Step 4: List Archived Changes

Optionally list recent archives:

```bash
ls openspec/changes/archive/ | tail -5
```

### Output Format

```
## Active Changes

| Change ID | Status | Description |
|-----------|--------|-------------|
| add-user-auth | Ready | Add user authentication system |
| update-api | In Progress | Update API rate limiting |

## Specifications

| Capability | Requirements | Description |
|------------|--------------|-------------|
| user-auth | 3 | User authentication and sessions |
| api-core | 5 | Core API functionality |

## Recent Archives (last 5)

- 2024-01-10-add-logging
- 2024-01-08-fix-validation
- 2024-01-05-update-schema
```

### Status Indicators

For changes:
- **Draft** - Only proposal.md exists
- **Specified** - Has specs/*.md files
- **Ready** - Has tasks.md, ready for implementation
- **In Progress** - Some tasks marked complete
- **Complete** - All tasks done, ready to archive

### Quick Commands

After listing, suggest relevant actions:
- If no changes: "Use /openspec:proposal to create a new change"
- If changes ready: "Use /openspec:apply <change-id> to implement"
- If changes complete: "Use /openspec:archive <change-id> to archive"
