# python
import json
from base64 import urlsafe_b64encode

import app.db as db
from app.db import Credential, CredentialRecord, UserRecord
from app.users import User


def test_credential_to_dict_and_from_dict():
    cred_id = b"\x01\x02\xff"
    pub = b"\x05\x06"
    cred = Credential(
        credential_id=cred_id, public_key=pub, sign_count=7, transports=["usb"]
    )
    d = cred.to_dict()

    expected_id = urlsafe_b64encode(cred_id).rstrip(b"=").decode("ascii")
    expected_pub = urlsafe_b64encode(pub).rstrip(b"=").decode("ascii")

    assert d["credential_id"] == expected_id
    assert d["public_key"] == expected_pub
    assert d["sign_count"] == 7
    assert d["transports"] == ["usb"]

    # from_dict should handle padded decoding and string sign_count
    d_input = {
        "credential_id": expected_id,
        "public_key": expected_pub,
        "sign_count": "7",
        "transports": ["usb"],
    }
    cred2 = Credential.from_dict(d_input)
    assert cred2.credential_id == cred_id
    assert cred2.public_key == pub
    assert cred2.sign_count == 7
    assert cred2.transports == ["usb"]


def test_user_get_pubkey_bytes_and_b64string():
    cred_id = b"\x10\x20"
    pub = b"public-bytes"
    cred = Credential(
        credential_id=cred_id, public_key=pub, sign_count=0, transports=None
    )
    user = User("bob", "pw", [cred])

    # bytes input
    assert user.get_pubkey(cred_id) == pub

    # base64 (no padding) string input
    b64id = urlsafe_b64encode(cred_id).rstrip(b"=").decode("ascii")
    assert user.get_pubkey(b64id) == pub

    # unknown id returns None
    assert user.get_pubkey(b"\x00\x00\x00") is None


def test_user_save_updates_userdb_and_calls_save_userdb(monkeypatch):
    # Inject a fresh userdb and a fake save_userdb
    db.userdb = {}
    called = {"v": False}

    def fake_save_userdb():
        called["v"] = True

    db.save_userdb = fake_save_userdb

    u = User("charlie", "secret", [])
    u.create()

    assert "charlie" in db.userdb
    entry = db.userdb["charlie"]
    assert entry["password"] == "secret"
    # credentials stored as provided (empty list)
    assert entry["credentials"] == []
    assert called["v"] is True


def test_get_by_id_and_find_user_by_credential_id():
    # Prepare userdb where credentials are stored as dicts (persisted form)
    db.userdb = {
        "u1": UserRecord(
            {
                "username": "u1",
                "password": "p1",
                "credentials": [
                    CredentialRecord(
                        credential_id="AAA",
                        public_key="BBB",
                        sign_count=0,
                        transports=[],
                    ),
                ],
            }
        ),
        "u2": UserRecord(
            {
                "username": "u2",
                "password": "p2",
                "credentials": [],
            }
        ),
    }
    user = User.get_by_id("u1")
    assert user is not None
    assert isinstance(user, User)
    assert user.id == "u1"
    assert user.password == "p1"
    # get_by_id returns the raw credentials value stored in userdb
    for user_cred, db_cred in zip(user.credentials, db.userdb["u1"]["credentials"]):
        assert user_cred == Credential.from_dict(db_cred)

    # find_user_by_credential_id should find u1 by matching credential_id string
    found = User.find_user_by_credential_id("AAA")
    assert found is not None
    assert found.id == "u1"
    assert found.password == "p1"

    # non-existing credential id returns None
    assert User.find_user_by_credential_id("NON-EXISTENT") is None


def test_save_userdb_encodes_bytes_and_writes_file(tmp_path, monkeypatch) -> None:
    out_file = tmp_path / "userdb.json"
    monkeypatch.setattr(db, "USERDB_FILE", str(out_file))

    cred_id = b"\x01\x02"
    pub = b"\x03\x04"
    expected_id = urlsafe_b64encode(cred_id).rstrip(b"=").decode("utf-8")
    expected_pub = urlsafe_b64encode(pub).rstrip(b"=").decode("utf-8")

    cred = db.CredentialRecord(
        {
            "credential_id": expected_id,
            "public_key": expected_pub,
            "sign_count": 5,
            "transports": ["usb"],
        }
    )
    db.userdb = {
        "alice": UserRecord(
            {
                "password": "pw",
                "credentials": [cred],
            }
        ),
    }

    db.save_userdb()

    with open(out_file, "r") as f:
        data = json.load(f)

    assert "alice" in data
    entry = data["alice"]
    assert entry["password"] == "pw"
    assert isinstance(entry["credentials"], list)
    saved_cred = entry["credentials"][0]
    assert saved_cred["credential_id"] == expected_id
    assert saved_cred["public_key"] == expected_pub
    assert saved_cred["sign_count"] == 5
    assert saved_cred["transports"] == ["usb"]


def test_save_userdb_includes_empty_credentials(tmp_path, monkeypatch):
    out_file = tmp_path / "userdb.json"
    monkeypatch.setattr(db, "USERDB_FILE", str(out_file))

    db.userdb = {
        "bob": UserRecord({"password": "p", "credentials": []}),
    }

    db.save_userdb()

    with open(out_file, "r") as f:
        data = json.load(f)

    assert "bob" in data
    assert data["bob"]["password"] == "p"
    # 空の credentials は [] として出力されること
    assert data["bob"]["credentials"] == []


def test_load_userdb_returns_empty_when_file_missing(tmp_path, monkeypatch):
    # Point USERDB_FILE to a non-existent file
    missing = tmp_path / "no_such_userdb.json"
    monkeypatch.setattr(db, "USERDB_FILE", str(missing))

    # Ensure file does not exist
    if missing.exists():
        missing.unlink()

    loaded = db.load_userdb()
    assert isinstance(loaded, dict)
    assert loaded == {}


def test_save_userdb_and_load_userdb_roundtrip(tmp_path, monkeypatch):
    # Prepare a temp file for USERDB_FILE
    out_file = tmp_path / "userdb.json"
    monkeypatch.setattr(db, "USERDB_FILE", str(out_file))

    # Prepare a user record as it would be persisted
    credential_id = "AAA"
    public_key = "BBB"
    cred_record = db.CredentialRecord(
        {
            "credential_id": credential_id,
            "public_key": public_key,
            "sign_count": 5,
            "transports": ["usb"],
        }
    )
    original_userdb = {
        "alice": db.UserRecord({"password": "pw", "credentials": [cred_record]})
    }

    # Inject into in-memory userdb and save to file
    db.userdb = original_userdb.copy()
    db.save_userdb()

    # Read file directly to assert it was written (sanity)
    with open(out_file, "r") as f:
        raw = json.load(f)
    assert "alice" in raw
    assert raw["alice"]["password"] == "pw"
    assert isinstance(raw["alice"]["credentials"], list)
    saved_cred = raw["alice"]["credentials"][0]
    assert saved_cred["credential_id"] == credential_id
    assert saved_cred["public_key"] == public_key
    assert saved_cred["sign_count"] == 5
    assert saved_cred["transports"] == ["usb"]

    # Clear in-memory userdb and load from file
    db.userdb = {}
    loaded = db.load_userdb()

    # Expect loaded to contain the same persisted structure
    assert "alice" in loaded
    entry = loaded["alice"]
    assert entry["password"] == "pw"
    assert isinstance(entry["credentials"], list)
    loaded_cred = entry["credentials"][0]
    assert loaded_cred["credential_id"] == credential_id
    assert loaded_cred["public_key"] == public_key
    assert int(loaded_cred["sign_count"]) == 5
    assert loaded_cred.get("transports") == ["usb"]
