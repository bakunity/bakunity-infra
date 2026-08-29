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

Audit metadata не должна содержать токены, пароли, private keys, raw session token, WebAuthn challenge и другие секреты.

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
 └── servers

roles
 └── role_permissions

 dns_providers
 └── dns_zones
       ├── domains
       │     ├── dns_records
       │     └── domain_bindings ──> servers
       └── zone-level dns_records

audit_events
 └── ссылки на actor и изменённый ресурс
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
- пользователю возвращается безопасный error code;
- операция может быть повторена через retry/reconciliation flow;
- наличие message queue не является обязательным требованием V1.

Queue/worker добавляются только если это реально требуется для надёжности или масштаба.

## Конкурентные изменения

При реализации необходимо предусмотреть защиту от ситуации, когда Web и Telegram одновременно меняют один ресурс.

Возможные механизмы:

- `updated_at` + optimistic concurrency;
- version column;
- ETag/version contract;
- транзакционные блокировки для критических операций.

Конкретный механизм фиксируется отдельным решением до реализации write endpoint.

## Что не хранить в таблицах открытым текстом

- Cloudflare API token;
- Telegram bot token;
- SSH private keys;
- raw browser session token;
- WebAuthn private keys;
- encryption master keys;
- пароли провайдеров.

Для таких данных используется защищённое secret storage, hash/verifier representation или зашифрованное хранилище с отдельным ключом в зависимости от типа секрета.

## Статус документа

Схема считается предварительной до начала первой миграции. После старта реализации каждое существенное изменение должно проходить через миграцию и при необходимости обновление этого документа.
