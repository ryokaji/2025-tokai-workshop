from typing import List, Optional

import app.db as db
from flask import Blueprint, jsonify, request, session
from flask_login import UserMixin, login_required
from werkzeug.security import generate_password_hash

bp = Blueprint("user", __name__)


# User class for flask_login
class User(UserMixin):
    id: str
    password: str
    credentials: List[db.Credential]

    def __init__(
        self,
        username: str,
        password: str,
        credentials: Optional[List[db.Credential]] = None,
    ):
        self.id = username
        self.password = password
        self.credentials = credentials or []

    def get_id(self):
        return self.id

    # Create a new user as a record in userdb
    def create(self):
        db.append_user(user_id=self.id, password=self.password)

    def update_credential(self, credential: db.Credential):
        db.update_user_credentials(user_id=self.id, credential=credential)

    # Return public_key corresponding to the given credential_id
    def get_pubkey(self, credential_id: bytes | str) -> Optional[bytes]:
        if isinstance(credential_id, str):
            return db.find_decoded_public_key(self.id, credential_id)

        if isinstance(credential_id, bytes):
            for cred in self.credentials:
                if cred.credential_id == credential_id:
                    return cred.public_key
        return None

    @staticmethod
    def get_by_id(user_id: str) -> Optional["User"]:
        user = db.userdb.get(user_id)
        if user:
            return User(
                user_id,
                user["password"],
                [db.Credential.from_dict(cred) for cred in user["credentials"]],
            )
        return None

    # SELECT credential.credential_id FROM user
    # INNER JOIN credential ON user.id = credential.user_id
    # find the user who has
    #   1. credentials related to the user are not empty
    #   2. at least 1 credential, credential_id matches request body's id (credential_id)
    @staticmethod
    def find_user_by_credential_id(credential_id: bytes | str) -> Optional["User"]:
        for user_id, user in db.userdb.items():
            for cred in user.get("credentials", []):
                if cred["credential_id"] == credential_id:
                    return User(
                        user_id,
                        user["password"],
                        [db.Credential.from_dict(cred) for cred in user["credentials"]],
                    )
        return None


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
    user.create()

    return jsonify({"status": "created", "username": username})


@bp.route("/users/me", methods=["GET"])
@login_required
def get_me():
    user = User.get_by_id(session.get("_user_id"))
    if not user:
        return jsonify({"error": "user not found"}), 404

    return jsonify({"username": user.id})
