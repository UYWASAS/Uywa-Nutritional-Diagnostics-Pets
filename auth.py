# Credenciales por defecto (usadas si no hay st.secrets disponibles)
_DEFAULT_USERS = {
    "demo": {"name": "Demo", "password": "1234", "premium": False},
    "admin": {"name": "Admin", "password": "adminpass", "premium": True},
}

# Alias público para que otros módulos puedan importar USERS_DB
USERS_DB = _DEFAULT_USERS
