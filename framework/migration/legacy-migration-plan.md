# Legacy Migration Plan

## Стратегия
- Self-dogfood: привести сам фреймворк к требованиям фреймворка, минимально меняя API; добавить предсказуемость (preflight), тестируемость и артефакты данных/ТЗ.

## Этапы
1) Stabilize: очистить/нормализовать пути worktree, добавить preflight-проверки окружения (python, git, runner CLI, права на запись в `framework/logs`, свободные worktree/ветки), расширить редакцию секретов в export-report.
2) Complete facts: заполнить `legacy-tech-spec`, `legacy-gap-report`, `legacy-migration-plan`, `approval`; приложить недостающие доки/шаблоны данных (пустые или sample CSV) и описать контракт; задокументировать DoD/Review/Tests/Observability в README.
3) Validate & ship: добавить базовый CI (lint + smoke `python -m py_compile`/`python -m compileall` + dry-run orchestrator), собрать новый `framework.zip`, прогнать фазы `legacy` и `post`, опционально опубликовать отчёт.

## Минимальные изменения (safe‑path)
- Не менять внешнее CLI API оркестратора; добавить только preflight и расширенную редакцию секретов.
- Положить sample CSV/док‑заглушки вместо реальных данных.
- Включить runner fallback (настроить `runners.codex.command` по умолчанию на no-op при отсутствии CLI) через конфиг/ENV, не патча оркестратор жёстко.

## Валидация
- `python3 framework/orchestrator/orchestrator.py --config framework/orchestrator/orchestrator.json --phase legacy --dry-run` (проверка зависимостей/префлайта).
- `python3 -m compileall framework` и `python3 scripts/package-framework.py` без ошибок.
- Прогон `--phase main` и `--phase post` в чистом хосте, артефакты в `framework/docs/orchestrator-run-summary.md`, `framework/framework-review/*` без FAIL.
