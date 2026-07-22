from __future__ import annotations

from typing import Any

from services.session_manager import (
    clear_auth_session,
    has_saved_auth_session,
    save_auth_session,
    update_auth_session,
)
from services.supabase_client import (
    create_public_supabase_client,
    get_supabase,
)


def sign_in(
    email: str,
    password: str,
) -> dict[str, Any]:
    """
    Inicia sesión mediante Supabase Auth y guarda los tokens dentro de
    la sesión individual de Streamlit.

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
        supabase = create_public_supabase_client()

        response = supabase.auth.sign_in_with_password(
            {
                "email": email_clean,
                "password": password_clean,
            }
        )

        user = getattr(response, "user", None)
        session = getattr(response, "session", None)

        if user is None or session is None:
            clear_auth_session()

            return {
                "success": False,
                "user": None,
                "session": None,
                "message": "No se pudo iniciar sesión.",
            }

        save_auth_session(
            session=session,
            user=user,
        )

        return {
            "success": True,
            "user": user,
            "session": session,
            "message": "Inicio de sesión correcto.",
        }

    except Exception as exc:
        clear_auth_session()

        message = str(exc)

        if "Invalid login credentials" in message:
            message = "Correo o contraseña incorrectos."

        elif "Email not confirmed" in message:
            message = (
                "Debes confirmar tu correo antes de iniciar sesión."
            )

        return {
            "success": False,
            "user": None,
            "session": None,
            "message": message,
        }


def restore_auth_session() -> dict[str, Any]:
    """
    Restaura la sesión autenticada usando los tokens guardados.

    Retorna una estructura similar a sign_in().
    """

    if not has_saved_auth_session():
        return {
            "success": False,
            "user": None,
            "session": None,
            "message": "No existe una sesión guardada.",
        }

    try:
        supabase = get_supabase()

        session_response = supabase.auth.get_session()
        session = getattr(session_response, "session", None)

        user_response = supabase.auth.get_user()
        user = getattr(user_response, "user", None)

        if user is None:
            clear_auth_session()

            return {
                "success": False,
                "user": None,
                "session": None,
                "message": "La sesión guardada ya no es válida.",
            }

        if session is not None:
            update_auth_session(session)

        return {
            "success": True,
            "user": user,
            "session": session,
            "message": "Sesión restaurada correctamente.",
        }

    except Exception as exc:
        clear_auth_session()

        return {
            "success": False,
            "user": None,
            "session": None,
            "message": (
                "No fue posible restaurar la sesión: "
                f"{exc}"
            ),
        }


def sign_out() -> tuple[bool, str]:
    """
    Cierra la sesión remota de Supabase y elimina los tokens locales.
    """

    remote_success = True
    remote_message = "Sesión cerrada correctamente."

    try:
        if has_saved_auth_session():
            supabase = get_supabase()
            supabase.auth.sign_out()

    except Exception as exc:
        remote_success = False
        remote_message = (
            "La sesión local fue cerrada, pero Supabase no confirmó "
            f"el cierre remoto: {exc}"
        )

    finally:
        clear_auth_session()

    return remote_success, remote_message


def get_auth_user():
    """
    Devuelve el usuario autenticado de la sesión actual, si existe.
    """

    if not has_saved_auth_session():
        return None

    try:
        supabase = get_supabase()

        response = supabase.auth.get_user()
        user = getattr(response, "user", None)

        if user is None:
            clear_auth_session()
            return None

        return user

    except Exception:
        clear_auth_session()
        return None
