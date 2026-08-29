# Активная работа

**Статус:** BI-0102 implementation находится в PR #8; выполняется Product CI + PCS verification.  
**Обновлено:** 2026-08-29

Этот файл отвечает только на вопрос: **что делается прямо сейчас и что является следующим конкретным шагом**.

## Активная задача

```text
BI-0102 — Конфигурация приложения, logging и correlation ID
Issue: #7
Branch: bi-0102-application-configuration
PR: #8
Base commit: f00fc1f03a134ae358458e7e18fa822527c6795a
Runtime scope: repository/local/CI only
```

## Что реализовано в ветке

### Typed configuration

`infrastructure/config.py`:

```text
AppEnvironment:
- development
- test
- staging
- production
```

Также:

- typed/normalized log level;
- bounded app name/request ID header settings;
- `is_production_like` helper;
- `SecretStr` для Telegram token;
- `BAKUNITY_` environment prefix сохранён.

### Structured logging

`infrastructure/observability.py`:

- stdlib JSON formatter;
- service/environment context;
- ContextVar request ID;
- безопасная нормализация входящего request ID;
- UUID generation при отсутствии/невалидном значении;
- общий `configure_logging()` для API и Telegram process.

### HTTP correlation

`apps/api/middleware.py`:

```text
incoming X-Request-ID
→ validate / regenerate
→ bind ContextVar
→ application
→ response X-Request-ID
→ structured request log
→ reset context
```

Request ID — correlation metadata, не authentication/identity/permission.

### Tests

Покрываются:

- `/health` + generated request ID;
- safe client request ID preservation;
- unsafe request ID replacement;
- typed environment parsing;
- log-level normalization;
- invalid environment rejection;
- SecretStr redaction in settings repr;
- JSON log formatter request context.

### Docs/config sample

Обновлены `.env.example` и `docs/DEVELOPMENT.md`.

## Что BI-0102 намеренно НЕ делает

- production secret storage backend;
- real provider credentials;
- Cloudflare integration;
- PostgreSQL business schema;
- WebAuthn/RBAC runtime;
- staging/production deploy;
- server mutation.

## Definition of Done BI-0102

- [x] ветка создана от стабильного `main` после PCS PASS;
- [x] config environment semantics реализованы;
- [x] structured logging foundation реализован;
- [x] request/correlation ID middleware реализован;
- [x] sensitive config использует redacted `SecretStr` representation;
- [x] `/health` contract сохранён;
- [x] tests добавлены;
- [x] docs/.env example reconciled;
- [x] PR #8 открыт;
- [ ] Ruff PASS;
- [ ] compile PASS;
- [ ] pytest PASS;
- [ ] PCS structural PASS;
- [ ] PCS readiness PASS;
- [ ] PR merged;
- [x] runtime/server untouched.

## Runtime boundary

Текущая работа — **repository/local/CI only**.

Любые SSH, staging/production deploy, Cloudflare mutation, production DB и production Telegram запуск остаются за отдельным live gate.

## Следующий безопасный шаг

Получить Product CI + PCS checks на PR #8; исправлять только подтверждённые проблемы реализации/контекста.
