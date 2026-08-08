# Row-level security for multi-tenant data isolation

We chose PostgreSQL row-level security (RLS) over schema-per-tenant or database-per-tenant isolation. Every table includes a `tenant_id` column enforced by RLS policies.

This keeps a single pgvector HNSW index shared across all tenants — schema-per-tenant would require N separate vector indexes, wasting memory and complicating search operations. The tradeoff is weaker isolation (a bug in RLS policies could theoretically leak data across tenants), but RLS is the industry-standard approach for SaaS on PostgreSQL and acceptable for MVP.

## Considered Options

- **Schema-per-tenant**: Stronger isolation, but each tenant gets its own pgvector index. At 1,536 dimensions with HNSW, each index carries significant memory overhead. Migrations must run per-schema. Rejected because the vector index duplication cost is disproportionate at scale.
- **Database-per-tenant**: Maximum isolation, operationally untenable for a SaaS product. Rejected outright.
