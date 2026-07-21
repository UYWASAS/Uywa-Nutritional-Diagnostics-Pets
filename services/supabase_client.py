import os

from supabase import Client, create_client


def get_supabase() -> Client:
    """
    Devuelve un cliente de Supabase.
    """

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url:
        raise ValueError("No existe SUPABASE_URL")

    if not key:
        raise ValueError("No existe SUPABASE_KEY")

    return create_client(url, key)
