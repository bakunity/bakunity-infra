# Project Context System в Bakunity Infra

Bakunity Infra использует адаптированную **Project Context System (PCS)** из репозитория `bakunity/Project-Context-System`.

Источник интеграции: commit `d6b8aaa4e1450841a601daa77d9da26aae101c88`.

Цель PCS — сделать состояние проекта переносимым между ChatGPT, Codex, другими AI agents и человеческими разработчиками без зависимости от памяти конкретного чата.

> **CHAT IS WORKSPACE. GIT IS MEMORY. DOCS ARE CURRENT KNOWLEDGE.**

## Почему система адаптирована, а не скопирована

Bakunity Infra уже имела развитую документацию до подключения PCS.

Поэтому мы не создаём дублирующие документы вроде второй архитектуры или второго roadmap. Вместо этого существующие authoritative файлы включены в карту PCS.

Кроме того, исходный репозиторий PCS на момент интеграции содержит спецификацию в `README.md`, но не содержит упомянутых installer/validator scripts. Поэтому интеграция выполнена вручную по принципам PCS.

## Профиль

Для Bakunity Infra используется профиль, близкий к **standard**, дополненный ссылками на уже существующую подробную продуктовую спецификацию.

Добавлено:

```text
AGENTS.md
.project/state.json
docs/PROJECT_STATE.md
docs/ACTIVE_WORK.md
docs/EVIDENCE.md
docs/ADR/
docs/INCIDENTS/
scripts/validate_context.py
```

## Карта authoritative knowledge

```text
Текущий state          → docs/PROJECT_STATE.md
Активная работа        → docs/ACTIVE_WORK.md
Цели                   → docs/GOALS.md
Продукт                → docs/PRODUCT.md
Архитектура            → docs/ARCHITECTURE.md
Решения                → docs/ADR/
Roadmap                 → docs/ROADMAP.md
Backlog                 → docs/BACKLOG_V1.md
Domain model            → docs/DOMAIN_MODEL.md
Database model          → docs/DATABASE_MODEL.md
API                     → docs/API_CONTRACT.md
Telegram UX             → docs/TELEGRAM_UX.md
Web UX                  → docs/WEB_UX.md
Permissions             → docs/PERMISSIONS.md
Security                → docs/SECURITY.md
Incidents/root cause    → docs/INCIDENTS/
Evidence                → docs/EVIDENCE.md
Freshness/bootstrap     → .project/state.json
История                 → Git
```

## Что нельзя делать

Нельзя создавать второй source of truth для уже существующего знания.

Например:

- не создавать `CONTEXT/ARCHITECTURE.md`, если authoritative architecture уже находится в `docs/ARCHITECTURE.md`;
- не копировать roadmap в `PROJECT_STATE.md`;
- не превращать handoff в постоянную параллельную документацию;
- не записывать runtime-факт только в чат;
- не использовать AI memory как единственное подтверждение project-specific состояния.

## Freshness

`.project/state.json` хранит commit, относительно которого project state был в последний раз сознательно сверён.

Если текущий HEAD отличается:

1. определить изменённые файлы;
2. понять, меняют ли они semantic project state;
3. при необходимости обновить `PROJECT_STATE`, `ACTIVE_WORK`, `EVIDENCE` и профильный authoritative документ;
4. только затем считать контекст reconciled.

Само отличие HEAD от `state_based_on_commit` не всегда означает ошибку: docs-only/context-only commit может не менять продуктовую истину. Но drift должен быть осознанным.

## Когда обновлять context

Обязательное обновление при:

- начале/завершении milestone;
- смене активной задачи;
- изменении V1 scope;
- новом ADR;
- изменении API/DB/domain model;
- подтверждённом incident/root cause;
- изменении deployment topology;
- подключении production provider;
- появлении runtime evidence, которое меняет понимание проекта.

## Handoff между AI-сессиями

Handoff не является отдельной памятью проекта.

Минимальный handoff:

```text
Base/HEAD commit
Active task
Что изменилось
Что проверено
Какие authoritative docs обновлены
Что делать следующим шагом
```

Новая сессия всё равно выполняет bootstrap из `AGENTS.md`.

## Validation

Запуск локально:

```bash
python scripts/validate_context.py .
```

Validator проверяет наличие обязательных PCS-файлов, валидность `.project/state.json` и базовые ссылки authoritative context.

Он не заменяет инженерную ревизию смысла документов.
