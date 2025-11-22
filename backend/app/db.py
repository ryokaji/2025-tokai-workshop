import json
import os
from typing import Dict, Optional

from app.model import Credential, CredentialRecord, UserRecord

USERDB_FILE = "userdb.json"


def load_userdb() -> Dict[str, UserRecord]:
    if not os.path.exists(USERDB_FILE):
        return {}

    with open(USERDB_FILE, "r") as f:
        content: dict[str, UserRecord] = json.load(f)
        return content


# Add a new user to userdb
# Assuming this is called by the endpoint creates a user
def append_user(user_id: str, password: str) -> None:
    if user_id in userdb:
        raise ValueError(f"user '{user_id}' already exists")
    # credentials is initialized as an empty list, not None
    userdb[user_id] = UserRecord(password=password, credentials=[])
    save_userdb()


# Add a given credential to the user's credentials list
# Assuming this is called by the endpoint verifies a response in the passkey registration
def update_user_credentials(user_id: str, credential: Credential) -> None:
    user = userdb.get(user_id)
    if not user:
        raise KeyError(f"user '{user_id}' not found")

    # Convert a credential object as a record type defined in this file.
    # `Credential` dataclass type is incompatible with `CredentialRecord` type directly.
    cred_dict = credential.to_dict()
    user["credentials"].append(
        CredentialRecord(
            credential_id=cred_dict["credential_id"],
            public_key=cred_dict["public_key"],
            sign_count=cred_dict["sign_count"],
            transports=cred_dict.get("transports", []),
        )
    )
    save_userdb()


# Return decoded public_key corresponding to the given credential_id
def find_decoded_public_key(user_id: str, credential_id: str) -> Optional[bytes]:
    user = userdb.get(user_id)

    if not user:
        return None

    for cred in user["credentials"]:
        if cred["credential_id"] == credential_id:
            # Return the value via converting dataclass for implementation reasons
            return Credential.from_dict(cred).public_key

    # no necessary, but for evasion of "no return" linter warning
    return None


# Persist userdb to USERDB_FILE.
# The process of converting data into a dict type in order to dump it
# is delegated to the UserRecord type as its responsibility.
def save_userdb() -> None:
    # This is not necessary if we operate the userdb directly,
    # but for implementation reasons this object is temporarily defined.
    formatted_userdb: Dict[str, UserRecord] = {}

    for user_id, user in userdb.items():
        formatted_userdb[user_id] = UserRecord(
            password=user["password"],
            credentials=user["credentials"],
        )

    with open(USERDB_FILE, "w") as f:
        json.dump(formatted_userdb, f, indent=2)


userdb: Dict[str, UserRecord] = load_userdb()
