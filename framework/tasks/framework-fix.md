# Task: Framework Fix (post-run, manual)

## Goal
Внести исправления в фреймворк по итогам framework‑review.

## Inputs
- `framework/framework-review/framework-bug-report.md`
- `framework/framework-review/framework-fix-plan.md`

## Outputs
- Изменения в коде фреймворка
- Обновлённый `framework/framework-review/framework-fix-plan.md`

## Rules
- Запускать только между прогонами.
- Не стартовать, если активен `framework/logs/framework-run.lock`.

## Done When
- Исправления внесены и описаны.
- План исправлений обновлён статусом выполненного.
