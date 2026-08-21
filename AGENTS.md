# AGENTS.md — правила работы AI с Bakunity Infra

Этот файл является входной точкой Project Context System (PCS) для ChatGPT, Codex и других coding agents.

> **CHAT IS WORKSPACE. GIT IS MEMORY. DOCS ARE CURRENT KNOWLEDGE.**

## Обязательный bootstrap новой сессии

Перед планированием или изменением проекта AI должен:

1. Прочитать `AGENTS.md`.
2. Прочитать `.project/state.json`.
3. Прочитать `docs/PROJECT_STATE.md`.
4. Прочитать `docs/ARCHITECTURE.md`.
5. Прочитать `docs/ACTIVE_WORK.md`.
6. Прочитать только релевантные документы из `docs/ADR/`, продуктовой спецификации и UX/API/DB-документов.
7. Проверить текущий Git HEAD и недавние коммиты.
8. Сравнить HEAD со `state_based_on_commit` из `.project/state.json`.
9. Если есть drift — понять, меняет ли он project truth, и при необходимости обновить context-файлы.
10. Кратко сформулировать текущее понимание проекта.
11. Только после этого планировать работу.

## Источники истины

Один тип знания должен иметь одно authoritative место.

| Что нужно узнать | Источник истины |
|---|---|
| Текущее состояние проекта | `docs/PROJECT_STATE.md` |
| Что делается прямо сейчас | `docs/ACTIVE_WORK.md` |
| Цели и вектор | `docs/GOALS.md` |
| Описание продукта | `docs/PRODUCT.md` |
| Архитектура | `docs/ARCHITECTURE.md` |
| Почему принято решение | `docs/ADR/` |
| Roadmap | `docs/ROADMAP.md` |
| Backlog V1 | `docs/BACKLOG_V1.md` |
| Предметная модель | `docs/DOMAIN_MODEL.md` |
| Модель БД | `docs/DATABASE_MODEL.md` |
| API-контракт | `docs/API_CONTRACT.md` |
| Telegram UX | `docs/TELEGRAM_UX.md` |
| Web UX | `docs/WEB_UX.md` |
| Роли и права | `docs/PERMISSIONS.md` |
| Безопасность | `docs/SECURITY.md` |
| Инциденты и root cause | `docs/INCIDENTS/` |
| Что реально проверено | `docs/EVIDENCE.md` |
| Машинный bootstrap/freshness | `.project/state.json` |
| История изменений | Git |

`README.md` — навигационная точка входа, но не заменяет специализированные authoritative документы.

## Статусы знания

При работе с контекстом различать:

- **CONFIRMED** — подтверждено repository/runtime evidence;
- **INFERRED** — логично следует из кода/документов, но не зафиксировано как truth;
- **UNKNOWN** — информации недостаточно;
- **STALE** — документ старее релевантного изменения;
- **CONFLICT** — authoritative источники расходятся.

Нельзя выдавать `INFERRED` или `UNKNOWN` за подтверждённое состояние проекта.

## Правила изменения проекта

1. Repository state важнее памяти чата.
2. Не додумывать project-specific факты, если их нет в Git/runtime evidence.
3. Не дублировать бизнес-логику между Web и Telegram.
4. Не обращаться к Cloudflare/SSH/другим провайдерам напрямую из UI.
5. Сохранять modular monolith, пока ADR явно не меняет решение.
6. Не добавлять production secrets, токены, ключи и пароли в Git.
7. Infrastructure mutation должна учитывать authorization и audit.
8. `Done` без теста/smoke/evidence не считается доказанным завершением.
9. Любой semantic state transition должен обновлять контекст вместе с кодом.
10. Если принято новое архитектурное решение — создать новый ADR, а не тихо переписывать старый.

## Semantic state transition

Контекст обязательно пересматривается, если изменилось хотя бы одно из следующего:

- граница V1;
- текущая фаза проекта;
- активная задача;
- архитектурное решение;
- модель данных или API-контракт;
- способ аутентификации/авторизации;
- production/staging topology;
- состояние интеграции с внешним provider;
- подтверждённый root cause инцидента;
- критерий `done` для milestone.

Минимально проверить:

```text
docs/PROJECT_STATE.md
docs/ACTIVE_WORK.md
docs/EVIDENCE.md
.project/state.json
```

и при необходимости профильный authoritative документ/ADR.

## Evidence

Не записывать в `docs/EVIDENCE.md` предположения.

Допустимое evidence:

- прошедший тест;
- smoke-check;
- подтверждённый API response;
- runtime status;
- проверенный commit;
- воспроизводимая команда/результат;
- подтверждённый факт из repository state.

## Handoff

Handoff — производный артефакт. Он не становится вторым source of truth.

При передаче работы следующей AI-сессии достаточно указать:

- base/head commit;
- активную задачу;
- что изменилось;
- что проверено;
- какие authoritative документы обновлены;
- следующий конкретный шаг.

## Язык

Проектная документация и рабочие пояснения ведутся преимущественно на русском. Имена API, классов, permissions, библиотек и другие технические идентификаторы сохраняются в исходной форме.

## Текущий режим

До явного старта реализации product-кода ориентироваться на `docs/PROJECT_STATE.md` и `docs/ACTIVE_WORK.md`. Наличие будущей структуры в архитектуре не означает, что соответствующий код уже существует.
