from models import db, Query


class QueryRepository:
    @staticmethod
    def create(
        user_id: int,
        question: str,
        answer: str,
        sources: list[str],
        pages: list[int],
        document_id: int | None = None,
    ) -> Query:
        record = Query(
            user_id=user_id,
            document_id=document_id,
            question=question,
            answer=answer,
            sources=", ".join(sources),
            pages=", ".join(str(p) for p in pages),
        )
        db.session.add(record)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return record

    @staticmethod
    def list_by_user(user_id: int) -> list[Query]:
        return (
            Query.query
            .filter_by(user_id=user_id)
            .order_by(Query.asked_at.desc())
            .all()
        )
