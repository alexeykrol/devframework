# Runbook: Framework Review (post-run)

## 1) Проверить, что основной прогон завершён
- Файл `framework/logs/framework-run.lock` должен отсутствовать.
- Есть `framework/docs/orchestrator-run-summary.md` и `framework/logs/framework-run.jsonl`.

## 2) Заполнить bundle и прочитать входные артефакты
- Заполнить `framework/framework-review/bundle.md` по данным из summary и логов
- `framework/framework-review/bundle.md`
- `framework/docs/orchestrator-run-summary.md`
- `framework/logs/framework-run.jsonl`
- `framework/logs/*.log`
- `framework/orchestrator/orchestrator.py`
- `framework/orchestrator/orchestrator.json`

## 3) Заполнить анализ
- `framework/framework-review/framework-log-analysis.md`

## 4) Сформировать баг‑репорт
- `framework/framework-review/framework-bug-report.md`

## 5) Подготовить план исправлений
- `framework/framework-review/framework-fix-plan.md`

## Важно
- Не менять код во время анализа.
- Фиксы делаются отдельной задачей и только между прогонами.
