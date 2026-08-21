# Evidence

Этот документ хранит только **подтверждённые факты и проверки**. Предположения, планы и желаемое состояние сюда не записываются.

## Правила

Каждая запись должна по возможности содержать:

- дату;
- что проверялось;
- результат;
- тип evidence;
- commit/request/runtime reference;
- ограничения проверки.

Статусы:

- `PASS` — проверка подтверждает ожидаемое состояние;
- `FAIL` — проверка подтверждает проблему;
- `PARTIAL` — проверено не полностью.

## 2026-08-21 — Phase 0 architecture review

**Result:** PASS  
**Evidence type:** repository review

Подтверждено документом `docs/PHASE0_REVIEW.md`:

- граница V1 согласована;
- Server Catalog V1 отделён от remote server management;
- Web/Telegram используют одно application core;
- Cloudflare является adapter, а не source of truth;
- известные противоречия спецификации устранены;
- открытые decision gates перечислены отдельно.

Ограничение: это архитектурная проверка документации, не runtime/product implementation test.

## 2026-08-21 — Product implementation отсутствует

**Result:** PASS  
**Evidence type:** repository structure

На момент bootstrap PCS корень репозитория содержит документацию и project metadata, но не содержит реализованных `apps/`, `modules/`, `infrastructure/` или production runtime.

Следствие: нельзя утверждать, что API, Telegram bot, Web Console, PostgreSQL migrations или Cloudflare integration уже реализованы.

## 2026-08-21 — PCS source inspected

**Result:** PASS  
**Evidence type:** repository inspection

Источник: `bakunity/Project-Context-System`, commit `d6b8aaa4e1450841a601daa77d9da26aae101c88`.

README источника фиксирует принципы:

- repository state beats chat memory;
- `AGENTS.md` как правила AI;
- `PROJECT_STATE.md` как текущее truth;
- `ACTIVE_WORK.md` как текущая работа;
- `ADR/`, `INCIDENTS/`, `EVIDENCE.md`;
- `.project/state.json` для bootstrap/freshness.

Ограничение: на момент интеграции исходный PCS-репозиторий содержит только `README.md`; упомянутые в README installer/validator scripts отсутствуют в репозитории. Поэтому Bakunity Infra получает адаптированную ручную интеграцию PCS, а не копирование готового installer output.

## 2026-08-21 — PCS integrated into Bakunity Infra

**Result:** PASS  
**Evidence type:** repository state

Добавлены/введены в процесс:

- `AGENTS.md`;
- `.project/state.json`;
- `docs/PROJECT_STATE.md`;
- `docs/ACTIVE_WORK.md`;
- `docs/EVIDENCE.md`;
- `docs/ADR/`;
- `docs/INCIDENTS/`;
- контекстные правила в contribution/PR workflow.

Проверка файлов выполняется через `scripts/validate_context.py`.

## Шаблон будущей записи

```text
## YYYY-MM-DD — Название проверки

Result: PASS / FAIL / PARTIAL
Evidence type: test / smoke / runtime / repository / API
Reference: commit / request_id / command / workflow

Что проверено:
- ...

Ограничения:
- ...
```
