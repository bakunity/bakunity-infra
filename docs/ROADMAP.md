# План развития

Этот roadmap фиксирует **последовательность продуктовых рубежей**, а не конкретные календарные сроки.

Стратегический вектор и критерии V1 описаны в [GOALS.md](GOALS.md).

# Этап 0 — Основа и проектирование

**Статус: завершён**

Цель: до начала реализации определить, что именно строит Bakunity Infra, где проходят границы модулей и какой результат считается первой рабочей версией.

Завершено:

- ✅ описание продукта;
- ✅ стратегический вектор и цели;
- ✅ архитектура модульного монолита;
- ✅ журнал архитектурных решений;
- ✅ модель предметной области;
- ✅ предварительная модель базы данных;
- ✅ предварительный API-контракт;
- ✅ Telegram UX;
- ✅ Web UX;
- ✅ роли и права;
- ✅ модель безопасности;
- ✅ архитектурная ревизия документов;
- ✅ упорядоченный backlog V1.

Архитектурная сверка: [PHASE0_REVIEW.md](PHASE0_REVIEW.md).

Backlog: [BACKLOG_V1.md](BACKLOG_V1.md).

Перед реализацией отдельных блоков остаются локальные decision gates — например Web authentication и конкретный optimistic concurrency mechanism. Они оформляются ADR и не меняют общий вектор продукта.

# Этап 1 — V1: Domains & DNS Control Plane

**Цель:** получить первую реально полезную версию Bakunity Infra, в которой домены и DNS управляются из Web и Telegram через одно ядро.

V1 включает четыре слоя.

## 1. Foundation

- User + Identity;
- authentication;
- permissions/RBAC;
- ownership/scopes foundation;
- audit log;
- PostgreSQL;
- стабильный `/api/v1`;
- secret/config boundaries.

## 2. DNS и домены

- несколько управляемых DNS-зон;
- Cloudflare adapter;
- создание поддоменов;
- A, AAAA, CNAME, TXT, MX, NS;
- изменение и удаление DNS records;
- sync/error states;
- пользовательские лимиты;
- destructive confirmations;
- provider retry/reconciliation path.

## 3. Минимальный Server Catalog

V1 Server — это control-plane resource, а не SSH-managed node.

Включено:

- имя;
- IPv4/IPv6;
- environment;
- provider/region;
- labels;
- registration status;
- permissions;
- использование сервера как DNS target;
- Domain Binding типа `direct_dns`.

Не включено:

- SSH execution;
- server agent;
- CPU/RAM monitoring;
- автоматическая настройка ОС.

## 4. Два клиента

### Telegram

Быстрые операционные сценарии:

- создать поддомен;
- мои домены;
- DNS records;
- выбрать сервер;
- история;
- короткие административные действия.

### Web

Полноценная консоль:

- dashboard;
- domains;
- DNS zones;
- DNS records;
- servers;
- users/permissions;
- audit;
- settings.

Telegram может получать UX раньше, но оба клиента используют одни application use case.

## Критерий завершения V1

V1 завершается только после прохождения критериев из [GOALS.md](GOALS.md), включая права, аудит, provider error handling, согласованность Web/Telegram и отсутствие ложных success-state.

# Этап 2 — Managed Delivery: Routing + HTTPS

**Цель:** перейти от управления DNS к управляемой доставке приложений.

Главная модель:

```text
Domain
  +
Server
  +
Target Port
   ↓
Reverse Proxy
   ↓
TLS / HTTPS
   ↓
Health Check
```

Планируемые возможности:

- безопасное подключение управляемого сервера;
- reverse-proxy adapter;
- route resource;
- домен + сервер + target port;
- генерация и применение конфигурации;
- TLS/ACME issuance и renewal;
- config validation;
- health checks;
- rollback;
- audit всех инфраструктурных изменений.

На этом этапе выбирается конкретная модель управления сервером: SSH service account, agent или их комбинация.

# Этап 3 — Deployments

**Цель:** сделать повторяемый application delivery поверх уже работающего Routing + HTTPS.

Возможные возможности:

- Deployment resource;
- deployment history;
- environment references;
- container-aware deployments;
- release status;
- rollback;
- связь deployment → route → domain → server;
- Telegram notifications;
- Web deployment UI.

Конкретный deployment engine выбирается по реальным требованиям, а не заранее.

# Этап 4 — Monitoring & Operations

**Цель:** добавить наблюдаемость и операционную реакцию.

Возможные возможности:

- endpoint/server health;
- availability history;
- DNS validation;
- certificate expiration;
- incidents;
- Telegram alerts;
- операционные сводки;
- dashboard состояния инфраструктуры.

Именно здесь `Online/Offline` становится формальным health state, а не декоративной меткой.

# Этап 5 — Platform

Добавляется только по фактической необходимости:

- CLI;
- external API consumers;
- дополнительные DNS providers;
- server agents;
- queues/workers;
- multi-region;
- provider reconciliation workers;
- отдельное secret-management решение;
- extraction отдельных модулей в сервисы.

# Правило развития

Каждый этап должен делать предыдущий слой сильнее, а не обходить его.

```text
DNS correctness
   ↓
Safe server binding
   ↓
Safe routing
   ↓
Safe deployments
   ↓
Observable operations
```

Если новая возможность требует обойти permissions, audit, domain model или provider adapter — это сигнал, что решение идёт против архитектуры.

# Явная не-цель

Bakunity Infra не превращается в микросервисную систему только из-за роста количества модулей. Выделение сервиса требует измеримой причины: нагрузка, fault isolation, отдельный lifecycle или операционная граница.
