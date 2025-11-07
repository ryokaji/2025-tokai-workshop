# User class for flask_login
from base64 import urlsafe_b64decode

from app.db import save_userdb, userdb
from flask_login import UserMixin


def _decode_public_key(pubkey_str: str) -> bytes:
    padding = "=" * (-len(pubkey_str) % 4)
    return urlsafe_b64decode((pubkey_str + padding))


# User class for flask_login
class User(UserMixin):
    def __init__(self, username, password, credentials=None):
        self.id = username
        self.password = password
        self.credentials = credentials or []

    def get_id(self):
        return self.id

    def save(self):
        # Insert
        userdb[self.id] = {
            "password": self.password,
            "credentials": self.credentials,
        }

        save_userdb()

    def get_pubkey(self, credential_id):
        for cred in self.credentials:
            if cred["credential_id"] == credential_id:
                return _decode_public_key(cred["public_key"])
        return None

    @staticmethod
    def get_by_id(user_id):
        user = userdb.get(user_id)
        if user:
            return User(user_id, user["password"], user["credentials"])
        return None

    # SELECT credential.credential_id FROM user
    # INNER JOIN credential ON user.id = credential.user_id
    # find the user who has
    #   1. credentials related to the user are not empty
    #   2. at least 1 credential, credential_id matches request body's id (credential id)
    @staticmethod
    def find_user_by_credential_id(credential_id):
        for user_id, user in userdb.items():
            for cred in user.get("credentials", []):
                if cred["credential_id"] == credential_id:
                    return User(user_id, user["password"], user["credentials"])
