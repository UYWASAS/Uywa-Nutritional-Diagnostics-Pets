from __future__ import annotations

import streamlit as st
from supabase import Client, create_client

from services.session_manager import (
    get_access_token,
    get_refresh_token,
    has_saved_auth_session,
    update_auth_session,
)


def _get_supabase_credentials() -> tuple[str, str]:
    """
    Obtiene y valida las credenciales configuradas en Streamlit Secrets.
    """

    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]

    except KeyError as exc:
        raise RuntimeError(
            f"Falta configurar el secreto {exc} en Streamlit Cloud."
        ) from exc

    normalized_url = str(url or "").strip()
    normalized_key = str(key or "").strip()

    if not normalized_url:
        raise RuntimeError("SUPABASE_URL está vacío.")

    if not normalized_key:
        raise RuntimeError("SUPABASE_KEY está vacío.")

    return normalized_url, normalized_key


def create_public_supabase_client() -> Client:
    """
    Crea un cliente nuevo sin restaurar una sesión autenticada.

    Se utiliza principalmente para iniciar sesión.
    """

    url, key = _get_supabase_credentials()

    return create_client(url, key)


def get_supabase() -> Client:
    """
    Devuelve un cliente nuevo para la sesión actual de Streamlit.

    Si existen tokens guardados, restaura la sesión autenticada antes
    de devolver el cliente. Así las consultas respetan correctamente
    las políticas RLS del usuario conectado.
    """

    client = create_public_supabase_client()

    if not has_saved_auth_session():
        return client

    access_token = get_access_token()
    refresh_token = get_refresh_token()

    if not access_token or not refresh_token:
        return client

    try:
        response = client.auth.set_session(
            access_token,
            refresh_token,
        )

        restored_session = getattr(response, "session", None)

        if restored_session is not None:
            update_auth_session(restored_session)

        return client

    except Exception as exc:
        raise RuntimeError(
            "No fue posible restaurar la sesión autenticada "
            "de Supabase."
        ) from exc
