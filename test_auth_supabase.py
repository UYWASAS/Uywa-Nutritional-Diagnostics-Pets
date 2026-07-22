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
    is_authenticated,
    set_current_user,
)
from uywa_core.services.user_service import (
    UserServiceError,
    load_current_user,
)


st.set_page_config(
    page_title="Prueba de autenticación | Uywa",
    page_icon="🔐",
    layout="centered",
)


def initialize_session_state() -> None:
    """
    Inicializa las variables utilizadas solamente por esta prueba.

    Estas variables son independientes de las que utiliza Uywa Core.
    Se conservan temporalmente para facilitar la depuración del proceso
    de autenticación.
    """

    defaults = {
        "supabase_authenticated": False,
        "supabase_user_id": None,
        "supabase_user_email": None,
        "platform_user_loaded": False,
        "platform_user_error": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_local_auth_state() -> None:
    """
    Limpia el estado local de autenticación de esta prueba y el usuario
    almacenado en Uywa Core.
    """

    st.session_state["supabase_authenticated"] = False
    st.session_state["supabase_user_id"] = None
    st.session_state["supabase_user_email"] = None
    st.session_state["platform_user_loaded"] = False
    st.session_state["platform_user_error"] = None

    clear_current_user()


def store_authenticated_user(auth_user: object) -> None:
    """
    Guarda la identidad básica recibida desde Supabase Auth.
    """

    user_id = getattr(auth_user, "id", None)
    user_email = getattr(auth_user, "email", None)

    st.session_state["supabase_authenticated"] = bool(user_id)
    st.session_state["supabase_user_id"] = (
        str(user_id)
        if user_id
        else None
    )
    st.session_state["supabase_user_email"] = user_email


def load_platform_user(auth_user: object) -> bool:
    """
    Consulta las tablas comerciales y construye el CurrentUser completo.

    Retorna True cuando el usuario pudo cargarse correctamente.
    """

    try:
        platform_user = load_current_user(auth_user)
        set_current_user(platform_user)

        st.session_state["platform_user_loaded"] = True
        st.session_state["platform_user_error"] = None

        return True

    except UserServiceError as exc:
        clear_current_user()

        st.session_state["platform_user_loaded"] = False
        st.session_state["platform_user_error"] = str(exc)

        return False

    except Exception as exc:
        clear_current_user()

        st.session_state["platform_user_loaded"] = False
        st.session_state["platform_user_error"] = (
            "Se produjo un error inesperado al cargar el usuario: "
            f"{exc}"
        )

        return False


def render_login() -> None:
    """
    Renderiza el formulario de inicio de sesión.
    """

    st.title("🔐 Acceso a Uywa")

    st.write(
        "Esta pantalla prueba la conexión entre Streamlit, Supabase Auth "
        "y el núcleo de Uywa Platform. No modifica todavía la aplicación "
        "principal de Pet Nutrition."
    )

    with st.form("supabase_login_form"):
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

    normalized_email = email.strip()

    if not normalized_email:
        st.warning("Ingresa el correo electrónico.")
        return

    if not password:
        st.warning("Ingresa la contraseña.")
        return

    with st.spinner("Verificando credenciales..."):
        result = sign_in(
            email=normalized_email,
            password=password,
        )

    if not result.get("success", False):
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
            "Supabase confirmó el acceso, pero no devolvió los datos "
            "del usuario."
        )
        return

    store_authenticated_user(auth_user)

    with st.spinner(
        "Cargando perfil, suscripción, plan y módulos..."
    ):
        platform_loaded = load_platform_user(auth_user)

    if not platform_loaded:
        st.error(
            "Las credenciales fueron correctas, pero no se pudo cargar "
            "el usuario completo de Uywa Platform."
        )

        error_message = st.session_state.get(
            "platform_user_error"
        )

        if error_message:
            st.code(error_message)

        return

    st.success("Inicio de sesión y carga del usuario correctos.")
    st.rerun()


def ensure_platform_user_loaded() -> None:
    """
    Intenta cargar el CurrentUser cuando existe autenticación básica,
    pero todavía no se ha construido el usuario de la plataforma.
    """

    if not st.session_state.get(
        "supabase_authenticated",
        False,
    ):
        return

    current_user = get_current_user()

    if (
        is_authenticated()
        and current_user.ready
    ):
        st.session_state["platform_user_loaded"] = True
        return

    auth_user = get_auth_user()

    if auth_user is None:
        return

    store_authenticated_user(auth_user)
    load_platform_user(auth_user)


def render_authenticated_user() -> None:
    """
    Muestra la identidad de Supabase Auth y los datos comerciales del
    usuario de Uywa Platform.
    """

    ensure_platform_user_loaded()

    st.title("✅ Autenticación correcta")

    st.success(
        "Streamlit se conectó correctamente con Supabase Auth."
    )

    st.subheader("Usuario autenticado")

    st.write(
        "**Correo:** "
        f"{st.session_state.get('supabase_user_email') or 'No disponible'}"
    )

    st.write(
        "**ID del usuario:** "
        f"`{st.session_state.get('supabase_user_id') or 'No disponible'}`"
    )

    st.divider()

    current_user = get_current_user()

    if not st.session_state.get(
        "platform_user_loaded",
        False,
    ):
        st.error(
            "La autenticación básica está activa, pero todavía no se "
            "pudo cargar el perfil comercial de Uywa Platform."
        )

        error_message = st.session_state.get(
            "platform_user_error"
        )

        if error_message:
            st.code(error_message)

        if st.button(
            "Reintentar carga del usuario",
            use_container_width=True,
        ):
            auth_user = get_auth_user()

            if auth_user is None:
                st.warning(
                    "No se pudo recuperar nuevamente la sesión de "
                    "Supabase Auth."
                )
            else:
                with st.spinner(
                    "Consultando perfil, plan y módulos..."
                ):
                    load_platform_user(auth_user)

                st.rerun()

        render_logout_button()
        return

    st.subheader("Usuario de Uywa Platform")

    column_left, column_right = st.columns(2)

    with column_left:
        st.write(
            "**Nombre:**",
            current_user.name or "No disponible",
        )

        st.write(
            "**Rol:**",
            current_user.role or "No disponible",
        )

        st.write(
            "**Plan:**",
            (
                current_user.plan_name
                or current_user.plan_code
                or "Sin plan"
            ),
        )

        st.write(
            "**Estado de suscripción:**",
            (
                current_user.subscription_status
                or "Sin suscripción"
            ),
        )

    with column_right:
        st.write(
            "**Perfil activo:**",
            current_user.active,
        )

        st.write(
            "**Usuario preparado:**",
            current_user.ready,
        )

        st.write(
            "**Suscripción vigente:**",
            current_user.subscription_is_active,
        )

        st.write(
            "**Acceso a Pet Nutrition:**",
            current_user.can_use("pet_nutrition"),
        )

    st.divider()

    st.subheader("Módulos habilitados")

    if current_user.modules:
        for module_code in current_user.modules:
            st.write(f"✅ `{module_code}`")
    else:
        st.warning(
            "El usuario no tiene módulos habilitados."
        )

    st.subheader("Permisos efectivos")

    if current_user.permissions:
        for permission_code, allowed in (
            current_user.permissions.items()
        ):
            icon = "✅" if allowed else "❌"
            st.write(
                f"{icon} `{permission_code}`"
            )
    else:
        st.info(
            "No se encontraron permisos configurados."
        )

    if current_user.limits:
        st.subheader("Límites efectivos")

        for limit_code, value in current_user.limits.items():
            st.write(
                f"- `{limit_code}`: **{value}**"
            )

    with st.expander(
        "Ver datos técnicos del usuario",
        expanded=False,
    ):
        st.json(current_user.to_dict())

    with st.expander(
        "Ver formato compatible con Pet Nutrition",
        expanded=False,
    ):
        st.json(current_user.to_legacy_dict())

    st.divider()

    if (
        current_user.can_use("pet_nutrition")
        and current_user.active
    ):
        st.success(
            "El usuario está preparado para ingresar al módulo "
            "Uywa Pet Nutrition."
        )
    else:
        st.warning(
            "El usuario está autenticado, pero no tiene acceso efectivo "
            "a Uywa Pet Nutrition."
        )

    render_logout_button()


def render_logout_button() -> None:
    """
    Renderiza y procesa el cierre de sesión.
    """

    if not st.button(
        "Cerrar sesión",
        use_container_width=True,
    ):
        return

    try:
        success, message = sign_out()

    except Exception as exc:
        success = False
        message = (
            "No fue posible cerrar la sesión remota de Supabase: "
            f"{exc}"
        )

    clear_local_auth_state()

    if success:
        st.success(message)
    else:
        st.warning(
            message
            or (
                "La sesión local fue cerrada, aunque Supabase no "
                "confirmó el cierre remoto."
            )
        )

    st.rerun()


def restore_existing_session() -> None:
    """
    Intenta reconocer una sesión existente en el cliente de Supabase.

    Si encuentra un usuario, también construye el CurrentUser de Uywa
    Platform.
    """

    if st.session_state.get(
        "supabase_authenticated",
        False,
    ):
        ensure_platform_user_loaded()
        return

    try:
        auth_user = get_auth_user()

    except Exception:
        auth_user = None

    if auth_user is None:
        return

    user_id = getattr(auth_user, "id", None)

    if not user_id:
        return

    store_authenticated_user(auth_user)
    load_platform_user(auth_user)


def main() -> None:
    """
    Punto de entrada de la prueba.
    """

    initialize_session_state()
    restore_existing_session()

    if st.session_state.get(
        "supabase_authenticated",
        False,
    ):
        render_authenticated_user()
    else:
        render_login()


if __name__ == "__main__":
    main()
