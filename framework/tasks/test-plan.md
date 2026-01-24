# Task: Test Plan (independent)

## Goal
Сформировать независимый план тестирования на основе ТЗ и DoD.

## Inputs
- `framework/docs/definition-of-done-ru.md`
- `framework/docs/orchestrator-plan-ru.md`
- `docs/tech-spec-ru.md` (если есть)
- `framework/review/review-brief.md`
- `framework/review/handoff.md` (если есть)

## Outputs
- `framework/review/test-plan.md` (по шаблону из `framework/review/`)

## Rules
- Не менять код.
- Указывать типы тестов (unit/integration/e2e/manual).
- Явно фиксировать пробелы, если данных/спека нет.

## Done When
- План тестирования покрывает критичные флоу и риски.
- План читаем и пригоден для независимого выполнения.
