from __future__ import annotations

import streamlit as st

from services.auth_service import (
    get_auth_user,
    sign_in,
    sign_out,
)
from uywa_core.current_session import (
    clear_current_user,
    get_current_user,
    set_current_user,
)
from uywa_core.launcher.launcher_page import render_launcher
from uywa_core.services.user_service import (
    UserServiceError,
    load_current_user,
)


st.set_page_config(
    page_title="Uywa Platform",
    page_icon="🐾",
    layout="wide",
)


def render_login() -> None:
    st.title("Acceso a Uywa Platform")

    with st.form("launcher_login_form"):
        email = st.text_input(
            "Correo electrónico"
        )

        password = st.text_input(
            "Contraseña",
            type="password",
        )

        submitted = st.form_submit_button(
            "Iniciar sesión",
            use_container_width=True,
        )

    if not submitted:
        return

    result = sign_in(
        email=email,
        password=password,
    )

    if not result.get("success"):
        st.error(
            result.get(
                "message",
                "No fue posible iniciar sesión.",
            )
        )
        return

    auth_user = result.get("user")

    try:
        platform_user = load_current_user(auth_user)
        set_current_user(platform_user)

    except UserServiceError as exc:
        clear_current_user()
        st.error(str(exc))
        return

    st.rerun()


def restore_platform_user() -> None:
    current_user = get_current_user()

    if current_user.authenticated:
        return

    auth_user = get_auth_user()

    if auth_user is None:
        return

    try:
        platform_user = load_current_user(auth_user)
        set_current_user(platform_user)

    except Exception:
        clear_current_user()


def render_sidebar() -> None:
    current_user = get_current_user()

    with st.sidebar:
        st.subheader("Uywa Platform")

        st.write(
            current_user.full_name
            or current_user.email
            or "Usuario"
        )

        st.caption(
            current_user.plan_name
            or current_user.role
            or ""
        )

        st.divider()

        if st.button(
            "Cerrar sesión",
            use_container_width=True,
        ):
            sign_out()
            clear_current_user()
            st.rerun()


def main() -> None:
    restore_platform_user()

    current_user = get_current_user()

    if not current_user.authenticated:
        render_login()
        return

    render_sidebar()
    render_launcher()


if __name__ == "__main__":
    main()
