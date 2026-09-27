"""
Saha İçi - Kimlik Doğrulama & Oturum Yönetimi (Auth Engine)
Telefondan ve bilgisayardan şifreli güvenli erişim sağlar.
"""
import os
import json
import time
import secrets
import hashlib
from typing import Optional, Dict

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "auth_config.json")
DEFAULT_PASSWORD = os.environ.get("APP_PASSWORD", "227546")
SESSION_EXPIRE_SECONDS = 30 * 24 * 3600  # 30 gün geçerli


def _hash_password(pw: str, salt: str = None) -> str:
    if not salt:
        salt = secrets.token_hex(8)
    h = hashlib.sha256((salt + pw).encode("utf-8")).hexdigest()
    return f"{salt}:{h}"


def _verify_password_hash(pw: str, stored_hash: str) -> bool:
    try:
        salt, expected_h = stored_hash.split(":")
        calc_h = hashlib.sha256((salt + pw).encode("utf-8")).hexdigest()
        return secrets.compare_digest(calc_h, expected_h)
    except Exception:
        return False


def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[AUTH LOAD ERROR] {e}")

    # Varsayılan konfigürasyon (Varsayılan şifre: 1234)
    default_cfg = {
        "password_hash": _hash_password(DEFAULT_PASSWORD),
        "sessions": {},
        "created_at": time.time(),
        "password_hint": "Varsayılan: 1234"
    }
    save_config(default_cfg)
    return default_cfg


def save_config(cfg: dict):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[AUTH SAVE ERROR] {e}")


def verify_password(password: str) -> bool:
    cfg = load_config()
    stored = cfg.get("password_hash")
    if not stored:
        return True
    return _verify_password_hash(password, stored)


def create_session() -> str:
    cfg = load_config()
    token = secrets.token_urlsafe(32)
    now = time.time()
    
    # Eski/süresi dolmuş oturumları temizle
    sessions = cfg.get("sessions", {})
    cleaned = {
        tok: data for tok, data in sessions.items()
        if data.get("expires_at", 0) > now
    }
    
    cleaned[token] = {
        "created_at": now,
        "expires_at": now + SESSION_EXPIRE_SECONDS
    }
    cfg["sessions"] = cleaned
    save_config(cfg)
    return token


def validate_token(token: str) -> bool:
    if not token:
        return False
    cfg = load_config()
    sessions = cfg.get("sessions", {})
    sess_data = sessions.get(token)
    if not sess_data:
        return False
    
    now = time.time()
    if sess_data.get("expires_at", 0) < now:
        try:
            del sessions[token]
            cfg["sessions"] = sessions
            save_config(cfg)
        except Exception:
            pass
        return False
        
    return True


def revoke_session(token: str) -> bool:
    if not token:
        return False
    cfg = load_config()
    sessions = cfg.get("sessions", {})
    if token in sessions:
        del sessions[token]
        cfg["sessions"] = sessions
        save_config(cfg)
        return True
    return False


def change_password(old_pw: str, new_pw: str):
    if not new_pw or len(new_pw) < 3:
        return False, "Yeni şifre en az 3 karakter olmalıdır."
    
    cfg = load_config()
    stored = cfg.get("password_hash")
    if stored and not _verify_password_hash(old_pw, stored):
        return False, "Mevcut şifre hatalı."
    
    cfg["password_hash"] = _hash_password(new_pw)
    cfg["password_hint"] = "Kullanıcı tarafından değiştirildi"
    cfg["sessions"] = {}
    save_config(cfg)
    return True, "Şifre başarıyla güncellendi."
