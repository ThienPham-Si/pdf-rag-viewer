import tiktoken
from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.title import chunk_by_title
from unstructured.documents.elements import Table

encoder = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    return len(encoder.encode(text))

def parse_and_chunk_pdf(file_path: str):
    # Partition with layout detection to preserve tables as markdown
    elements = partition_pdf(
        filename=file_path,
        strategy="hi_res",
        pdf_infer_table_structure=True,
    )
    
    # We want tables as markdown. partition_pdf with hi_res and pdf_infer_table_structure=True 
    # creates Table elements with `.metadata.text_as_html`. We can convert it to markdown, or Unstructured 
    # might do it. For simplicity, we'll chunk by title which respects sections.
    
    # Group into parent chunks (1000 - 4000 tokens)
    parent_chunks = chunk_by_title(
        elements,
        max_characters=4000 * 4, # rough char equivalent
        new_after_n_chars=3500 * 4,
        overlap=0,
        combine_text_under_n_chars=1000 * 4,
        overlap_all=False,
    )
    
    # Actually, Unstructured's chunking is based on characters. We can refine tokens.
    # We'll construct parent and child chunks manually or use the token counts.
    
    result = []
    
    for p_elem in parent_chunks:
        p_text = p_elem.text
        # if Table, we might want to represent it as markdown if unstructured doesn't do it perfectly by default
        if hasattr(p_elem, "metadata") and hasattr(p_elem.metadata, "text_as_html") and p_elem.metadata.text_as_html:
            # Table html could be parsed, but let's stick to .text which unstructured provides
            pass
            
        p_tokens = count_tokens(p_text)
        page_num = p_elem.metadata.page_number if hasattr(p_elem, "metadata") else None
        
        # Split into child chunks (256-512 tokens)
        # We can do a simple character or sentence split, or just use tiktoken directly for exact tokens, 
        # but let's do a simple recursive split or just block split.
        
        child_texts = split_into_children(p_text, max_tokens=512, overlap_tokens=50)
        
        children = []
        for i, c_text in enumerate(child_texts):
            children.append({
                "content": c_text,
                "token_count": count_tokens(c_text),
                "chunk_index": i,
                "page_number": page_num
            })
            
        result.append({
            "content": p_text,
            "token_count": p_tokens,
            "page_number": page_num,
            "children": children
        })
        
    return result

def split_into_children(text: str, max_tokens: int = 512, overlap_tokens: int = 50) -> list[str]:
    tokens = encoder.encode(text)
    if len(tokens) <= max_tokens:
        return [text]
    
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + max_tokens
        chunk_tokens = tokens[start:end]
        chunks.append(encoder.decode(chunk_tokens))
        start += max_tokens - overlap_tokens
    
    return chunks
