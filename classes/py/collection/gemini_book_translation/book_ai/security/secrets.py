import os
import re
import json
from pathlib import Path
from typing import Optional, Dict
from cryptography.fernet import Fernet
from book_ai.config import SECRETS_DIR

KEY_FILE = SECRETS_DIR / ".master.key"
VAULT_FILE = SECRETS_DIR / "secrets.enc"

ENV_MAP = {
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "custom": "CUSTOM_API_KEY",
}

class SecretManager:
    def __init__(self):
        self._fernet = self._init_fernet()

    def _init_fernet(self) -> Fernet:
        if not KEY_FILE.exists():
            key = Fernet.generate_key()
            KEY_FILE.write_bytes(key)
            try:
                os.chmod(KEY_FILE, 0o600)
            except OSError:
                pass
        else:
            key = KEY_FILE.read_bytes()
        return Fernet(key)

    def _load_vault(self) -> Dict[str, str]:
        if not VAULT_FILE.exists():
            return {}
        try:
            decrypted = self._fernet.decrypt(VAULT_FILE.read_bytes())
            return json.loads(decrypted.decode("utf-8"))
        except Exception:
            return {}

    def _save_vault(self, data: Dict[str, str]) -> None:
        encrypted = self._fernet.encrypt(json.dumps(data).encode("utf-8"))
        tmp = VAULT_FILE.with_suffix(".tmp")
        tmp.write_bytes(encrypted)
        try:
            os.chmod(tmp, 0o600)
        except OSError:
            pass
        tmp.replace(VAULT_FILE)

    def save_key(self, provider: str, api_key: str) -> None:
        vault = self._load_vault()
        vault[provider.lower()] = api_key.strip()
        self._save_vault(vault)

    def delete_key(self, provider: str) -> None:
        vault = self._load_vault()
        vault.pop(provider.lower(), None)
        self._save_vault(vault)

    def get_key(self, provider: str, temp_key: Optional[str] = None) -> Optional[str]:
        if temp_key and temp_key.strip():
            return temp_key.strip()
        vault = self._load_vault()
        if provider.lower() in vault and vault[provider.lower()]:
            return vault[provider.lower()]
        env_var = ENV_MAP.get(provider.lower())
        if env_var and os.getenv(env_var):
            return os.getenv(env_var)
        return None

    def get_status(self) -> Dict[str, Dict[str, bool]]:
        vault = self._load_vault()
        status = {}
        for prov in ["openai", "gemini", "anthropic", "openrouter", "ollama", "custom", "mock"]:
            env_var = ENV_MAP.get(prov, "")
            has_saved = bool(vault.get(prov))
            has_env = bool(env_var and os.getenv(env_var))
            status[prov] = {
                "saved": has_saved,
                "env": has_env,
                "configured": has_saved or has_env or prov in ("ollama", "mock")
            }
        return status

    def redact(self, text: str) -> str:
        if not text:
            return ""
        redacted = text
        vault = self._load_vault()
        for secret in vault.values():
            if secret and len(secret) > 5:
                redacted = redacted.replace(secret, "***REDACTED_KEY***")
        for env_var in ENV_MAP.values():
            val = os.getenv(env_var)
            if val and len(val) > 5:
                redacted = redacted.replace(val, "***REDACTED_ENV_KEY***")
        redacted = re.sub(r'(sk-[a-zA-Z0-9\-_]{16,}|AIza[0-9A-Za-z\-_]{25,})', '***REDACTED_TOKEN***', redacted)
        return redacted

secret_manager = SecretManager()
