# OpenSpec: Initialize Project

Initialize OpenSpec in this project.

## Instructions

Set up OpenSpec spec-driven development structure in the current project.

### Step 1: Check Existing Setup

First, check if OpenSpec is already initialized:
```bash
ls -la openspec/
```

If `openspec/` exists:
- Show current structure
- Ask if user wants to reset or update

### Step 2: Create Directory Structure

Create the OpenSpec directory structure:

```bash
mkdir -p openspec/specs
mkdir -p openspec/changes
mkdir -p openspec/changes/archive
```

### Step 3: Create project.md

Create `openspec/project.md` with project conventions:

```markdown
# Project: <Project Name>

## Overview

<!-- Brief description of the project -->

## Tech Stack

<!-- List main technologies, frameworks, languages -->
- Language:
- Framework:
- Database:
- Other:

## Conventions

### Code Style
<!-- Coding conventions and standards -->

### Architecture
<!-- High-level architecture patterns -->

### Testing
<!-- Testing approach and requirements -->

### Documentation
<!-- Documentation standards -->

## Directory Structure

<!-- Key directories and their purposes -->

## Getting Started

<!-- How to set up and run the project -->
```

### Step 4: Create Example Spec (Optional)

If user wants an example, create a sample spec:

`openspec/specs/example/spec.md`:
```markdown
# Example Specification

## Purpose

This is an example specification to demonstrate the OpenSpec format.

## ADDED Requirements

### Requirement: Example Feature
The system SHALL provide an example feature for demonstration.

#### Scenario: Basic usage
- **WHEN** user triggers the example feature
- **THEN** the system responds with expected behavior

#### Scenario: Error handling
- **WHEN** user provides invalid input
- **THEN** the system returns an appropriate error message
```

### Step 5: Update .gitignore (Optional)

Suggest adding to `.gitignore` if needed:
```
# OpenSpec - keep specs but ignore local state
# (usually you want to commit everything in openspec/)
```

### Step 6: Provide Next Steps

After initialization, inform the user:

```
OpenSpec initialized successfully!

Directory structure created:
  openspec/
  ├── project.md          # Project conventions (please fill in)
  ├── specs/              # Current specifications
  └── changes/            # Change proposals
      └── archive/        # Completed changes

Next steps:
1. Edit openspec/project.md to describe your project
2. Use /openspec:proposal to create your first change
3. Use /openspec:list to view changes and specs

Quick start:
  /openspec:proposal Add user authentication
```

### Output

```
═══════════════════════════════════════════════════════════════
OPENSPEC INITIALIZED
═══════════════════════════════════════════════════════════════

Created:
  ✓ openspec/project.md
  ✓ openspec/specs/
  ✓ openspec/changes/
  ✓ openspec/changes/archive/

Please edit openspec/project.md to add your project details.

Available commands:
  /openspec:proposal <description>  - Create a change proposal
  /openspec:apply <change-id>       - Implement a change
  /openspec:archive <change-id>     - Archive completed change
  /openspec:list                    - List changes and specs
  /openspec:show <item>             - Show details

═══════════════════════════════════════════════════════════════
```

## Notes

- OpenSpec works without any external dependencies
- All files are Markdown for easy reading and editing
- The structure is designed to work with any AI coding assistant
- Specs are the source of truth; changes are proposals
