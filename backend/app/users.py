from app.model import User
from flask import Blueprint, jsonify, request, session
from flask_login import login_required
from werkzeug.security import generate_password_hash

bp = Blueprint("user", __name__)


@bp.route("/users", methods=["POST"])
def create_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    if User.get_by_id(username):
        return jsonify({"error": "user already exists"}), 400

    user = User(username, generate_password_hash(password))
    user.save()

    return jsonify({"status": "created", "username": username})


@bp.route("/users/me", methods=["GET"])
@login_required
def get_me():
    user = User.get_by_id(session.get("_user_id"))
    if not user:
        return jsonify({"error": "user not found"}), 404

    return jsonify({"username": user.id})
