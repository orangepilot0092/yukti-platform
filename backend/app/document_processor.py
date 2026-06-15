import uuid
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.vector_db.embeddings import embed_and_store

def process_and_ingest_pdf(file_path: str, metadata: dict = None) -> list:
    """
    1. Extracts text from a PDF.
    2. Chunks the text intelligently.
    3. Embeds and stores each chunk in Qdrant.
    Returns a list of created point IDs.
    """
    # 1. Extract Text
    reader = PdfReader(file_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
    
    if not full_text.strip():
        raise ValueError("No text could be extracted from the PDF.")

    # 2. Chunk the Text (Production-grade strategy)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,      # ~125 tokens
        chunk_overlap=50,    # Overlap ensures context isn't lost at chunk boundaries
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_text(full_text)

    # 3. Embed and Store in Qdrant
    point_ids = []
    meta = metadata or {}
    
    for i, chunk in enumerate(chunks):
        # Add chunk-specific metadata
        chunk_meta = meta.copy()
        chunk_meta["chunk_index"] = i
        chunk_meta["total_chunks"] = len(chunks)
        
        point_id = embed_and_store(text=chunk, metadata=chunk_meta)
        point_ids.append(point_id)
        
    return point_ids
