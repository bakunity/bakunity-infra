# Bakunity Infra

> Платформа управления инфраструктурой для доменов, DNS, серверов и доставки приложений.

**Статус:** Phase 0 завершён / подготовка к V1  
**Архитектура:** Модульный монолит  
**Интерфейсы:** Веб-панель, Telegram-бот, REST API  
**Контекст разработки:** Project Context System (PCS)

Bakunity Infra — единая система управления инфраструктурой, которая должна упростить повседневные операции с доменами и серверами как через веб-интерфейс, так и через Telegram.

Проект начинается с безопасного управления доменами, DNS и серверными target-ресурсами, а затем развивается в control plane для reverse proxy, TLS, деплоев, мониторинга и эксплуатации приложений.

## Коротко о векторе

```text
Домены и DNS
      ↓
Каталог серверов и привязки
      ↓
Reverse Proxy / Routing
      ↓
TLS / HTTPS
      ↓
Deployments
      ↓
Monitoring & Operations
```

Главный принцип: каждый следующий слой строится поверх стабильного предыдущего, а не обходит модель прав, аудит и состояние ресурсов.

Полный стратегический вектор: [docs/GOALS.md](docs/GOALS.md).

## North Star-сценарий V1

Пользователь должен иметь возможность выполнить типовую операцию примерно так:

```text
Web / Telegram
      ↓
Выбрать DNS-зону
      ↓
Ввести поддомен
      ↓
Выбрать Server / IPv4 / CNAME
      ↓
Подтвердить
      ↓
Bakunity Infra применяет DNS
      ↓
Состояние видно в обоих клиентах
      ↓
Действие записано в audit log
```

## Интерфейсы

Bakunity Infra — не Telegram-only продукт. Telegram и Web являются двумя клиентами одного application core.

- **Веб-панель** — полноценный интерфейс управления.
- **Telegram-бот** — быстрый операционный интерфейс для частых действий.
- **REST API** — стабильная программная граница для Web и будущих интеграций.
- **CLI** — возможный клиент позже.

Telegram может получать UX раньше, потому что его быстрее разрабатывать и тестировать, но отдельной Telegram-бизнес-логики быть не должно.

## Основные модули

Планируемый модульный монолит разделяется по бизнес-возможностям:

- Identity & Access;
- Domains;
- DNS;
- Servers;
- Deployments;
- Proxy;
- Certificates;
- Monitoring;
- Audit.

Внешние системы подключаются через adapters/ports.

Первый DNS-провайдер: **Cloudflare**.

## Архитектурные принципы

1. **Модульный монолит сначала.** Одна кодовая база и одна основная граница деплоя, но строгие внутренние границы.
2. **Одно ядро, несколько клиентов.** Telegram и Web используют одни use case и одну модель авторизации.
3. **Provider abstraction.** Cloudflare, SSH, proxy engines и другие внешние системы — adapters, а не бизнес-логика.
4. **Стабильные API-контракты.** UI не зависит от внутренних деталей модулей и provider-specific форматов.
5. **Аудит изменений.** Значимые infrastructure mutation привязаны к actor, client и resource.
6. **Никаких секретов в Git.** Токены, ключи и production credentials не хранятся в репозитории.
7. **Без ложного success.** Ошибка внешнего provider не должна превращаться во внутреннее успешное состояние.
8. **Без преждевременных микросервисов.** Выделение сервиса возможно только при измеримой необходимости.

## V1

**V1 = безопасное управление доменами и DNS с минимальным каталогом серверов через Web и Telegram.**

В V1 входят:

- несколько управляемых DNS-зон;
- Cloudflare DNS adapter;
- создание и удаление поддоменов;
- A, AAAA, CNAME, TXT, MX, NS;
- редактирование DNS-записей;
- Server Catalog;
- Domain Binding типа `direct_dns`;
- роли, permissions, ownership и limits;
- audit log;
- REST API `/api/v1`;
- Telegram workflows;
- Web workflows;
- provider sync/error states;
- idempotency/concurrency protection для критичных mutation;
- staging и release hardening.

V1 намеренно **не включает**:

- SSH automation;
- произвольное remote shell execution;
- reverse proxy;
- TLS issuance;
- application deployment;
- полноценный server monitoring;
- Kubernetes;
- собственный authoritative DNS;
- microservice decomposition.

## Планируемая структура репозитория

```text
bakunity-infra/
├── apps/
│   ├── api/
│   ├── telegram/
│   └── web/
├── modules/
│   ├── identity/
│   ├── domains/
│   ├── dns/
│   ├── servers/
│   ├── deployments/
│   ├── proxy/
│   ├── certificates/
│   ├── monitoring/
│   └── audit/
├── infrastructure/
├── docs/
├── deploy/
└── tests/
```

Эта структура является целевой архитектурой. Production-код пока не создан.

## Project Context System

Проект использует [Project Context System](https://github.com/bakunity/Project-Context-System), чтобы рабочее состояние не зависело от памяти конкретного чата или AI-сессии.

> **CHAT IS WORKSPACE. GIT IS MEMORY. DOCS ARE CURRENT KNOWLEDGE.**

Новая AI-сессия начинает работу с `AGENTS.md`, `.project/state.json`, `docs/PROJECT_STATE.md`, `docs/ARCHITECTURE.md` и `docs/ACTIVE_WORK.md`, а затем читает только релевантные ADR и профильные документы.

Ключевые PCS-файлы:

- [`AGENTS.md`](AGENTS.md) — правила работы AI;
- [`.project/state.json`](.project/state.json) — машинный state/freshness;
- [`docs/PROJECT_STATE.md`](docs/PROJECT_STATE.md) — что истинно о проекте сейчас;
- [`docs/ACTIVE_WORK.md`](docs/ACTIVE_WORK.md) — что делается сейчас;
- [`docs/ADR/`](docs/ADR/README.md) — почему были приняты решения;
- [`docs/INCIDENTS/`](docs/INCIDENTS/README.md) — инциденты и root cause;
- [`docs/EVIDENCE.md`](docs/EVIDENCE.md) — что реально проверено;
- [`docs/CONTEXT_SYSTEM.md`](docs/CONTEXT_SYSTEM.md) — правила интеграции PCS в этот репозиторий.

Локальная базовая проверка контекста:

```bash
python scripts/validate_context.py .
```

## Документация

### Вектор продукта

- [Стратегические цели и North Star](docs/GOALS.md)
- [Описание продукта](docs/PRODUCT.md)
- [План развития](docs/ROADMAP.md)
- [Backlog V1](docs/BACKLOG_V1.md)

### Архитектура

- [Архитектура](docs/ARCHITECTURE.md)
- [ADR registry](docs/ADR/README.md)
- [Архитектурные решения — совместимый индекс](docs/DECISIONS.md)
- [Архитектурная ревизия Phase 0](docs/PHASE0_REVIEW.md)
- [Модель предметной области](docs/DOMAIN_MODEL.md)
- [Модель базы данных](docs/DATABASE_MODEL.md)
- [API-контракт](docs/API_CONTRACT.md)

### Клиенты и доступ

- [UX Telegram-бота](docs/TELEGRAM_UX.md)
- [UX веб-панели](docs/WEB_UX.md)
- [Роли и права доступа](docs/PERMISSIONS.md)

### Безопасность и разработка

- [Модель безопасности](docs/SECURITY.md)
- [Правила разработки](CONTRIBUTING.md)

## Порядок проектирования и реализации

```text
Product
   ↓
Goals
   ↓
Architecture
   ↓
Domain Model
   ↓
Database Model
   ↓
API Contract
   ↓
Telegram UX + Web UX
   ↓
Security / Permissions
   ↓
Architecture Review
   ↓
Backlog V1
   ↓
Development
```

Phase 0 прошёл архитектурную сверку. Перед реализацией отдельных блоков остаются локальные decision gates — например конкретный Web authentication и optimistic concurrency mechanism. Они оформляются отдельными ADR и не меняют общий вектор.

## Первый milestone разработки

Первый vertical slice должен доказать архитектуру сквозным сценарием:

> Пользователь с разрешением выбирает `bakunity.online`, создаёт `test.bakunity.online` на заданный IPv4, Cloudflare получает запись, PostgreSQL хранит ресурс, audit фиксирует действие, а результат доступен через API и Telegram. После этого тот же use case подключается к Web.

## Текущий этап

**Phase 0 завершён. Разработка V1 ещё не начата.**

Текущее состояние всегда сверяется по [`docs/PROJECT_STATE.md`](docs/PROJECT_STATE.md), а текущая работа — по [`docs/ACTIVE_WORK.md`](docs/ACTIVE_WORK.md).

Следующий шаг — выполнять [BACKLOG_V1.md](docs/BACKLOG_V1.md) с начала, закрывая decision gates перед соответствующими блоками реализации.

Production-учётные данные, серверные ключи и секреты DNS-провайдеров никогда не должны попадать в этот репозиторий.
