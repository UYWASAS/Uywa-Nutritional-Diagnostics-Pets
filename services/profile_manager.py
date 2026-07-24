import json
import os
from datetime import datetime


PROFILE_VERSION = "1.0"
PROFILES_DIR = "profiles"


def ensure_profiles_dir():
    """
    Crea la carpeta de perfiles si no existe.
    """
    os.makedirs(PROFILES_DIR, exist_ok=True)


def sanitize_filename(text):
    """
    Convierte texto en nombre seguro para archivo.
    """
    safe = "".join(
        c if c.isalnum() or c in ("_", "-")
        else "_"
        for c in str(text)
    )

    return safe.strip("_")


def get_profile_path(user):
    """
    Devuelve la ruta completa del perfil.
    """
    ensure_profiles_dir()

    username = sanitize_filename(user["name"])

    return os.path.join(
        PROFILES_DIR,
        f"{username}_profile.json"
    )


def create_default_profile(user):
    """
    Perfil base compatible con la aplicación actual.
    """
    return {
        "profile_version": PROFILE_VERSION,
        "updated_at": datetime.now().isoformat(),
        "name": user["name"],
        "premium": user.get("premium", False),

        # Compatibilidad actual
        "mascota": {},

        # Futuro módulo clínico
        "pacientes": []
    }


def load_profile(user):
    """
    Carga perfil desde disco.
    """

    filepath = get_profile_path(user)

    if not os.path.exists(filepath):
        return create_default_profile(user)

    try:

        with open(filepath, "r", encoding="utf-8") as f:
            profile = json.load(f)

        # Compatibilidad hacia atrás
        if "mascota" not in profile:
            profile["mascota"] = {}

        if "pacientes" not in profile:
            profile["pacientes"] = []

        if "profile_version" not in profile:
            profile["profile_version"] = PROFILE_VERSION

        return profile

    except Exception as e:

        print(
            f"[PROFILE] Error cargando perfil: {e}"
        )

        return create_default_profile(user)


def save_profile(user, profile):
    """
    Guarda perfil en disco.
    """

    filepath = get_profile_path(user)

    profile["updated_at"] = datetime.now().isoformat()

    try:

        with open(filepath, "w", encoding="utf-8") as f:

            json.dump(
                profile,
                f,
                indent=4,
                ensure_ascii=False
            )

        return True

    except Exception as e:

        print(
            f"[PROFILE] Error guardando perfil: {e}"
        )

        return False
