# Активная работа

**Статус:** BI-0102 implementation готова в рабочей ветке; PR/CI ещё не выполнены.  
**Обновлено:** 2026-08-29

Этот файл отвечает только на вопрос: **что делается прямо сейчас и что является следующим конкретным шагом**.

## Активная задача

```text
BI-0102 — Конфигурация приложения, logging и correlation ID
Issue: #7
Branch: bi-0102-application-configuration
PR: ещё не открыт
Base commit: f00fc1f03a134ae358458e7e18fa822527c6795a
Runtime scope: repository/local/CI only
```

## Что реализовано в ветке

### Typed configuration

`infrastructure/config.py` теперь определяет:

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
- прежний `BAKUNITY_` environment prefix сохранён.

### Structured logging

Добавлен `infrastructure/observability.py`:

- stdlib JSON formatter;
- service/environment context;
- ContextVar request ID;
- безопасная нормализация входящего request ID;
- UUID-based generation при отсутствии/невалидном значении;
- общий `configure_logging()` для API и Telegram process.

### HTTP correlation

Добавлен `apps/api/middleware.py`:

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

Добавлены/расширены tests для:

- `/health` и автоматически созданного request ID;
- сохранения безопасного client request ID;
- замены unsafe request ID;
- typed environment parsing;
- log-level normalization;
- invalid environment rejection;
- SecretStr redaction from settings repr;
- JSON log formatter correlation context.

### Docs/config sample

Обновлены:

- `.env.example`;
- `docs/DEVELOPMENT.md`.

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
- [ ] PR открыт;
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

Открыть PR BI-0102, получить Product CI + PCS checks и исправить только подтверждённые проблемы.
