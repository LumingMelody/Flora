# OpenSpec: Validate Change or Spec

Validate OpenSpec change or specification: $ARGUMENTS

## Instructions

Validate the structure and format of OpenSpec changes and specifications.

### Step 1: Identify What to Validate

If `$ARGUMENTS` is provided:
- Check if it's a change in `openspec/changes/<argument>/`
- Check if it's a spec in `openspec/specs/<argument>/`

If no argument provided:
- Validate all changes and specs
- Report summary of issues

### Step 2: Validate Change

For each change in `openspec/changes/<change-id>/`:

#### 2.1 Check Required Files
```
✓/✗ proposal.md exists
✓/✗ tasks.md exists
✓/✗ specs/ directory exists (if has deltas)
```

#### 2.2 Validate proposal.md
```
✓/✗ Has ## Why section
✓/✗ Has ## What Changes section
✓/✗ Has ## Capabilities section
✓/✗ Has ## Impact section
```

#### 2.3 Validate tasks.md
```
✓/✗ Has numbered task groups (## 1., ## 2., etc.)
✓/✗ Tasks use checkbox format (- [ ] or - [x])
✓/✗ Tasks have hierarchical numbering (1.1, 1.2, etc.)
```

#### 2.4 Validate Spec Deltas
For each `specs/<capability>/spec.md`:
```
✓/✗ Has valid delta operation headers (## ADDED/MODIFIED/REMOVED/RENAMED Requirements)
✓/✗ Requirements use ### Requirement: format
✓/✗ Every requirement has at least one #### Scenario:
✓/✗ Scenarios use WHEN/THEN format
✓/✗ Requirements use SHALL/MUST (not should/may)
```

### Step 3: Validate Spec

For each spec in `openspec/specs/<capability>/`:

#### 3.1 Check Required Files
```
✓/✗ spec.md exists
```

#### 3.2 Validate spec.md
```
✓/✗ Has # heading (capability name)
✓/✗ Has ## Purpose or ## Overview section
✓/✗ Requirements use ### Requirement: format
✓/✗ Every requirement has at least one #### Scenario:
✓/✗ Scenarios use WHEN/THEN format
✓/✗ Requirements use SHALL/MUST
```

### Common Validation Errors

| Error | Description | Fix |
|-------|-------------|-----|
| Missing scenario | Requirement has no `#### Scenario:` | Add at least one scenario |
| Wrong scenario format | Using `### Scenario:` or `- **Scenario:**` | Use exactly `#### Scenario:` |
| Weak requirement | Using "should" or "may" | Use "SHALL" or "MUST" |
| Missing delta header | No `## ADDED/MODIFIED/REMOVED Requirements` | Add appropriate header |
| Incomplete MODIFIED | MODIFIED doesn't include full content | Copy entire requirement and edit |

### Output Format

```
═══════════════════════════════════════════════════════════════
VALIDATION REPORT
═══════════════════════════════════════════════════════════════

## Change: <change-id>

### Files
✓ proposal.md
✓ tasks.md
✓ specs/user-auth/spec.md

### proposal.md
✓ Has Why section
✓ Has What Changes section
✓ Has Capabilities section
✓ Has Impact section

### tasks.md
✓ Valid task groups
✓ Valid checkbox format
✓ Valid numbering

### specs/user-auth/spec.md
✓ Valid delta headers
✓ Requirements properly formatted
✗ ERROR: Requirement "User Login" missing scenario
✗ ERROR: Scenario uses wrong format (### instead of ####)

───────────────────────────────────────────────────────────────

## Summary

Total items validated: 3
Passed: 2
Failed: 1

Errors to fix:
1. specs/user-auth/spec.md:15 - Add scenario to "User Login" requirement
2. specs/user-auth/spec.md:23 - Change ### Scenario to #### Scenario

═══════════════════════════════════════════════════════════════
```

### Strict Mode

When validating strictly, also check:
- No orphaned files (files not referenced)
- All capabilities in proposal.md have corresponding spec deltas
- Task numbering is sequential
- No duplicate requirement names
- Scenarios have both WHEN and THEN

### Auto-Fix Suggestions

For each error, provide a fix suggestion:

```
ERROR: Requirement "User Login" missing scenario

FIX: Add a scenario block:

#### Scenario: Successful login
- **WHEN** user provides valid credentials
- **THEN** system returns authentication token
```

## Notes

- Validation is non-destructive (read-only)
- Use validation before implementing or archiving
- Fix all errors before proceeding with workflow
