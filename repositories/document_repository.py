from models import db, Document


class DocumentRepository:
    @staticmethod
    def list_by_user(user_id: int) -> list[Document]:
        return (
            Document.query
            .filter_by(user_id=user_id)
            .order_by(Document.uploaded_at.desc())
            .all()
        )

    @staticmethod
    def get_latest(user_id: int) -> Document | None:
        return (
            Document.query
            .filter_by(user_id=user_id)
            .order_by(Document.uploaded_at.desc())
            .first()
        )

    @staticmethod
    def create(user_id: int, filename: str, chunks: int) -> Document:
        doc = Document(user_id=user_id, filename=filename, chunks=chunks)
        db.session.add(doc)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return doc

    @staticmethod
    def get_by_id(doc_id: int, user_id: int) -> Document | None:
        return Document.query.filter_by(id=doc_id, user_id=user_id).first()

    @staticmethod
    def delete(doc_id: int, user_id: int) -> bool:
        doc = DocumentRepository.get_by_id(doc_id, user_id)
        if not doc:
            return False
        db.session.delete(doc)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return True
