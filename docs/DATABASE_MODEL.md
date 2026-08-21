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

Связывает пользователя с Telegram, Web или будущим способом входа.

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

Примеры `provider`:

```text
telegram
web
```

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

```text
user_id UUID FK -> users.id
role_id UUID FK -> roles.id
scope_type TEXT NULL
scope_id UUID NULL
created_at TIMESTAMPTZ
PRIMARY KEY(user_id, role_id, scope_type, scope_id)
```

`scope_*` позволяет позже назначать роль не только глобально, но и на конкретный ресурс или область.

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

Для первой версии желательно обеспечить одну активную основную привязку домена, если продуктовый сценарий не требует нескольких серверов.

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

Audit metadata не должна содержать токены, пароли, private keys и другие секреты.

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
       └── dns_records

audit_events
 └── ссылки на actor и изменённый ресурс
```

## Удаление данных

Для инфраструктурных сущностей предпочтительно различать:

- удаление в Bakunity Infra;
- удаление во внешнем provider;
- soft delete для истории;
- окончательную очистку при необходимости.

Нельзя помечать ресурс успешно удалённым до получения определённого результата от provider или постановки операции в гарантированную очередь обработки.

## Конкурентные изменения

При реализации необходимо предусмотреть защиту от ситуации, когда Web и Telegram одновременно меняют один ресурс.

Возможные механизмы:

- `updated_at` + optimistic concurrency;
- version column;
- транзакционные блокировки для критических операций.

Конкретный механизм фиксируется при реализации persistence layer.

## Что не хранить в таблицах открытым текстом

- Cloudflare API token;
- Telegram bot token;
- SSH private keys;
- session secrets;
- encryption master keys;
- пароли провайдеров.

Для таких данных используется защищённое secret storage или зашифрованное хранилище с отдельным ключом.

## Статус документа

Схема считается предварительной до начала первой миграции. После старта реализации каждое существенное изменение должно проходить через миграцию и при необходимости обновление этого документа.