# Project Brief: Devframework

## Overview
Devframework is a local scaffold for orchestrating parallel tasks using AI agents and git worktrees. It solves the bottlenecks of serial AI assistance (one task at a time, manual supervision) by treating AI agents as a parallel "construction crew" managed by an Orchestrator.

## Core Goals
1. **Parallel Execution**: Run multiple AI agents simultaneously (e.g., Database, Logic, UI) to reduce development time from ~8 hours to ~2.5 hours.
2. **Isolation**: Use Git worktrees to prevent conflict between agents working on different features.
3. **Autonomy**: Shift from "Interaction First" (chatting) to "Delegation First" (long-running autonomous tasks).
4. **Quality Control**: Automated review agents and comprehensive logging/documentation.

## Key Features
- **Orchestrator**: Python-based dispatch system reading from `orchestrator.json`.
- **Git Worktree Integration**: Automatic management of isolated environments for each task.
- **Task Templates**: Markdown-based prompts defining specific roles (DB Architect, Backend Dev, etc.).
- **Multi-Agent Support**: Supports Claude Code, OpenAI Codex, Aider, and GPT-5.2 Pro.
- **Lifecycle Management**: Discovery -> Development -> Review -> Hand-off.

## Success Criteria
- Reduction in development time for standard feature sets.
- Zero git conflicts between parallel agents.
- Comprehensive artifacts (logs, handoffs, reviews) generated for every run.
- Seamless integration with existing projects via `install-fr.sh`.
