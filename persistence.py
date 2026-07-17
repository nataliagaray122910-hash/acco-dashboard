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
import time
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
def emit_progress(
    progress_callback,
    message: str,
    step: int,
    total_steps: int,
) -> None:
    """
    Envía una etapa real del proceso de persistencia al componente visual
    que será administrado desde app.py.

    El callback es opcional para conservar compatibilidad con las llamadas
    actuales. No calcula porcentajes ni agrega pausas artificiales.
    """
    if progress_callback is None:
        return

    progress_callback(
        message=message,
        step=int(step),
        total_steps=int(total_steps),
    )


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


def _local_save(payload: dict, progress_callback=None) -> bool:
    total_steps = 5

    emit_progress(
        progress_callback,
        "Resolviendo la ubicación del respaldo local",
        1,
        total_steps,
    )
    file_path = get_local_persistent_data_file()

    emit_progress(
        progress_callback,
        "Preparando la carpeta de persistencia",
        2,
        total_steps,
    )
    file_path.parent.mkdir(parents=True, exist_ok=True)

    emit_progress(
        progress_callback,
        "Serializando y comprimiendo la carga administrativa",
        3,
        total_steps,
    )
    payload_bytes = _serialize_payload(payload)

    emit_progress(
        progress_callback,
        "Guardando el respaldo local",
        4,
        total_steps,
    )
    file_path.write_bytes(payload_bytes)

    emit_progress(
        progress_callback,
        "Confirmando el guardado del respaldo local",
        5,
        total_steps,
    )
    if not file_path.exists() or file_path.stat().st_size == 0:
        raise RuntimeError("El respaldo local no pudo confirmarse después del guardado.")

    return True


def _local_load(progress_callback=None) -> dict | None:
    total_steps = 5

    emit_progress(
        progress_callback,
        "Resolviendo la ubicación del respaldo local",
        1,
        total_steps,
    )
    file_path = get_local_persistent_data_file()

    emit_progress(
        progress_callback,
        "Verificando si existe información guardada",
        2,
        total_steps,
    )
    if not file_path.exists():
        return None

    emit_progress(
        progress_callback,
        "Leyendo el respaldo local",
        3,
        total_steps,
    )
    payload_bytes = file_path.read_bytes()

    emit_progress(
        progress_callback,
        "Descomprimiendo y recuperando la información",
        4,
        total_steps,
    )
    payload = _deserialize_payload(payload_bytes)

    emit_progress(
        progress_callback,
        "Validando la carga recuperada",
        5,
        total_steps,
    )
    if not isinstance(payload, dict):
        raise ValueError("El respaldo local recuperado no contiene un payload válido.")

    return payload


def _local_delete(progress_callback=None) -> bool:
    total_steps = 4

    emit_progress(
        progress_callback,
        "Resolviendo la ubicación del respaldo local",
        1,
        total_steps,
    )
    file_path = get_local_persistent_data_file()

    emit_progress(
        progress_callback,
        "Verificando si existe un respaldo guardado",
        2,
        total_steps,
    )
    if file_path.exists():
        emit_progress(
            progress_callback,
            "Eliminando el respaldo local",
            3,
            total_steps,
        )
        file_path.unlink()
    else:
        emit_progress(
            progress_callback,
            "No se encontró un respaldo local para eliminar",
            3,
            total_steps,
        )

    emit_progress(
        progress_callback,
        "Confirmando la eliminación del respaldo",
        4,
        total_steps,
    )
    if file_path.exists():
        raise RuntimeError("El respaldo local sigue existiendo después de intentar eliminarlo.")

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
    """
    Ejecuta una llamada JSON a la API de GitHub con reintentos.

    GitHub puede responder 502/503/504 de forma temporal, especialmente cuando
    se actualiza un archivo grande mediante Contents API. En esos casos no se
    debe fallar al primer intento: se espera unos segundos y se reintenta.
    """
    data = None if body is None else json.dumps(body).encode("utf-8")
    retry_status_codes = {502, 503, 504}
    max_attempts = int(_get_config_value("GITHUB_API_MAX_ATTEMPTS", 4) or 4)
    base_sleep_seconds = float(_get_config_value("GITHUB_API_RETRY_SLEEP_SECONDS", 3) or 3)
    timeout_seconds = int(_get_config_value("GITHUB_API_TIMEOUT_SECONDS", 180) or 180)

    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        request = urllib.request.Request(url=url, data=data, method=method)
        request.add_header("Authorization", f"Bearer {token}")
        request.add_header("Accept", "application/vnd.github+json")
        request.add_header("X-GitHub-Api-Version", "2022-11-28")
        if body is not None:
            request.add_header("Content-Type", "application/json")

        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                response_bytes = response.read()
                if not response_bytes:
                    return None
                return json.loads(response_bytes.decode("utf-8"))

        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None

            detail = exc.read().decode("utf-8", errors="ignore")
            last_error = RuntimeError(f"GitHub API respondió {exc.code}. Detalle: {detail}")

            if exc.code in retry_status_codes and attempt < max_attempts:
                time.sleep(base_sleep_seconds * attempt)
                continue

            raise last_error from exc

        except urllib.error.URLError as exc:
            last_error = RuntimeError(f"No fue posible conectar con GitHub API. Detalle: {exc}")
            if attempt < max_attempts:
                time.sleep(base_sleep_seconds * attempt)
                continue
            raise last_error from exc

    if last_error:
        raise last_error

    return None


def _github_request_raw_bytes(url: str, token: str) -> bytes | None:
    """
    Descarga el archivo como bytes crudos desde GitHub.

    Esto es necesario cuando el archivo persistente pesa más de 1 MB.
    En ese caso, GitHub puede regresar el metadata JSON con content vacío,
    por lo que no basta leer el campo base64 "content".
    """
    retry_status_codes = {502, 503, 504}
    max_attempts = int(_get_config_value("GITHUB_API_MAX_ATTEMPTS", 4) or 4)
    base_sleep_seconds = float(_get_config_value("GITHUB_API_RETRY_SLEEP_SECONDS", 3) or 3)
    timeout_seconds = int(_get_config_value("GITHUB_RAW_TIMEOUT_SECONDS", 180) or 180)

    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        request = urllib.request.Request(url=url, method="GET")
        request.add_header("Authorization", f"Bearer {token}")
        request.add_header("Accept", "application/vnd.github.raw")
        request.add_header("X-GitHub-Api-Version", "2022-11-28")

        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                response_bytes = response.read()
                if not response_bytes:
                    return None
                return response_bytes

        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None

            detail = exc.read().decode("utf-8", errors="ignore")
            last_error = RuntimeError(f"GitHub RAW respondió {exc.code}. Detalle: {detail}")

            if exc.code in retry_status_codes and attempt < max_attempts:
                time.sleep(base_sleep_seconds * attempt)
                continue

            raise last_error from exc

        except urllib.error.URLError as exc:
            last_error = RuntimeError(f"No fue posible descargar RAW desde GitHub. Detalle: {exc}")
            if attempt < max_attempts:
                time.sleep(base_sleep_seconds * attempt)
                continue
            raise last_error from exc

    if last_error:
        raise last_error

    return None


def _github_get_file_info() -> dict | None:
    cfg = _github_required_config()
    url = _github_api_url(cfg["repo"], cfg["path"])
    url = f"{url}?ref={urllib.parse.quote(str(cfg['branch']))}"
    return _github_request("GET", url, cfg["token"])


def _github_exists() -> bool:
    return _github_get_file_info() is not None


def _github_save(payload: dict, progress_callback=None) -> bool:
    total_steps = 6

    emit_progress(
        progress_callback,
        "Validando la configuración de GitHub Storage",
        1,
        total_steps,
    )
    cfg = _github_required_config()

    emit_progress(
        progress_callback,
        "Consultando la versión actual del respaldo",
        2,
        total_steps,
    )
    file_info = _github_get_file_info()
    sha = file_info.get("sha") if file_info else None

    emit_progress(
        progress_callback,
        "Serializando y comprimiendo la carga administrativa",
        3,
        total_steps,
    )
    content_bytes = _serialize_payload(payload)

    emit_progress(
        progress_callback,
        "Preparando el archivo para enviarlo a GitHub",
        4,
        total_steps,
    )
    content_b64 = base64.b64encode(content_bytes).decode("utf-8")

    body = {
        "message": "Update dashboard persistent payload",
        "content": content_b64,
        "branch": cfg["branch"],
    }

    if sha:
        body["sha"] = sha

    emit_progress(
        progress_callback,
        "Guardando la carga administrativa en GitHub",
        5,
        total_steps,
    )
    url = _github_api_url(cfg["repo"], cfg["path"])
    _github_request("PUT", url, cfg["token"], body=body)

    emit_progress(
        progress_callback,
        "Confirmando el guardado en GitHub Storage",
        6,
        total_steps,
    )
    if _github_get_file_info() is None:
        raise RuntimeError("GitHub no confirmó la existencia del respaldo después del guardado.")

    return True


def _github_load(progress_callback=None) -> dict | None:
    total_steps = 6

    emit_progress(
        progress_callback,
        "Validando la configuración de GitHub Storage",
        1,
        total_steps,
    )
    cfg = _github_required_config()

    emit_progress(
        progress_callback,
        "Buscando la última carga administrativa",
        2,
        total_steps,
    )
    file_info = _github_get_file_info()
    if not file_info:
        return None

    emit_progress(
        progress_callback,
        "Preparando la descarga del respaldo",
        3,
        total_steps,
    )
    content_text = file_info.get("content", "")

    if content_text:
        emit_progress(
            progress_callback,
            "Descargando el contenido guardado",
            4,
            total_steps,
        )
        content_bytes = base64.b64decode(content_text.replace("\n", ""))
    else:
        emit_progress(
            progress_callback,
            "Descargando el archivo completo desde GitHub",
            4,
            total_steps,
        )
        raw_url = _github_api_url(cfg["repo"], cfg["path"])
        raw_url = f"{raw_url}?ref={urllib.parse.quote(str(cfg['branch']))}"
        content_bytes = _github_request_raw_bytes(raw_url, cfg["token"])
        if not content_bytes:
            return None

    emit_progress(
        progress_callback,
        "Descomprimiendo y recuperando la información",
        5,
        total_steps,
    )
    payload = _deserialize_payload(content_bytes)

    emit_progress(
        progress_callback,
        "Validando la carga recuperada",
        6,
        total_steps,
    )
    if not isinstance(payload, dict):
        raise ValueError("El respaldo recuperado de GitHub no contiene un payload válido.")

    return payload


def _github_delete(progress_callback=None) -> bool:
    total_steps = 5

    emit_progress(
        progress_callback,
        "Validando la configuración de GitHub Storage",
        1,
        total_steps,
    )
    cfg = _github_required_config()

    emit_progress(
        progress_callback,
        "Buscando el respaldo guardado",
        2,
        total_steps,
    )
    file_info = _github_get_file_info()
    if not file_info:
        emit_progress(
            progress_callback,
            "No se encontró una carga guardada para eliminar",
            5,
            total_steps,
        )
        return True

    emit_progress(
        progress_callback,
        "Preparando la eliminación del respaldo",
        3,
        total_steps,
    )
    body = {
        "message": "Delete dashboard persistent payload",
        "sha": file_info.get("sha"),
        "branch": cfg["branch"],
    }

    emit_progress(
        progress_callback,
        "Eliminando la carga administrativa de GitHub",
        4,
        total_steps,
    )
    url = _github_api_url(cfg["repo"], cfg["path"])
    _github_request("DELETE", url, cfg["token"], body=body)

    emit_progress(
        progress_callback,
        "Confirmando la eliminación del respaldo",
        5,
        total_steps,
    )
    if _github_get_file_info() is not None:
        raise RuntimeError("GitHub sigue mostrando el respaldo después de intentar eliminarlo.")

    return True


# =========================================================
# 4. API PÚBLICA DEL MÓDULO
# =========================================================
def persistent_data_exists(progress_callback=None) -> bool:
    total_steps = 2

    emit_progress(
        progress_callback,
        "Resolviendo el almacenamiento de persistencia",
        1,
        total_steps,
    )
    backend = get_persistence_backend()

    emit_progress(
        progress_callback,
        "Verificando si existe información guardada",
        2,
        total_steps,
    )
    if backend == "github":
        return _github_exists()

    return _local_exists()


def save_dashboard_payload(payload: dict, progress_callback=None) -> bool:
    if not isinstance(payload, dict):
        raise ValueError("La carga administrativa debe enviarse como un diccionario.")

    backend = get_persistence_backend()

    if backend == "github":
        return _github_save(payload, progress_callback=progress_callback)

    return _local_save(payload, progress_callback=progress_callback)


def load_dashboard_payload(progress_callback=None) -> dict | None:
    backend = get_persistence_backend()

    if backend == "github":
        return _github_load(progress_callback=progress_callback)

    return _local_load(progress_callback=progress_callback)


def delete_dashboard_payload(progress_callback=None) -> bool:
    backend = get_persistence_backend()

    if backend == "github":
        return _github_delete(progress_callback=progress_callback)

    return _local_delete(progress_callback=progress_callback)


def get_persistence_status_label() -> str:
    backend = get_persistence_backend()
    if backend == "github":
        return "GitHub Storage"
    return "Local"
