from datetime import date


_DEFAULT_USERS = {
    "demo": {
        "name": "Demo Uywa",
        "password": "UywaDemo2026",
        "plan": "Demo",
        "role": "demo",
        "premium": False,
        "active": True,
        "expires": "2026-07-15",
    },
    "cliente_profesional": {
        "name": "Cliente Profesional",
        "password": "UywaPro2026",
        "plan": "Profesional",
        "role": "professional",
        "premium": True,
        "active": True,
        "expires": "2026-12-31",
    },
    "admin": {
        "name": "Admin",
        "password": "adminpass",
        "plan": "Admin",
        "role": "admin",
        "premium": True,
        "active": True,
        "expires": None,
    },
}


def normalize_username(username):
    """
    Normaliza el nombre de usuario para evitar errores por mayúsculas o espacios.
    """
    return str(username or "").strip().lower()


def is_user_active(user):
    """
    Valida si un usuario está activo y si su fecha de expiración sigue vigente.
    """
    if not user:
        return False, "El usuario no existe."

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


def authenticate_user(username, password):
    """
    Autentica usuario y contraseña.

    Retorna:
        tuple: (is_authenticated, user_data, message)
    """
    username_clean = normalize_username(username)
    user = USERS_DB.get(username_clean)

    if not user:
        return False, None, "Usuario o contraseña incorrectos."

    if user.get("password") != password:
        return False, None, "Usuario o contraseña incorrectos."

    is_active, message = is_user_active(user)

    if not is_active:
        return False, None, message

    return True, user, ""


def user_has_premium_access(user):
    """
    Indica si el usuario tiene acceso a funciones premium.
    """
    return bool(user and user.get("premium", False))


def user_is_admin(user):
    """
    Indica si el usuario tiene rol administrador.
    """
    return bool(user and user.get("role") == "admin")


def get_user_plan(user):
    """
    Devuelve el nombre del plan del usuario.
    """
    if not user:
        return "Sin plan"

    return user.get("plan", "Sin plan")


USERS_DB = _DEFAULT_USERS
