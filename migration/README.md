# Legacy Migration (safe-mode)

Цель: вернуть legacy‑проект на рельсы фреймворка без риска сломать существующий код.
Вся миграция изолирована и проходит в режиме read‑only до явного одобрения человека.

## Принципы безопасности
- Анализ — только чтение (без правок кода).
- Все изменения — в отдельной ветке и worktree.
- Обязательная точка одобрения (approval gate).
- Возможность отката: main не трогаем до явного merge.
 - Ветка миграции создаётся автоматически как `legacy-migration-<run_id>`.

## Выходные артефакты
- `migration/legacy-snapshot.md` — объективная картина проекта
- `migration/legacy-tech-spec.md` — обратное ТЗ из кода
- `migration/legacy-gap-report.md` — чего не хватает относительно фреймворка
- `migration/legacy-risk-assessment.md` — риски и критичные зоны
- `migration/legacy-migration-plan.md` — поэтапный план миграции
- `migration/legacy-migration-proposal.md` — предложение к одобрению
- `migration/approval.md` — решение человека
- `migration/rollback-plan.md` — план отката

## Этапы
1) **Legacy Audit (read‑only)**
2) **Reverse Spec (read‑only)**
3) **Gap + Risk (read‑only)**
4) **Migration Plan (read‑only)**
5) **Approval Gate (human)**
6) **Apply in branch**
7) **Review + Tests**
8) **Merge (manual)**

Подробные шаги: `migration/runbook.md`.
