# OpenSpec: Apply Change

Implement the OpenSpec change: $ARGUMENTS

## Instructions

You are implementing an approved OpenSpec change proposal. Follow these steps:

### Step 1: Load Context

1. **Identify the change**: If no change-id provided, list available changes:
   ```bash
   ls openspec/changes/
   ```

2. **Read the proposal files** in order:
   - `openspec/changes/<change-id>/proposal.md` - Understand WHY and WHAT
   - `openspec/changes/<change-id>/design.md` - Review HOW (if exists)
   - `openspec/changes/<change-id>/specs/**/*.md` - Understand requirements
   - `openspec/changes/<change-id>/tasks.md` - Get implementation checklist

3. **Read related existing specs** in `openspec/specs/` for context

### Step 2: Implement Tasks

Work through tasks sequentially from `tasks.md`:

1. **Track progress using TodoWrite tool** - Create todos for each task
2. **Implement each task one by one**
3. **Mark tasks complete as you go** - Update both TodoWrite and tasks.md

For each task:
```markdown
- [ ] 1.1 Task description  →  - [x] 1.1 Task description
```

### Step 3: Update Task Status

After completing each task, update `tasks.md`:
- Change `- [ ]` to `- [x]` for completed tasks
- Add notes if implementation differs from plan

### Step 4: Verify Implementation

Before marking the change as complete:

1. **Check all tasks are done** - Every `- [ ]` should be `- [x]`
2. **Verify against specs** - Each scenario in spec deltas should be satisfied
3. **Run relevant tests** - Ensure nothing is broken
4. **Review the code** - Check for quality and consistency

### Implementation Guidelines

**Follow the specs exactly:**
- Each `#### Scenario:` is a test case
- SHALL/MUST requirements are mandatory
- WHEN/THEN conditions define expected behavior

**Keep changes focused:**
- Only implement what's in the proposal
- Don't add extra features or "improvements"
- If you find issues, note them but don't fix unrelated things

**Handle blockers:**
- If a task is blocked, document why
- Ask for clarification if requirements are unclear
- Don't guess - pause and ask

### Output

After implementation, report:
1. Tasks completed (X/Y)
2. Files created/modified
3. Any deviations from the plan
4. Blockers or issues encountered
5. Next steps (testing, review, archive)

### Example Workflow

```
1. Read proposal.md → Understand the change
2. Read design.md → Understand technical approach
3. Read specs/*.md → Understand requirements
4. Read tasks.md → Get task list

5. For each task:
   - Mark as in_progress in TodoWrite
   - Implement the task
   - Mark as completed in TodoWrite
   - Update tasks.md: - [ ] → - [x]

6. Verify all scenarios are satisfied
7. Report completion status
```

## Important Notes

- **Do NOT start implementation until proposal is approved**
- **Complete tasks in order** - Dependencies matter
- **Update tasks.md as you go** - Don't batch updates
- **Ask questions early** - Don't make assumptions
