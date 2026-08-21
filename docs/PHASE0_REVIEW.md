# Архитектурная ревизия Phase 0

Дата ревизии: 2026-08-21

Цель документа — проверить, что спецификация Bakunity Infra перед началом реализации не содержит известных противоречий по продуктовой границе, архитектуре, данным, API, UX и безопасности.

# Итог

**Статус: PASS после внесения перечисленных корректировок.**

Архитектурный вектор проекта считается согласованным для начала подготовки к реализации V1.

# Проверенные документы

- `README.md`
- `docs/PRODUCT.md`
- `docs/GOALS.md`
- `docs/ARCHITECTURE.md`
- `docs/DECISIONS.md`
- `docs/DOMAIN_MODEL.md`
- `docs/DATABASE_MODEL.md`
- `docs/API_CONTRACT.md`
- `docs/TELEGRAM_UX.md`
- `docs/WEB_UX.md`
- `docs/PERMISSIONS.md`
- `docs/SECURITY.md`
- `docs/ROADMAP.md`
- `docs/BACKLOG_V1.md`

# Найденные расхождения и решения

## R-001 — Каталог серверов одновременно относился к V1 и следующему этапу

### Проблема

Product/README/API/UX предполагали, что пользователь уже в первой версии может выбрать сервер как target, однако roadmap выделял серверный каталог в отдельный следующий этап.

### Решение

V1 однозначно включает **минимальный Server Catalog + Domain Binding**.

При этом V1 Server — только ресурс control plane:

- metadata;
- IPv4/IPv6;
- доступ к использованию как target;
- привязка домена.

SSH, agent, управление ОС, reverse proxy и мониторинг сервера остаются за пределами V1.

## R-002 — Статус `Online` создавал впечатление готового мониторинга

### Проблема

Примеры Telegram/Web показывали `Online`, хотя monitoring module планируется позже.

### Решение

В V1 разделяем:

```text
registration/status: active / disabled / archived
```

и будущую отдельную reachability/health-сигнализацию.

UI не должен показывать `Online`, пока нет определённого механизма проверки доступности.

## R-003 — Nullable scope в составном PRIMARY KEY

### Проблема

Предварительная таблица `user_roles` использовала nullable `scope_type/scope_id` внутри PRIMARY KEY. В PostgreSQL колонки PRIMARY KEY не могут быть NULL.

### Решение

`user_roles` получает собственный UUID primary key. Уникальность назначения роли задаётся отдельным constraint/index с корректной семантикой global/scoped assignment.

Финальный способ реализации уникальности фиксируется при первой миграции.

## R-004 — Удаление ссылалось на «гарантированную очередь», которой V1 не требует

### Проблема

Database Model допускала завершение удаления после постановки в гарантированную очередь, хотя архитектура сознательно не требует message broker/background queue в первой версии.

### Решение

V1 не обязана иметь очередь.

Правило:

- `success` только после подтверждённого результата provider;
- при неопределённом/ошибочном результате ресурс остаётся в явном промежуточном/error состоянии;
- пользователь может выполнить безопасный retry/reconciliation flow.

Queue добавляется только при доказанной необходимости.

## R-005 — DNS records могли относиться и к Domain Resource, и напрямую к Zone без чёткого UX

### Проблема

Модель БД допускает `domain_id = NULL` для zone-level records, тогда как основной пользовательский UX строится вокруг конкретного управляемого поддомена.

### Решение

В V1 обычный пользователь управляет DNS records через `Domain Resource`.

Zone-level/apex/system records считаются отдельной административной областью и не должны случайно попадать в обычный user flow.

Техническая модель может поддерживать zone-level record, но endpoint/permission должны явно различать эти сценарии.

## R-006 — Web authentication пока не выбран

### Проблема

Архитектура identity определена, но конкретный способ входа в Web ещё не зафиксирован.

### Решение

Это не требует менять доменную модель, но является **обязательным decision gate до реализации Identity**.

Создана задача `BI-0002` в V1 backlog. После выбора создаётся отдельный ADR.

## R-007 — Concurrency и idempotency описаны как требования, но механизм не выбран

### Решение

Сохраняем их как обязательные свойства V1, а технический механизм выбираем перед write API.

Создана задача `BI-0003`.

# Согласованные границы V1

V1 включает:

- Identity/Authorization foundation;
- несколько DNS-зон;
- Cloudflare DNS adapter;
- Domain Resource lifecycle;
- A/AAAA/CNAME/TXT/MX/NS records;
- минимальный Server Catalog;
- Domain Binding (`direct_dns`);
- ownership, roles, permissions, limits;
- audit log;
- Telegram operational UX;
- Web Console UX;
- REST API;
- provider sync/error states;
- idempotency/concurrency protection для критичных mutation;
- staging/release hardening.

V1 не включает:

- SSH automation;
- reverse proxy;
- TLS issuance;
- application deployments;
- server agent;
- полноценный monitoring;
- Kubernetes;
- microservice decomposition;
- собственный authoritative DNS.

# Архитектурные инварианты после ревизии

1. Bakunity Infra остаётся модульным монолитом.
2. Web и Telegram используют одно application core.
3. PostgreSQL — внутренний source of truth.
4. Cloudflare — adapter, а не доменная модель.
5. UI не обращается к provider напрямую.
6. Authorization проверяется на backend.
7. Каждый значимый infrastructure mutation аудируется.
8. Секреты не хранятся в Git и не попадают в audit metadata.
9. Server Catalog V1 не равен remote server management.
10. Состояние provider error не маскируется под success.
11. Будущий reverse proxy/TLS/deploy строится поверх Domain Binding, а не встраивается хаотично в DNS UI.
12. Новый сервис выделяется из монолита только по измеримой причине.

# Открытые decision gates перед первой строкой production-кода

До реализации соответствующего блока требуется закрыть:

- Web authentication mechanism;
- optimistic concurrency mechanism;
- Idempotency-Key storage/TTL;
- concrete secret storage for production;
- точная семантика zone-level/apex DNS operations;
- начальная стратегия provider reconciliation/retry.

Эти вопросы уже не меняют стратегический вектор проекта и могут решаться последовательно в начале backlog.

# Вывод

После этой ревизии документация задаёт достаточно чёткую систему координат:

```text
Зачем строим
   ↓
Что входит в V1
   ↓
Какие сущности существуют
   ↓
Кто что может делать
   ↓
Как это выглядит в Telegram и Web
   ↓
Какой API это обслуживает
   ↓
В каком порядке реализуем
```

Phase 0 может считаться архитектурно завершённым после отражения корректировок из этой ревизии в основных документах.
