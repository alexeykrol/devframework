# Rollback Plan

## Условия отката
- Пайплайн падает из-за отсутствия runner/прав записи или конфликтующих worktree.
- После обновления `framework/` ломается установка/запуск в хостах.
- Публикация отчёта выявила неотредактированные секреты.

## Шаги отката
1) Вернуться к бэкапу `framework.backup.<ts>` (создаётся инсталлером при `--update`): `rm -rf framework && mv framework.backup.<ts> framework`.
2) Удалить созданные worktree/ветки: `rm -rf _worktrees && git worktree prune && git branch -D task/* legacy-migration-* || true`.

## Восстановление состояния
- Повторно собрать проверенный `framework.zip` из стабильной версии (`scripts/package-framework.py`), перезапустить `./install-fr.sh --zip ./framework.zip --update --phase legacy --dry-run` для валидации.
