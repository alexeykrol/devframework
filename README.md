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

## Parallel review flow (two-agent)
1) Dev agent completes tasks and prepares `review/handoff.md` (and test results if any).
2) In parallel, a second agent uses `review/runbook.md` and `review/review-brief.md` to run review/testing.
3) Review outputs go to `review/` and are fed back to the dev agent.

## AGENTS.md behavior (Codex)
1) When AGENTS.md is read
   Codex builds the instruction chain at session start (one time per launch; in TUI this is one session).
   It reads AGENTS.md before work begins and applies it for the whole session.
   Source: `developers.openai.com/codex/guides/agents-md/`
2) What /init does
   /init only creates AGENTS.md. Reading happens only on the next launch/session.
   If you create or change the file during an active session, you must start a new session for it to apply.
   Source: `developers.openai.com/codex/guides/agents-md/`
3) Where instructions are loaded from
   - Global: first `~/.codex/AGENTS.override.md` if it exists, otherwise `~/.codex/AGENTS.md`.
   - Project: from repo root to current folder, in each directory it looks for `AGENTS.override.md`,
     then `AGENTS.md`, then fallback names.
   - Merge order: files are combined top‑down; closer to the current folder has higher priority.
   - Limit: reading is capped by `project_doc_max_bytes`.
   This is all constructed at session start.
   Source: `developers.openai.com/codex/guides/agents-md/`
4) How to verify instructions were applied
   In the docs they suggest starting Codex and asking it to “show which instructions are active”
   or “summarize instructions” — it should list files in priority order.
   Source: `developers.openai.com/codex/guides/agents-md/`

Summary: there is no explicit “read” command — it is automatic on session start. /init ≠ “read”.
/init = “create template”; reading happens on the next launch.
