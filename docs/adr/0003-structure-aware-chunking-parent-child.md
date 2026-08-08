# Structure-aware chunking with parent-child retrieval

We chose structure-aware chunking (using Unstructured.io's document layout detection) over fixed-size or semantic chunking, combined with a parent-child retrieval strategy.

Financial documents (SEC 10-Ks) contain 30–50% tables. Fixed-size chunking at 512 tokens slices tables mid-row, destroying their meaning and disconnecting figures from column headers. Semantic chunking (splitting by embedding similarity between sentences) triggers false split points at table/narrative boundaries.

Structure-aware chunking preserves tables as indivisible units and respects section boundaries. Small child chunks (256–512 tokens) are indexed in pgvector for precise vector retrieval; the larger parent section (1,000–4,000 tokens) is passed to the LLM for synthesis. This gives retrieval precision without sacrificing generation context.

## Consequences

- The data model requires a parent-child relationship between chunks (not a flat list)
- Chunk quality depends on Unstructured.io's layout detection accuracy — degraded parsing on unusual PDFs will silently reduce RAG quality
- Tables must be converted to a text-friendly format (Markdown or HTML) before embedding
