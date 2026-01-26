# План работ (самохост devframework)

## Этапы
1) Discovery завершить (Q21+ готово) — status: done.
2) Сформировать артефакты: ТЗ, план, inputs, тест‑план — status: in progress.
3) Подготовить оркестратор к запуску на самохосте (конфиг, no‑op) — pending.
4) Прогнать main‑фазу в no‑op, собрать логи/сводку — pending.
5) Провести post‑run framework review (analyze/bag reports) — pending.
6) Итеративные фиксы фреймворка по выводам review — pending.
7) Повторный прогон (main/post) до стабильного green — pending.

## Параллелизация (опора на `orchestrator-plan-ru.md`)
- Параллельно: Data research (templates), DB schema+RLS, Business logic stubs, UI/UX шаблоны, PDF, Prompts/Policies, Tests, DevOps, Review prep, Framework review, Legacy analysis.
- Зависимости: UI после выбора компонентов; точные расчёты после данных; интеграции после базового каркаса; post‑run только без lock файла.

## Основные задачи ближайшего спринта
- Проверить/обновить `orchestrator.json` под самохост (пути worktree, runner noop).
- Дописать discovery при необходимости и внедрить автоматический «порог полноты».
- Дополнить шаблоны: data templates, inputs-required, DoD (если пустые места критичны).
- Настроить безопасное редактирование логов/секретов в export/publish.
- Добавить централизованный сбор баг‑репортов от хост‑проектов.

## Риски и смягчение
- Нет реальных данных/кредов → запуск только в no‑op: задокументировать, ожидать стоп‑точки на креды.
- Отсутствие тестов на оркестратор → приоритезировать unit/integration на питон‑утилиты.
- Сложность worktree путей → валидация путей и preflight.

## Готовность / Definition of Done
- End‑to‑end прогон main → post без ошибок, все тесты зелёные.
- Артефакты: discovery log, generated ТЗ/план/inputs, test‑plan, run summary, framework‑review отчёты.
- Экспорт отчёта проходит с редактированием секретов.
