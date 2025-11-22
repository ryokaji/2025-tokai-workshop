from base64 import urlsafe_b64decode, urlsafe_b64encode
from dataclasses import dataclass
from typing import List, Optional, TypedDict


class CredentialRecord(TypedDict):
    credential_id: str
    public_key: str
    sign_count: int
    transports: List[str]


class UserRecord(TypedDict):
    password: str
    credentials: List[CredentialRecord]


@dataclass
class Credential:
    credential_id: bytes
    public_key: bytes
    sign_count: int
    transports: Optional[List[str]]

    def to_dict(self) -> dict:
        """Return a JSON-serializable dict; bytes fields are urlsafe-base64 encoded w/o padding."""

        def _b64_no_pad(b: bytes) -> str:
            return urlsafe_b64encode(b).rstrip(b"=").decode("ascii")

        return {
            "credential_id": _b64_no_pad(self.credential_id),
            "public_key": _b64_no_pad(self.public_key),
            "sign_count": self.sign_count,
            "transports": self.transports,
        }

    @staticmethod
    def from_dict(d: CredentialRecord) -> "Credential":
        """Create a Credential from a dict (assuming produced by to_dict)."""

        def _decode_b64(s: str) -> bytes:
            s_p = s + "=" * (-len(s) % 4)
            return urlsafe_b64decode(s_p)

        return Credential(
            credential_id=_decode_b64(d["credential_id"]),
            public_key=_decode_b64(d["public_key"]),
            sign_count=int(d["sign_count"]),
            transports=d.get("transports"),
        )
