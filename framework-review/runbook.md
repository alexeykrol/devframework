# Runbook: Framework Review (post-run)

## 1) Проверить, что основной прогон завершён
- Файл `logs/framework-run.lock` должен отсутствовать.
- Есть `docs/orchestrator-run-summary.md` и `logs/framework-run.jsonl`.

## 2) Заполнить bundle и прочитать входные артефакты
- Заполнить `framework-review/bundle.md` по данным из summary и логов
- `framework-review/bundle.md`
- `docs/orchestrator-run-summary.md`
- `logs/framework-run.jsonl`
- `logs/*.log`
- `framework/orchestrator/orchestrator.py`
- `framework/orchestrator/orchestrator.yaml`

## 3) Заполнить анализ
- `framework-review/framework-log-analysis.md`

## 4) Сформировать баг‑репорт
- `framework-review/framework-bug-report.md`

## 5) Подготовить план исправлений
- `framework-review/framework-fix-plan.md`

## Важно
- Не менять код во время анализа.
- Фиксы делаются отдельной задачей и только между прогонами.
