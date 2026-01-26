# Требуемые данные и секреты (самохост devframework)

## Данные/шаблоны
- Discovery ответы — есть (`docs/discovery/interview.md`).
- Data templates (пример домена субсидий): `plans_2026.csv`, `zip_rating_map_2026.csv`, `fpl_2026.csv`, `slcsp_2026.csv` — статус: MISSING (использовать синтетические/пустые до появления реальных).
- Макеты/UI: не требуются на MVP; можно генерировать черновые.

## Секреты / доступы (запрашивать при первой необходимости)
- Supabase: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_KEY`.
- Stripe: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` (если webhooks).
- Email (опционально SES): `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `SES_SENDER`.
- Vercel или Netlify: токен/cli auth, проект/среды (dev/staging/prod).
- Локальные пути для worktree: подтвердить, что свободны.

## Политика получения
- До запроса секретов работаем в no‑op/синтетическом режиме.
- При первом реальном деплое — стоп‑точка с просьбой заполнить `.env` по списку выше.
- Секреты не логировать; перед экспортом отчётов прогонять редакцию.

## UNKNOWN / TODO
- Уточнить шаблон централизованного баг‑репорта и репозиторий приёма.
- Проверить, нужны ли дополнительные ключи (OAuth, analytics) для будущих интеграций.
