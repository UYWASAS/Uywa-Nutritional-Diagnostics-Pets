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
from uywa_core.router import render_selected_module
from uywa_core.launcher.launcher_sidebar import (
    render_platform_sidebar,
)
from uywa_core.services.user_service import (
    UserServiceError,
    load_current_user,
)
from uywa_core.theme import inject_platform_theme

from uywa_core.theme.html_utils import clean_html

st.set_page_config(
    page_title="Uywa Platform",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_platform_theme()


def render_login() -> None:
    """
    Renderiza la pantalla temporal de acceso a Uywa Platform.
    """

    _, login_column, _ = st.columns(
        [1, 1.15, 1]
    )

    with login_column:
        login_header = clean_html(
            """
            <div class="uywa-login-header">
                <h1>Acceso a Uywa</h1>
                <p>Ingresa tus credenciales para continuar.</p>
            </div>
            """
        )
        
        st.markdown(
            login_header,
            unsafe_allow_html=True,
        )

        with st.form(
            "launcher_login_form",
            clear_on_submit=False,
        ):
            email = st.text_input(
                "Correo electrónico",
                placeholder="usuario@correo.com",
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

        email = email.strip()

        if not email or not password:
            st.warning(
                "Ingresa el correo electrónico y la contraseña."
            )
            return

        with st.spinner(
            "Verificando credenciales..."
        ):
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

        if auth_user is None:
            st.error(
                "La autenticación fue aceptada, pero no se "
                "recuperaron los datos del usuario."
            )
            return

        try:
            platform_user = load_current_user(
                auth_user
            )

            set_current_user(
                platform_user
            )

        except UserServiceError as exc:
            clear_current_user()
            st.error(str(exc))
            return

        except Exception as exc:
            clear_current_user()

            st.error(
                "No fue posible cargar la cuenta de "
                f"Uywa Platform: {exc}"
            )
            return

        st.rerun()


def restore_platform_user() -> None:
    """
    Restaura el usuario de la plataforma cuando existe una
    sesión autenticada almacenada.
    """

    current_user = get_current_user()

    if getattr(
        current_user,
        "authenticated",
        False,
    ):
        return

    try:
        auth_user = get_auth_user()
    except Exception:
        clear_current_user()
        return

    if auth_user is None:
        return

    try:
        platform_user = load_current_user(
            auth_user
        )

        set_current_user(
            platform_user
        )

    except Exception:
        clear_current_user()


def process_logout() -> None:
    """
    Cierra la sesión de Supabase y limpia el estado local.
    """

    try:
        sign_out()
    finally:
        clear_current_user()

        st.session_state.pop(
            "uywa_selected_module",
            None,
        )

    st.rerun()


def main() -> None:
    """
    Punto principal de entrada del Launcher de prueba.
    """

    restore_platform_user()

    current_user = get_current_user()

    if not getattr(
        current_user,
        "authenticated",
        False,
    ):
        render_login()
        return

    logout_clicked = render_platform_sidebar(
        current_user=current_user,
        logo_path="assets/logo.png",
    )

    if logout_clicked:
        process_logout()
        return

    module_rendered = render_selected_module()

    if not module_rendered:
        render_launcher()


if __name__ == "__main__":
    main()
