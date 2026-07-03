from flask import Blueprint, jsonify, session
from schemas.query_schema import QueryRequestSchema, QueryResponseSchema
from repositories.document_repository import DocumentRepository
from repositories.query_repository import QueryRepository
from services.rag_service import get_chain, has_vectorstore
from utils.decorators import login_required
from utils.validators import parse_request

query_bp = Blueprint("query", __name__, url_prefix="/api")

_response_schema = QueryResponseSchema()


@query_bp.route("/query", methods=["POST"])
@login_required
def query():
    data, err = parse_request(QueryRequestSchema())
    if err:
        return err

    user_id = session["user_id"]
    question = data["question"].strip()

    if not has_vectorstore(user_id):
        return jsonify({"error": "No documents ingested yet. Please upload a PDF first."}), 400

    try:
        qa_chain, retriever = get_chain(user_id)
        source_docs = retriever.invoke(question)
    except Exception as e:
        return jsonify({"error": f"Failed to load knowledge base: {e}"}), 500

    try:
        answer = qa_chain.invoke(question)
        sources = list({doc.metadata.get("source", "unknown") for doc in source_docs})
        pages = sorted({doc.metadata.get("page") for doc in source_docs if doc.metadata.get("page")})

        latest_doc = DocumentRepository.get_latest(user_id)
        QueryRepository.create(
            user_id=user_id,
            question=question,
            answer=answer,
            sources=sources,
            pages=pages,
            document_id=latest_doc.id if latest_doc else None,
        )

        result = _response_schema.dump({"answer": answer, "sources": sources, "pages": pages})
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"{type(e).__name__}: {e}"}), 500
