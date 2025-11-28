"""
BC-Lite Licensing Module

Supports:
- Trial mode (time-limited, based on first-run timestamp)
- Machine-locked license file (offline)
- Simple HMAC-based signature check (replace with real signing in production)

This is intentionally lightweight and self-contained. For serious commercial use,
replace HMAC verification with a proper asymmetric signature check and move secrets
out of the client binary.
"""
import os
import json
import hmac
import hashlib
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

# NOTE: CHANGE THIS SECRET FOR REAL PRODUCT USE.
# Ideally, you replace HMAC with asymmetric crypto and keep private key off client.
_LICENSE_SECRET = b"CHANGE_ME_TO_A_SECURE_RANDOM_SECRET"

CONFIG_DIR = Path(os.getenv("BC_LITE_CONFIG_DIR") or (Path.home() / ".bc-lite"))
LICENSE_PATH = CONFIG_DIR / "license.json"
TRIAL_FILE = CONFIG_DIR / "trial.json"

TRIAL_DAYS = 14

@dataclass
class LicenseInfo:
    name: str
    email: str
    edition: str            # "pro" expected for BC-Lite Pro
    machine_id: str
    expires_at: str         # ISO8601 date string, e.g. "2026-01-01"
    signature: str          # hex HMAC-SHA256 over payload

def _machine_id() -> str:
    """
    Compute a simple machine identifier.

    This is *not* cryptographically strong and can be spoofed,
    but is enough for basic machine-lock behavior.
    """
    import platform
    import uuid
    node = platform.node()
    mac = uuid.getnode()
    return f"{node}-{mac:x}"

def _sign_payload(payload: dict) -> str:
    msg = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hmac.new(_LICENSE_SECRET, msg, hashlib.sha256).hexdigest()

def _verify_signature(lic: LicenseInfo) -> bool:
    payload = {
        "name": lic.name,
        "email": lic.email,
        "edition": lic.edition,
        "machine_id": lic.machine_id,
        "expires_at": lic.expires_at,
    }
    expected = _sign_payload(payload)
    try:
        return hmac.compare_digest(expected, lic.signature)
    except Exception:
        return False

def _load_license() -> Optional[LicenseInfo]:
    try:
        raw = json.loads(LICENSE_PATH.read_text(encoding="utf-8"))
        return LicenseInfo(**raw)
    except Exception:
        return None

def _parse_date(s: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None

def _load_trial_info() -> dict:
    try:
        return json.loads(TRIAL_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _save_trial_info(info: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    TRIAL_FILE.write_text(json.dumps(info, indent=2), encoding="utf-8")

def get_trial_status() -> tuple[bool, int]:
    """
    Returns (trial_active, days_left).

    - If first run, initializes trial file.
    - If expired, returns (False, 0).
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    info = _load_trial_info()
    if "started_at" not in info:
        now = datetime.utcnow()
        info["started_at"] = now.isoformat()
        _save_trial_info(info)
        return True, TRIAL_DAYS

    started = _parse_date(info.get("started_at", ""))
    if not started:
        # corrupt, reset trial (or treat as expired depending on policy)
        now = datetime.utcnow()
        info["started_at"] = now.isoformat()
        _save_trial_info(info)
        return True, TRIAL_DAYS

    now = datetime.utcnow()
    days_used = (now - started).days
    days_left = TRIAL_DAYS - days_used
    if days_left <= 0:
        return False, 0
    return True, days_left

def check_license(edition_required: str = "pro") -> tuple[bool, str]:
    """
    Check if a valid license exists for the requested edition.

    Returns (ok, message). If ok is False, message describes the failure.
    """
    lic = _load_license()
    if not lic:
        trial_ok, days_left = get_trial_status()
        if trial_ok:
            return True, f"Trial mode active, {days_left} day(s) left."
        return False, "No license found and trial period expired."

    if lic.edition.lower() != edition_required.lower():
        return False, f"License edition mismatch: expected {edition_required}, got {lic.edition}"

    if lic.machine_id != _machine_id():
        return False, "License is bound to another machine."

    if not _verify_signature(lic):
        return False, "License signature invalid."

    exp = _parse_date(lic.expires_at)
    if not exp:
        return False, "License expiry date invalid."
    if datetime.utcnow() > exp:
        return False, "License has expired."

    return True, "Valid license."

def generate_license_template(name: str, email: str, edition: str = "pro",
                              days_valid: int = 365) -> dict:
    """
    Helper for the *vendor side* (not normally shipped to client).

    Given user info and desired validity duration, returns a dict that can be
    exported as license.json, including HMAC-based signature.

    You should run this on a secure machine and not ship this function in production.
    """
    payload = {
        "name": name,
        "email": email,
        "edition": edition,
        "machine_id": _machine_id(),  # call on user machine or override with known value
        "expires_at": (datetime.utcnow() + timedelta(days=days_valid)).isoformat(),
    }
    payload["signature"] = _sign_payload(payload)
    return payload
