import os
import sys
from dotenv import load_dotenv

load_dotenv()

if not os.environ.get("GEMINI_KEY"):
    print("Error: GEMINI_KEY environment variable is not set.")
    sys.exit(1)

from rag import load_and_chunk, build_vectorstore, load_vectorstore, build_qa_chain, collection_has_data

CLI_USER = "cli"


def ingest(file_path: str):
    if not os.path.exists(file_path):
        print(f"Error: file '{file_path}' not found.")
        sys.exit(1)
    chunks = load_and_chunk(file_path)
    build_vectorstore(chunks, CLI_USER)
    print("Ingestion complete. Run with --query to start asking questions.")


def query_mode():
    if not collection_has_data(CLI_USER):
        print("No documents ingested yet. Run: python main.py --ingest <your_file.pdf>")
        sys.exit(1)

    print("Loading vector store...")
    vectorstore = load_vectorstore(CLI_USER)
    qa_chain, retriever = build_qa_chain(vectorstore)
    print("Ready. Type your question (or 'quit' to exit):\n")

    while True:
        try:
            question = input("Q: ").strip()
        except KeyboardInterrupt:
            print("\nExiting.")
            break
        if question.lower() in ("quit", "exit", "q"):
            break
        if not question:
            continue

        source_docs = retriever.invoke(question)
        try:
            answer = qa_chain.invoke(question)
            print(f"\nA: {answer}\n")
            if source_docs:
                sources = {doc.metadata.get("source", "unknown") for doc in source_docs}
                pages = sorted({doc.metadata.get("page") for doc in source_docs if doc.metadata.get("page")})
                print(f"Sources: {', '.join(sources)}", end="")
                if pages:
                    print(f"  |  Pages: {', '.join(str(p) for p in pages)}", end="")
                print()
        except Exception as e:
            print(f"\n[Gemini error ({type(e).__name__}) — showing retrieved context]\n")
            for i, doc in enumerate(source_docs, 1):
                print(f"--- Chunk {i} ---\n{doc.page_content}\n")
        print()


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python main.py --ingest <path_to_file.pdf>   Load and store a PDF")
        print("  python main.py --query                        Ask questions interactively")
        sys.exit(0)

    mode = sys.argv[1]

    if mode == "--ingest":
        if len(sys.argv) < 3:
            print("Error: provide a file path.  Example: python main.py --ingest doc.pdf")
            sys.exit(1)
        ingest(sys.argv[2])
    elif mode == "--query":
        query_mode()
    else:
        print(f"Unknown argument: {mode}")
        print("Use --ingest <file.pdf> or --query")
        sys.exit(1)


if __name__ == "__main__":
    main()
