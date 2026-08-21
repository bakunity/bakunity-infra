# Architecture

## Architectural style

Bakunity Infra is designed as a **modular monolith**.

The system remains one product and one primary application boundary while its internal capabilities are separated into explicit business modules.

The goal is to avoid both extremes:

- a tightly coupled monolith where everything imports everything;
- premature microservices that add deployment and operational complexity before it is justified.

## High-level model

```text
                  ┌─────────────────┐
                  │   Web Console   │
                  └────────┬────────┘
                           │
                  ┌────────▼────────┐
                  │    REST API     │
                  └────────┬────────┘
                           │
┌─────────────────┐        │
│  Telegram Bot   ├────────┤
└─────────────────┘        │
                           ▼
                 ┌───────────────────┐
                 │ Application Core  │
                 └─────────┬─────────┘
                           │
      ┌────────────┬───────┼──────────┬────────────┐
      ▼            ▼       ▼          ▼            ▼
   Identity     Domains   DNS      Servers      Audit
                              
              Deployments / Proxy / Certificates
                     added in later phases
```

## Module boundaries

Planned modules:

### Identity & Access

Owns users, roles, permissions, client identities and access decisions.

### Domains

Owns managed subdomains, ownership, lifecycle, limits and relationships to zones and servers.

### DNS

Owns DNS records, DNS operations and provider-neutral DNS behavior.

### Servers

Owns server inventory and server metadata. Remote provisioning is intentionally outside the initial scope.

### Deployments

Owns application deployment state and lifecycle in later phases.

### Proxy

Owns reverse-proxy routing behavior in later phases.

### Certificates

Owns certificate lifecycle and TLS-related state in later phases.

### Monitoring

Owns health and availability signals in later phases.

### Audit

Owns append-oriented records of meaningful user and system actions.

## Clients are not business logic

Telegram handlers and web pages must not contain infrastructure business rules.

For example, Telegram must not directly call Cloudflare to create a record.

Preferred flow:

```text
Telegram/Web
    │
    ▼
Application use case
    │
    ▼
Domain/DNS module
    │
    ▼
Provider interface
    │
    ▼
Cloudflare adapter
```

This keeps behavior consistent across clients and allows providers to change without rewriting the product interface.

## Ports and adapters at external boundaries

External systems should be accessed through explicit interfaces/adapters.

Examples:

- DNS provider adapter;
- database adapter;
- SSH adapter;
- reverse-proxy adapter;
- certificate provider/ACME adapter;
- notification adapter.

Cloudflare is the planned first DNS adapter, not a permanent dependency of the domain model.

## Data ownership

Each module should own its own business rules and data access patterns even if the first version uses one PostgreSQL database.

A single database does not mean unrestricted cross-module access.

Cross-module interaction should happen through explicit application services, commands, queries or published internal contracts rather than arbitrary table access.

## API boundary

The REST API is a public application boundary for Web and future integrations.

Telegram may run in the same deployable unit, but it must invoke the same application use cases as the HTTP API rather than maintaining separate business rules.

## Planned technology direction

Current architectural direction, not yet implementation:

- Python / FastAPI for backend and REST API;
- aiogram for Telegram;
- PostgreSQL for persistent state;
- SQLAlchemy and Alembic for persistence and migrations;
- Next.js / TypeScript for the Web Console;
- Cloudflare as the initial DNS provider.

Technology choices may be adjusted before implementation if a better fit is identified.

## Deployment philosophy

Initial deployment should stay simple:

- one repository;
- one primary application stack;
- one PostgreSQL instance;
- clear process separation where useful;
- no service decomposition without a concrete need.

A module can later be extracted into an independent service when there is a measurable reason such as isolation, scaling, workload type or ownership boundaries.

## Architectural invariants

These should remain true unless an architecture decision explicitly changes them:

1. Web and Telegram share one source of truth.
2. Business logic is independent from Telegram UI and web UI.
3. External providers are accessed through adapters.
4. Secrets are never stored in source control.
5. Infrastructure mutations are auditable.
6. Authorization is enforced in the application layer, not only in the UI.
7. The first implementation favors simplicity over distributed-system complexity.
