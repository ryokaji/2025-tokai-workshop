import os
import traceback

from app.users import User
from flask import Blueprint, jsonify, request, session
from flask_login import login_user
from webauthn.authentication.generate_authentication_options import (
    generate_authentication_options,
)
from webauthn.authentication.verify_authentication_response import (
    verify_authentication_response,
)
from webauthn.helpers import options_to_json_dict
from webauthn.helpers.structs import (
    UserVerificationRequirement,
)

RP_ID = os.getenv("RP_ID")
EXPECTED_ORIGIN = os.getenv("EXPECTED_ORIGIN")

bp = Blueprint("auth", __name__)


# 認証オプション生成
@bp.route("/generate-authentication-options", methods=["GET"])
def authenticate_options():
    options = generate_authentication_options(
        rp_id=RP_ID,
        user_verification=UserVerificationRequirement.PREFERRED,
    )

    data = options_to_json_dict(options)
    session["challenge"] = options.challenge
    return jsonify(data)


# 認証レスポンス検証
@bp.route("/verify-authentication", methods=["POST"])
def authenticate_verify():
    body = request.json

    user = User.find_user_by_credential_id(body["id"])

    # Doesn't disclose whether user (or credential) exists for security reasons
    if not user:
        return jsonify({"error": "No credential for user with this site"}), 404

    public_key = user.get_pubkey(body["id"])

    if not public_key:
        return jsonify({"error": "No credential for user with this site"}), 404

    try:
        verification = verify_authentication_response(
            credential=body,
            expected_challenge=session.get("challenge"),
            expected_rp_id=RP_ID,
            expected_origin=EXPECTED_ORIGIN,
            credential_public_key=public_key,
            credential_current_sign_count=0,
            require_user_verification=False,
        )
        session["challenge"] = None
        session.clear()
        login_user(user)
        return jsonify({"status": "ok", "verified": verification.user_verified})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "failed", "error": str(e)}), 400
