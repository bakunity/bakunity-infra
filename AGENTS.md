# AGENTS.md — правила работы AI с Bakunity Infra

Этот файл — обязательная входная точка Project Context System (PCS) для ChatGPT, Codex и других coding agents.

> **CHAT IS WORKSPACE. GIT IS MEMORY. DOCS ARE CURRENT KNOWLEDGE.**

## Source of truth

Repository state важнее памяти чата/сессии.

Не использовать прошлый conversation memory как authoritative project-specific truth, когда в репозитории есть или требуется repository evidence.

GitHub Issues, GitHub Projects и описания Pull Request координируют работу, но **не заменяют** authoritative context-файлы репозитория.

## Обязательный bootstrap новой сессии

Перед планированием или изменением проекта AI должен:

1. Прочитать `.project/state.json`.
2. Прочитать `docs/PROJECT_STATE.md`.
3. Прочитать `docs/ARCHITECTURE.md`.
4. Прочитать `docs/ACTIVE_WORK.md`, если он существует.
5. Прочитать только релевантные `docs/ADR/` и профильные PRODUCT/API/DB/UX/SECURITY документы.
6. Выполнить `git status --short`.
7. Проверить недавние коммиты.
8. Сравнить текущий `HEAD` со `state_based_on_commit`.
9. При расхождении inspect diff и классифицировать контекст как current / stale / conflicting.
10. Прочитать связанный GitHub Issue/task brief, если он есть.
11. Кратко сформулировать текущее понимание проекта.
12. Только после этого планировать изменения.

## Источники истины Bakunity Infra

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
| GitHub operational layer | `docs/GITHUB_INTEGRATION.md` |
| Инциденты и root cause | `docs/INCIDENTS/` |
| Что реально проверено | `docs/EVIDENCE.md` |
| Машинный bootstrap/freshness | `.project/state.json` |
| История изменений | Git |

`README.md` — навигационная точка входа, а не второй source of truth.

## Статусы знания

Использовать:

- **CONFIRMED** — подтверждено repository/runtime evidence;
- **INFERRED** — сильно следует из кода/состояния, но не зафиксировано как authoritative truth;
- **UNKNOWN** — информации нет;
- **STALE** — документ старее релевантного кода/состояния;
- **CONFLICT** — authoritative источники расходятся.

Нельзя молча превращать `INFERRED` или `UNKNOWN` в `CONFIRMED`.

## Scope

Уважать task-specific allowed и forbidden paths.

Не расширять scope молча. Предпочитать минимальное изменение, достаточное для задачи, если refactoring явно не разрешён.

## Development vs runtime boundary

По умолчанию работа AI ограничена **repository / local / CI**.

Если задача явно не разрешает runtime scope, AI не должен:

- подключаться к серверам;
- деплоить staging/production;
- менять runtime infrastructure;
- выпускать или ротировать production credentials/certificates;
- выполнять destructive live tests.

Может существовать `Live gate`: repository implementation готова, но staging/server verification ещё не выполнена. Runtime-работа после этого требует отдельной явной задачи, указанного environment, verification plan и обновления evidence.

## Project-specific архитектурные правила

1. Не дублировать бизнес-логику между Web и Telegram.
2. Не обращаться к Cloudflare/SSH/другим providers напрямую из UI.
3. Сохранять modular monolith, пока новый ADR явно не меняет решение.
4. Infrastructure mutation должна учитывать authorization и audit.
5. PostgreSQL остаётся внутренним source of truth; внешний DNS provider — adapter.
6. Ошибка provider не должна маскироваться под успешное внутреннее состояние.
7. Не добавлять SSH/reverse proxy/deployment automation раньше соответствующего этапа и security foundation.

## Architecture changes

Архитектурное изменение не считается завершённым, пока вместе не reconciled:

- соответствующий код/контракт;
- тесты, когда реализация уже существует;
- `docs/ARCHITECTURE.md`;
- новый или обновлённый ADR;
- связанные authoritative документы.

## Bug fixes и incidents

Значимый bug fix должен фиксировать:

- root cause;
- regression protection;
- evidence;
- incident entry, когда сбой достаточно значим для долгосрочной памяти проекта.

## Verification

Фраза `done` не является evidence.

Нужно указывать точные tests/smoke checks, environment, ограничения и то, что **не** проверялось.

Static CI PASS не означает автоматически live/runtime PASS.

Падение test harness само по себе не доказывает поломку продукта — при возможности нужно отдельно проверить независимое состояние.

## Semantic state transition

Контекст обязательно пересматривается, если изменилось хотя бы одно из следующего:

- граница V1;
- текущая фаза проекта;
- активная задача;
- архитектурное решение;
- модель данных или API-контракт;
- способ authentication/authorization;
- staging/production topology;
- состояние внешней интеграции;
- подтверждённый root cause;
- критерий `done` для milestone.

Минимально проверить:

```text
docs/PROJECT_STATE.md
docs/ACTIVE_WORK.md
docs/EVIDENCE.md
.project/state.json
```

и релевантный authoritative документ/ADR.

## Git и GitHub

Работать относительно явного base commit для bounded agent tasks.

Нельзя утверждать, что проверен moving branch, если тестировался только более старый SHA.

Предпочтительная цепочка:

```text
Issue -> branch/task -> commits -> PR -> CI/review -> merge
```

Issues — единицы работы. Project — execution view. PR — implementation review. Они не переопределяют `PROJECT_STATE`, ADR, architecture или evidence.

## Context updates

Persistent context обновляется в том же изменении, которое меняет project truth.

Не создавать дублирующие truth-файлы.

Ownership:

- `PROJECT_STATE.md` = текущая project truth;
- `ACTIVE_WORK.md` = текущая execution/workstream;
- `ARCHITECTURE.md` = структура системы;
- `ROADMAP.md` = будущий вектор;
- `ADR/*` = почему принято решение;
- `INCIDENTS/*` = память о failures/root cause;
- `EVIDENCE.md` = принятая verification memory;
- Git = история.

## Evidence

В `docs/EVIDENCE.md` не записываются предположения.

Допустимое evidence:

- прошедший test;
- smoke check;
- подтверждённый API response;
- runtime status;
- проверенный commit;
- воспроизводимая команда/результат;
- подтверждённый repository fact.

## Secrets

Никогда не записывать secrets, tokens, private keys, credentials или sensitive raw logs в context/docs/evidence/ADR/incidents/Issues/PR bodies.

## Approval boundaries

Merge, deploy, release, destructive operations, production mutation и irreversible actions требуют явного approval, если задача прямо не разрешает их.

## Codex / agent task brief

Для существенной делегированной задачи зафиксировать:

- Goal;
- Base commit;
- Context to read;
- Linked Issue, если есть;
- Allowed files/paths;
- Forbidden files/paths;
- Required behavior;
- Must preserve;
- Change policy;
- Tests to run;
- Smoke test;
- Runtime access: No / Later live gate / Explicitly allowed;
- Context/docs that may need update;
- Approval required before;
- Expected report.

Expected report должен содержать: plan, changed files, diff summary, tests, smoke, evidence, not verified, known limitations, context updates и next safe action.

## Handoff

Handoff — производный артефакт, а не второй source of truth.

Минимум:

- base/head commit;
- активная задача;
- что изменилось;
- что проверено;
- какие authoritative документы обновлены;
- следующий безопасный шаг.

Новая сессия всё равно выполняет bootstrap из этого файла.

## Язык

Проектная документация и рабочие пояснения ведутся преимущественно на русском. Имена API, классов, permissions, библиотек и технические идентификаторы сохраняются в исходной форме.

## Текущий режим

До явного старта product-code ориентироваться на `docs/PROJECT_STATE.md` и `docs/ACTIVE_WORK.md`.

Наличие будущей структуры в архитектуре не означает, что соответствующий код уже существует.
