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

## 2026-08-21 — Product implementation отсутствовал на Phase 0

**Result:** PASS  
**Evidence type:** repository structure

На момент bootstrap PCS корень репозитория содержал документацию и project metadata, но не содержал реализованных `apps/`, `modules/`, `infrastructure/` или production runtime.

Эта запись историческая: текущее implementation state всегда проверяется через `PROJECT_STATE.md` и Git.

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

Позже эта integration была migrated/reconciled до PCS V1.

## 2026-08-21 — PCS V1 migration / reconciliation

**Result:** PASS  
**Evidence type:** repository/tooling validation  
**PCS source:** `06cd250d2847ee87f66f73930d471d7c1f60991d`  
**Project base:** `812a36a569e8b11d7eeb317b30b1b3525bad6fbc`  
**Profile:** `standard-adapted`

Проверено:

- существующий project truth не заменён PCS templates;
- `AGENTS.md` reconciled с PCS V1 и сохранил Bakunity Infra rules;
- `.project/state.json` содержит canonical PCS V1 fields и project-specific fields;
- добавлены Issue Forms, CODEOWNERS, GitHub manifests, `setup_github.py` и consumer PCS workflow;
- validator поддерживает `--ready`;
- ADR-0001...ADR-0008 сохранены;
- runtime/server не трогался.

Validation:

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
**Evidence type:** repository/CI/merge validation  
**Issue:** `#1`  
**PR:** `#2`  
**ADR:** `docs/ADR/0010-web-auth-passkeys.md`  
**Merge commit:** `c1e70d768255c86c089f6b06f070d2c710fa0bb6`  
**Main workflow run:** `33260864549`

Подтверждено:

- Passkeys/WebAuthn выбран основным Web authentication mechanism V1;
- browser authentication создаёт server-side session;
- Telegram/Web связываются через общий internal `User`;
- API/DB/Web UX/Security context reconciled;
- PR final PCS structural/readiness checks PASS;
- после merge main PCS Context Check PASS.

Ограничения:

- WebAuthn runtime не реализовывался в BI-0002;
- server/staging/production не трогались.

## 2026-08-29 — BI-0003 optimistic concurrency + idempotency

**Result:** PASS  
**Evidence type:** repository/CI/merge validation  
**Issue:** `#3`  
**PR:** `#4`  
**ADR:** `docs/ADR/0011-concurrency-idempotency.md`  
**Final PR head:** `c7e93967bd287a5d1538423109b0e7aa92b2976e`  
**PR workflow run:** `33261153253`  
**Merge commit:** `daea95ab7d042069c1cd962c038bb4fad8fd2d59`  
**Main workflow run:** `33261170180`

Проверено:

```text
Validate PCS structure   → success
Validate PCS readiness   → success
```

Принято:

- integer `version` для optimistic concurrency mutable resources;
- `ETag` + `If-Match` для HTTP и `expected_version` для internal application calls;
- stale write → `409 resource_version_conflict`;
- PostgreSQL-backed `idempotency_operations`;
- request fingerprint и operation scope;
- duplicate completed request не запускает второй side effect;
- default completed retention — 24 часа;
- неопределённый provider outcome → `unknown`, без blind retry.

После squash merge `main` снова прошёл PCS structural/readiness workflow.

Ограничения:

- BI-0003 фиксировал contract/design, а не runtime persistence implementation;
- PostgreSQL migration для version/idempotency ещё не создана;
- server/staging/production не трогались.

## 2026-08-29 — Runtime boundary до начала BI-0101

**Result:** PASS  
**Evidence type:** task scope / repository operations

В BI-0002 и BI-0003 выполнялись только Git/repository/GitHub Actions операции.

Не выполнялись:

- SSH к серверу;
- staging/production deploy;
- Cloudflare mutation;
- production DB mutation;
- production Telegram bot запуск.

Следующая активная задача: `BI-0101`, Issue `#5`.

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
