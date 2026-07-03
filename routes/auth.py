from flask import Blueprint, jsonify, session, redirect
from schemas.auth_schema import SignupSchema, LoginSchema
from repositories.user_repository import UserRepository
from services.rag_service import evict_chain
from utils.validators import parse_request
from extensions import oauth
from config import Config

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data, err = parse_request(SignupSchema())
    if err:
        return err

    username = data["username"].strip()
    password = data["password"]

    if UserRepository.username_exists(username):
        return jsonify({"error": "Username already taken. Please choose another."}), 409

    user = UserRepository.create(username, password)
    session["user_id"] = user.id
    session["username"] = user.username
    return jsonify({"message": "Account created", "username": user.username}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data, err = parse_request(LoginSchema())
    if err:
        return err

    user = UserRepository.find_by_username(data["username"])
    if not user:
        return jsonify({"error": "No account found. Please sign up first."}), 404
    if not user.check_password(data["password"]):
        return jsonify({"error": "Incorrect password. Please try again."}), 401

    session["user_id"] = user.id
    session["username"] = user.username
    return jsonify({"message": "Logged in", "username": user.username})


@auth_bp.route("/logout", methods=["POST"])
def logout():
    evict_chain(session.get("user_id"))
    session.clear()
    return jsonify({"message": "Logged out"})


@auth_bp.route("/me", methods=["GET"])
def me():
    if "user_id" not in session:
        return jsonify({"authenticated": False})
    return jsonify({"authenticated": True, "username": session["username"]})


# ─── Google OAuth ─────────────────────────────────────────────────


@auth_bp.route("/providers", methods=["GET"])
def providers():
    """Tell the frontend which SSO providers are configured."""
    return jsonify({
        "google": bool(Config.GOOGLE_CLIENT_ID and Config.GOOGLE_CLIENT_SECRET)
    })


@auth_bp.route("/google")
def google_login():
    if not Config.GOOGLE_CLIENT_ID or not Config.GOOGLE_CLIENT_SECRET:
        return redirect(f"{Config.FRONTEND_URL}?oauth_error=Google+OAuth+is+not+configured+in+.env")
    return oauth.google.authorize_redirect(Config.GOOGLE_REDIRECT_URI)


@auth_bp.route("/google/callback")
def google_callback():
    try:
        token = oauth.google.authorize_access_token()
    except Exception as e:
        return redirect(f"{Config.FRONTEND_URL}?oauth_error={str(e)[:120]}")
    userinfo = token.get("userinfo") or {}

    google_id = userinfo.get("sub", "")
    email = userinfo.get("email", "")
    name = userinfo.get("name") or email.split("@")[0]

    user = UserRepository.find_by_google_id(google_id)
    if not user:
        user = UserRepository.find_by_email(email)
        if user:
            UserRepository.link_google(user.id, google_id)
        else:
            username = _unique_username(name)
            user = UserRepository.create_oauth(username, email, google_id)

    session["user_id"] = user.id
    session["username"] = user.username
    return redirect(Config.FRONTEND_URL)


def _unique_username(base: str) -> str:
    """Return `base` (sanitized) or append _N to avoid collisions."""
    candidate = base.strip().replace(" ", "_")
    if not UserRepository.username_exists(candidate):
        return candidate
    n = 2
    while UserRepository.username_exists(f"{candidate}_{n}"):
        n += 1
    return f"{candidate}_{n}"
