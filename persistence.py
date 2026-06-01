# =========================================================
# PERSISTENCIA DE CARGA ADMINISTRATIVA
# Archivo: persistence.py
# =========================================================

"""
Este módulo centraliza el guardado, lectura, verificación y borrado de la
última carga administrativa del dashboard.

La app sigue usando st.session_state para trabajar rápido durante una sesión
activa, pero este módulo permite respaldar la carga fuera de la sesión temporal.

Backends disponibles:
- local: guarda un archivo .pkl.gz en la carpeta configurada. Sirve para localhost.
- github: guarda el archivo comprimido en un repositorio GitHub mediante API.
          Sirve para Streamlit Cloud porque sobrevive a reinicios de la app.

Para usar GitHub en Streamlit Cloud, configura estos secretos:
GITHUB_TOKEN = "ghp_xxx"
GITHUB_REPO = "usuario/repositorio"
GITHUB_BRANCH = "main"
GITHUB_PERSISTENCE_PATH = "persistent_data/latest_dashboard_data.pkl.gz"
"""

from __future__ import annotations

import base64
import gzip
import json
import os
import pickle
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import config

try:
    import streamlit as st
except Exception:  # pragma: no cover
    st = None


# =========================================================
# 1. HELPERS GENERALES
# =========================================================
def _get_config_value(name: str, default: Any = None) -> Any:
    return getattr(config, name, default)


def _get_secret(name: str, default: str | None = None) -> str | None:
    """Obtiene un secreto desde Streamlit secrets o variable de entorno."""
    if st is not None:
        try:
            value = st.secrets.get(name)  # type: ignore[attr-defined]
            if value:
                return str(value)
        except Exception:
            pass

    value = os.environ.get(name)
    if value:
        return str(value)

    return default


def get_persistence_backend() -> str:
    """
    Resuelve el backend activo.

    Si está en AUTO y existen secretos de GitHub, usa github.
    Si no existen, usa local para que la app siga funcionando en localhost.
    """
    backend = str(_get_config_value("PERSISTENCE_BACKEND", "auto") or "auto").strip().lower()

    if backend == "auto":
        github_token = _get_secret("GITHUB_TOKEN")
        github_repo = _get_secret("GITHUB_REPO")
        if github_token and github_repo:
            return "github"
        return "local"

    return backend


def _serialize_payload(payload: dict) -> bytes:
    """Serializa y comprime el payload para reducir peso."""
    raw_bytes = pickle.dumps(payload, protocol=pickle.HIGHEST_PROTOCOL)
    return gzip.compress(raw_bytes)


def _deserialize_payload(payload_bytes: bytes) -> dict:
    """Descomprime y deserializa el payload."""
    raw_bytes = gzip.decompress(payload_bytes)
    return pickle.loads(raw_bytes)


# =========================================================
# 2. BACKEND LOCAL
# =========================================================
def get_local_persistent_data_folder() -> Path:
    folder_name = _get_config_value("PERSISTENT_DATA_PATH", "persistent_data")
    folder = Path(str(folder_name))
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def get_local_persistent_data_file() -> Path:
    file_name = _get_config_value("PERSISTENT_DATA_FILE_NAME", "latest_dashboard_data.pkl.gz")
    return get_local_persistent_data_folder() / str(file_name)


def _local_exists() -> bool:
    return get_local_persistent_data_file().exists()


def _local_save(payload: dict) -> bool:
    file_path = get_local_persistent_data_file()
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(_serialize_payload(payload))
    return True


def _local_load() -> dict | None:
    file_path = get_local_persistent_data_file()
    if not file_path.exists():
        return None
    return _deserialize_payload(file_path.read_bytes())


def _local_delete() -> bool:
    file_path = get_local_persistent_data_file()
    if file_path.exists():
        file_path.unlink()
    return True


# =========================================================
# 3. BACKEND GITHUB
# =========================================================
def _github_required_config() -> dict:
    token = _get_secret("GITHUB_TOKEN")
    repo = _get_secret("GITHUB_REPO")
    branch = _get_secret("GITHUB_BRANCH", _get_config_value("GITHUB_BRANCH", "main"))
    storage_path = _get_secret(
        "GITHUB_PERSISTENCE_PATH",
        _get_config_value("GITHUB_PERSISTENCE_PATH", "persistent_data/latest_dashboard_data.pkl.gz"),
    )

    if not token:
        raise ValueError("Falta configurar GITHUB_TOKEN en Streamlit secrets.")
    if not repo:
        raise ValueError("Falta configurar GITHUB_REPO en Streamlit secrets.")

    return {
        "token": token,
        "repo": repo,
        "branch": branch or "main",
        "path": str(storage_path).lstrip("/"),
    }


def _github_api_url(repo: str, path: str) -> str:
    encoded_path = urllib.parse.quote(path, safe="/")
    return f"https://api.github.com/repos/{repo}/contents/{encoded_path}"


def _github_request(method: str, url: str, token: str, body: dict | None = None) -> dict | None:
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = urllib.request.Request(url=url, data=data, method=method)
    request.add_header("Authorization", f"Bearer {token}")
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("X-GitHub-Api-Version", "2022-11-28")
    if body is not None:
        request.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            response_bytes = response.read()
            if not response_bytes:
                return None
            return json.loads(response_bytes.decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"GitHub API respondió {exc.code}. Detalle: {detail}") from exc


def _github_request_raw_bytes(url: str, token: str) -> bytes | None:
    """
    Descarga el archivo como bytes crudos desde GitHub.

    Esto es necesario cuando el archivo persistente pesa más de 1 MB.
    En ese caso, GitHub puede regresar el metadata JSON con content vacío,
    por lo que no basta leer el campo base64 "content".
    """
    request = urllib.request.Request(url=url, method="GET")
    request.add_header("Authorization", f"Bearer {token}")
    request.add_header("Accept", "application/vnd.github.raw")
    request.add_header("X-GitHub-Api-Version", "2022-11-28")

    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            response_bytes = response.read()
            if not response_bytes:
                return None
            return response_bytes
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"GitHub RAW respondió {exc.code}. Detalle: {detail}") from exc


def _github_get_file_info() -> dict | None:
    cfg = _github_required_config()
    url = _github_api_url(cfg["repo"], cfg["path"])
    url = f"{url}?ref={urllib.parse.quote(str(cfg['branch']))}"
    return _github_request("GET", url, cfg["token"])


def _github_exists() -> bool:
    return _github_get_file_info() is not None


def _github_save(payload: dict) -> bool:
    cfg = _github_required_config()
    file_info = _github_get_file_info()
    sha = file_info.get("sha") if file_info else None

    content_bytes = _serialize_payload(payload)
    content_b64 = base64.b64encode(content_bytes).decode("utf-8")

    body = {
        "message": "Update dashboard persistent payload",
        "content": content_b64,
        "branch": cfg["branch"],
    }

    if sha:
        body["sha"] = sha

    url = _github_api_url(cfg["repo"], cfg["path"])
    _github_request("PUT", url, cfg["token"], body=body)
    return True


def _github_load() -> dict | None:
    cfg = _github_required_config()

    file_info = _github_get_file_info()
    if not file_info:
        return None

    content_text = file_info.get("content", "")

    # Archivos pequeños: GitHub devuelve el contenido en base64 dentro del JSON.
    if content_text:
        content_bytes = base64.b64decode(content_text.replace("\n", ""))
        return _deserialize_payload(content_bytes)

    # Archivos grandes: GitHub puede devolver metadata con content vacío.
    # En ese caso se fuerza lectura RAW desde la API de contents.
    raw_url = _github_api_url(cfg["repo"], cfg["path"])
    raw_url = f"{raw_url}?ref={urllib.parse.quote(str(cfg['branch']))}"

    raw_bytes = _github_request_raw_bytes(raw_url, cfg["token"])
    if not raw_bytes:
        return None

    return _deserialize_payload(raw_bytes)


def _github_delete() -> bool:
    cfg = _github_required_config()
    file_info = _github_get_file_info()
    if not file_info:
        return True

    body = {
        "message": "Delete dashboard persistent payload",
        "sha": file_info.get("sha"),
        "branch": cfg["branch"],
    }

    url = _github_api_url(cfg["repo"], cfg["path"])
    _github_request("DELETE", url, cfg["token"], body=body)
    return True


# =========================================================
# 4. API PÚBLICA DEL MÓDULO
# =========================================================
def persistent_data_exists() -> bool:
    backend = get_persistence_backend()

    if backend == "github":
        return _github_exists()

    return _local_exists()


def save_dashboard_payload(payload: dict) -> bool:
    backend = get_persistence_backend()

    if backend == "github":
        return _github_save(payload)

    return _local_save(payload)


def load_dashboard_payload() -> dict | None:
    backend = get_persistence_backend()

    if backend == "github":
        return _github_load()

    return _local_load()


def delete_dashboard_payload() -> bool:
    backend = get_persistence_backend()

    if backend == "github":
        return _github_delete()

    return _local_delete()


def get_persistence_status_label() -> str:
    backend = get_persistence_backend()
    if backend == "github":
        return "GitHub Storage"
    return "Local"

