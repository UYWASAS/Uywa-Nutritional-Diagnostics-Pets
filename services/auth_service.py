from typing import Any

from services.supabase_client import get_supabase


def sign_in(email: str, password: str) -> dict[str, Any]:
    """
    Inicia sesión mediante Supabase Auth.

    Retorna:
        {
            "success": bool,
            "user": objeto usuario o None,
            "session": objeto sesión o None,
            "message": str,
        }
    """
    email_clean = str(email or "").strip().lower()
    password_clean = str(password or "")

    if not email_clean:
        return {
            "success": False,
            "user": None,
            "session": None,
            "message": "Ingresa tu correo electrónico.",
        }

    if not password_clean:
        return {
            "success": False,
            "user": None,
            "session": None,
            "message": "Ingresa tu contraseña.",
        }

    try:
        supabase = get_supabase()

        response = supabase.auth.sign_in_with_password(
            {
                "email": email_clean,
                "password": password_clean,
            }
        )

        user = getattr(response, "user", None)
        session = getattr(response, "session", None)

        if user is None or session is None:
            return {
                "success": False,
                "user": None,
                "session": None,
                "message": "No se pudo iniciar sesión.",
            }

        return {
            "success": True,
            "user": user,
            "session": session,
            "message": "Inicio de sesión correcto.",
        }

    except Exception as exc:
        message = str(exc)

        if "Invalid login credentials" in message:
            message = "Correo o contraseña incorrectos."
        elif "Email not confirmed" in message:
            message = "Debes confirmar tu correo antes de iniciar sesión."

        return {
            "success": False,
            "user": None,
            "session": None,
            "message": message,
        }


def sign_out() -> tuple[bool, str]:
    """
    Cierra la sesión actual de Supabase.
    """
    try:
        supabase = get_supabase()
        supabase.auth.sign_out()
        return True, "Sesión cerrada correctamente."

    except Exception as exc:
        return False, f"No se pudo cerrar la sesión: {exc}"


def get_auth_user():
    """
    Devuelve el usuario autenticado en el cliente actual, si existe.
    """
    try:
        supabase = get_supabase()
        response = supabase.auth.get_user()
        return getattr(response, "user", None)

    except Exception:
        return None
