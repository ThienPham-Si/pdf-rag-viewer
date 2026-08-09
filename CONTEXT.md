# Document Intelligence

A multi-tenant SaaS system that parses financial and legal PDF documents, enabling natural-language Q&A with exact page citations.

## Language

**Document**:
An uploaded PDF — a single SEC filing, legal contract, or other financial document — belonging to a user within a Tenant.
_Avoid_: File, upload, attachment

**Chunk**:
A structural unit extracted from a Document that preserves section boundaries and table integrity. Either a Parent Chunk or a Child Chunk.
_Avoid_: Segment, fragment, piece

**Parent Chunk**:
A broad contextual section (containing one or more Child Chunks) passed to the LLM for answer synthesis.
_Avoid_: Section, block

**Child Chunk**:
A small, precisely-scoped unit of content within a Parent Chunk. The unit of retrieval during search.
_Avoid_: Sub-chunk, snippet

**Embedding**:
A vector representation of a Child Chunk used for similarity search.
_Avoid_: Vector (as a domain noun)

**Conversation**:
A stateful chat session scoped to a user-selected set of Documents.
_Avoid_: Chat, session, thread

**Message**:
A single user query or assistant response within a Conversation.
_Avoid_: Turn, utterance

**Citation**:
A reference linking a claim in an assistant Message to a specific page in a source Document.
_Avoid_: Reference, source, footnote

**Tenant**:
An isolated organizational boundary. All data is scoped to exactly one Tenant. In the current model, each Tenant maps 1:1 to a single User.
_Avoid_: Organization, workspace, account

**User**:
A person who authenticates via Clerk and owns exactly one Tenant. The identity boundary for login and API access.
_Avoid_: Account, member, profile

