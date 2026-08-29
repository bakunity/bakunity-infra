# Архитектурные решения

Этот файл сохранён как короткая точка входа для совместимости со старой структурой документации.

Authoritative источник архитектурных и процессных решений находится в [`docs/ADR/`](ADR/README.md) в рамках Project Context System.

## Принятые решения

| ADR | Решение | Статус |
|---|---|---|
| [ADR-0001](ADR/0001-modular-monolith.md) | Модульный монолит | Accepted |
| [ADR-0002](ADR/0002-web-telegram-one-core.md) | Web и Telegram — клиенты одного ядра | Accepted |
| [ADR-0003](ADR/0003-rest-api-boundary.md) | REST API как first-class boundary | Accepted |
| [ADR-0004](ADR/0004-provider-neutral-dns.md) | Provider-neutral DNS core | Accepted |
| [ADR-0005](ADR/0005-postgresql-source-of-truth.md) | PostgreSQL как внутренний source of truth | Accepted |
| [ADR-0006](ADR/0006-security-before-automation.md) | Security foundation до remote automation | Accepted |
| [ADR-0007](ADR/0007-no-premature-microservices.md) | Никаких преждевременных микросервисов | Accepted |
| [ADR-0008](ADR/0008-project-context-system.md) | Project Context System | Accepted |
| [ADR-0009](ADR/0009-pcs-v1-reconciliation.md) | Reconciliation существующей PCS-интеграции с PCS V1 | Accepted |
| [ADR-0010](ADR/0010-web-auth-passkeys.md) | Web authentication через Passkeys/WebAuthn | Accepted |

## Правило

Новые решения не добавляются длинными секциями в этот файл.

Создаётся новый `docs/ADR/NNNN-short-title.md` с context, decision, consequences и alternatives. Старый ADR не переписывается незаметно: если решение заменено, его статус меняется на `Superseded` со ссылкой на новый ADR.
