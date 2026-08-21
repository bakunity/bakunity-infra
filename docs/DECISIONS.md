# Architecture Decision Log

This file records project-level decisions that should not be changed casually during implementation.

## ADR-001 — Modular monolith

**Status:** Accepted

Bakunity Infra starts as a modular monolith rather than microservices.

Reasons:

- the product is early-stage;
- modules need strong boundaries but not distributed-system overhead;
- one repository and one primary deployment make iteration easier;
- individual modules can be extracted later if real scaling or isolation needs appear.

## ADR-002 — Web and Telegram are clients of one core

**Status:** Accepted

The Web Console and Telegram Bot are separate user interfaces over the same application logic and source of truth.

Business rules must not be independently reimplemented in each client.

Telegram is expected to be faster to iterate on, but it is not the architectural center of the product.

## ADR-003 — REST API is a first-class boundary

**Status:** Accepted

The system should expose a stable REST API for the Web Console and future integrations.

The API is not a replacement for the application layer; it is one interface into it.

## ADR-004 — Provider-neutral DNS core

**Status:** Accepted

Cloudflare is the first DNS provider, but DNS business logic must not depend permanently on Cloudflare-specific APIs or data shapes.

A provider interface/adaptor boundary should make additional DNS providers possible later.

## ADR-005 — PostgreSQL as the initial source of truth

**Status:** Accepted in principle

Bakunity Infra should maintain its own persistent model for users, zones, domains, records, servers, relationships and audit events rather than treating an external DNS provider as the product database.

PostgreSQL is the planned initial persistent store.

## ADR-006 — Infrastructure automation follows security foundations

**Status:** Accepted

Broad SSH automation, reverse-proxy mutation and automated deployment are intentionally deferred until identity, authorization, auditing, credential handling and rollback principles are established.

## ADR-007 — No premature service extraction

**Status:** Accepted

A module may become an independent service only when there is a concrete reason such as workload characteristics, scaling pressure, fault isolation or operational ownership.

Module count alone is not a reason to create microservices.

---

Future architecture decisions should be appended with a new ADR number, status, context and consequences rather than silently rewriting accepted assumptions.
