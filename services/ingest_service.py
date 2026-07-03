from rag import load_and_chunk, build_vectorstore, build_qa_chain, clear_vectorstore
from services.rag_service import set_chain, evict_chain


def ingest_pdf(user_id: int, file_path: str, display_name: str) -> int:
    evict_chain(user_id)
    clear_vectorstore(user_id)

    chunks = load_and_chunk(file_path, display_name=display_name)
    vs = build_vectorstore(chunks, user_id)
    set_chain(user_id, build_qa_chain(vs))

    return len(chunks)
