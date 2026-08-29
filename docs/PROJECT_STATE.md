# Текущее состояние проекта

**Статус знания:** CONFIRMED  
**Последняя сверка:** 2026-08-29  
**Фаза:** V1 foundation; BI-0101 merged, активная задача BI-0102.

Этот документ отвечает только на вопрос: **что истинно о Bakunity Infra прямо сейчас**.

Подробные цели, архитектура и roadmap хранятся в профильных authoritative документах и здесь не дублируются.

## Что существует сейчас

- Архитектура: **modular monolith**.
- Клиенты продукта: **Web Console**, **Telegram Bot**, **REST API**.
- Web и Telegram используют одно application core и одну модель прав.
- PostgreSQL выбран внутренним source of truth для persistent product state.
- Cloudflare выбран первым DNS provider adapter.
- V1 — управление доменами/DNS с минимальным Server Catalog и Domain Binding.
- PCS reconciled до **PCS V1** baseline `06cd250d2847ee87f66f73930d471d7c1f60991d`, профиль `standard-adapted`.
- `BI-0002` merged: Passkeys/WebAuthn + server-side Web sessions (`ADR-0010`).
- `BI-0003` merged: integer version + ETag/If-Match и PostgreSQL-backed idempotency operation state (`ADR-0011`).
- `BI-0101` merged как `91ae2239475a7c9560dfcff5a16424cb9cb3134c`: первый product-code scaffold существует в `main`.
- Активная следующая задача: `BI-0102`, Issue #7 — configuration/logging/correlation foundation.

## Подтверждённый scaffold BI-0101

В `main` существуют:

```text
apps/
├── api/
├── telegram/
└── web/README.md

modules/
infrastructure/
tests/
deploy/README.md
```

Подтверждены:

- Python 3.13 project metadata через `pyproject.toml`;
- FastAPI application entrypoint;
- `GET /health` с ответом `{"status":"ok","service":"bakunity-infra"}`;
- Telegram entrypoint/bootstrap router без provider/business logic;
- application settings foundation на `pydantic-settings`;
- `.env.example` без реальных secrets;
- health + Telegram bootstrap tests;
- Ruff/compile/pytest Product CI;
- `docs/DEVELOPMENT.md` для local workflow;
- Web/deploy boundaries без ложного runtime implementation.

PR #6 final Product CI и PCS checks были PASS. После merge Product CI на commit `91ae2239...`, workflow run `33261628217`, также завершился `success`.

Первый post-merge PCS run `33261628261` завершился structural FAIL по одной конкретной причине:

```text
state_based_on_commit is not an ancestor of HEAD
```

Причина: PCS state ссылался на pre-squash PR head `93ce9415...`, который после squash merge не является предком `main`. Product/scaffold failure не было. `.project/state.json` reconciled на squash merge commit `91ae2239...`; новый PCS run должен подтвердить исправление.

## Что пока НЕ реализовано

Scaffold не означает готовность следующих возможностей. Пока нет подтверждённой реализации:

- PostgreSQL connection/migrations/business schema;
- WebAuthn runtime и browser session persistence;
- RBAC/ownership/audit runtime;
- optimistic concurrency runtime;
- idempotency persistence/runtime;
- Cloudflare adapter;
- DNS zones/domain lifecycle;
- Telegram domain/DNS business flows;
- полноценный Next.js Web Console;
- Server Catalog runtime;
- SSH/server management;
- reverse proxy;
- TLS automation;
- deployments;
- monitoring.

## Зафиксированная граница V1

V1 включает Identity/Authorization foundation, WebAuthn/session auth, DNS zones/provider adapter, Domain Resource lifecycle, A/AAAA/CNAME/TXT/MX/NS, минимальный Server Catalog, direct DNS bindings, ownership/RBAC/limits, audit, Web/Telegram/API, provider sync/error states, concurrency/idempotency и staging/release hardening.

V1 не включает SSH automation, reverse proxy, TLS issuance, deployments, server agent, полноценный monitoring, Kubernetes, собственный authoritative DNS или преждевременные микросервисы.

## Закрытые decision gates

### Web authentication — ADR-0010

```text
Passkeys/WebAuthn
→ backend verification
→ server-side session
→ Secure + HttpOnly opaque cookie
→ backend authorization
```

### Optimistic concurrency + idempotency — ADR-0011

```text
Mutable resource
→ version BIGINT
→ ETag / If-Match / expected_version
→ stale write = resource_version_conflict
```

Retry-sensitive mutation использует `Idempotency-Key`/`operation_id`, PostgreSQL state и request fingerprint. Default completed retention V1 — 24 часа. `unknown` external outcome не маскируется под success/blind retry.

## Открытые stage-specific decision gates

1. Production secret storage — до реальных provider credentials.
2. Zone-level/apex DNS semantics — до административного apex write flow.
3. Provider reconciliation/retry strategy — до DNS provider write flow.

При Identity implementation также нужно конкретизировать bootstrap/recovery UX для WebAuthn enrollment без изменения authentication primitive.

## Текущий инженерный рубеж

Активная задача:

```text
BI-0102 — Конфигурация приложения, logging и correlation ID
Issue #7
```

Она развивает scaffold до typed environment semantics, startup validation, structured logging и request/correlation context. Production secret storage backend не выбирается фиктивно в BI-0102 и остаётся отдельным gate до provider credentials.

После foundation epics первый продуктовый vertical milestone остаётся:

```text
User + permission
→ bakunity.online
→ test.bakunity.online → IPv4
→ Cloudflare DNS
→ PostgreSQL Domain Resource
→ Audit
→ API
→ Telegram
→ Web
```

## Runtime boundary

До текущего состояния выполнялись repository/GitHub Actions операции. BI-0101 не использовал SSH, staging/production deploy, Cloudflare mutation, production DB или production Telegram runtime.

## Authoritative ссылки

- Цели: `docs/GOALS.md`
- Product: `docs/PRODUCT.md`
- Архитектура: `docs/ARCHITECTURE.md`
- ADR: `docs/ADR/`
- Roadmap: `docs/ROADMAP.md`
- Backlog: `docs/BACKLOG_V1.md`
- API: `docs/API_CONTRACT.md`
- DB: `docs/DATABASE_MODEL.md`
- Security: `docs/SECURITY.md`
- Development: `docs/DEVELOPMENT.md`
- Active work: `docs/ACTIVE_WORK.md`
- Evidence: `docs/EVIDENCE.md`
