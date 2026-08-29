# ADR-0011 — Optimistic concurrency и idempotency

Status: Accepted  
Date: 2026-08-29

## Context

Bakunity Infra имеет несколько клиентов — Web, Telegram и REST API — которые используют одно application core и могут почти одновременно изменять один ресурс. Кроме того, infrastructure mutation может быть повторно отправлена после сетевого timeout, повторного клика или retry клиента.

До реализации write-path необходимо исключить два класса ошибок:

1. **lost update** — устаревший клиент перезаписывает более новое состояние;
2. **duplicate mutation** — повтор запроса создаёт второй домен/DNS record или повторяет внешнюю provider operation.

Решение должно работать в modular monolith с PostgreSQL и не требовать distributed queue для V1.

## Decision

### 1. Optimistic concurrency: integer version

Для mutable resource/aggregate в V1 используется монотонное поле:

```text
version BIGINT NOT NULL DEFAULT 1
```

Каждая успешная логическая mutation увеличивает `version` на 1.

Минимально versioning применяется к ресурсам, которые реально редактируются конкурентно:

- Domain Resource;
- DNS Record;
- Server;
- Domain Binding;
- административным mutable resources, когда для них появляются write endpoints.

`updated_at` остаётся timestamp для UX/audit, но **не используется как единственный concurrency token**.

### 2. HTTP contract: ETag + If-Match

Read endpoint mutable resource возвращает текущую версию в representation и HTTP `ETag`.

Пример:

```text
ETag: "7"
```

Для update/delete существующего mutable resource клиент передаёт:

```text
If-Match: "7"
```

Backend выполняет атомарное изменение по смыслу:

```text
UPDATE ...
SET ..., version = version + 1
WHERE id = :id AND version = :expected_version
```

Если ожидаемая версия устарела, mutation не выполняется и возвращается:

```text
409 resource_version_conflict
```

Без silent last-write-wins.

Для internal application call (например Telegram без HTTP к самому себе) use case получает `expected_version` напрямую. Таким образом Web/API/Telegram используют одну concurrency semantics.

Для create operations `If-Match` не нужен.

### 3. Не использовать database lock как основной UX contract

Транзакционные row locks могут применяться внутри короткой критической секции, если это требуется для инварианта, но не заменяют `version`/expected-version contract.

Долгие provider calls нельзя удерживать внутри долгой DB lock/transaction только ради concurrency.

### 4. Idempotency: application operation key

Retry-sensitive create/infrastructure mutation получает application-level `operation_id`.

Для HTTP/Web/API внешний контракт:

```text
Idempotency-Key: <opaque client-generated value>
```

Backend нормализует его в application `operation_id`.

Telegram при финальном подтверждении flow создаёт/сохраняет собственный operation id и повторно использует его при retry того же подтверждённого действия.

### 5. Scope idempotency key

Уникальность операции определяется минимум по:

```text
actor_user_id
+ operation_scope
+ idempotency_key
```

`operation_scope` включает стабильную логическую операцию/route, например `POST:/api/v1/domains`.

Одинаковый key у другого пользователя или в другом operation scope — другая операция.

### 6. Request fingerprint

При первом запросе сохраняется fingerprint канонического набора значимых входных данных.

Повтор:

- **same key + same scope + same fingerprint** → тот же логический результат;
- **same key + same scope + different fingerprint** → `409 idempotency_key_reused`;
- key не может быть способом изменить уже начатую операцию.

Fingerprint не должен содержать raw secrets.

### 7. PostgreSQL storage

Idempotency state хранится в PostgreSQL, а не только in-memory cache.

Предварительная сущность `idempotency_operations` содержит:

- actor;
- scope;
- hash key/fingerprint;
- status;
- resource/result reference;
- нормализованный безопасный response snapshot при необходимости;
- timestamps и expiration.

Уникальный constraint предотвращает одновременное создание двух строк для одной logical operation.

### 8. Status model

Минимальные состояния:

```text
in_progress
completed
failed
unknown
```

`unknown` используется, когда нельзя безопасно доказать, применился ли внешний side effect. В таком состоянии backend не должен слепо повторять provider mutation; дальнейшее поведение определяется provider reconciliation/retry policy.

### 9. Поведение повторов

Если операция `completed`, повтор с тем же key/fingerprint возвращает тот же нормализованный результат без повторного side effect.

Если операция `in_progress`, повтор не запускает вторую mutation. V1 возвращает стабильный конфликт/operation-in-progress response (предпочтительно `409 idempotency_in_progress`; при необходимости `Retry-After`).

Если операция `failed`, автоматический повтор допустим только если failure классифицирован как гарантированно произошедший **до** external side effect. Иначе используется `unknown/reconciliation` path.

### 10. TTL

Default retention idempotency record для V1:

```text
24 hours after finalization
```

TTL конфигурируемый, но не должен быть короче типичного окна client retry.

`in_progress`/`unknown` записи нельзя удалять только потому, что обычный completed TTL истёк; для них применяется отдельная stale/reconciliation policy.

После истечения retention key может быть использован снова только после безопасной очистки соответствующей idempotency record.

### 11. Какие endpoints требуют idempotency

Обязательно для retry-sensitive create/mutation с инфраструктурным side effect, начиная с:

- `POST /domains`;
- создание DNS records;
- будущие deployment/proxy/certificate operations.

Для обычного idempotent `GET` не нужен.

`PUT`/`DELETE` всё равно используют expected version там, где ресурс mutable; наличие HTTP-метода с идемпотентной семантикой не отменяет provider-side retry protection.

## Error codes

Минимум:

```text
resource_version_conflict
idempotency_key_reused
idempotency_in_progress
operation_state_unknown
```

Provider-specific raw errors не становятся частью публичного contract.

## Audit/correlation

`request_id`, `operation_id` и audit event должны позволять связать:

```text
client request
→ application use case
→ idempotency record
→ resource mutation
→ provider operation
→ audit event
```

Без записи секретов.

## Consequences

Плюсы:

- Web и Telegram не перезаписывают друг друга молча;
- retry после сетевой ошибки не создаёт второй resource;
- concurrency token не зависит от точности timestamp;
- одна semantics работает для HTTP и internal Telegram calls;
- PostgreSQL достаточно для V1, отдельный distributed lock/queue не нужен.

Стоимость:

- mutable resources получают version field;
- clients должны передавать expected version при mutation;
- требуется persistence/cleanup idempotency operations;
- provider operation со статусом `unknown` требует отдельной reconciliation policy.

## Alternatives considered

### `updated_at` как concurrency token

Отклонено: timestamp хуже выражает логическую версию и сложнее для строгого сравнения/тестирования.

### Silent last-write-wins

Отклонено: опасно для infrastructure control plane и двух параллельных клиентов.

### Redis-only idempotency

Отклонено для V1: добавляет отдельный state store без необходимости. PostgreSQL уже является source of truth и обеспечивает unique constraints/transactions.

### Distributed lock / message queue как обязательная основа

Отклонено для V1: лишняя сложность до появления измеримой потребности.

### UUID operation id без request fingerprint

Отклонено: случайное повторное использование key с другим payload нельзя безопасно отличить от корректного retry.

## Invariants

1. Stale write никогда не превращается в silent overwrite.
2. Duplicate idempotent request не запускает второй side effect.
3. Один idempotency key нельзя переиспользовать с другим значимым payload в том же scope.
4. `unknown` provider outcome не маскируется под success или safe retry.
5. Telegram и HTTP clients используют одну application concurrency/idempotency model.
6. `version` и operation state принадлежат backend/source-of-truth, а не UI.
7. Idempotency storage не содержит raw credentials/secrets.

## References

- Issue #3 — `BI-0003`
- `docs/ARCHITECTURE.md`
- `docs/API_CONTRACT.md`
- `docs/DATABASE_MODEL.md`
- `docs/SECURITY.md`
- `docs/BACKLOG_V1.md`
