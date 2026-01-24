# Devframework

Local scaffold for orchestrating parallel tasks with git worktrees.

## Structure
- framework/orchestrator/ - script and YAML config
- framework/docs/ - process docs, checklists, orchestration plan
- docs/tasks/ - task mini-spec templates
- review/ - independent review artifacts and runbook

## Quick start
1) Fill in the task files in `docs/tasks/*.md`.
2) Review `framework/orchestrator/orchestrator.yaml`.
3) Run:
   `python3 framework/orchestrator/orchestrator.py --config framework/orchestrator/orchestrator.yaml`

## Outputs
- `logs/*.log`
- `docs/orchestrator-run-summary.md`
- `review/*.md`

## Notes
- Relative paths in YAML are resolved from the config file; task paths are resolved from `project_root`.
- The repo must be a git repository (for `git worktree`).
