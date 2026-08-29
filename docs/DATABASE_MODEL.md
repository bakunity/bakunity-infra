# Модель базы данных

Этот документ описывает предварительную структуру PostgreSQL для Bakunity Infra. Это не финальная миграция и не SQL-схема: до начала разработки названия и отдельные поля могут быть уточнены.

## Общие принципы

- PostgreSQL — основной источник истины приложения.
- Внешний DNS-провайдер не заменяет внутреннюю БД.
- Основные сущности используют UUID.
- Время хранится в UTC.
- Секреты не хранятся в открытом виде.
- Межмодульные связи не должны превращаться в произвольный доступ ко всем таблицам.
- Audit log проектируется как append-oriented история.
- Mutable business resources используют монотонный integer `version` для optimistic concurrency по ADR-0011.
- Retry-sensitive mutation хранит idempotency/application operation state в PostgreSQL.

## Основные таблицы

### users

```text
id UUID PK
display_name TEXT
status TEXT
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
```

Статусы на старте:

```text
active
blocked
disabled
```

### user_identities

Связывает пользователя с Telegram или будущими внешними identity providers.

```text
id UUID PK
user_id UUID FK -> users.id
provider TEXT
external_id TEXT
metadata JSONB
created_at TIMESTAMPTZ
last_seen_at TIMESTAMPTZ
```

Уникальность:

```text
UNIQUE(provider, external_id)
```

Пример `provider` V1:

```text
telegram
```

Web authentication V1 использует WebAuthn credentials в отдельной таблице, потому что credential имеет собственный lifecycle и verification material. Internal `User` при этом остаётся общим для Telegram и Web.

### webauthn_credentials

Credential пользователя для Web authentication по ADR-0010.

```text
id UUID PK
user_id UUID FK -> users.id
credential_id BYTEA UNIQUE
public_key BYTEA
sign_count BIGINT NULL
transports JSONB NULL
aaguid UUID NULL
label TEXT NULL
created_at TIMESTAMPTZ
last_used_at TIMESTAMPTZ NULL
revoked_at TIMESTAMPTZ NULL
```

Backend хранит только public verification material и безопасные metadata. Private key passkey в Bakunity Infra не хранится.

Один пользователь может иметь несколько credentials.

### web_sessions

Server-side browser sessions.

```text
id UUID PK
user_id UUID FK -> users.id
session_token_hash BYTEA UNIQUE
created_at TIMESTAMPTZ
last_used_at TIMESTAMPTZ
expires_at TIMESTAMPTZ
revoked_at TIMESTAMPTZ NULL
ip_address INET NULL
user_agent_hash TEXT NULL
metadata JSONB NULL
```

Browser получает opaque session identifier в `Secure` + `HttpOnly` cookie. В БД желательно хранить hash/token verifier, а не reusable raw session token.

Роли/permissions не копируются в session как authoritative security state: backend вычисляет effective access из актуального пользователя и назначений ролей.

### webauthn_challenges

Краткоживущий state для registration/authentication ceremonies.

```text
id UUID PK
user_id UUID FK -> users.id NULL
challenge_hash BYTEA UNIQUE
purpose TEXT
expires_at TIMESTAMPTZ
used_at TIMESTAMPTZ NULL
metadata JSONB NULL
created_at TIMESTAMPTZ
```

Challenge одноразовый и имеет короткий TTL. Raw reusable challenge не должен сохраняться дольше, чем требуется для ceremony.

### roles

```text
id UUID PK
code TEXT UNIQUE
name TEXT
system BOOLEAN
created_at TIMESTAMPTZ
```

### permissions

```text
id UUID PK
code TEXT UNIQUE
description TEXT
```

### role_permissions

```text
role_id UUID FK -> roles.id
permission_id UUID FK -> permissions.id
PRIMARY KEY(role_id, permission_id)
```

### user_roles

Назначение роли пользователю глобально или в определённом scope.

```text
id UUID PK
user_id UUID FK -> users.id
role_id UUID FK -> roles.id
scope_type TEXT NULL
scope_id UUID NULL
created_at TIMESTAMPTZ
```

Важно: `scope_type/scope_id` намеренно **не входят в PRIMARY KEY**, потому что global assignment использует NULL. Уникальность назначения роли задаётся отдельным constraint/index с корректной семантикой global/scoped assignment при первой миграции.

`scope_*` позволяет назначать роль не только глобально, но и на конкретную область, например DNS-зону или другой ресурс.

## DNS

### dns_providers

Описание подключённого DNS backend.

```text
id UUID PK
code TEXT
name TEXT
adapter TEXT
status TEXT
config_ref TEXT NULL
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
```

`config_ref` — ссылка на защищённую конфигурацию/секрет, а не сам API token.

### dns_zones

```text
id UUID PK
provider_id UUID FK -> dns_providers.id
name TEXT UNIQUE
provider_zone_id TEXT
status TEXT
public_registration BOOLEAN
max_domains_per_user INTEGER NULL
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
```

Пример:

```text
name = bakunity.online
provider_zone_id = Cloudflare zone ID
```

Когда административные zone write endpoints появятся, zone resource также должен получить `version`/expected-version semantics, если он редактируется конкурентно.

### domains

Управляемые домены/поддомены Bakunity Infra.

```text
id UUID PK
zone_id UUID FK -> dns_zones.id
owner_user_id UUID FK -> users.id
label TEXT
fqdn TEXT UNIQUE
status TEXT
max_records INTEGER NULL
version BIGINT NOT NULL DEFAULT 1
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
deleted_at TIMESTAMPTZ NULL
```

Индексы:

```text
INDEX(zone_id)
INDEX(owner_user_id)
UNIQUE(fqdn)
```

`version` увеличивается на 1 при каждой успешной логической mutation ресурса.

### dns_records

```text
id UUID PK
zone_id UUID FK -> dns_zones.id
domain_id UUID FK -> domains.id NULL
provider_record_id TEXT NULL
type TEXT
name TEXT
content TEXT
ttl INTEGER NULL
priority INTEGER NULL
proxied BOOLEAN NULL
sync_status TEXT
last_error_code TEXT NULL
version BIGINT NOT NULL DEFAULT 1
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
deleted_at TIMESTAMPTZ NULL
```

`priority` используется, например, для MX.

`proxied` — provider-specific возможность и поэтому должна быть опциональной; доменная бизнес-логика не должна зависеть от неё.

Статусы синхронизации:

```text
pending
synced
error
deleting
```

### Domain-level и zone-level records

В обычном пользовательском V1 flow DNS-запись относится к конкретному `Domain Resource`.

`domain_id = NULL` резервируется для административных zone-level/apex/system records. Такие записи должны иметь отдельные permissions/API flow и не должны случайно попадать в интерфейс «Мои домены».

## Серверы

### servers

```text
id UUID PK
owner_user_id UUID FK -> users.id NULL
name TEXT
ipv4 INET NULL
ipv6 INET NULL
environment TEXT
provider_name TEXT NULL
region TEXT NULL
status TEXT
labels JSONB
version BIGINT NOT NULL DEFAULT 1
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
deleted_at TIMESTAMPTZ NULL
```

В V1 `status` — состояние регистрации ресурса control plane, например:

```text
active
disabled
archived
```

Это **не** health/online status. Reachability и monitoring добавляются отдельным состоянием на соответствующем этапе roadmap.

На первом этапе таблица не должна содержать SSH private key.

### domain_bindings

```text
id UUID PK
domain_id UUID FK -> domains.id
server_id UUID FK -> servers.id
binding_type TEXT
status TEXT
version BIGINT NOT NULL DEFAULT 1
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
```

На первом этапе:

```text
binding_type = direct_dns
```

Позже могут появиться:

```text
reverse_proxy
deployment
load_balancer
```

Для V1 желательно обеспечить одну активную основную привязку домена, если продуктовый сценарий не требует нескольких серверов.

## Idempotency operations

### idempotency_operations

Persistence для retry-sensitive application operations по ADR-0011.

```text
id UUID PK
actor_user_id UUID FK -> users.id NOT NULL
operation_scope TEXT NOT NULL
idempotency_key_hash BYTEA NOT NULL
request_fingerprint BYTEA NOT NULL
status TEXT NOT NULL
resource_type TEXT NULL
resource_id UUID NULL
response_status INTEGER NULL
response_body JSONB NULL
last_error_code TEXT NULL
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
finalized_at TIMESTAMPTZ NULL
expires_at TIMESTAMPTZ NULL
```

Уникальность:

```text
UNIQUE(actor_user_id, operation_scope, idempotency_key_hash)
```

В БД не обязательно хранить raw `Idempotency-Key`; предпочтительно хранить безопасный hash/verifier, достаточный для поиска и сравнения.

Минимальные статусы:

```text
in_progress
completed
failed
unknown
```

Семантика:

- `in_progress` — логическая операция уже принята и не может стартовать второй раз;
- `completed` — безопасный нормализованный result можно вернуть при retry без второго side effect;
- `failed` — операция доказанно завершилась ошибкой; retry зависит от классификации failure;
- `unknown` — нельзя доказать, применился ли внешний side effect; blind retry запрещён до reconciliation decision.

Default retention для завершённой записи V1 — 24 часа после finalization. `in_progress`/`unknown` не очищаются обычным completed TTL без stale/reconciliation policy.

`response_body` может хранить только безопасный нормализованный response snapshot; raw provider payload, tokens и credentials туда не записываются.

## Аудит

### audit_events

```text
id UUID PK
actor_user_id UUID FK -> users.id NULL
source_client TEXT
action TEXT
resource_type TEXT
resource_id UUID NULL
result TEXT
request_id TEXT NULL
operation_id UUID NULL
ip_address INET NULL
metadata JSONB
created_at TIMESTAMPTZ
```

Примеры `source_client`:

```text
web
telegram
api
system
```

Примеры `action`:

```text
domain.created
domain.deleted
dns_record.created
dns_record.updated
dns_record.deleted
server.created
server.updated
role.assigned
```

`operation_id` позволяет связать audit event с retry-safe logical operation/idempotency record, если операция использует такой механизм.

Audit metadata не должна содержать токены, пароли, private keys, raw session token, WebAuthn challenge, raw idempotency key и другие секреты.

## Возможная таблица лимитов

Если лимиты быстро станут сложнее простого поля на пользователе или зоне, вводится отдельная сущность:

### resource_limits

```text
id UUID PK
subject_type TEXT
subject_id UUID
resource_type TEXT
limit_value INTEGER
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
```

До появления реальной потребности можно не усложнять схему этой таблицей.

## Связи

```text
users
 ├── user_identities
 ├── webauthn_credentials
 ├── web_sessions
 ├── user_roles
 ├── domains
 ├── servers
 └── idempotency_operations

roles
 └── role_permissions

 dns_providers
 └── dns_zones
       ├── domains
       │     ├── dns_records
       │     └── domain_bindings ──> servers
       └── zone-level dns_records

audit_events
 └── ссылки на actor, operation и изменённый ресурс
```

## Удаление данных и provider state

Для инфраструктурных сущностей различаем:

- внутреннее состояние Bakunity Infra;
- подтверждённое состояние внешнего provider;
- soft delete для истории;
- окончательную очистку при необходимости.

В V1 ресурс нельзя считать успешно удалённым, пока provider не подтвердил соответствующую операцию.

Если provider недоступен или результат неопределён:

- ресурс остаётся в явном `error/deleting/pending` состоянии;
- application operation при неопределённом side effect получает `unknown`;
- пользователю возвращается безопасный error code;
- blind retry той же provider mutation запрещён, пока reconciliation policy не определит безопасное действие;
- наличие message queue не является обязательным требованием V1.

Queue/worker добавляются только если это реально требуется для надёжности или масштаба.

## Optimistic concurrency

Решение зафиксировано в `ADR-0011`.

Для mutable resource используется integer:

```text
version BIGINT NOT NULL DEFAULT 1
```

Обновление выполняется атомарно по ожидаемой версии:

```text
UPDATE resource
SET ..., version = version + 1
WHERE id = :id AND version = :expected_version
```

Если row не обновлён из-за stale version, application возвращает `resource_version_conflict` и не выполняет silent overwrite.

`updated_at` остаётся полезным для UX/audit, но не является единственным concurrency token.

Короткие transactional locks допустимы для конкретных инвариантов, но долгий provider call не должен удерживать DB transaction/row lock только ради concurrency.

## Idempotency retention/cleanup

Default completed retention V1:

```text
24 hours after finalization
```

Cleanup должен различать:

- безопасно завершённые `completed/failed` записи;
- stale `in_progress`;
- `unknown`, требующий reconciliation.

Нельзя удалять `unknown` запись обычным cron TTL и тем самым терять память о потенциальном внешнем side effect.

## Что не хранить в таблицах открытым текстом

- Cloudflare API token;
- Telegram bot token;
- SSH private keys;
- raw browser session token;
- WebAuthn private keys;
- raw reusable idempotency keys, если достаточно hash/verifier;
- encryption master keys;
- пароли провайдеров.

Для таких данных используется защищённое secret storage, hash/verifier representation или зашифрованное хранилище с отдельным ключом в зависимости от типа секрета.

## Статус документа

Схема считается предварительной до начала первой миграции. После старта реализации каждое существенное изменение должно проходить через миграцию и при необходимости обновление этого документа.
