# OpenSpec: Archive Change

Archive the completed OpenSpec change: $ARGUMENTS

## Instructions

You are archiving a completed OpenSpec change. This moves the change to archive and updates the source-of-truth specs.

### Step 1: Verify Completion

1. **Identify the change**: If no change-id provided, list available changes:
   ```bash
   ls openspec/changes/
   ```

2. **Check all tasks are complete**:
   - Read `openspec/changes/<change-id>/tasks.md`
   - Verify every task is marked `- [x]`
   - If any tasks are incomplete, do NOT archive

3. **Verify implementation matches specs**:
   - Review each scenario in `openspec/changes/<change-id>/specs/**/*.md`
   - Confirm the implementation satisfies all requirements

### Step 2: Update Source Specs

Apply the delta changes to the source-of-truth specs in `openspec/specs/`:

1. **For ADDED Requirements**:
   - If capability doesn't exist, create `openspec/specs/<capability>/spec.md`
   - Add the new requirements to the spec file

2. **For MODIFIED Requirements**:
   - Find the existing requirement in `openspec/specs/<capability>/spec.md`
   - Replace it with the updated content from the delta

3. **For REMOVED Requirements**:
   - Remove the requirement from `openspec/specs/<capability>/spec.md`
   - Keep a comment or note about the removal if needed

4. **For RENAMED Requirements**:
   - Update the requirement name in `openspec/specs/<capability>/spec.md`

### Step 3: Move to Archive

1. **Create archive directory** with date prefix:
   ```bash
   mkdir -p openspec/changes/archive/YYYY-MM-DD-<change-id>
   ```
   Use today's date in YYYY-MM-DD format.

2. **Move all change files**:
   ```bash
   mv openspec/changes/<change-id>/* openspec/changes/archive/YYYY-MM-DD-<change-id>/
   rmdir openspec/changes/<change-id>
   ```

### Step 4: Verify Archive

1. **Check the archive is complete**:
   - `openspec/changes/archive/YYYY-MM-DD-<change-id>/proposal.md`
   - `openspec/changes/archive/YYYY-MM-DD-<change-id>/tasks.md`
   - `openspec/changes/archive/YYYY-MM-DD-<change-id>/specs/` (if had deltas)

2. **Check specs are updated**:
   - All ADDED requirements are in `openspec/specs/`
   - All MODIFIED requirements are updated
   - All REMOVED requirements are gone

### Special Cases

**Skip spec updates** (use `--skip-specs` flag mentally):
- For tooling-only changes that don't affect specs
- For documentation-only changes
- When specs were already updated manually

**Multiple capabilities**:
- Process each capability's delta separately
- Update each `openspec/specs/<capability>/spec.md` file

### Output

After archiving, report:
1. Change archived: `<change-id>` → `archive/YYYY-MM-DD-<change-id>`
2. Specs updated:
   - Added: list of new requirements
   - Modified: list of changed requirements
   - Removed: list of removed requirements
3. Archive location: `openspec/changes/archive/YYYY-MM-DD-<change-id>/`

### Example

```
Archiving change: add-user-auth

1. Verified all tasks complete (5/5)
2. Updated specs:
   - ADDED: openspec/specs/user-auth/spec.md
     - Requirement: User Authentication
     - Requirement: Session Management
3. Moved to: openspec/changes/archive/2024-01-15-add-user-auth/

Archive complete. Ready for next feature!
```

## Important Notes

- **Do NOT archive incomplete changes** - All tasks must be `- [x]`
- **Always update source specs** - Unless explicitly skipping
- **Use date prefix** - Format: YYYY-MM-DD-<change-id>
- **Keep archive intact** - Don't modify archived files
