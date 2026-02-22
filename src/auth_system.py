import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

ROLES = {"Admin", "Coordinator", "Technician"}


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def hash_password(password: str, salt: Optional[bytes] = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return f"{_b64url_encode(salt)}:{_b64url_encode(digest)}"


def verify_password(password: str, stored: str) -> bool:
    salt_b64, digest_b64 = stored.split(":")
    expected = hash_password(password, _b64url_decode(salt_b64)).split(":")[1]
    return hmac.compare_digest(digest_b64, expected)


@dataclass
class User:
    username: str
    role: str
    password_hash: str
    must_change_password: bool = False


@dataclass
class ResetToken:
    username: str
    expires_at: int


@dataclass
class UserStore:
    users: Dict[str, User] = field(default_factory=dict)
    reset_tokens: Dict[str, ResetToken] = field(default_factory=dict)

    def add_user(self, username: str, role: str, password: str, must_change_password: bool = False) -> User:
        if role not in ROLES:
            raise ValueError("Invalid role")
        if username in self.users:
            raise ValueError("Username already exists")
        user = User(username=username, role=role, password_hash=hash_password(password), must_change_password=must_change_password)
        self.users[username] = user
        return user


class AuthManager:
    def __init__(self, store: UserStore, jwt_secret: Optional[str] = None, issuer: str = "maxdax-fsm"):
        self.store = store
        self.jwt_secret = (jwt_secret or os.environ.get("JWT_SECRET") or secrets.token_urlsafe(32)).encode("utf-8")
        self.issuer = issuer

    def _sign(self, message: bytes) -> str:
        return _b64url_encode(hmac.new(self.jwt_secret, message, hashlib.sha256).digest())

    def create_jwt(self, username: str, role: str, ttl_seconds: int = 3600) -> str:
        header = {"alg": "HS256", "typ": "JWT"}
        now = int(time.time())
        payload = {
            "sub": username,
            "role": role,
            "iat": now,
            "exp": now + ttl_seconds,
            "iss": self.issuer,
        }
        encoded_header = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
        encoded_payload = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
        signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
        signature = self._sign(signing_input)
        return f"{encoded_header}.{encoded_payload}.{signature}"

    def verify_jwt(self, token: str) -> Dict:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid token format")
        encoded_header, encoded_payload, provided_signature = parts
        signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
        expected_signature = self._sign(signing_input)
        if not hmac.compare_digest(provided_signature, expected_signature):
            raise ValueError("Invalid token signature")
        payload = json.loads(_b64url_decode(encoded_payload))
        now = int(time.time())
        if payload.get("iss") != self.issuer:
            raise ValueError("Invalid issuer")
        if payload.get("exp", 0) < now:
            raise ValueError("Token expired")
        if payload.get("role") not in ROLES:
            raise ValueError("Invalid role")
        return payload

    def login(self, username: str, password: str) -> Dict:
        user = self.store.users.get(username)
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")
        return {
            "access_token": self.create_jwt(user.username, user.role),
            "token_type": "Bearer",
            "role": user.role,
            "must_change_password": user.must_change_password,
        }

    def create_technician(self, creator_role: str, username: str) -> Dict:
        if creator_role != "Admin":
            raise PermissionError("Only Admin can create technicians")
        temp_password = secrets.token_urlsafe(12)
        self.store.add_user(username, "Technician", temp_password, must_change_password=True)
        return {"username": username, "temp_password": temp_password, "role": "Technician"}

    def request_password_reset(self, username: str, ttl_seconds: int = 900) -> str:
        if username not in self.store.users:
            raise ValueError("User not found")
        token = secrets.token_urlsafe(24)
        self.store.reset_tokens[token] = ResetToken(username=username, expires_at=int(time.time()) + ttl_seconds)
        return token

    def confirm_password_reset(self, token: str, new_password: str) -> None:
        reset = self.store.reset_tokens.get(token)
        if not reset:
            raise ValueError("Invalid reset token")
        if reset.expires_at < int(time.time()):
            del self.store.reset_tokens[token]
            raise ValueError("Reset token expired")
        user = self.store.users[reset.username]
        user.password_hash = hash_password(new_password)
        user.must_change_password = False
        del self.store.reset_tokens[token]


def require_roles(payload: Dict, allowed_roles: List[str]) -> None:
    role = payload.get("role")
    if role not in allowed_roles:
        raise PermissionError("Insufficient permissions")


def bootstrap_default_store() -> Tuple[UserStore, AuthManager]:
    store = UserStore()
    store.add_user("admin", "Admin", "admin123")
    store.add_user("coordinator", "Coordinator", "coord123")
    auth = AuthManager(store)
    return store, auth
