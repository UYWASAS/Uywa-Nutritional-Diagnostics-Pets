from datetime import date
import streamlit as st


_DEFAULT_USERS = {
    "demo": {
        "name": "Demo Uywa",
        "password": "UywaDemo2026",
        "plan": "Demo",
        "premium": False,
        "active": True,
        "expires": "2026-07-15",
    },
    "cliente_profesional": {
        "name": "Cliente Profesional",
        "password": "UywaPro2026",
        "plan": "Profesional",
        "premium": True,
        "active": True,
        "expires": "2026-12-31",
    },
    "admin": {
        "name": "Admin",
        "password": "adminpass",
        "plan": "Admin",
        "premium": True,
        "active": True,
        "expires": None,
    },
}


def get_users_db():
    """
    Retorna usuarios desde st.secrets si existen.
    Si no existen, usa _DEFAULT_USERS.
    """
    try:
        users = st.secrets.get("USERS", None)

        if users:
            return dict(users)

    except Exception:
        pass

    return _DEFAULT_USERS


def is_user_active(user):
    """Valida si el usuario está activo y no vencido."""
    if not user.get("active", False):
        return False, "El usuario se encuentra inactivo."

    expires = user.get("expires")

    if expires:
        try:
            expires_date = date.fromisoformat(str(expires))

            if date.today() > expires_date:
                return False, f"El acceso venció el {expires_date.isoformat()}."

        except Exception:
            return False, "La fecha de expiración del usuario no es válida."

    return True, ""


USERS_DB = get_users_db()
