# OpenSpec: Create Change Proposal

Create a spec-driven change proposal for: $ARGUMENTS

## Instructions

You are helping create an OpenSpec change proposal. Follow these steps:

### Step 1: Understand Context

1. Check if `openspec/` directory exists. If not, create the basic structure:
   ```
   openspec/
   ├── project.md          # Project conventions
   ├── specs/              # Current truth - what IS built
   └── changes/            # Proposals - what SHOULD change
   ```

2. Review existing specs in `openspec/specs/` to understand current capabilities
3. Check `openspec/changes/` for any conflicting or related proposals

### Step 2: Create Change Proposal

1. **Choose a unique change-id**: Use kebab-case, verb-led naming (e.g., `add-user-auth`, `update-api-rate-limit`, `remove-legacy-export`)

2. **Create the change directory structure**:
   ```
   openspec/changes/<change-id>/
   ├── proposal.md         # Why and what changes
   ├── tasks.md            # Implementation checklist
   ├── design.md           # Technical decisions (optional)
   └── specs/              # Delta changes
       └── <capability>/
           └── spec.md     # ADDED/MODIFIED/REMOVED requirements
   ```

3. **Write proposal.md** with these sections:
   ```markdown
   # Change: <Brief description>

   ## Why
   <!-- 1-2 sentences on the problem or opportunity. What problem does this solve? Why now? -->

   ## What Changes
   <!-- Bullet list of changes. Mark breaking changes with **BREAKING** -->
   - Change 1
   - Change 2

   ## Capabilities

   ### New Capabilities
   <!-- New capabilities being introduced. Each creates specs/<name>/spec.md -->
   - `<name>`: <brief description>

   ### Modified Capabilities
   <!-- Existing capabilities whose REQUIREMENTS are changing -->
   - `<existing-name>`: <what requirement is changing>

   ## Impact
   <!-- Affected code, APIs, dependencies, systems -->
   ```

4. **Write spec deltas** in `specs/<capability>/spec.md`:
   ```markdown
   ## ADDED Requirements

   ### Requirement: <Name>
   The system SHALL/MUST <requirement description>.

   #### Scenario: <Scenario name>
   - **WHEN** <condition>
   - **THEN** <expected outcome>

   ## MODIFIED Requirements
   <!-- Include FULL updated requirement content -->

   ### Requirement: <Existing Name>
   <Complete modified requirement with all scenarios>

   ## REMOVED Requirements

   ### Requirement: <Name to remove>
   **Reason**: <Why removing>
   **Migration**: <How to handle>
   ```

5. **Write tasks.md**:
   ```markdown
   ## 1. <Task Group Name>

   - [ ] 1.1 <Task description>
   - [ ] 1.2 <Task description>

   ## 2. <Task Group Name>

   - [ ] 2.1 <Task description>
   - [ ] 2.2 <Task description>
   ```

6. **Write design.md** (only if needed - for complex changes):
   Create design.md if any of these apply:
   - Cross-cutting change (multiple services/modules)
   - New external dependency or significant data model changes
   - Security, performance, or migration complexity

   ```markdown
   ## Context
   <!-- Background, constraints, stakeholders -->

   ## Goals / Non-Goals
   **Goals:**
   - ...

   **Non-Goals:**
   - ...

   ## Decisions
   <!-- Key design decisions and rationale -->

   ## Risks / Trade-offs
   <!-- Known risks and trade-offs -->
   ```

### Step 3: Validate

After creating the proposal:
1. Ensure every requirement has at least one `#### Scenario:`
2. Use SHALL/MUST for normative requirements
3. Verify change-id is unique
4. Check that all affected capabilities have delta specs

### Important Rules

- **Scenarios MUST use exactly 4 hashtags (`####`)** - Using 3 hashtags or bullets will fail
- **MODIFIED requirements must include FULL content** - Partial deltas lose detail
- **Every requirement needs at least one scenario**
- **Use verb-led change-id prefixes**: `add-`, `update-`, `remove-`, `refactor-`

## When to Skip Proposal

Skip proposal for:
- Bug fixes (restore intended behavior)
- Typos, formatting, comments
- Dependency updates (non-breaking)
- Configuration changes
- Tests for existing behavior

## Output

After creating the proposal, summarize:
1. Change ID created
2. Files created
3. Capabilities affected
4. Next steps (review and approval before implementation)
