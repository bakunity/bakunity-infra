# Текущее состояние проекта

**Статус знания:** CONFIRMED  
**Последняя сверка:** 2026-08-29  
**Фаза:** старт реализации V1; BI-0101 scaffold реализован и проверен в PR #6.

Этот документ отвечает только на вопрос: **что истинно о Bakunity Infra прямо сейчас**.

Подробные цели, архитектура и roadmap хранятся в профильных authoritative документах и здесь не дублируются.

## Что существует сейчас

- Архитектура зафиксирована как **modular monolith**.
- Клиенты продукта: **Web Console**, **Telegram Bot**, **REST API**.
- Web и Telegram используют одно application core и одну модель прав.
- PostgreSQL выбран как внутренний source of truth для будущего persistent product state.
- Cloudflare выбран первым DNS provider adapter.
- V1 зафиксирована как управление доменами/DNS с минимальным Server Catalog и Domain Binding.
- Project Context System reconciled до **PCS V1** baseline `06cd250d2847ee87f66f73930d471d7c1f60991d`, профиль `standard-adapted`.
- `BI-0002` принят и merged: Web authentication V1 — Passkeys/WebAuthn + server-side browser sessions (`ADR-0010`).
- `BI-0003` принят и merged: integer resource version + ETag/If-Match и PostgreSQL-backed application operation/idempotency state (`ADR-0011`).
- `BI-0101` реализовал первый product-code scaffold в PR #6.

## Подтверждённый scaffold BI-0101

На проверенном PR head `93ce9415af1e4f793b0bae69607e3e2a8ebca7ae` существуют:

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
- отдельный Telegram entrypoint/bootstrap router без provider/business logic;
- application settings foundation через `pydantic-settings`;
- `.env.example` без реальных secrets;
- pytest tests для health и Telegram dispatcher bootstrap;
- Ruff/compile/pytest Product CI;
- `docs/DEVELOPMENT.md` для local repository workflow;
- Web/deploy boundaries без ложного утверждения о готовом frontend/runtime.

Product CI run `33261488967` на этом head завершился `success`:

```text
Install project → success
Ruff            → success
Compile         → success
Tests           → success
```

PCS Context Check run `33261488963` завершился `success`:

```text
Structural validation → success
Readiness validation  → success
```

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

V1 включает:

- Identity/Authorization foundation;
- Passkeys/WebAuthn для Web authentication;
- server-side Web sessions с revocation/expiration;
- несколько DNS-зон;
- Cloudflare DNS adapter;
- Domain Resource lifecycle;
- A/AAAA/CNAME/TXT/MX/NS records;
- минимальный Server Catalog;
- Domain Binding `direct_dns`;
- ownership, roles, permissions и limits;
- audit log;
- Telegram operational UX;
- Web Console UX;
- REST API;
- provider sync/error states;
- optimistic concurrency protection;
- idempotency protection для retry-sensitive infrastructure mutation;
- staging/release hardening.

V1 не включает SSH automation, reverse proxy, TLS issuance, deployments, server agent, полноценный monitoring, Kubernetes, собственный authoritative DNS или преждевременные микросервисы.

## Закрытые decision gates

### Web authentication — ADR-0010

```text
Passkeys / WebAuthn
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

Retry-sensitive mutation:

```text
Idempotency-Key / operation_id
→ PostgreSQL idempotency state
→ request fingerprint
→ one logical operation
```

Default completed retention V1 — 24 часа. `unknown` external outcome не маскируется под success/blind retry.

## Открытые stage-specific decision gates

1. Production secret storage — до реальных provider credentials.
2. Zone-level/apex DNS semantics — до административного apex write flow.
3. Provider reconciliation/retry strategy — до DNS provider write flow.

При Identity implementation также нужно конкретизировать bootstrap/recovery UX для WebAuthn enrollment без изменения authentication primitive.

Эти gate не блокировали BI-0101 и не должны закрываться фиктивно раньше соответствующего этапа.

## Текущий инженерный рубеж

BI-0101 готов к merge после финального context-only PCS check.

После merge следующий backlog item:

```text
BI-0102 — Конфигурация приложения
```

Он должен развить базовый config scaffold до environment separation, logging, request/correlation ID и безопасных secret references.

После foundation epics первый продуктовый vertical milestone остаётся:

```text
Пользователь с permission
→ выбирает bakunity.online
→ создаёт test.bakunity.online на IPv4
→ Cloudflare получает DNS record
→ PostgreSQL хранит Domain Resource
→ Audit фиксирует mutation
→ результат читается через API
→ виден в Telegram
→ тот же use case подключается к Web
```

## Runtime boundary

BI-0101 проверялся только в repository/GitHub Actions scope.

Не выполнялись:

- SSH к серверу;
- staging/production deploy;
- Cloudflare mutation;
- production DB mutation;
- production Telegram bot run.

## Authoritative ссылки

- Цели: `docs/GOALS.md`
- Product boundary: `docs/PRODUCT.md`
- Архитектура: `docs/ARCHITECTURE.md`
- Решения: `docs/ADR/`
- Web authentication: `docs/ADR/0010-web-auth-passkeys.md`
- Concurrency/idempotency: `docs/ADR/0011-concurrency-idempotency.md`
- Roadmap: `docs/ROADMAP.md`
- Backlog: `docs/BACKLOG_V1.md`
- API: `docs/API_CONTRACT.md`
- DB model: `docs/DATABASE_MODEL.md`
- Security: `docs/SECURITY.md`
- Development: `docs/DEVELOPMENT.md`
- Активная работа: `docs/ACTIVE_WORK.md`
- Evidence: `docs/EVIDENCE.md`
