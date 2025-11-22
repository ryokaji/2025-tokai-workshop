from app.users import User
from flask import Blueprint, jsonify, request
from flask_login import (
    login_user,
    logout_user,
)
from werkzeug.security import check_password_hash

bp = Blueprint("login", __name__)


@bp.route("/login", methods=["POST"])
def login():
    username = request.form.get("username") or request.json.get("username")
    password = request.form.get("password") or request.json.get("password")
    error = None

    user = User.get_by_id(username)

    if user is None or not check_password_hash(user.password, password):
        error = "Incorrect username or password."
        return jsonify({"error": error}), 400

    login_user(user)
    return jsonify({"status": "logged_in", "username": username})


@bp.route("/logout", methods=["POST"])
def logout():
    logout_user()
    return jsonify({"status": "logged_out"})
