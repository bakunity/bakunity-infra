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

## 2026-08-21 — Early PCS source inspected

**Result:** PASS  
**Evidence type:** repository inspection

Источник ранней integration: `bakunity/Project-Context-System`, commit `d6b8aaa4e1450841a601daa77d9da26aae101c88`.

На том baseline были зафиксированы основные PCS-принципы, по которым была создана первая адаптированная integration Bakunity Infra.

Это историческое evidence ранней integration и не описывает актуальный PCS V1 baseline.

## 2026-08-21 — Early PCS integrated into Bakunity Infra

**Result:** PASS  
**Evidence type:** repository state

Ранняя integration добавила:

- `AGENTS.md`;
- `.project/state.json`;
- `docs/PROJECT_STATE.md`;
- `docs/ACTIVE_WORK.md`;
- `docs/EVIDENCE.md`;
- `docs/ADR/`;
- `docs/INCIDENTS/`;
- первоначальный `scripts/validate_context.py`.

Позже эта integration была migrated/reconciled до PCS V1, см. следующую запись.

## 2026-08-21 — PCS V1 migration / reconciliation

**Result:** PASS  
**Evidence type:** repository/tooling validation  
**PCS source:** `06cd250d2847ee87f66f73930d471d7c1f60991d`  
**Project base:** `812a36a569e8b11d7eeb317b30b1b3525bad6fbc`  
**Profile:** `standard-adapted`

Проверено:

- существующий project truth не заменён PCS templates;
- `AGENTS.md` reconciled с актуальными PCS V1 правилами и сохранил Bakunity Infra rules;
- `.project/state.json` содержит canonical PCS V1 fields и дополнительные project-specific fields;
- добавлены GitHub Issue Forms, CODEOWNERS, GitHub manifests, `setup_github.py` и consumer PCS workflow;
- canonical `scripts/validate_context.py` поддерживает `--ready`;
- ADR-0001...ADR-0008 сохранены;
- runtime/server не трогался.

Команды validation в локальном migration worktree:

```text
python scripts/validate_context.py .
PCS structural validation: PASS

python scripts/validate_context.py . --ready
PCS readiness validation: PASS
```

Ограничения:

- validation подтверждает PCS structure/readiness, а не product runtime;
- GitHub labels/project/ruleset manifests не применялись live;
- server/staging/production checks не выполнялись.

## 2026-08-29 — BI-0002 Web authentication decision

**Result:** PASS  
**Evidence type:** repository/CI validation  
**Issue:** `#1`  
**PR:** `#2`  
**Validated commit:** `a299dd00408c6ca2de8f7c31dd22502a46b6ec2b`  
**Workflow run:** `33256192021`

Проверено в GitHub Actions job `validate-context`:

```text
Validate PCS structure   → success
Validate PCS readiness   → success
```

Branch `bi-0002-web-auth` на момент проверки содержала:

- `ADR-0010` с решением Passkeys/WebAuthn + server-side session;
- reconciled API/DB/Web UX/Security docs;
- обновлённый PCS state и active work;
- сохранённый runtime boundary `repository/local/CI only`.

Ограничения:

- это validation документации/PCS, а не реализация WebAuthn runtime;
- backend, DB migrations и Web Console ещё не реализованы;
- server/staging/production не трогались;
- после добавления этой evidence-записи новый PR HEAD должен снова пройти PCS checks перед merge.

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
