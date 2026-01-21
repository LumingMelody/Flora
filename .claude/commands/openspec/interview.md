# OpenSpec: Interview Mode

Start an interactive interview to clarify requirements before creating a proposal.

Topic: $ARGUMENTS

## Instructions

You are conducting a requirements interview. Your goal is to deeply understand what the user wants before writing any code or creating a formal proposal.

### Interview Process

#### Phase 1: Understanding the Goal (1-2 questions)

Start by understanding the high-level goal:

```
═══════════════════════════════════════════════════════════════
🎯 OPENSPEC INTERVIEW: <Topic>
═══════════════════════════════════════════════════════════════

Let me help you clarify this requirement before we start.

**Question 1: What problem are you trying to solve?**

Please describe:
- What's the current situation?
- What's painful or missing?
- What would success look like?
```

Wait for user response before continuing.

#### Phase 2: Scope & Boundaries (2-3 questions)

After understanding the goal, clarify scope:

- What's IN scope vs OUT of scope?
- Are there any constraints (time, tech, compatibility)?
- Who are the users/consumers of this feature?
- What existing code/systems does this touch?

Ask ONE question at a time. Wait for response.

#### Phase 3: Behavior & Scenarios (2-4 questions)

Dig into specific behaviors:

- Walk me through the happy path - what happens step by step?
- What are the edge cases or error scenarios?
- Are there any specific inputs/outputs you have in mind?
- How should the system behave when X happens?

Ask ONE question at a time. Wait for response.

#### Phase 4: Technical Preferences (1-2 questions, if relevant)

Only ask if not already clear:

- Do you have a preference for how this should be implemented?
- Are there existing patterns in the codebase we should follow?
- Any performance or security requirements?

#### Phase 5: Summary & Confirmation

After gathering enough information, summarize:

```
═══════════════════════════════════════════════════════════════
📋 INTERVIEW SUMMARY
═══════════════════════════════════════════════════════════════

**Problem Statement:**
<1-2 sentences summarizing the problem>

**Proposed Solution:**
<Brief description of what will be built>

**Key Requirements:**
1. <Requirement 1>
2. <Requirement 2>
3. <Requirement 3>

**Scope:**
- ✅ In scope: <list>
- ❌ Out of scope: <list>

**Key Scenarios:**
1. <Scenario 1: happy path>
2. <Scenario 2: edge case>
3. <Scenario 3: error handling>

**Technical Approach:**
<Brief technical direction if discussed>

**Affected Areas:**
- <File/module 1>
- <File/module 2>

═══════════════════════════════════════════════════════════════

Does this accurately capture what you want?

Reply:
- **"yes"** or **"确认"** - I'll create the formal proposal
- **"no"** or provide corrections - I'll update the summary
- **"more"** - Let's discuss more details
```

### After Confirmation

When user confirms, automatically run the proposal creation:

1. Create the change proposal using `/openspec:proposal` format
2. Generate appropriate specs with scenarios from the interview
3. Create tasks.md based on the discussed scope

### Interview Guidelines

**DO:**
- Ask ONE question at a time
- Wait for user response before next question
- Use the user's language and terminology
- Summarize and reflect back what you heard
- Be concise - respect user's time
- Skip questions if already answered

**DON'T:**
- Ask multiple questions at once
- Assume requirements - always verify
- Jump to implementation details too early
- Make the interview feel like an interrogation
- Ask more than 8-10 questions total

### Adaptive Behavior

- If user gives detailed initial description → skip basic questions
- If user seems unsure → offer options/examples
- If scope is small → shorter interview (3-5 questions)
- If scope is large → suggest breaking into multiple proposals

### Output Format

Use clear visual separators and formatting:
- Use `═══` for major sections
- Use `───` for subsections
- Use emoji sparingly for visual anchors (🎯 📋 ✅ ❌)
- Keep questions bold and clearly numbered

## Example Interview Flow

```
User: /openspec:interview 添加用户认证功能

Claude:
═══════════════════════════════════════════════════════════════
🎯 OPENSPEC INTERVIEW: 添加用户认证功能
═══════════════════════════════════════════════════════════════

Let me help you clarify this requirement.

**Question 1: What authentication method do you need?**

Options:
- Username/password login
- OAuth (Google, GitHub, etc.)
- API key authentication
- JWT tokens
- Something else?

User: 用户名密码登录，然后用JWT

Claude:
Got it - username/password with JWT tokens.

**Question 2: What user operations do you need?**

- [ ] Register new account
- [ ] Login
- [ ] Logout
- [ ] Password reset
- [ ] Email verification
- [ ] Other: ___

User: 注册、登录、登出就行，密码重置以后再说

Claude:
Understood - register, login, logout for now. Password reset is out of scope.

**Question 3: Where will this be used?**

- Which service(s) need authentication?
- Is this for the API, frontend, or both?

...continues...
```
