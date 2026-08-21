# Roadmap

This roadmap describes product stages, not delivery dates.

## Phase 0 — Foundation and design

**Status: current**

Goals:

- define product scope;
- define modular-monolith boundaries;
- define Web + Telegram as equal clients of one application core;
- document security expectations;
- define the first release boundary;
- avoid implementation before the architecture is clear enough.

Deliverables:

- project README;
- product definition;
- architecture document;
- security document;
- contribution rules;
- initial backlog before coding starts.

## Phase 1 — DNS and domains

Goal: make domain and DNS operations fully manageable through Bakunity Infra.

Planned capabilities:

- managed DNS zones;
- subdomain creation;
- A records;
- AAAA records;
- CNAME records;
- TXT records;
- MX records;
- NS records;
- editing and deleting records;
- ownership and per-user limits;
- Cloudflare provider integration;
- audit trail;
- Telegram workflows;
- corresponding Web Console workflows.

Telegram can be ahead in UX delivery, but both clients must use the same backend logic.

## Phase 2 — Server inventory

Goal: connect DNS concepts to managed infrastructure without yet automating remote configuration.

Planned capabilities:

- server catalog;
- IPv4/IPv6 metadata;
- labels and environment metadata;
- basic reachability/status information;
- attach domain/subdomain to a server;
- display domain-to-server relationships;
- permissions around server management.

## Phase 3 — Routing and HTTPS

Goal: move from DNS management to application delivery.

Planned capabilities:

- reverse-proxy abstraction;
- domain + server + target port mapping;
- managed routing configuration;
- TLS certificate issuance and renewal;
- deployment validation;
- health checks;
- safe rollback model.

## Phase 4 — Deployments

Goal: provide repeatable application deployment workflows.

Possible capabilities:

- deployment records;
- environment configuration references;
- container-aware deployment workflows;
- deployment history;
- rollback;
- status and health reporting.

Exact deployment technology should be selected only after requirements are validated.

## Phase 5 — Monitoring and operations

Goal: turn Bakunity Infra into a broader infrastructure operations surface.

Possible capabilities:

- server and endpoint monitoring;
- certificate expiration visibility;
- DNS validation;
- availability history;
- incident notifications;
- operational summaries in Telegram;
- richer dashboard in Web Console.

## Phase 6 — Platform capabilities

Only when justified by actual usage:

- CLI;
- external API clients;
- additional DNS providers;
- multi-region infrastructure;
- background workers or queues;
- extraction of high-load modules into separate services.

## Explicit non-goal

The project should not become microservices simply because it contains multiple modules. Service extraction requires a concrete operational or scaling reason.
