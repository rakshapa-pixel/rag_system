import os
import sys
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

# Allow OAuth over plain HTTP in development (disabled only when PRODUCTION=1)
if not os.environ.get("PRODUCTION"):
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

if not os.environ.get("GEMINI_KEY"):
    print("Error: GEMINI_KEY environment variable is not set.")
    sys.exit(1)

from config import Config
from models import db
from extensions import oauth
from routes.auth import auth_bp
from routes.documents import documents_bp
from routes.query import query_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, supports_credentials=True, origins=Config.CORS_ORIGINS)
    db.init_app(app)

    oauth.init_app(app)
    oauth.register(
        name="google",
        client_id=Config.GOOGLE_CLIENT_ID,
        client_secret=Config.GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

    with app.app_context():
        db.create_all()

    app.register_blueprint(auth_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(query_bp)

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"})

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
