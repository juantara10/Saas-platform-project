# Architecture Notes

The system is a modular monolith by design. It preserves transactional simplicity while exposing clean boundaries around identity, organizations, billing, developer access, auditing and operations. Extract a service only when scaling, ownership or failure-isolation evidence justifies the operational cost.

## Trust boundaries
- Public browser → web/API edge
- Authenticated principal → tenant membership check
- Application → PostgreSQL/Redis
- Stripe → signature-verified webhook endpoint
- CI → AWS through short-lived OIDC credentials

## Reliability
Use timeouts/retries with jitter for external calls, idempotency for webhook/job handlers, connection pooling, health probes, graceful shutdown, backups and restore drills.
