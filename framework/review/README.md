# Независимое тестирование и код‑ревью (QA/Review)

Эта папка содержит всё необходимое для независимого AI‑ревью и плана тестирования.

## Что внутри
- `review-brief.md` — краткая инструкция ревьюеру
- `handoff.md` — handoff от dev‑агента (контекст, команды, риски)
- `bundle.md` — единая точка входа для ревью
- `test-plan.md` — шаблон плана тестирования
- `test-results.md` — результаты прогонов тестов
- `code-review-report.md` — шаблон отчёта ревью
- `bug-report.md` — шаблон баг‑репортов
- `qa-coverage.md` — факт выполнения тестов и покрытие
- `runbook.md` — пошаговый запуск ревью (worktree)

## Рекомендуемый процесс
1) Dev‑агент заполняет `framework/review/handoff.md` (и `framework/review/test-results.md`, если тесты прогонялись).
2) Независимый агент читает `framework/review/review-brief.md` + `framework/review/handoff.md`.
3) Составляет `framework/review/test-plan.md`, выполняет проверки, заполняет отчёты.
4) Возвращает результаты в основную ветку.
