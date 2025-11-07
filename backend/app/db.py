import base64
import json
import os


def _decode_cred_key(cred, key):
    val = cred.get(key)
    if not val:
        return
    try:
        out = base64.b64decode(val).decode("utf-8")
        cred[key] = out
        return out
    except Exception:
        pass


def _encode_cred_key(cred, key):
    val = cred.get(key)
    if not val:
        return
    if isinstance(val, bytes):
        val = base64.urlsafe_b64encode(val).rstrip(b"=").decode("utf-8")
    else:
        val = base64.b64encode(str(val).encode("utf-8")).decode("utf-8")
    cred[key] = val
    return val


def load_userdb():
    if not os.path.exists(USERDB_FILE):
        return {}

    with open(USERDB_FILE, "r") as f:
        userdb = json.load(f)
        for user in userdb.values():
            creds = user.get("credentials")
            if not creds:
                continue

            _creds = []
            for cred in creds:
                _creds.append(
                    {
                        "credential_id": _decode_cred_key(cred, "credential_id"),
                        "public_key": _decode_cred_key(cred, "public_key"),
                        "sign_count": cred["sign_count"],
                        "transports": cred.get("transports", []),
                    }
                )
        return userdb


def save_userdb():
    # credentialsのbase64 encode
    import copy

    userdb_copy = copy.deepcopy(userdb)

    for user_id, user in userdb_copy.items():
        creds = user.get("credentials")
        if not creds:
            continue

        _creds = []
        for cred in creds:
            _creds.append(
                {
                    "credential_id": _encode_cred_key(cred, "credential_id"),
                    "public_key": _encode_cred_key(cred, "public_key"),
                    "sign_count": cred["sign_count"],
                    "transports": cred.get("transports", []),
                }
            )

        userdb_copy[user_id]["credentials"] = _creds
        userdb_copy[user_id]["password"] = user["password"]

    with open(USERDB_FILE, "w") as f:
        json.dump(userdb_copy, f, indent=2)


USERDB_FILE = "userdb.json"
userdb = load_userdb()
