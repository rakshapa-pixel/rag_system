import os
import chromadb
import pypdf
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

CHROMA_LOCAL_DIR = "/tmp/chroma_db"
EMBED_MODEL = "models/text-embedding-004"
GEMINI_MODEL = "gemini-2.5-flash"
INGEST_BATCH_SIZE = 100

_chroma_client = None
_embeddings = None


def _get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = GoogleGenerativeAIEmbeddings(
            model=EMBED_MODEL,
            google_api_key=os.environ.get("GEMINI_KEY")
        )
    return _embeddings


def _get_chroma_client():
    global _chroma_client
    if _chroma_client is not None:
        return _chroma_client

    if os.environ.get("CHROMA_API_KEY"):
        try:
            client = chromadb.CloudClient()
            client.heartbeat()
            _chroma_client = client
            print("✓ Connected to TryChroma Cloud")
        except Exception as e:
            print(f"\n⚠️  TryChroma Cloud connection failed: {e}")
            print("   Falling back to local ChromaDB.\n")
            _chroma_client = chromadb.PersistentClient(path=CHROMA_LOCAL_DIR)
    else:
        _chroma_client = chromadb.PersistentClient(path=CHROMA_LOCAL_DIR)

    return _chroma_client


def user_collection_name(user_id) -> str:
    return f"user_{user_id}"


def collection_has_data(user_id) -> bool:
    try:
        client = _get_chroma_client()
        col = client.get_collection(user_collection_name(user_id))
        return col.count() > 0
    except Exception as e:
        err = str(e).lower()
        if "not found" in err or "does not exist" in err or "no such collection" in err:
            return False
        raise


def load_and_chunk(file_path: str, chunk_size: int = 1000, chunk_overlap: int = 200, display_name: str = None):
    source_name = display_name or os.path.basename(file_path)
    if file_path.lower().endswith(".pdf"):
        reader = pypdf.PdfReader(file_path)
        documents = [
            Document(
                page_content=page.extract_text() or "",
                metadata={"source": source_name, "page": i + 1},
            )
            for i, page in enumerate(reader.pages)
            if page.extract_text()
        ]
    else:
        with open(file_path, encoding="utf-8") as f:
            text = f.read()
        documents = [Document(page_content=text, metadata={"source": source_name})]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    chunks = splitter.split_documents(documents)
    print(f"Loaded '{file_path}': {len(documents)} page(s) → {len(chunks)} chunks")
    return chunks


def clear_vectorstore(user_id):
    client = _get_chroma_client()
    try:
        client.delete_collection(user_collection_name(user_id))
    except Exception:
        pass


def build_vectorstore(chunks, user_id):
    client = _get_chroma_client()
    embeddings = _get_embeddings()
    collection_name = user_collection_name(user_id)
    total = len(chunks)

    first_batch = chunks[:INGEST_BATCH_SIZE]
    vectorstore = Chroma.from_documents(
        documents=first_batch,
        embedding=embeddings,
        client=client,
        collection_name=collection_name,
    )
    stored = len(first_batch)
    print(f"  Stored {stored}/{total} chunks...")

    for i in range(INGEST_BATCH_SIZE, total, INGEST_BATCH_SIZE):
        batch = chunks[i: i + INGEST_BATCH_SIZE]
        vectorstore.add_documents(batch)
        stored += len(batch)
        print(f"  Stored {stored}/{total} chunks...")

    print(f"Done. {total} chunks stored in collection '{collection_name}'")
    return vectorstore


def load_vectorstore(user_id):
    client = _get_chroma_client()
    embeddings = _get_embeddings()
    return Chroma(
        client=client,
        collection_name=user_collection_name(user_id),
        embedding_function=embeddings,
    )


def build_qa_chain(vectorstore):
    gemini_key = os.environ.get("GEMINI_KEY")
    llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, google_api_key=gemini_key)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    prompt = PromptTemplate(
        template=(
            "Use the following context to answer the question.\n"
            "If the answer is not in the context, say "
            "'I don't have enough information to answer this.'\n\n"
            "Context:\n{context}\n\n"
            "Question: {question}\n\n"
            "Answer:"
        ),
        input_variables=["context", "question"],
    )

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain, retriever