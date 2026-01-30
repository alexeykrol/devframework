# Tech Context

## Core Technologies
- **Python 3**: The primary language for the Orchestrator and helper scripts.
- **Git**: Heavily used for `worktree` management, branching, and merging.
- **Shell (Bash)**: Used for installation (`install-fr.sh`) and environment setup.

## AI Tools Supported
- **Claude Code (Anthropic)**: Primary agent for complex tasks. Needs specific "autonomy protocols" (see `claude-code/`).
- **OpenAI Codex**: Used via CLI wrapper.
- **Aider**: Supported as a runner backend.
- **GPT-5.2 Pro**: Referenced as a high-level architect/team lead role.

## Configuration Formats
- **JSON**: Main configuration (`orchestrator.json`).
- **YAML**: Alternative config format supported.
- **Markdown**: Task templates and documentation.

## Development Environment
- **OS**: macOS/Linux (Bash required).
- **Dependencies**: Python 3 standard library (minimizing external deps for portability).
- **Project Structure**:
  - `framework/`: The executable core.
  - `_worktrees/`: Transient directory for active agents (git ignored).

## Constraints
- **Local Execution**: Designed to run on the user's machine, not a cloud service.
- **Git Repository Required**: The host project must be a git repo.
- **API Keys**: Users must provide their own keys for the AI tools used.
