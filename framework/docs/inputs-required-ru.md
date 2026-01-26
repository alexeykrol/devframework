# Требуемые входы

Минимальный перечень входных артефактов и доступов для корректной работы фреймворка.

## 1) Обязательные документы
- Discovery протокол: `framework/docs/discovery/interview.md`.
- Сгенерированное ТЗ/план/inputs:  
  `framework/docs/tech-spec-generated.md`,  
  `framework/docs/plan-generated.md`,  
  `framework/docs/data-inputs-generated.md`.
- (При необходимости) Доменные шаблоны данных: `framework/docs/data-templates-ru.md`.

## 2) Данные (если применимо)
- CSV в `framework/data/` (пример домена 2026):  
  `plans_2026.csv`, `zip_rating_map_2026.csv`, `fpl_2026.csv`, `slcsp_2026.csv`.

## 3) Доступы и секреты (запрашивать по мере необходимости)
- Политика: до реальной необходимости работаем без кредов; при первом использовании — стоп‑точка.
- `.env` (примерные переменные):
  - Пример файла: `framework/.env.example`.
  - Supabase: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_KEY`.
  - Stripe: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` (если webhooks).
  - SES (опционально): `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `SES_SENDER`.
  - Vercel/Netlify: токен доступа + идентификатор проекта.

## 4) Инструменты
- Доступные runner CLI: `codex` / `claude` / `aider` (или заменить в `orchestrator.json`).
- Git‑репозиторий и права на запись в `framework/logs`.
