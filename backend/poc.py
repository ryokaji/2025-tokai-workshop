import base64
import os

from flask import Flask, jsonify, request, session
from flask_cors import CORS
from webauthn.authentication.generate_authentication_options import (
    generate_authentication_options,
)
from webauthn.authentication.verify_authentication_response import (
    verify_authentication_response,
)
from webauthn.helpers import options_to_json_dict
from webauthn.helpers.structs import (
    PublicKeyCredentialDescriptor,
    PublicKeyCredentialType,
    UserVerificationRequirement,
)
from webauthn.registration.generate_registration_options import (
    generate_registration_options,
)
from webauthn.registration.verify_registration_response import (
    verify_registration_response,
)

RP_ID = os.getenv("RP_ID")
EXPECTED_ORIGIN = os.getenv("EXPECTED_ORIGIN")

app = Flask(__name__, template_folder=".")
app.secret_key = os.urandom(24)
CORS(app, supports_credentials=True)

# サンプル: メモリ上でユーザー・認証情報を保持
users = {
    "loggedInUserId": {
        "id": "internalUserId",
        "username": "user@localhost",
        "credentials": [],
    }
}


# 登録オプション生成
@app.route("/generate-registration-options", methods=["GET"])
def register_options():
    _, username, _credentials = users["loggedInUserId"]
    try:
        options = generate_registration_options(
            rp_id=RP_ID,
            rp_name="Example WebAuthn",
            user_name=username,
        )
        data = options_to_json_dict(options)

        session["challenge"] = options.challenge
        return jsonify(data)
    except Exception as e:
        print("error: with", e)
        return jsonify({"status": "failed", "error": str(e)}), 400


# 登録レスポンス検証
@app.route("/verify-registration", methods=["POST"])
def register_verify():
    user = users["loggedInUserId"]
    credential = request.json

    expected_challenge = None

    if "challenge" in session:
        expected_challenge = session.get("challenge")

    try:
        verification = verify_registration_response(
            credential=credential,
            expected_challenge=expected_challenge,
            expected_rp_id=RP_ID,
            expected_origin=EXPECTED_ORIGIN,
            require_user_verification=False,
        )
        verified = verification.user_verified

        existingCredential = verification.credential_id in user["credentials"]
        if not existingCredential:
            user["credentials"].append(
                {
                    "credential_id": verification.credential_id,
                    "public_key": verification.credential_public_key,
                    "sign_count": verification.sign_count,
                    "transports": credential.get("transports", []),
                }
            )

        session["challenge"] = None
        return jsonify({"status": "ok", "verified": verified})
    except Exception as e:
        return jsonify({"status": "failed", "error": str(e)}), 400


# 認証オプション生成
@app.route("/generate-authentication-options", methods=["GET"])
def authenticate_options():
    user = users["loggedInUserId"]

    if not user:
        return jsonify({"error": "User not found"}), 404

    options = generate_authentication_options(
        rp_id=RP_ID,
        user_verification=UserVerificationRequirement.PREFERRED,
        allow_credentials=[
            PublicKeyCredentialDescriptor(
                id=cred["credential_id"],
                transports=cred.get("transports", []),
                type=PublicKeyCredentialType.PUBLIC_KEY,
            )
            for cred in user["credentials"]
        ],
    )

    data = options_to_json_dict(options)
    session["challenge"] = options.challenge
    return jsonify(data)


# 認証レスポンス検証
@app.route("/verify-authentication", methods=["POST"])
def authenticate_verify():
    user = users["loggedInUserId"]
    credential = request.json

    dbCredential = None
    for cred in user["credentials"]:
        # stored user credential_id is bytes
        # treats credential_id to utf-8 str for comparison
        decoded_cred_id = (
            base64.urlsafe_b64encode(cred["credential_id"]).rstrip(b"=").decode("utf-8")
        )
        if decoded_cred_id == credential["id"]:
            dbCredential = cred
            break

    if not dbCredential:
        return jsonify({"error": "Authenticator is not registered with this site"}), 400

    expected_challenge = None
    if "challenge" in session:
        expected_challenge = session.get("challenge")

    public_key = dbCredential.get("public_key")
    if not public_key:
        return jsonify({"error": "No credential for user"}), 404

    try:
        verification = verify_authentication_response(
            credential=credential,
            expected_challenge=expected_challenge,
            expected_rp_id=RP_ID,
            expected_origin=EXPECTED_ORIGIN,
            credential_public_key=public_key,
            credential_current_sign_count=0,
            require_user_verification=False,
        )
        session["challenge"] = None
        return jsonify({"status": "ok", "verified": verification.user_verified})
    except Exception as e:
        return jsonify({"status": "failed", "error": str(e)}), 400


if __name__ == "__main__":
    app.run(port=8000, debug=True)
