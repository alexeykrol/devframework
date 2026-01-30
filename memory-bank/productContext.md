# Product Context

## Problem Statement
Working with AI coding assistants (Claude Code, Codex, Aider) typically involves a serial, interactive workflow. A developer must supervise one agent at a time, answering frequent questions and resolving conflicts manually if multiple agents touch the codebase. This limits throughput and demands constant human attention.

## Solution Strategy
Devframework introduces an orchestration layer that decouples AI execution from direct human supervision.
- **Role-Based Delegation**: Instead of "help me with code," the system assigns roles: "You are the DB Architect, produce schema X."
- **Worktree Isolation**: Each agent gets its own git worktree, ensuring filesystem-level isolation.
- **Structured Handoffs**: Tasks produce standard outputs (specs, schemas, code) that feed into subsequent tasks or a merge phase.

## User Experience
1. **Setup**: User clones the framework or installs it into an existing project.
2. **Configuration**: User defines high-level tasks in `orchestrator.json` or uses defaults.
3. **Execution**: User runs the orchestrator.
   - **Discovery Phase**: Interactive interview to gather requirements.
   - **Development Phase**: The user steps back while multiple agents work in parallel.
   - **Review Phase**: Automated agents critique the work.
4. **Result**: User receives a set of merged changes, logs, and reports ready for final human approval.

## Business Value
- **Scalability**: One developer can manage a "team" of AI agents.
- **Efficiency**: Parallel processing drastically reduces total elapsed time for features.
- **Consistency**: Standardized prompts and workflows reduce variance in AI output.
- **Safety**: Isolation and review steps minimize the risk of destructive AI edits.
