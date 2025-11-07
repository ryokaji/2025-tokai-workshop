import os
import traceback

from app.model import User
from flask import Blueprint, jsonify, request, session
from flask_login import login_required
from webauthn.helpers import options_to_json_dict
from webauthn.registration.generate_registration_options import (
    generate_registration_options,
)
from webauthn.registration.verify_registration_response import (
    verify_registration_response,
)

RP_ID = os.getenv("RP_ID")
EXPECTED_ORIGIN = os.getenv("EXPECTED_ORIGIN")

bp = Blueprint("register", __name__)


# 登録オプション生成
@bp.route("/generate-registration-options", methods=["GET"])
@login_required
def register_options():
    user = User.get_by_id(session.get("_user_id"))

    try:
        options = generate_registration_options(
            rp_id=RP_ID,
            rp_name="Example WebAuthn",
            user_name=user.get_id(),
        )
        data = options_to_json_dict(options)

        session["challenge"] = options.challenge
        return jsonify(data)
    except Exception as e:
        print("error: with", e)
        return jsonify({"status": "failed", "error": str(e)}), 400


# 登録レスポンス検証
@bp.route("/verify-registration", methods=["POST"])
@login_required
def register_verify():
    user = User.get_by_id(session.get("_user_id"))
    body = request.json

    try:
        v = verify_registration_response(
            credential=body,
            expected_challenge=session.get("challenge"),
            expected_rp_id=RP_ID,
            expected_origin=EXPECTED_ORIGIN,
            require_user_verification=False,
        )

        user.credentials.append(
            {
                "credential_id": v.credential_id,
                "public_key": v.credential_public_key,
                "sign_count": v.sign_count,
                "transports": body.get("transports", []),
            }
        )
        user.save()
        session["challenge"] = None
        return jsonify({"status": "ok", "verified": v.user_verified})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "failed", "error": str(e)}), 400
