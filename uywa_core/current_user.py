from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class CurrentUser:
    """
    Representa al usuario autenticado dentro de Uywa Platform.

    Este objeto no depende directamente de Streamlit ni de Supabase.
    Los servicios externos deben obtener los datos y construir una
    instancia de CurrentUser.
    """

    # Identidad
    id: str | None = None
    email: str = ""
    full_name: str = ""
    role: str = "viewer"

    # Estado general
    authenticated: bool = False
    active: bool = False
    ready: bool = False

    # Información comercial
    plan_code: str | None = None
    plan_name: str | None = None
    subscription_id: str | None = None
    subscription_status: str | None = None
    subscription_starts_at: str | None = None
    subscription_expires_at: str | None = None

    # Acceso por módulos y permisos
    modules: list[str] = field(default_factory=list)
    permissions: dict[str, bool] = field(default_factory=dict)

    # Límites comerciales efectivos
    limits: dict[str, int | float | None] = field(default_factory=dict)

    # Organización futura
    organization_id: str | None = None
    organization_name: str | None = None

    # Información adicional que no requiera un campo específico
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def anonymous(cls) -> "CurrentUser":
        """
        Devuelve un usuario no autenticado.

        Se utiliza como valor seguro inicial antes de iniciar sesión.
        """
        return cls(
            authenticated=False,
            active=False,
            ready=False,
            role="viewer",
        )

    @property
    def username(self) -> str:
        """
        Alias compatible con partes antiguas de Pet Nutrition.

        Mientras se completa la migración, el correo se utiliza como
        nombre de usuario.
        """
        return self.email

    @property
    def name(self) -> str:
        """
        Alias compatible con la estructura anterior de usuario.
        """
        return self.full_name or self.email

    @property
    def is_admin(self) -> bool:
        """
        Indica si el usuario posee un rol administrativo.
        """
        return self.role in {
            "super_admin",
            "organization_admin",
            "admin",
        }

    @property
    def premium(self) -> bool:
        """
        Compatibilidad temporal con el sistema antiguo.

        Un usuario se considera premium si:
        - es administrador, o
        - tiene una suscripción activa con al menos un módulo habilitado.
        """
        if self.is_admin:
            return True

        return (
            self.active
            and self.subscription_status == "active"
            and bool(self.modules)
        )

    @property
    def subscription_is_active(self) -> bool:
        """
        Verifica si la suscripción está activa y no ha expirado.

        Si no existe una fecha de expiración, se considera válida mientras
        el estado sea 'active'.
        """
        if self.subscription_status != "active":
            return False

        if not self.subscription_expires_at:
            return True

        expires_at = self._parse_datetime(self.subscription_expires_at)

        if expires_at is None:
            return False

        return expires_at > datetime.now(timezone.utc)

    def can_use(self, module_code: str) -> bool:
        """
        Comprueba si el usuario puede utilizar un módulo.

        Ejemplo:
            user.can_use("pet_nutrition")
        """
        if not self.authenticated or not self.active:
            return False

        if self.is_admin:
            return True

        if not self.subscription_is_active:
            return False

        normalized_code = str(module_code).strip().lower()

        normalized_modules = {
            str(module).strip().lower()
            for module in self.modules
        }

        return normalized_code in normalized_modules

    def has_permission(
        self,
        permission_code: str,
        default: bool = False,
    ) -> bool:
        """
        Comprueba un permiso concreto.

        Ejemplo:
            user.has_permission("can_export")
        """
        if not self.authenticated or not self.active:
            return False

        if self.is_admin:
            return True

        normalized_code = str(permission_code).strip()

        return bool(
            self.permissions.get(
                normalized_code,
                default,
            )
        )

    def get_limit(
        self,
        limit_code: str,
        default: int | float | None = None,
    ) -> int | float | None:
        """
        Devuelve el límite efectivo asociado al usuario.

        Ejemplo:
            user.get_limit("max_patients", 10)
        """
        return self.limits.get(limit_code, default)

    def to_dict(self) -> dict[str, Any]:
        """
        Convierte el usuario completo en un diccionario.
        """
        return asdict(self)

    def to_legacy_dict(self) -> dict[str, Any]:
        """
        Convierte CurrentUser al formato aproximado que espera la
        aplicación Pet Nutrition actual.

        Esto permitirá integrar el nuevo usuario sin modificar todas
        las páginas al mismo tiempo.
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "name": self.name,
            "full_name": self.full_name,
            "role": self.role,
            "plan": self.plan_code,
            "premium": self.premium,
            "active": self.active,
            "authenticated": self.authenticated,
            "modules": list(self.modules),
            "permissions": dict(self.permissions),
            "limits": dict(self.limits),
        }

    @staticmethod
    def _parse_datetime(value: str) -> datetime | None:
        """
        Convierte una fecha ISO 8601 en datetime con zona horaria.
        """
        try:
            normalized_value = str(value).strip()

            if normalized_value.endswith("Z"):
                normalized_value = (
                    normalized_value[:-1] + "+00:00"
                )

            parsed = datetime.fromisoformat(normalized_value)

            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)

            return parsed.astimezone(timezone.utc)

        except (TypeError, ValueError):
            return None
