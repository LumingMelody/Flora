# OpenSpec: Show Change or Spec Details

Show details for: $ARGUMENTS

## Instructions

Display detailed information about a specific change or specification.

### Step 1: Identify the Item

If `$ARGUMENTS` is provided, determine if it's a change or spec:
- Check `openspec/changes/<argument>/` for changes
- Check `openspec/specs/<argument>/` for specs

If no argument provided, list available items and ask user to specify.

### Step 2: Show Change Details

If showing a change (`openspec/changes/<change-id>/`):

1. **Read and display proposal.md**:
   ```
   ## Proposal: <change-id>

   <contents of proposal.md>
   ```

2. **Read and display tasks.md** with progress:
   ```
   ## Tasks

   Progress: X/Y complete

   <contents of tasks.md>
   ```

3. **Read and display design.md** (if exists):
   ```
   ## Design

   <contents of design.md>
   ```

4. **List spec deltas**:
   ```
   ## Spec Deltas

   Affected capabilities:
   - <capability-1>: X added, Y modified, Z removed
   - <capability-2>: ...
   ```

5. **Show delta details** for each capability:
   ```
   ### Delta: <capability>

   <contents of specs/<capability>/spec.md>
   ```

### Step 3: Show Spec Details

If showing a spec (`openspec/specs/<capability>/`):

1. **Read and display spec.md**:
   ```
   ## Specification: <capability>

   <contents of spec.md>
   ```

2. **Count and list requirements**:
   ```
   Requirements: X total

   1. <Requirement Name 1>
      - Scenarios: Y
   2. <Requirement Name 2>
      - Scenarios: Z
   ```

3. **Show design.md** (if exists):
   ```
   ## Design

   <contents of design.md>
   ```

### Output Format

For changes:
```
═══════════════════════════════════════════════════════════════
CHANGE: <change-id>
═══════════════════════════════════════════════════════════════

## Proposal

<proposal content>

───────────────────────────────────────────────────────────────

## Tasks (X/Y complete)

<tasks content>

───────────────────────────────────────────────────────────────

## Spec Deltas

### <capability-1>
<delta content>

═══════════════════════════════════════════════════════════════
```

For specs:
```
═══════════════════════════════════════════════════════════════
SPECIFICATION: <capability>
═══════════════════════════════════════════════════════════════

## Requirements (X total)

<spec content>

═══════════════════════════════════════════════════════════════
```

### Helpful Analysis

After showing details, provide:

For changes:
- Current status (Draft/Specified/Ready/In Progress/Complete)
- Next recommended action
- Any issues or missing pieces

For specs:
- Number of requirements and scenarios
- Related changes (if any pending changes affect this spec)
- Coverage assessment

### Error Handling

If item not found:
```
Item '<argument>' not found.

Did you mean one of these?
- Changes: <list similar change names>
- Specs: <list similar spec names>

Use /openspec:list to see all available items.
```
