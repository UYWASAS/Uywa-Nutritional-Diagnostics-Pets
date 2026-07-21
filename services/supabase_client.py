import streamlit as st

from supabase import Client, create_client


def get_supabase() -> Client:
    """
    Crea y devuelve un cliente de Supabase usando los secretos
    configurados en Streamlit Cloud.
    """
    try:
        url = st.secrets["https://olujwxbbqwurylbeijoj.supabase.co"]
        key = st.secrets["sb_publishable_mFsEw7Bxpms-fgVpTwya5A_ypaEQ8T5"]

    except KeyError as exc:
        raise RuntimeError(
            f"Falta configurar el secreto {exc} en Streamlit Cloud."
        ) from exc

    if not str(url).strip():
        raise RuntimeError("SUPABASE_URL está vacío.")

    if not str(key).strip():
        raise RuntimeError("SUPABASE_KEY está vacío.")

    return create_client(str(url).strip(), str(key).strip())
