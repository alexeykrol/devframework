# Task: Framework Review (post-run)

## Goal
Проанализировать работу фреймворка и сформировать баг‑репорт на основании логов.

## Inputs
- `logs/framework-run.jsonl`
- `docs/orchestrator-run-summary.md`
- `logs/*.log`
- `framework/orchestrator/orchestrator.py`
- `framework/orchestrator/orchestrator.yaml`

## Outputs
- `framework-review/framework-log-analysis.md`
- `framework-review/framework-bug-report.md`
- `framework-review/framework-fix-plan.md`

## Rules
- Запускать только между прогонами (нет `logs/framework-run.lock`).
- Код не изменять, только отчёты.

## Done When
- Анализ и баг‑репорт заполнены.
- Есть план исправлений.
