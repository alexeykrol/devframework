#!/usr/bin/env python3
import argparse
import re
from pathlib import Path


def parse_interview(path: Path) -> dict:
    answers = {}
    current_q = None
    current_a = []
    in_answer = False
    q_re = re.compile(r"^-\s*Q(\d+):")
    a_re = re.compile(r"^\s*-\s*A(\d+):")

    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.rstrip()
        if not line:
            if in_answer and current_q:
                current_a.append("")
            continue
        q_match = q_re.match(line)
        if q_match:
            if current_q and current_a:
                answers[current_q] = " ".join([s.strip() for s in current_a if s is not None]).strip()
            current_q = q_match.group(1)
            current_a = []
            in_answer = False
            continue
        a_match = a_re.match(line)
        if a_match:
            current_q = a_match.group(1)
            answer = line.split(":", 1)[1].strip() if ":" in line else ""
            current_a = [answer]
            in_answer = True
            continue
        if in_answer and current_q:
            current_a.append(line.strip())

    if current_q and current_a:
        answers[current_q] = " ".join([s.strip() for s in current_a if s is not None]).strip()
    return answers


def get_answer(answers: dict, qnum: str, fallback: str) -> str:
    return answers.get(qnum, fallback)


def missing_questions(answers: dict, required: list) -> list:
    return [q for q in required if q not in answers or not answers[q].strip()]


def write_file(path: Path, content: str, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def build_tech_spec(answers: dict) -> str:
    missing = missing_questions(
        answers,
        ["1", "2", "3", "5", "6", "8", "10", "12", "13", "14", "15", "16", "17", "19", "21"],
    )
    return f"""
# Сгенерированное ТЗ (self-host devframework)

## 1. Цель и критерий успеха
- {get_answer(answers, "1", "UNKNOWN: цель продукта")}
- {get_answer(answers, "8", "UNKNOWN: критерии успеха")}

## 2. Пользователь и опыт
- Роли: {get_answer(answers, "2", "UNKNOWN: роли/персоны")}
- Минимальный контакт после интервью: {get_answer(answers, "4", "UNKNOWN")}
- Ключевой сценарий: {get_answer(answers, "5", "UNKNOWN")}
- Финальное уведомление: {get_answer(answers, "6", "UNKNOWN")}

## 3. Область (scope)
- Включено: discovery → ТЗ → план → оркестратор → review/post-run.
- Типы хост‑проектов: {get_answer(answers, "9", "UNKNOWN")}
- Исключено: оптимизации/перф на MVP (см. SLO).

## 4. Архитектура и процессы
- Оркестратор + worktree по задачам + фазы main/post/legacy.
- Карта параллельных задач: `docs/orchestrator-plan-ru.md`.
- Self-review и сбор баг‑репортов: {get_answer(answers, "21", "UNKNOWN")}
- Стоп‑точки: {get_answer(answers, "10", "UNKNOWN")}

## 5. Стек по умолчанию
- {get_answer(answers, "14", "UNKNOWN: стек")}

## 6. Деплой и окружения
- {get_answer(answers, "16", "UNKNOWN: деплой")}

## 7. Интеграции
- {get_answer(answers, "17", "UNKNOWN: интеграции")}

## 8. Секреты и доступы
- {get_answer(answers, "12", "UNKNOWN: секреты/креды")}

## 9. Логирование и отчётность
- {get_answer(answers, "13", "UNKNOWN: логирование")}

## 10. Нефункциональные требования (MVP)
- {get_answer(answers, "15", "UNKNOWN: SLO/перф")}

## 11. Формат артефактов
- {get_answer(answers, "19", "UNKNOWN: формат артефактов")}

## 12. TODO / UNKNOWN
{"- Missing required answers: " + ", ".join([f"Q{q}" for q in missing]) if missing else "- None"}
""".strip()


def build_plan() -> str:
    return """
# План работ (self-host devframework)

## Этапы
1) Завершить discovery и сформировать артефакты.
2) Запустить main‑фазу оркестратора (no‑op или реальная).
3) Провести post‑run framework review.
4) Исправления по баг‑репортам, повторный прогон.

## Параллелизация
- Использовать карту задач из `docs/orchestrator-plan-ru.md`.
- UI после выбора компонентов; реальные расчёты после данных.

## Риски
- Недостаток данных/кредов → стоп‑точка с запросом.
- Worktree коллизии → валидации preflight.

## Definition of Done
- Main→post прогон завершён без ошибок.
- Артефакты сгенерированы и связаны.
""".strip()


def build_data_inputs(answers: dict) -> str:
    return f"""
# Требуемые данные и секреты (self-host devframework)

## Данные/шаблоны
- Discovery ответы — `docs/discovery/interview.md`.
- Data templates (если нужны доменные таблицы) — `docs/data-templates-ru.md`.
- Дополнительно: {get_answer(answers, "18", "UNKNOWN")}

## Секреты / доступы
- Политика: {get_answer(answers, "12", "UNKNOWN")}
- Интеграции: {get_answer(answers, "17", "UNKNOWN")}
## Базовый список секретов (по умолчанию)
- Supabase: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_KEY`.
- Stripe: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` (если webhooks).
- SES (опционально): `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `SES_SENDER`.
- Vercel/Netlify: токен доступа + идентификатор проекта.
""".strip()


def build_test_plan() -> str:
    return """
# План тестирования (самохост devframework)

## 1) Цели
- Проверить, что devframework может провести интервью, сгенерировать артефакты и выполнить main→post прогон без ошибок.
- Убедиться, что секреты не утекают в логи/отчёты.
- Проверить готовность к типовым хост‑репо (пустой, legacy).

## 2) Область охвата
- Orchestrator CLI и конфиг (`orchestrator.py`, `orchestrator.json`).
- Discovery поток и генерация файлов (`docs/discovery/interview.md`, generated docs).
- Инструменты экспорта/публикации отчётов (`tools/export-report.py`, `tools/publish-report.py`).
- Framework-review поток (post phase).

## 3) Типы тестов
- Unit: разбор конфигурации, worktree path validation, lock handling, redact-функции, YAML/JSON I/O.
- Integration: no‑op прогон main; export-report на синтетических логах; publish-report dry-run.
- E2E: установка через `install-framework.sh` в пустой репо; запуск main→post в no‑op; запуск legacy анализа (read-only).
- Manual/UX: проверка понятности сгенерированных артефактов для не‑тех пользователя.

## 4) Критические сценарии
1) Установка в пустой репо → main no‑op → генерируются артефакты, нет ошибок.
2) Запуск legacy-фазы в репо с произвольными файлами → создаются migration артефакты, код не меняется.
3) Export + redact → в отчёте отсутствуют секреты, присутствуют ключевые логи.
4) Framework post‑run review → генерируются `framework-review/*` без падений.

## 5) Негативные кейсы
- Несуществующие worktree пути / занятые пути → корректная ошибка, без порчи репо.
- Отсутствие git → понятное сообщение, graceful exit.
- Нет PyYAML / зависимостей → сообщение с инструкцией.
- Пустой или повреждённый orchestrator config → валидационная ошибка.
- Отсутствуют креды при попытке реального деплоя → стоп‑точка, без утечек секретов.

## 6) Критерии приемки
- Все критические сценарии проходят; нет P0/P1.
- Логи без секретов; экспорт/публикация не раскрывают токены.
- Main→post no‑op завершается успешно и повторяемо.

## 7) Данные и фикстуры
- Синтетические логи и run‑jsonl для export/redact.
- Пустой git репо для установки; репо с «мусорными» файлами для legacy проверки.
- Заглушки data templates (`plans_2026.csv` etc.) при необходимости.
""".strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate framework artifacts from discovery interview.")
    parser.add_argument("--interview", default="framework/docs/discovery/interview.md")
    parser.add_argument("--docs-dir", default="framework/docs")
    parser.add_argument("--review-dir", default="framework/review")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    interview_path = Path(args.interview)
    docs_dir = Path(args.docs_dir)
    review_dir = Path(args.review_dir)

    answers = parse_interview(interview_path)

    write_file(docs_dir / "tech-spec-generated.md", build_tech_spec(answers), overwrite=args.overwrite)
    write_file(docs_dir / "plan-generated.md", build_plan(), overwrite=args.overwrite)
    write_file(docs_dir / "data-inputs-generated.md", build_data_inputs(answers), overwrite=args.overwrite)
    write_file(review_dir / "test-plan.md", build_test_plan(), overwrite=args.overwrite)


if __name__ == "__main__":
    main()
