import streamlit as st

from services.supabase_client import get_supabase
from uywa_core.current_session import (
    clear_current_user,
    get_current_user,
    initialize_session,
    is_authenticated,
    set_current_user,
)
from uywa_core.current_user import CurrentUser

st.set_page_config(
    page_title="Prueba Supabase",
    layout="centered",
)

st.title("Prueba de conexión con Supabase")

try:
    supabase = get_supabase()

    st.success("Cliente de Supabase creado correctamente.")
    st.info(
        "La URL y la clave pública fueron leídas desde los secretos "
        "de Streamlit Cloud."
    )

except Exception as exc:
    st.error(f"Error de conexión: {exc}")
st.divider()
st.subheader("Prueba de Uywa Core")

initialize_session()

current_user = get_current_user()

st.write(
    {
        "authenticated": is_authenticated(),
        "user": current_user.to_dict(),
    }
)

if st.button("Crear usuario de prueba Core"):
    test_user = CurrentUser(
        id="test-user-001",
        email="prueba@uywanutrition.com",
        full_name="Usuario de prueba",
        role="super_admin",
        authenticated=True,
        active=True,
        ready=True,
        plan_code="admin",
        plan_name="Administrador",
        subscription_status="active",
        modules=["pet_nutrition"],
        permissions={
            "can_export": True,
            "can_compare": True,
        },
    )

    set_current_user(test_user)
    st.rerun()

if st.button("Cerrar sesión Core"):
    clear_current_user()
    st.rerun()
