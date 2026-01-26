# Legacy Tech Spec (Reverse)

## Назначение
- Локальный каркас Devframework (v2026.01.24.2) для оркестрации параллельных задач разработки через git worktree, автоматизации запуска агентов, логирования и формирования отчётных артефактов/пакетов для репортинга.

## Функциональные требования (из кода)
- Читает конфиг `framework/orchestrator/orchestrator.json|yaml`, нормализует задачи, фазы (`main`, `legacy`, `post`) и зависимости.
- Для каждой задачи создаёт ветку и git worktree по заданному пути, выполняет внешнюю команду runner’а (по умолчанию `codex exec - < "{prompt}"`), пишет stdout/stderr в персональный лог.
- Ведёт события в `framework/logs/framework-run.jsonl`, ставит lock для основной фазы, пишет сводку в `framework/docs/orchestrator-run-summary.md`.
- Поддерживает опцию `--include-manual` (включает задачи с `manual: true`) и dry-run.
- Инсталлер `install-framework.sh` доставляет/обновляет `framework/` из локального `framework.zip` или GitHub, делает бэкап при `--update`, автоопределяет фазу (legacy, если в корне есть чужие файлы).
- Инструменты `framework/tools/export-report.py` и `publish-report.py` собирают артефакты/логи в zip и могут отправлять PR/Issue в GitHub при наличии `GITHUB_TOKEN`.

## Нефункциональные требования
- Требуются `python3`, `git`, доступные runner CLI (codex/claude/aider) и при YAML-конфиге — PyYAML.
- Работает локально, без сетевых вызовов в оркестраторе (кроме publish-report, который пушит в GitHub).
- Логирование файловое, без ротации; ожидается запись в `framework/logs` с правами на запись.
- Без встроенных тестов; надежность опирается на корректность окружения и runner’ов.

## Интеграции
- Git (worktree, ветки, статус).
- Внешние агенты CLI: `codex`, `claude`, `aider` (путь указывается в конфиге).
- GitHub API через `publish-report.py` (curl/subprocess).
- Опционально `curl` для загрузки zip в инсталлере.

## Данные / Контракты
- Конфигурация задач: name/branch/worktree/prompt/runner/depends_on/log/phase/manual.
- Артефакты: логи задач (`framework/logs/*.log`), события (`framework-run.jsonl`), сводка (`docs/orchestrator-run-summary.md`), миграционные документы (`framework/migration/*.md`), отчётные бандлы (`reports/<host>/<run_id>.zip` при публикации).
- Нет приложенного продуктового кода, SQL, CSV-шаблонов или фикстур; задекларированные файлы `plans_2026.csv`, `zip_rating_map_2026.csv`, `fpl_2026.csv`, `slcsp_2026.csv` отсутствуют.

## Ограничения / Допущения
- Хост обязан быть git-репозиторием; worktree пути должны быть свободны.
- Предполагается наличие внешних runner’ов; при их отсутствии задачи падают или зависают.
- Секреты в логах редактируются частично (regex в export-report), возможны утечки нестандартных токенов.
- Нет встроенной валидации наличия данных/ТЗ; оркестратор выполнится даже при пустых входах.
