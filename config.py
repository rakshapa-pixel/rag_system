import os
import sqlalchemy as sa

_PRODUCTION = bool(os.environ.get("PRODUCTION"))


def _resolve_db_url() -> str:
    raw = os.environ.get("DATABASE_URL", "").strip()
    if not raw:
        if _PRODUCTION:
            raise RuntimeError("DATABASE_URL is required in production")
        return "sqlite:///rag_app.db"

    url = raw.replace("postgres://", "postgresql://", 1)

    if url.startswith("sqlite"):
        return url

    # Test the connection before handing it to Flask-SQLAlchemy.
    # If it fails (wrong password, network issue, etc.) fall back to SQLite in dev.
    try:
        engine = sa.create_engine(url, connect_args={"connect_timeout": 5})
        with engine.connect() as conn:
            conn.execute(sa.text("SELECT 1"))
        engine.dispose()
        host = url.split("@")[-1].split("?")[0]
        print(f"✓ Connected to Aiven PostgreSQL: {host}")
        return url
    except Exception as e:
        if _PRODUCTION:
            raise
        print(f"\n⚠️  Cannot reach configured DATABASE_URL: {e}")
        print("   Fix the password in .env to use Aiven.")
        print("   Falling back to local SQLite for now.\n")
        return "sqlite:///rag_app.db"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")

    SQLALCHEMY_DATABASE_URI = _resolve_db_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _PRODUCTION   # HTTPS only in production
    SESSION_COOKIE_HTTPONLY = True

    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")

    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", "http://localhost:5000/api/auth/google/callback")
    FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")
