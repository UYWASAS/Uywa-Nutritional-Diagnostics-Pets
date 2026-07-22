from __future__ import annotations

import streamlit as st

from uywa_core.current_user import CurrentUser


CURRENT_USER_KEY = "uywa_current_user"
AUTHENTICATED_KEY = "uywa_authenticated"
SESSION_INITIALIZED_KEY = "uywa_session_initialized"


def initialize_session() -> None:
    """
    Inicializa las variables de sesión utilizadas por Uywa Platform.

    Esta función puede llamarse varias veces sin sobrescribir una sesión
    ya iniciada.
    """

    if SESSION_INITIALIZED_KEY not in st.session_state:
        st.session_state[SESSION_INITIALIZED_KEY] = True

    if CURRENT_USER_KEY not in st.session_state:
        st.session_state[CURRENT_USER_KEY] = CurrentUser.anonymous()

    if AUTHENTICATED_KEY not in st.session_state:
        st.session_state[AUTHENTICATED_KEY] = False


def get_current_user() -> CurrentUser:
    """
    Devuelve el usuario actual de la sesión.

    Si todavía no existe un usuario, crea y devuelve un usuario anónimo.
    """

    initialize_session()

    user = st.session_state.get(CURRENT_USER_KEY)

    if isinstance(user, CurrentUser):
        return user

    anonymous_user = CurrentUser.anonymous()
    st.session_state[CURRENT_USER_KEY] = anonymous_user
    st.session_state[AUTHENTICATED_KEY] = False

    return anonymous_user


def set_current_user(user: CurrentUser) -> None:
    """
    Guarda un usuario autenticado en la sesión actual.

    Cada navegador de Streamlit posee su propio st.session_state, por lo
    que el usuario no se comparte con otras sesiones.
    """

    if not isinstance(user, CurrentUser):
        raise TypeError(
            "set_current_user esperaba una instancia de CurrentUser."
        )

    initialize_session()

    st.session_state[CURRENT_USER_KEY] = user
    st.session_state[AUTHENTICATED_KEY] = bool(
        user.authenticated
        and user.active
    )


def is_authenticated() -> bool:
    """
    Indica si la sesión actual contiene un usuario autenticado y activo.
    """

    initialize_session()

    user = get_current_user()

    return bool(
        st.session_state.get(AUTHENTICATED_KEY, False)
        and user.authenticated
        and user.active
    )


def clear_current_user() -> None:
    """
    Elimina el usuario actual y devuelve la sesión al estado anónimo.

    Esta función debe utilizarse al cerrar sesión.
    """

    initialize_session()

    st.session_state[CURRENT_USER_KEY] = CurrentUser.anonymous()
    st.session_state[AUTHENTICATED_KEY] = False


def reset_platform_session() -> None:
    """
    Reinicia solamente las variables propias de Uywa Platform.

    No elimina todavía los datos clínicos o temporales de Pet Nutrition
    almacenados con otras claves de st.session_state.
    """

    keys_to_remove = [
        CURRENT_USER_KEY,
        AUTHENTICATED_KEY,
        SESSION_INITIALIZED_KEY,
    ]

    for key in keys_to_remove:
        st.session_state.pop(key, None)

    initialize_session()


def get_legacy_user() -> dict:
    """
    Devuelve el usuario actual en formato compatible con la aplicación
    antigua de Pet Nutrition.
    """

    user = get_current_user()
    return user.to_legacy_dict()
