import streamlit as st

from supabase import Client, create_client


def get_supabase() -> Client:
    """
    Crea y devuelve un cliente de Supabase usando los secretos
    configurados en Streamlit Cloud.
    """
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]

    except KeyError as exc:
        raise RuntimeError(
            f"Falta configurar el secreto {exc} en Streamlit Cloud."
        ) from exc

    if not str(url).strip():
        raise RuntimeError("SUPABASE_URL está vacío.")

    if not str(key).strip():
        raise RuntimeError("SUPABASE_KEY está vacío.")

    return create_client(str(url).strip(), str(key).strip())
