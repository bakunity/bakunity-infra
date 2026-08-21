# Bakunity Infra

> Infrastructure control plane for domains, DNS, servers and application delivery.

**Status:** Planning / architecture  
**Architecture:** Modular Monolith  
**Interfaces:** Web Console, Telegram Bot, REST API

Bakunity Infra is a single infrastructure management system designed to make routine domain and server operations simple from both a web interface and Telegram.

The project starts with domain and DNS management and is designed to grow into a broader control plane for servers, reverse proxy, TLS certificates, deployments, monitoring and audit.

## Product idea

A user should be able to create a subdomain, attach it to a server and manage its DNS without manually opening a registrar or DNS provider dashboard.

```text
Web Console / Telegram
          │
          ▼
      Bakunity Infra
          │
    ┌─────┼───────────┐
    ▼     ▼           ▼
 Domains  DNS       Servers
          │
          ▼
     DNS Provider
```

Later the same control plane can also manage application routing and delivery:

```text
subdomain
   +
server
   +
target port
   │
   ▼
reverse proxy
   │
   ▼
TLS / HTTPS
   │
   ▼
health check
```

## Interfaces

Bakunity Infra is not a Telegram-only bot. Telegram and the website are two clients of the same application core.

- **Web Console** — full management interface.
- **Telegram Bot** — fast operational interface for common actions.
- **REST API** — programmatic interface and boundary for external integrations.
- **CLI** — possible future client.

Telegram is expected to reach usable functionality first because it is faster to iterate on, while the web console is developed against the same backend and domain model.

## Core modules

The planned modular monolith is divided by business capability rather than by generic technical folders.

- Identity & Access
- Domains
- DNS
- Servers
- Deployments
- Proxy
- Certificates
- Monitoring
- Audit

External systems are connected through adapters so that, for example, the DNS module does not depend directly on one provider forever.

Initial DNS provider: **Cloudflare**.

## Architecture principles

1. **Modular monolith first.** One codebase and deployment boundary, with strict internal module boundaries.
2. **One application core, multiple clients.** Telegram and Web reuse the same use cases and authorization model.
3. **Provider abstraction.** Cloudflare, SSH, proxy engines and other external systems are adapters, not business logic.
4. **API-first boundaries.** External clients interact through stable application/API contracts.
5. **Auditability.** Infrastructure-changing actions should be attributable to a user and source client.
6. **No secrets in Git.** Tokens, credentials and private keys never belong in the repository.
7. **Grow by extraction, not premature microservices.** A module becomes a separate service only when there is a real scaling or isolation reason.

## Initial scope

The first usable version focuses on DNS and domain operations:

- multiple managed DNS zones;
- subdomain creation;
- A, AAAA, CNAME, TXT, MX and NS records;
- record editing and deletion;
- domain ownership inside Bakunity Infra;
- server catalog;
- attaching a domain/subdomain to a server;
- roles and limits;
- audit log;
- both Telegram and Web clients using the same backend logic.

Automatic SSH provisioning, reverse proxy configuration, TLS issuance and application deployment are intentionally deferred until the DNS/domain foundation is stable.

## Planned repository shape

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

This structure is a target architecture, not an indication that implementation has started.

## Documentation

- [Product definition](docs/PRODUCT.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Architecture decisions](docs/DECISIONS.md)
- [Roadmap](docs/ROADMAP.md)
- [Security model](docs/SECURITY.md)
- [Contributing](CONTRIBUTING.md)

## Current phase

The repository is currently in the **planning and architecture phase**. The goal of this phase is to define clear boundaries before implementation begins.

No production credentials, server keys or DNS-provider secrets should ever be committed here.
