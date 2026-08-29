# API-контракт

Этот документ задаёт предварительную внешнюю границу Bakunity Infra. Он нужен до начала реализации, чтобы Web и будущие интеграции не зависели от внутренних деталей модулей.

Базовый префикс:

```text
/api/v1
```

## Общие принципы

- API работает с внутренними ресурсами Bakunity Infra, а не с сырой моделью Cloudflare.
- Авторизация проверяется на backend.
- Web использует этот API как основной клиентский контракт.
- Telegram использует те же application use case, даже если технически запускается в одном процессе и не делает HTTP-запрос к самому себе.
- Значимые изменения создают audit event.
- Ошибки внешнего provider нормализуются и не должны раскрывать секреты.
- Mutable resources используют одну optimistic concurrency semantics во всех клиентах.
- Retry-sensitive infrastructure mutation использует application-level operation id/idempotency protection.

## Формат идентификаторов

Основные ресурсы используют UUID.

Пример:

```json
{
  "id": "b1d92b3e-1c67-4e53-bbb6-403f53ff6a6b"
}
```

## Ошибки

Единый формат ошибки:

```json
{
  "error": {
    "code": "domain_already_exists",
    "message": "Такой поддомен уже существует",
    "request_id": "req_...",
    "details": null
  }
}
```

Клиент не должен разбирать текст `message` для логики. Для этого используется стабильный `code`.

Примерные HTTP-коды:

- 400 — неверные данные;
- 401 — не выполнен вход;
- 403 — недостаточно прав;
- 404 — ресурс не найден;
- 409 — конфликт состояния/дубликат/idempotency conflict;
- 422 — данные синтаксически корректны, но нарушают правила;
- 429 — превышение лимитов/частоты;
- 502/503 — временная проблема внешнего provider или инфраструктуры.

## Пагинация

Для списков:

```text
?page=1&page_size=20
```

Ответ:

```json
{
  "items": [],
  "page": 1,
  "page_size": 20,
  "total": 0
}
```

Позже для больших журналов допускается cursor pagination без изменения бизнес-сущностей.

# Identity

## GET /me

Возвращает текущего пользователя, роли и эффективные права.

```json
{
  "id": "...",
  "display_name": "Timas",
  "status": "active",
  "roles": ["admin"],
  "permissions": ["domains.read", "domains.create"]
}
```

## Web authentication V1

Web authentication зафиксирован в `ADR-0010`: основной механизм — Passkeys/WebAuthn с server-side session.

Browser не хранит роли/permissions как доверенное security state и не получает долгоживущий bearer token в `localStorage`.

### POST /auth/webauthn/authentication/options

Начать authentication ceremony.

Ответ содержит только WebAuthn options/challenge, необходимые браузеру. Challenge одноразовый и ограничен по времени.

### POST /auth/webauthn/authentication/verify

Проверить WebAuthn assertion.

Backend обязан проверить как минимум:

- challenge;
- RP ID;
- origin;
- credential;
- signature;
- credential state;
- статус внутреннего `User`.

После успешной проверки backend создаёт server-side session и устанавливает opaque session cookie с `Secure` + `HttpOnly` и подходящей `SameSite` policy.

Успешный ответ может вернуть актуальный профиль пользователя либо минимальное подтверждение, после чего Web вызывает `GET /me`.

### POST /auth/logout

Отзывает текущую server-side session и очищает browser cookie.

### Passkey enrollment

Публичная самостоятельная регистрация по умолчанию не входит в V1.

Добавление passkey выполняется отдельным authenticated/bootstrap use case. Предварительные endpoint:

```text
POST   /auth/webauthn/registration/options
POST   /auth/webauthn/registration/verify
GET    /me/passkeys
DELETE /me/passkeys/{credential_id}
```

Точный bootstrap/invite flow фиксируется при реализации Identity module, но не должен менять выбранный authentication primitive.

Удаление последнего credential должно иметь защиту от потери доступа.

### Session security

Cookie-authenticated write requests должны иметь CSRF protection.

Backend должен поддерживать:

- session expiration;
- explicit logout;
- server-side revocation;
- запрет новых session для `blocked`/`disabled` user;
- повторную authorization проверку по актуальному состоянию пользователя.

Session identifier не является business identity пользователя.

Telegram identity аналогично разрешается во внутреннего `User` через `telegram_id`; Telegram и Web не имеют независимых role stores.

# DNS-зоны

## GET /zones

Список зон, доступных текущему пользователю.

## GET /zones/{zone_id}

Карточка зоны и допустимые действия.

Административные операции подключения/изменения provider configuration должны иметь отдельные права и не смешиваться с обычной выдачей поддоменов.

# Домены и поддомены

## GET /domains

Фильтры:

```text
zone_id
owner_id
status
server_id
search
```

Обычный пользователь по умолчанию видит только разрешённые ему ресурсы.

## POST /domains

Создание управляемого поддомена.

Для этого endpoint `Idempotency-Key` обязателен после включения write implementation V1.

```json
{
  "zone_id": "...",
  "label": "panel",
  "target": {
    "type": "server",
    "server_id": "..."
  }
}
```

Альтернативный target:

```json
{
  "target": {
    "type": "ipv4",
    "value": "203.0.113.10"
  }
}
```

или:

```json
{
  "target": {
    "type": "cname",
    "value": "example.host"
  }
}
```

Backend должен сам решить, какие DNS-операции требуются для выбранного сценария.

Успешный ответ:

```json
{
  "id": "...",
  "fqdn": "panel.bakunity.online",
  "status": "active",
  "version": 1,
  "zone_id": "...",
  "owner_id": "...",
  "binding": {
    "type": "server",
    "server_id": "..."
  }
}
```

Mutable resource response также возвращает HTTP `ETag`, соответствующий текущему `version`.

## GET /domains/{domain_id}

Карточка доменного ресурса.

Ответ содержит `version` и `ETag`.

## PATCH /domains/{domain_id}

Изменение разрешённых свойств ресурса. Изменение FQDN лучше рассматривать как отдельный use case, а не как произвольный patch.

Клиент передаёт ожидаемую версию:

```text
If-Match: "7"
```

Если current version уже не `7`, mutation не выполняется и API возвращает `409 resource_version_conflict`.

## DELETE /domains/{domain_id}

Удаление доменного ресурса.

Для mutable resource destructive operation также использует `If-Match`/expected version.

Backend обязан:

1. проверить права;
2. проверить ожидаемую версию;
3. проверить зависимости;
4. выполнить или запланировать внешние DNS-операции;
5. записать результат в audit log;
6. не сообщать об успешном удалении, если внешнее состояние осталось неопределённым.

# DNS-записи

## GET /domains/{domain_id}/records

Список записей домена.

Mutable DNS record содержит `version`.

## POST /domains/{domain_id}/records

Retry-sensitive create использует `Idempotency-Key`.

Пример A:

```json
{
  "type": "A",
  "name": "panel",
  "content": "203.0.113.10",
  "ttl": 300
}
```

Пример MX:

```json
{
  "type": "MX",
  "name": "@",
  "content": "mail.example.net",
  "priority": 10,
  "ttl": 300
}
```

## PATCH /records/{record_id}

Изменение записи с `If-Match` текущей версии.

## DELETE /records/{record_id}

Удаление записи с `If-Match` текущей версии.

Поддерживаемые типы первой версии:

```text
A
AAAA
CNAME
TXT
MX
NS
```

# Серверы

## GET /servers

Список доступных серверов.

## POST /servers

Требует соответствующего права. Для create retry применяется `Idempotency-Key` там, где endpoint может быть безопасно повторён клиентом.

```json
{
  "name": "Hermes",
  "ipv4": "203.0.113.20",
  "ipv6": null,
  "environment": "production",
  "provider_name": "example-provider",
  "region": "eu"
}
```

## GET /servers/{server_id}

Карточка сервера и связанные домены. Mutable representation содержит `version`/`ETag`.

## PATCH /servers/{server_id}

Изменение метаданных с `If-Match`.

## DELETE /servers/{server_id}

Удаление/деактивация из каталога с проверкой активных связей и `If-Match`.

# Привязки доменов

## PUT /domains/{domain_id}/binding

Создать или заменить основную привязку.

```json
{
  "server_id": "...",
  "binding_type": "direct_dns"
}
```

При замене существующей mutable binding backend использует expected version semantics.

## DELETE /domains/{domain_id}/binding

Снять привязку с expected version.

На этапах reverse proxy/deploy этот контракт будет расширен отдельными ресурсами, а не десятками несвязанных полей в domain.

# Аудит

## GET /audit

Требует `audit.read` или ограниченного права на собственные события.

Фильтры:

```text
actor_id
source_client
action
resource_type
resource_id
from
to
```

# Администрирование

Будущая административная группа:

```text
/api/v1/admin/...
```

Сюда относятся:

- пользователи;
- роли;
- права;
- подключение DNS-провайдеров;
- управление зонами;
- системные лимиты.

Обычные пользовательские endpoint не должны случайно получать административные возможности через параметры запроса.

# Optimistic concurrency

Решение зафиксировано в `ADR-0011`.

Mutable resources используют монотонный integer `version`.

HTTP read representation возвращает:

```text
version: 7
ETag: "7"
```

HTTP update/delete передаёт:

```text
If-Match: "7"
```

Internal Telegram/application call передаёт тот же concurrency token как `expected_version`.

Backend выполняет mutation только если expected version совпадает с current version. При успехе version увеличивается на 1.

Stale write:

```text
HTTP 409
error.code = resource_version_conflict
```

`updated_at` используется для отображения/аудита, но не является единственным concurrency token.

Create operation version начинается с `1` и не требует `If-Match`.

# Идемпотентность

Решение зафиксировано в `ADR-0011`.

Retry-sensitive infrastructure mutation использует application operation id.

Для Web/API:

```text
Idempotency-Key: <opaque value>
```

Scope:

```text
actor_user_id + operation_scope + idempotency_key
```

Первый запрос сохраняет canonical request fingerprint в PostgreSQL.

Поведение:

```text
same key + same scope + same payload
→ тот же logical operation/result

same key + same scope + different payload
→ 409 idempotency_key_reused

operation already in_progress
→ 409 idempotency_in_progress

provider outcome cannot be proven
→ operation_state_unknown
```

Completed result не запускает повторный provider side effect.

Default retention завершённой idempotency operation:

```text
24 hours
```

TTL конфигурируемый. `in_progress`/`unknown` state не удаляется обычным completed TTL без отдельной stale/reconciliation policy.

Telegram не создаёт отдельную модель: финальный confirmation flow сохраняет application operation id и повторно использует его при retry той же операции.

# Correlation

Для значимой mutation должны быть различимы:

- `request_id` — конкретный transport/request;
- `operation_id` — логическая идемпотентная операция;
- resource id/version;
- audit event;
- provider operation/result.

Повторный HTTP request может иметь новый `request_id`, но тот же `operation_id`.

# Нормализованные ошибки BI-0003

```text
resource_version_conflict
idempotency_key_reused
idempotency_in_progress
operation_state_unknown
```

Raw provider error не должен становиться стабильным публичным API code.

# Версионирование API

Breaking changes требуют новой версии API или явно управляемой миграции контракта.

Нельзя менять смысл существующего поля только потому, что изменился внешний DNS-provider.

# Что остаётся уточнить перед соответствующей реализацией

Закрыты:

- Web authentication mechanism — `ADR-0010`;
- optimistic concurrency — `ADR-0011`;
- idempotency storage/TTL — `ADR-0011`.

Остаётся уточнить до соответствующих этапов:

- точную модель pagination;
- production secret storage;
- формат provider-specific дополнительных параметров;
- правила редактирования root/apex записей;
- provider reconciliation/retry strategy;
- rate limits;
- bootstrap/recovery UX для WebAuthn enrollment.

Эти решения не блокируют `BI-0101` repository scaffold. Secret storage должно быть закрыто до реальных provider credentials, а reconciliation/retry — до DNS write flow.
