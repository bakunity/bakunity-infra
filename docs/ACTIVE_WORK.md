# Активная работа

**Статус:** BI-0002 и BI-0003 merged; активная задача — первый product-code scaffold BI-0101.  
**Обновлено:** 2026-08-29

Этот файл отвечает только на вопрос: **что делается прямо сейчас и что является следующим конкретным шагом**.

## Активная задача

```text
BI-0101 — Repository scaffold
Issue: #5
Branch: ещё не создана
PR: нет
Base semantic commit: daea95ab7d042069c1cd962c038bb4fad8fd2d59
Runtime scope: repository/local/CI only
```

## Закрытые prerequisite decisions

### BI-0002

Web authentication V1:

```text
Passkeys/WebAuthn
→ server-side session
→ Secure + HttpOnly opaque cookie
→ backend authorization
```

ADR: `docs/ADR/0010-web-auth-passkeys.md`.

Merged commit:

```text
c1e70d768255c86c089f6b06f070d2c710fa0bb6
```

Main PCS run `33260864549` → success.

### BI-0003

Concurrency/idempotency:

```text
version + ETag/If-Match
PostgreSQL-backed idempotency operations
24h completed retention default
unknown provider outcome != blind retry
```

ADR: `docs/ADR/0011-concurrency-idempotency.md`.

Merged commit:

```text
daea95ab7d042069c1cd962c038bb4fad8fd2d59
```

Main PCS run `33261170180` → success.

## Цель BI-0101

Создать **минимальный рабочий scaffold**, а не пустой каталог будущих возможностей.

Целевые верхнеуровневые границы:

```text
apps/
modules/
infrastructure/
tests/
deploy/
```

Первый scaffold должен дать:

- Python project metadata/dependency management;
- FastAPI application entrypoint;
- `/health` endpoint;
- отдельный Telegram client entrypoint без provider/business logic;
- application config foundation;
- минимальную структуру для общего application core;
- pytest/ruff foundation;
- product-code GitHub Actions workflow;
- `.env.example` только с placeholders/non-secret development defaults;
- документацию запуска локальных проверок.

## Не создавать преждевременно

BI-0101 не должен изображать реализованными:

- Cloudflare integration;
- PostgreSQL business schema/migrations;
- WebAuthn runtime;
- полноценный Next.js Web Console;
- SSH;
- Deployments;
- Proxy;
- Certificates;
- Monitoring.

Для будущих модулей достаточно архитектурной документации до их фактического этапа.

## Definition of Done BI-0101

- [ ] рабочая ветка создана от актуального `main`;
- [ ] scaffold импортируется;
- [ ] FastAPI `/health` работает в test harness;
- [ ] Telegram entrypoint не содержит инфраструктурной бизнес-логики;
- [ ] config foundation создан без secrets;
- [ ] `ruff check` PASS;
- [ ] `pytest` PASS;
- [ ] PCS structural validation PASS;
- [ ] PCS readiness validation PASS;
- [ ] PR открыт и CI зелёный;
- [ ] runtime/server untouched.

## Оставшиеся stage-specific decision gates

1. Production secret storage — до подключения реальных provider credentials.
2. Zone-level/apex DNS semantics — до административных apex write endpoints.
3. Provider reconciliation/retry — до Cloudflare/DNS write flow.

Они не блокируют BI-0101.

## Runtime boundary

Текущая задача — **repository/local/CI only**.

Не разрешены и не требуются:

- server SSH;
- staging/production deploy;
- Cloudflare token;
- production database;
- production Telegram token;
- любые live infrastructure mutations.

## Следующий шаг

Создать ветку BI-0101 от актуального `main`, реализовать минимальный scaffold, запустить product tests + PCS checks и открыть PR.
