"""
JWT — JSON Web Token Implementation
=====================================
Implements HS256 (HMAC-SHA256) signed tokens using only Python stdlib.

Why stdlib instead of PyJWT?
    PyJWT is an excellent library and should be used when available.
    This implementation exists for environments where package installation
    is restricted. The public interface (create_access_token, decode_access_token)
    is designed to match PyJWT's API so the swap is a one-file change:

        # To switch to PyJWT:
        import jwt
        def create_access_token(user_id, email):
            return jwt.encode({...}, settings.SECRET_KEY, algorithm="HS256")
        def decode_access_token(token):
            return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

Token structure (standard JWT):
    Header:    {"alg": "HS256", "typ": "JWT"}
    Payload:   {"sub": user_id, "email": email, "iat": timestamp, "exp": timestamp}
    Signature: HMAC-SHA256(base64url(header) + "." + base64url(payload), SECRET_KEY)
    Token:     base64url(header).base64url(payload).base64url(signature)

Security:
    - Constant-time signature comparison via hashlib.compare_digest
    - Expiry enforced on every decode
    - Any tampering with header or payload invalidates the signature
"""

import base64
import hashlib
import hmac
import json
import time
from typing import Any

from config import settings
from domain.exceptions import AuthenticationError


# ── Internal helpers ──────────────────────────────────────────────────────────


def _b64url_encode(data: bytes) -> str:
    """Base64-URL encode without padding (JWT spec)."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(s: str) -> bytes:
    """Base64-URL decode, re-adding stripped padding."""
    remainder = len(s) % 4
    if remainder:
        s += "=" * (4 - remainder)
    return base64.urlsafe_b64decode(s)


def _sign(header_b64: str, payload_b64: str) -> str:
    """Compute HMAC-SHA256 signature over header.payload."""
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    signature_bytes = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()
    return _b64url_encode(signature_bytes)


# ── Public API ────────────────────────────────────────────────────────────────


def create_access_token(user_id: str, email: str) -> str:
    """
    Create a signed JWT access token for the given user.

    The token is valid for settings.ACCESS_TOKEN_EXPIRE_MINUTES minutes.

    Claims:
        sub   — subject (user UUID as string)
        email — user's email address
        iat   — issued-at timestamp (Unix time)
        exp   — expiry timestamp (Unix time)
    """
    header = _b64url_encode(
        json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode()
    )
    payload = _b64url_encode(
        json.dumps(
            {
                "sub": user_id,
                "email": email,
                "iat": int(time.time()),
                "exp": int(time.time()) + settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            },
            separators=(",", ":"),
        ).encode()
    )
    signature = _sign(header, payload)
    return f"{header}.{payload}.{signature}"


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Validate and decode a JWT access token.

    Returns the payload dict if the token is valid.

    Raises:
        AuthenticationError: if the token format is wrong, the signature
                             does not match (tampering), or the token has expired.

    Why three separate error cases but one exception type?
        From the caller's perspective (the auth dependency), any of these
        conditions means "the request is unauthenticated." A single HTTP 401
        is the correct response for all three. Leaking which check failed
        would give an attacker information about the token structure.
    """
    try:
        parts = token.strip().split(".")
        if len(parts) != 3:
            raise AuthenticationError("Invalid token format.")

        header_b64, payload_b64, sig_b64 = parts

        # ── Step 1: verify signature BEFORE decoding payload ────────────────
        # If we decoded the payload first and then failed the signature check,
        # an attacker could craft payloads that trigger different code paths.
        # Always verify the signature first.
        expected_sig = _sign(header_b64, payload_b64)
        actual_sig = _b64url_decode(sig_b64)
        expected_sig_bytes = _b64url_decode(expected_sig)

        if not hmac.compare_digest(expected_sig_bytes, actual_sig):
            # Deliberately vague — do not reveal whether it was the header,
            # payload, or signature that was wrong.
            raise AuthenticationError("Token is invalid.")

        # ── Step 2: decode payload ───────────────────────────────────────────
        payload: dict = json.loads(_b64url_decode(payload_b64))

        # ── Step 3: check expiry ─────────────────────────────────────────────
        exp = payload.get("exp", 0)
        if exp < time.time():
            raise AuthenticationError(
                "Your session has expired. Please log in again."
            )

        return payload

    except AuthenticationError:
        raise  # re-raise domain errors unchanged
    except Exception:
        # Catch-all for malformed base64, invalid JSON, etc.
        # Never expose the internal error — it reveals token structure.
        raise AuthenticationError("Token is invalid.")
