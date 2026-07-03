from sqlalchemy import func
from models import db, User


class UserRepository:
    @staticmethod
    def find_by_username(username: str) -> User | None:
        return User.query.filter(
            func.lower(User.username) == username.strip().lower()
        ).first()

    @staticmethod
    def find_by_email(email: str) -> User | None:
        return User.query.filter(
            func.lower(User.email) == email.strip().lower()
        ).first()

    @staticmethod
    def find_by_google_id(google_id: str) -> User | None:
        return User.query.filter_by(google_id=google_id).first()

    @staticmethod
    def username_exists(username: str) -> bool:
        return UserRepository.find_by_username(username) is not None

    @staticmethod
    def create(username: str, password: str) -> User:
        user = User(username=username.strip())
        user.set_password(password)
        db.session.add(user)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return user

    @staticmethod
    def create_oauth(username: str, email: str, google_id: str) -> User:
        user = User(username=username.strip(), email=email, google_id=google_id)
        db.session.add(user)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return user

    @staticmethod
    def link_google(user_id: int, google_id: str) -> None:
        User.query.filter_by(id=user_id).update({"google_id": google_id})
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
