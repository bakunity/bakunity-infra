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

Это историческое evidence ранней integration и не описывает актуальный PCS V1 baseline.

## 2026-08-21 — PCS V1 migration / reconciliation

**Result:** PASS  
**Evidence type:** repository/tooling validation  
**PCS source:** `06cd250d2847ee87f66f73930d471d7c1f60991d`  
**Project base:** `812a36a569e8b11d7eeb317b30b1b3525bad6fbc`  
**Profile:** `standard-adapted`

Проверено:

- project truth не заменён PCS templates;
- `AGENTS.md` reconciled и сохранил Bakunity Infra rules;
- canonical PCS V1 state fields добавлены;
- Issue Forms/CODEOWNERS/GitHub manifests/setup script/workflow добавлены;
- validator поддерживает `--ready`;
- ADR-0001...ADR-0008 сохранены;
- runtime/server не трогался.

```text
python scripts/validate_context.py .          → PASS
python scripts/validate_context.py . --ready  → PASS
```

## 2026-08-29 — BI-0002 Web authentication decision

**Result:** PASS  
**Evidence type:** repository/CI/merge validation  
**Issue:** `#1`  
**PR:** `#2`  
**ADR:** `docs/ADR/0010-web-auth-passkeys.md`  
**Merge commit:** `c1e70d768255c86c089f6b06f070d2c710fa0bb6`  
**Main PCS run:** `33260864549`

Подтверждено:

- Passkeys/WebAuthn — основной Web auth V1;
- server-side browser sessions;
- Telegram/Web разрешаются в общий internal `User`;
- API/DB/Web UX/Security context reconciled;
- PR и main PCS checks PASS;
- runtime/server не трогались.

## 2026-08-29 — BI-0003 optimistic concurrency + idempotency

**Result:** PASS  
**Evidence type:** repository/CI/merge validation  
**Issue:** `#3`  
**PR:** `#4`  
**ADR:** `docs/ADR/0011-concurrency-idempotency.md`  
**Final PR head:** `c7e93967bd287a5d1538423109b0e7aa92b2976e`  
**PR PCS run:** `33261153253`  
**Merge commit:** `daea95ab7d042069c1cd962c038bb4fad8fd2d59`  
**Main PCS run:** `33261170180`

Подтверждено:

- integer resource version;
- `ETag` + `If-Match` / `expected_version`;
- stale write → `resource_version_conflict`;
- PostgreSQL-backed idempotency operation model;
- request fingerprint/scope;
- completed retention default 24 часа;
- `unknown` provider outcome без blind retry;
- PR/main PCS checks PASS;
- runtime/server не трогались.

## 2026-08-29 — BI-0101 repository scaffold

**Result:** PASS  
**Evidence type:** repository/product CI/PCS CI/merge  
**Issue:** `#5`  
**PR:** `#6`  
**Validated product-code head:** `93ce9415af1e4f793b0bae69607e3e2a8ebca7ae`  
**Final PR head:** `0407f78d59994846219bd578edb761273b41dea2`  
**Initial Product CI run:** `33261488967`  
**Initial PCS run:** `33261488963`  
**Final Product CI run:** `33261598766`  
**Final PCS run:** `33261598820`  
**Merge commit:** `91ae2239475a7c9560dfcff5a16424cb9cb3134c`  
**Main Product CI run:** `33261628217`

PR verification:

```text
Install project         → PASS
Ruff                    → PASS
Compile                 → PASS
Tests                   → PASS
PCS structural          → PASS
PCS readiness           → PASS
```

Main Product CI после squash merge:

```text
Install project → PASS
Ruff            → PASS
Compile         → PASS
Tests           → PASS
```

Проверенный/merged scaffold содержит:

- Python 3.13 project/package metadata;
- FastAPI application entrypoint;
- `GET /health` и test;
- Telegram bootstrap entrypoint/router без provider/business logic;
- `pydantic-settings` config foundation;
- `.env.example` без secrets;
- pytest/Ruff/compile quality foundation;
- Product CI workflow;
- local development guide;
- Web/deploy boundaries без фиктивного runtime implementation.

Ограничения:

- PostgreSQL/Alembic не подключены;
- WebAuthn/RBAC runtime не реализованы;
- Cloudflare/DNS business logic не реализованы;
- полноценный Web client не создан;
- server/staging/production не трогались.

## 2026-08-29 — PCS drift после squash merge BI-0101

**Result:** FAIL → RECONCILED  
**Evidence type:** PCS post-merge validation  
**Failing main PCS run:** `33261628261`  
**Merge commit:** `91ae2239475a7c9560dfcff5a16424cb9cb3134c`

Первый PCS structural check после squash merge завершился:

```text
PCS structural validation: FAIL
ERROR: state_based_on_commit is not an ancestor of HEAD
```

Root cause: `.project/state.json` был корректно основан на проверенном PR head `93ce9415...`, но GitHub squash merge создал новый commit `91ae2239...`; PR head не является его Git-предком.

Это **не product failure**: main Product CI на merge commit PASS.

Reconciliation:

- `state_based_on_commit` переведён на `91ae2239475a7c9560dfcff5a16424cb9cb3134c`;
- `last_verified_commit` переведён на тот же merge commit;
- `active_branch` возвращён на `main`;
- `active_pr` очищен;
- BI-0101 зафиксирован как merged;
- активная работа переключена на BI-0102 / Issue #7.

После этих context-only изменений требуется новый PCS structural/readiness PASS. Runtime/server при reconciliation не затрагивались.

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
