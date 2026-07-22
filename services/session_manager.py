from __future__ import annotations

from typing import Any

import streamlit as st


ACCESS_TOKEN_KEY = "uywa_supabase_access_token"
REFRESH_TOKEN_KEY = "uywa_supabase_refresh_token"
AUTH_USER_ID_KEY = "uywa_supabase_auth_user_id"
AUTH_USER_EMAIL_KEY = "uywa_supabase_auth_user_email"


def save_auth_session(
    session: Any,
    user: Any | None = None,
) -> None:
    """
    Guarda los tokens de Supabase dentro de la sesión actual de Streamlit.

    Cada navegador mantiene su propio st.session_state, por lo que los
    tokens no se comparten entre usuarios.
    """

    access_token = getattr(session, "access_token", None)
    refresh_token = getattr(session, "refresh_token", None)

    if not access_token or not refresh_token:
        raise ValueError(
            "La sesión de Supabase no contiene access_token "
            "y refresh_token válidos."
        )

    st.session_state[ACCESS_TOKEN_KEY] = str(access_token)
    st.session_state[REFRESH_TOKEN_KEY] = str(refresh_token)

    if user is not None:
        user_id = getattr(user, "id", None)
        user_email = getattr(user, "email", None)

        st.session_state[AUTH_USER_ID_KEY] = (
            str(user_id)
            if user_id
            else None
        )
        st.session_state[AUTH_USER_EMAIL_KEY] = user_email


def update_auth_session(session: Any) -> None:
    """
    Actualiza los tokens cuando Supabase renueva la sesión.
    """

    save_auth_session(session=session)


def get_access_token() -> str | None:
    """
    Devuelve el access token de la sesión actual.
    """

    value = st.session_state.get(ACCESS_TOKEN_KEY)

    if not value:
        return None

    return str(value)


def get_refresh_token() -> str | None:
    """
    Devuelve el refresh token de la sesión actual.
    """

    value = st.session_state.get(REFRESH_TOKEN_KEY)

    if not value:
        return None

    return str(value)


def get_saved_auth_identity() -> dict[str, str | None]:
    """
    Devuelve la identidad básica almacenada localmente.
    """

    return {
        "id": st.session_state.get(AUTH_USER_ID_KEY),
        "email": st.session_state.get(AUTH_USER_EMAIL_KEY),
    }


def has_saved_auth_session() -> bool:
    """
    Indica si existen ambos tokens necesarios para restaurar la sesión.
    """

    return bool(
        get_access_token()
        and get_refresh_token()
    )


def clear_auth_session() -> None:
    """
    Elimina tokens e identidad básica de la sesión actual.
    """

    keys = [
        ACCESS_TOKEN_KEY,
        REFRESH_TOKEN_KEY,
        AUTH_USER_ID_KEY,
        AUTH_USER_EMAIL_KEY,
    ]

    for key in keys:
        st.session_state.pop(key, None)
