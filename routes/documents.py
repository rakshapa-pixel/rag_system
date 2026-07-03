import os
import tempfile
from flask import Blueprint, request, jsonify, session
from schemas.document_schema import DocumentResponseSchema, IngestResponseSchema
from repositories.document_repository import DocumentRepository
from services.ingest_service import ingest_pdf
from services.rag_service import evict_chain, has_vectorstore
from rag import clear_vectorstore
from utils.decorators import login_required

documents_bp = Blueprint("documents", __name__, url_prefix="/api")

_list_schema = DocumentResponseSchema(many=True)
_ingest_schema = IngestResponseSchema()


@documents_bp.route("/documents", methods=["GET"])
@login_required
def get_documents():
    docs = DocumentRepository.list_by_user(session["user_id"])
    result = _list_schema.dump([
        {"id": d.id, "filename": d.filename, "chunks": d.chunks,
         "uploaded_at": d.uploaded_at.isoformat()}
        for d in docs
    ])
    return jsonify(result)


@documents_bp.route("/ingest", methods=["POST"])
@login_required
def ingest():
    user_id = session["user_id"]

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["file"]
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported"}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        chunk_count = ingest_pdf(user_id, tmp_path, file.filename)
        doc = DocumentRepository.create(user_id, file.filename, chunk_count)
        result = _ingest_schema.dump({
            "message": "Ingestion complete",
            "chunks": chunk_count,
            "filename": file.filename,
            "document_id": doc.id,
        })
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        os.unlink(tmp_path)


@documents_bp.route("/documents/<int:doc_id>", methods=["DELETE"])
@login_required
def delete_document(doc_id):
    user_id = session["user_id"]

    doc = DocumentRepository.get_by_id(doc_id, user_id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    DocumentRepository.delete(doc_id, user_id)

    if not DocumentRepository.get_latest(user_id):
        evict_chain(user_id)
        clear_vectorstore(user_id)

    return jsonify({"message": "Document removed"})
