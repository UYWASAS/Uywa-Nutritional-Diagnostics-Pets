import streamlit as st

from services.supabase_client import get_supabase


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
