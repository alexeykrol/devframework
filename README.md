# Devframework

Local scaffold for orchestrating parallel tasks with git worktrees.

## Structure
- framework/orchestrator/ - script and YAML config
- framework/docs/ - process docs, checklists, orchestration plan
- framework/tasks/ - task mini-spec templates
- framework/review/ - independent review artifacts and runbook
- framework/framework-review/ - framework QA artifacts (third flow)
- framework/migration/ - legacy migration analysis and safety artifacts
- framework/VERSION - framework release identifier
- framework.zip - portable bundle for host projects
- install-framework.sh - installer for framework.zip
- scripts/package-framework.py - build helper for framework.zip

## Quick start
1) Fill in the task files in `framework/tasks/*.md`.
2) Review `framework/orchestrator/orchestrator.yaml`.
3) Run:
   `python3 framework/orchestrator/orchestrator.py --config framework/orchestrator/orchestrator.yaml`

## Install in a host project (launcher)
1) Copy `install-framework.sh` into the host project root.
2) Run (downloads `framework.zip` from GitHub and installs into `./framework`):
   `./install-framework.sh --run`

Options:
- Use a local zip: `./install-framework.sh --zip ./framework.zip`
- Update an existing install (creates a backup first): `./install-framework.sh --update`
- Force phase: `./install-framework.sh --phase legacy` or `--phase main`
- Override repo/ref:
  `FRAMEWORK_REPO=alexeykrol/devframework FRAMEWORK_REF=main ./install-framework.sh --run`

Auto-detection:
- If the host root contains files other than `.git`, `framework/`, `framework.zip`, or
  `install-framework.sh`, the launcher assumes a legacy project and runs `--phase legacy`.

## End-to-end flows (memory cheatsheet)

### A) New project (clean host)
1) `./install-framework.sh --run`
2) Orchestrator runs `--phase main`.
3) Dev flow completes → parallel review flow uses `framework/review/`.
4) Optional post-run framework QA:
   `python3 framework/orchestrator/orchestrator.py --phase post`
5) Auto-publish (optional): set `FRAMEWORK_REPORTING_*` env vars before step 1.

### B) Legacy project (migration + safety)
1) `./install-framework.sh --run` (auto-detects legacy, runs `--phase legacy`)
2) Review migration artifacts:
   - `framework/migration/legacy-snapshot.md`
   - `framework/migration/legacy-tech-spec.md`
   - `framework/migration/legacy-gap-report.md`
   - `framework/migration/legacy-risk-assessment.md`
   - `framework/migration/legacy-migration-plan.md`
   - `framework/migration/legacy-migration-proposal.md`
3) Human approval gate:
   - Fill `framework/migration/approval.md`
4) Apply changes in isolated branch:
   `python3 framework/orchestrator/orchestrator.py --phase legacy --include-manual`
   (branch name includes `legacy-migration-<run_id>`)
5) Run review/tests, then merge manually if safe.
6) Optional framework QA (post-run) and auto-publish.

### C) Framework improvement loop (3rd agent)
1) Main or legacy run finishes.
2) Framework QA (post phase):
   `python3 framework/orchestrator/orchestrator.py --phase post`
3) Output:
   - `framework/framework-review/framework-log-analysis.md`
   - `framework/framework-review/framework-bug-report.md`
   - `framework/framework-review/framework-fix-plan.md`
4) Apply fixes between runs:
   `python3 framework/orchestrator/orchestrator.py --phase post --include-manual`
5) Rebuild release zip if framework changed:
   `python3 scripts/package-framework.py --version <new_version>`

### D) Auto‑report publishing (no manual steps)
1) Set env before running the launcher:
   - `FRAMEWORK_REPORTING_ENABLED=1`
   - `FRAMEWORK_REPORTING_REPO=alexeykrol/devframework`
   - `FRAMEWORK_REPORTING_MODE=pr|issue|both`
   - `FRAMEWORK_REPORTING_HOST_ID=<host>`
   - `FRAMEWORK_REPORTING_PHASES=legacy,main,post`
   - (optional) `FRAMEWORK_REPORTING_INCLUDE_MIGRATION=1`
   - (optional) `FRAMEWORK_REPORTING_INCLUDE_REVIEW=1`
   - (optional) `FRAMEWORK_REPORTING_INCLUDE_TASK_LOGS=1`
   - `GITHUB_TOKEN=...`
2) `./install-framework.sh --run`
3) PR/issue will be created automatically in `devframework`.

## Build release zip (maintainers)
```
python3 scripts/package-framework.py
```
Produces `framework.zip` and keeps `framework/VERSION` as the version string.
Use `--version <value>` to update `framework/VERSION`.

## Report bundle + auto publish (host project)
1) Export report bundle (redacts logs by default):
   `python3 framework/tools/export-report.py --include-migration`
2) Publish to central repo (creates PR by default):
   `export GITHUB_TOKEN=...`
   `python3 framework/tools/publish-report.py --repo alexeykrol/devframework --run-id <RUN_ID> --host-id <HOST_ID>`

Auto-publish from orchestrator (no manual command):
- Set `reporting` in `framework/orchestrator/orchestrator.yaml` or via env vars:
  - `FRAMEWORK_REPORTING_ENABLED=1`
  - `FRAMEWORK_REPORTING_REPO=alexeykrol/devframework`
  - `FRAMEWORK_REPORTING_MODE=pr|issue|both`
  - `FRAMEWORK_REPORTING_HOST_ID=<host>`
  - `FRAMEWORK_REPORTING_PHASES=legacy,main,post`
  - `FRAMEWORK_REPORTING_INCLUDE_MIGRATION=1` (optional)
  - `FRAMEWORK_REPORTING_INCLUDE_REVIEW=1` (optional)
  - `FRAMEWORK_REPORTING_INCLUDE_TASK_LOGS=1` (optional, redacted)
- Requires `GITHUB_TOKEN`.

Notes:
- The publish script pushes a report zip into `reports/<host>/<run_id>.zip` and opens a PR/Issue.
- Redaction replaces obvious secrets in logs; turn off with `--no-redact` during export if needed.

## Outputs
- `framework/logs/*.log`
- `framework/logs/framework-run.jsonl`
- `framework/docs/orchestrator-run-summary.md`
- `framework/review/*.md`
- `framework/framework-review/*.md`
- `framework/migration/*.md`

## Notes
- Relative paths in YAML are resolved from the config file; task paths are resolved from `project_root`.
- The repo must be a git repository (for `git worktree`).
- `framework/logs/framework-run.lock` exists only during an active main run; post-run tasks require it to be absent.

## Parallel review flow (two-agent)
1) Dev agent completes tasks and prepares `framework/review/handoff.md` (and test results if any).
2) In parallel, a second agent uses `framework/review/runbook.md` and `framework/review/review-brief.md` to run review/testing.
3) Review outputs go to `framework/review/` and are fed back to the dev agent.

## Framework QA flow (third agent, post-run)
1) Main run finishes and `framework/logs/framework-run.lock` is removed.
2) Run post phase:
   `python3 framework/orchestrator/orchestrator.py --phase post`
3) Framework review outputs are written to `framework/framework-review/`.
4) If fixes are needed, run:
   `python3 framework/orchestrator/orchestrator.py --phase post --include-manual`
5) Use `framework/framework-review/bundle.md` as the single entry point for the third agent.

## Legacy migration flow (read-only + approval gate)
1) Run legacy analysis phase:
   `python3 framework/orchestrator/orchestrator.py --phase legacy`
2) Review artifacts in `framework/migration/`.
3) Human approval in `framework/migration/approval.md`.
4) Apply changes in isolated branch (manual):
   `python3 framework/orchestrator/orchestrator.py --phase legacy --include-manual`
   (branch name: `legacy-migration-<run_id>`)

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

## AGENTS.md config (Codex)
Where to edit
- Codex config file: `~/.codex/config.toml` (or `$CODEX_HOME/config.toml` if `CODEX_HOME` is set).
  Source: `developers.openai.com/codex/local-config`

Keys to add
- `project_doc_fallback_filenames` — list of alternative filenames Codex will look for if AGENTS.md is missing.
- (optional) `project_doc_max_bytes` — cap on total bytes read from instructions.
  Source: `developers.openai.com/codex/guides/agents-md/`

Example (top-level, not inside sections)
```\n# ~/.codex/config.toml\nproject_doc_fallback_filenames = [\"TEAM_GUIDE.md\", \".agents.md\"]\nproject_doc_max_bytes = 65536\n```

Important
- After changing `config.toml`, restart Codex / open a new session for settings to apply.
  Source: `developers.openai.com/codex/guides/agents-md/`

## AGENTS.md usage pattern (Codex)
Important clarifications
- Codex automatically reads only `AGENTS.md` (and `AGENTS.override.md`) at the start of a new session.
  This is the entry instruction file, not a “launch script”.
- This file should hold persistent project context: goals, constraints, commands, process,
  key links, and a short snapshot.
- The size is limited by `project_doc_max_bytes`, so keep AGENTS.md compact and push details
  into separate files (for example, `SNAPSHOT.md`) and explicitly instruct the agent to read them.

Practical pattern
1) In `AGENTS.md` — short memory: what the project is, what is done, what to do next, rules/commands.
2) In `SNAPSHOT.md` — the full status and details.
3) In `AGENTS.md` — add a line: “Always read `SNAPSHOT.md` first.”

Important limitation
Codex does not read `SNAPSHOT.md` automatically — only `AGENTS.md`/`AGENTS.override.md` are auto‑loaded.
If you need the snapshot to be always included, you must either:
- embed key parts of the snapshot into `AGENTS.md`, or
- temporarily rename `SNAPSHOT.md` to `AGENTS.md`, or
- start a new session and manually say “read `SNAPSHOT.md`”.

## Skills (Codex)
Short version
- Custom skills: yes. Explicit invocation uses `$skill-name`; `/skills` helps list/select skills.
- Skills are not invoked as `/my-skill` — slash commands are a separate mechanism.
- Implicit invocation: Codex can choose a skill if the task matches its description.

Details
- Explicit invocation: run `/skills` or type `$skill-name`.
- Implicit invocation: automatic when the user request matches the skill description.
- Storage: repo-scoped `.codex/skills/<skill-name>/SKILL.md`; user-scoped `~/.codex/skills/<skill-name>/SKILL.md`.
- Create a skill: manually (folder + `SKILL.md`) or use `$skill-creator`.
- Slash-command style belongs to deprecated custom prompts (use `/prompts:<name>`), not skills (avoid `/my-skill`).

Sources:
- `developers.openai.com/codex/skills/`
- `developers.openai.com/codex/skills/create-skill/`
- `developers.openai.com/codex/cli/slash-commands`
- `developers.openai.com/codex/custom-prompts`

## Skills auto-trigger (Codex)
How auto-trigger works
1) On session start, Codex loads only each skill’s `name` and `description` (not the body).
2) When a user request matches the meaning of `name`/`description`, Codex can auto-activate the skill.
3) The body is loaded only after activation, so the description is the primary trigger signal.

How to write descriptions that trigger
- Use an explicit “when/когда” clause.
- Keep the scope narrow and concrete to avoid overlap with other skills.
- If skills overlap, refine the description with more context and expected output.

Recommended template
`description: <what it does> — use when the user asks for <explicit trigger>`

Example
`description: Draft a conventional commit message when the user asks for help writing a commit message.`

Practical checklist
- SKILL.md has valid one‑line `name` and `description`.
- Description includes an explicit “when/когда”.
- No overlapping skill with the same intent.
- Codex was restarted after creating/updating the skill.
- Test request repeats the trigger wording from the description.

If auto-trigger does not work
- Verify the skill path (`.codex/skills/...` or `~/.codex/skills/...`).
- Restart Codex (skills are loaded only at session start).
- Check YAML validity (single-line `name`/`description`).
- Shorten/clarify the description and remove overlaps.

### Если хочешь, могу
1) предложить формулировки `description` под будущие skills,
2) сделать пример skill в `.codex/skills/...` с auto‑trigger,
3) дать матрицу триггер‑фраз для стабильного срабатывания.

Ниже — подробное объяснение с этими тремя частями.

### 1) Формулировки `description`, чтобы автотриггер срабатывал
- Явно указывай “когда/when”: “используй, когда пользователь просит …”.
- Делай описание узким и конкретным (иначе навыки будут пересекаться).
- Держи `name` и `description` одной строкой.
- Тестируй авто‑триггер запросом, который повторяет слова из `description`.

Примеры формулировок:
- `description: Составь техническое задание, когда пользователь просит ТЗ, спецификацию или список требований.`
- `description: Сформируй план тестирования, когда пользователь просит тест‑план или QA план.`
- `description: Обнови snapshot‑статус, когда пользователь просит зафиксировать текущее состояние проекта.`
- `description: Сгенерируй deep‑research промпт, когда пользователь просит промпт для сбора данных.`
- `description: Подготовь код‑ревью отчёт, когда пользователь просит review или QA отчёт.`

### 2) Пример структуры skill и SKILL.md
Минимальная структура:
```
.codex/skills/build-tech-spec/
├── SKILL.md
├── references/   # опционально
├── assets/       # опционально
└── scripts/      # опционально
```

Пример `SKILL.md`:
```
---
name: build-tech-spec
description: Составь техническое задание, когда пользователь просит ТЗ или спецификацию.
---
Собери требования из диалога и оформи ТЗ по разделам:
1) Обзор
2) Функциональные требования
3) Нефункциональные требования
4) Интеграции
5) Данные/схемы
6) Тестирование
7) Риски и допущения
```

Важно:
- После добавления/изменения skills нужен перезапуск Codex, чтобы они загрузились.
- Автотриггер использует только `name`/`description`; тело подгружается после активации.

### 3) Матрица триггер‑фраз (пример)
| Сценарий | Ключевые триггеры в `description` | Пример запроса пользователя |
|---|---|---|
| ТЗ / спецификация | “ТЗ”, “техническое задание”, “спецификация” | “Сделай ТЗ на это приложение” |
| Список входных данных | “входные данные”, “таблицы”, “креды” | “Дай список данных и кредов” |
| Deep‑research промпт | “deep research”, “сбор данных”, “промпт” | “Сделай промпт для агентов на сбор данных” |
| Snapshot / статус | “snapshot”, “статус”, “зафиксируй текущее” | “Зафиксируй текущий статус в snapshot” |
| План тестирования / QA | “тест‑план”, “QA”, “проверки” | “Сделай тест‑план для проверки проекта” |
| Код‑ревью отчёт | “код‑ревью”, “review”, “bugs” | “Сделай код‑ревью отчёт” |
| Архитектурная схема | “архитектура”, “схема”, “диаграмма” | “Сформируй архитектурную схему” |
| Экспорт данных | “экспорт”, “zip”, “выгрузка” | “Сделай инструкцию по экспорту данных” |
