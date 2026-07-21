import streamlit as st

from services.auth_service import get_auth_user, sign_in, sign_out


st.set_page_config(
    page_title="Prueba de autenticación | Uywa",
    page_icon="🔐",
    layout="centered",
)


def initialize_session_state() -> None:
    """
    Inicializa las variables utilizadas solamente por esta prueba.
    """
    defaults = {
        "supabase_authenticated": False,
        "supabase_user_id": None,
        "supabase_user_email": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_local_auth_state() -> None:
    """
    Limpia únicamente el estado local de autenticación de esta prueba.
    """
    st.session_state["supabase_authenticated"] = False
    st.session_state["supabase_user_id"] = None
    st.session_state["supabase_user_email"] = None


def render_login() -> None:
    """
    Renderiza el formulario de inicio de sesión.
    """
    st.title("🔐 Acceso a Uywa")

    st.write(
        "Esta pantalla prueba la conexión entre Streamlit y "
        "Supabase Auth. No modifica la aplicación principal."
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

    with st.spinner("Verificando credenciales..."):
        result = sign_in(email=email, password=password)

    if not result["success"]:
        st.error(result["message"])
        return

    user = result["user"]

    user_id = getattr(user, "id", None)
    user_email = getattr(user, "email", None)

    st.session_state["supabase_authenticated"] = True
    st.session_state["supabase_user_id"] = str(user_id) if user_id else None
    st.session_state["supabase_user_email"] = user_email

    st.success("Inicio de sesión correcto.")
    st.rerun()


def render_authenticated_user() -> None:
    """
    Muestra información mínima del usuario autenticado.
    """
    st.title("✅ Autenticación correcta")

    st.success(
        "Streamlit se conectó correctamente con Supabase Auth."
    )

    st.subheader("Usuario autenticado")

    st.write(
        f"**Correo:** "
        f"{st.session_state.get('supabase_user_email') or 'No disponible'}"
    )

    st.write(
        f"**ID del usuario:** "
        f"`{st.session_state.get('supabase_user_id') or 'No disponible'}`"
    )

    st.info(
        "En el siguiente paso utilizaremos este identificador para "
        "crear el perfil, la suscripción y el acceso al módulo "
        "Uywa Pet Nutrition."
    )

    if st.button(
        "Cerrar sesión",
        use_container_width=True,
    ):
        success, message = sign_out()
        clear_local_auth_state()

        if success:
            st.success(message)
        else:
            st.warning(message)

        st.rerun()


def restore_existing_session() -> None:
    """
    Intenta reconocer una sesión ya existente en el cliente de Supabase.

    Esta verificación es complementaria. La sesión principal de la prueba
    continúa controlándose mediante st.session_state.
    """
    if st.session_state["supabase_authenticated"]:
        return

    user = get_auth_user()

    if user is None:
        return

    user_id = getattr(user, "id", None)
    user_email = getattr(user, "email", None)

    if user_id:
        st.session_state["supabase_authenticated"] = True
        st.session_state["supabase_user_id"] = str(user_id)
        st.session_state["supabase_user_email"] = user_email


def main() -> None:
    initialize_session_state()
    restore_existing_session()

    if st.session_state["supabase_authenticated"]:
        render_authenticated_user()
    else:
        render_login()


if __name__ == "__main__":
    main()
