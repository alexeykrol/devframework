# Task: Framework Review (post-run)

## Goal
Проанализировать работу фреймворка и сформировать баг‑репорт на основании логов.

## Inputs
- `framework/logs/framework-run.jsonl`
- `framework/docs/orchestrator-run-summary.md`
- `framework/logs/*.log`
- `framework/orchestrator/orchestrator.py`
- `framework/orchestrator/orchestrator.json`

## Outputs
- `framework/framework-review/bundle.md`
- `framework/framework-review/framework-log-analysis.md`
- `framework/framework-review/framework-bug-report.md`
- `framework/framework-review/framework-fix-plan.md`

## Rules
- Запускать только между прогонами (нет `framework/logs/framework-run.lock`).
- Код не изменять, только отчёты.

## Done When
- Анализ и баг‑репорт заполнены.
- Есть план исправлений.
