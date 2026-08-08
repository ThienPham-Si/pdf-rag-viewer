# Direct browser-to-FastAPI communication bypassing Vercel

The Next.js frontend calls the FastAPI backend directly (`browser → api.domain.com`) rather than proxying through Next.js API routes (`browser → Vercel → FastAPI`).

This avoids Vercel's serverless function timeout (60s on Pro, 300s on Enterprise) which would truncate SSE streams during LLM chat generation. Financial document Q&A often produces long, detailed responses that exceed these limits. The tradeoff is that the FastAPI API is publicly accessible and requires CORS configuration, but it is authenticated via Clerk JWT validation on every request. This is preferable to having Vercel silently kill chat streams mid-response.

## Consequences

- FastAPI must validate Clerk JWTs directly (using Clerk's JWKS endpoint)
- CORS must be configured on FastAPI to allow the Vercel frontend origin
- The API surface is publicly discoverable (mitigated by authentication + rate limiting)
