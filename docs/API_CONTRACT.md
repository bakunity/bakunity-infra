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
- 409 — конфликт состояния/дубликат;
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
  "zone_id": "...",
  "owner_id": "...",
  "binding": {
    "type": "server",
    "server_id": "..."
  }
}
```

## GET /domains/{domain_id}

Карточка доменного ресурса.

## PATCH /domains/{domain_id}

Изменение разрешённых свойств ресурса. Изменение FQDN лучше рассматривать как отдельный use case, а не как произвольный patch.

## DELETE /domains/{domain_id}

Удаление доменного ресурса.

Backend обязан:

1. проверить права;
2. проверить зависимости;
3. выполнить или запланировать внешние DNS-операции;
4. записать результат в audit log;
5. не сообщать об успешном удалении, если внешнее состояние осталось неопределённым.

# DNS-записи

## GET /domains/{domain_id}/records

Список записей домена.

## POST /domains/{domain_id}/records

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

Изменение записи.

## DELETE /records/{record_id}

Удаление записи.

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

Требует соответствующего права.

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

Карточка сервера и связанные домены.

## PATCH /servers/{server_id}

Изменение метаданных.

## DELETE /servers/{server_id}

Удаление/деактивация из каталога с проверкой активных связей.

# Привязки доменов

## PUT /domains/{domain_id}/binding

Создать или заменить основную привязку.

```json
{
  "server_id": "...",
  "binding_type": "direct_dns"
}
```

## DELETE /domains/{domain_id}/binding

Снять привязку.

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

# Идемпотентность

Для операций создания инфраструктуры стоит поддержать `Idempotency-Key`, особенно когда клиент может повторить запрос после сетевой ошибки.

Ожидаемое поведение:

```text
один пользователь + один endpoint + один Idempotency-Key
→ одна логическая операция
```

Механизм хранения ключей определяется на этапе реализации.

# Конкурентность

API должен уметь обнаруживать конфликт устаревшего изменения, если Web и Telegram одновременно редактируют один ресурс.

Конкретный вариант — version/ETag/updated_at — фиксируется перед реализацией write endpoint.

# Версионирование

Breaking changes требуют новой версии API или явно управляемой миграции контракта.

Нельзя менять смысл существующего поля только потому, что изменился внешний DNS-provider.

# Что остаётся уточнить перед разработкой

Web authentication mechanism закрыт ADR-0010.

Остаётся уточнить:

- точную модель pagination;
- механизм optimistic concurrency;
- idempotency storage;
- формат provider-specific дополнительных параметров;
- правила редактирования root/apex записей;
- rate limits;
- bootstrap/recovery UX для WebAuthn enrollment.

Эти решения не мешают зафиксировать основные ресурсы и границы API уже сейчас.
