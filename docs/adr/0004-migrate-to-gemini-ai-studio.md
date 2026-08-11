# Migrate to Gemini and Google AI Studio

## Context

We currently use OpenAI for generating embeddings (`text-embedding-3-small` with 1536 dimensions) and chat models. However, we want to provide a free alternative during development and potentially production to reduce API costs. Google AI Studio offers a generous free tier for their Gemini models, including `gemini-1.5-flash` for chat/generation and `text-embedding-004` (768 dimensions) for embeddings.

While Google AI Studio provides an OpenAI-compatible endpoint that would allow us to keep the `openai` Python package with minimal changes, we decided to switch to the official `google-genai` SDK for better long-term support and access to Gemini-specific features.

## Decision

1. We will replace the `openai` Python package with the official `google-genai` SDK.
2. We will use `gemini-1.5-flash` for all Chat/Generation tasks due to its speed and high free tier limits.
3. We will use `text-embedding-004` for all embedding tasks.
4. Because `text-embedding-004` uses 768 dimensions by default (unlike `text-embedding-3-small`'s 1536 dimensions), we will alter the `pgvector` column in the `Chunk` model to 768 dimensions and drop any existing 1536-dimensional embeddings.
5. We will rename the `OPENAI_API_KEY` environment variable to `GEMINI_API_KEY` for clarity.

## Consequences

- The `chunks` table schema is updated to use `VECTOR(768)`. Existing database vectors will be dropped or migrated, requiring a re-index of documents if they were already parsed.
- The backend dependencies have changed; developers must run `pip install` or sync their environments to pick up `google-genai` and drop `openai`.
- The environment variables change; all developers must update their `.env` files to provide `GEMINI_API_KEY`.
