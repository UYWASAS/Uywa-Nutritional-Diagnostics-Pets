from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from services.supabase_client import get_supabase
from uywa_core.current_user import CurrentUser


ACTIVE_SUBSCRIPTION_STATUSES = {
    "active",
    "trial",
    "trialing",
}


class UserServiceError(RuntimeError):
    """Error al construir el usuario de Uywa Platform."""


def load_current_user(
    auth_user: Any,
) -> CurrentUser:
    """
    Construye un CurrentUser a partir del usuario autenticado en Supabase.

    Consulta:

    - profiles
    - subscriptions
    - plans
    - subscription_modules
    - modules

    Parameters
    ----------
    auth_user:
        Usuario devuelto por Supabase Auth. Debe tener al menos:
        - id
        - email

    Returns
    -------
    CurrentUser
        Usuario completo de Uywa Platform.
    """

    if auth_user is None:
        return CurrentUser.anonymous()

    user_id = _get_value(auth_user, "id")
    email = _get_value(auth_user, "email", "")

    if not user_id:
        raise UserServiceError(
            "El usuario autenticado no contiene un identificador."
        )

    supabase = get_supabase()

    try:
        profile = _load_profile(
            supabase=supabase,
            user_id=str(user_id),
        )

        subscription = _load_subscription(
            supabase=supabase,
            user_id=str(user_id),
        )

        plan = None
        modules: list[str] = []

        if subscription:
            plan_id = subscription.get("plan_id")

            if plan_id:
                plan = _load_plan(
                    supabase=supabase,
                    plan_id=str(plan_id),
                )

            subscription_id = subscription.get("id")

            if subscription_id:
                modules = _load_subscription_modules(
                    supabase=supabase,
                    subscription_id=str(subscription_id),
                )

        role = str(
            profile.get("role", "viewer")
            if profile
            else "viewer"
        ).strip()

        active = _resolve_profile_active(profile)

        full_name = _resolve_full_name(
            profile=profile,
            email=str(email or ""),
        )

        plan_code = _first_available(
            plan,
            "code",
            "plan_code",
            "slug",
        )

        plan_name = _first_available(
            plan,
            "name",
            "plan_name",
            "display_name",
        )

        permissions = _build_initial_permissions(
            role=role,
            plan=plan,
            modules=modules,
        )

        limits = _build_effective_limits(
            plan=plan,
            subscription=subscription,
        )

        subscription_status = (
            subscription.get("status")
            if subscription
            else None
        )

        current_user = CurrentUser(
            id=str(user_id),
            email=str(email or ""),
            full_name=full_name,
            role=role,
            authenticated=True,
            active=active,
            ready=True,
            plan_code=_as_optional_string(plan_code),
            plan_name=_as_optional_string(plan_name),
            subscription_id=_as_optional_string(
                subscription.get("id")
                if subscription
                else None
            ),
            subscription_status=_as_optional_string(
                subscription_status
            ),
            subscription_starts_at=_as_optional_string(
                subscription.get("starts_at")
                if subscription
                else None
            ),
            subscription_expires_at=_as_optional_string(
                subscription.get("expires_at")
                if subscription
                else None
            ),
            modules=modules,
            permissions=permissions,
            limits=limits,
            organization_id=_as_optional_string(
                profile.get("organization_id")
                if profile
                else None
            ),
            organization_name=None,
            metadata={
                "profile_loaded": bool(profile),
                "subscription_loaded": bool(subscription),
                "plan_loaded": bool(plan),
            },
        )

        return current_user

    except UserServiceError:
        raise

    except Exception as exc:
        raise UserServiceError(
            "No fue posible cargar el usuario completo desde Supabase."
        ) from exc


def _load_profile(
    supabase: Any,
    user_id: str,
) -> dict[str, Any] | None:
    response = (
        supabase.table("profiles")
        .select("*")
        .eq("id", user_id)
        .limit(1)
        .execute()
    )

    return _first_row(response)


def _load_subscription(
    supabase: Any,
    user_id: str,
) -> dict[str, Any] | None:
    response = (
        supabase.table("subscriptions")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )

    rows = _response_rows(response)

    if not rows:
        return None

    # Primero intenta encontrar una suscripción vigente.
    for subscription in rows:
        if _subscription_is_usable(subscription):
            return subscription

    # Si ninguna está vigente, conserva la más reciente para mostrar
    # correctamente su estado en la plataforma.
    return rows[0]


def _load_plan(
    supabase: Any,
    plan_id: str,
) -> dict[str, Any] | None:
    response = (
        supabase.table("plans")
        .select("*")
        .eq("id", plan_id)
        .limit(1)
        .execute()
    )

    return _first_row(response)


def _load_subscription_modules(
    supabase: Any,
    subscription_id: str,
) -> list[str]:
    response = (
        supabase.table("subscription_modules")
        .select("*")
        .eq("subscription_id", subscription_id)
        .eq("active", True)
        .execute()
    )

    module_assignments = _response_rows(response)

    if not module_assignments:
        return []

    module_ids = [
        str(row["module_id"])
        for row in module_assignments
        if row.get("module_id")
        and _module_assignment_is_usable(row)
    ]

    if not module_ids:
        return []

    modules_response = (
        supabase.table("modules")
        .select("*")
        .in_("id", module_ids)
        .execute()
    )

    module_rows = _response_rows(modules_response)

    module_codes: list[str] = []

    for module in module_rows:
        code = _first_available(
            module,
            "code",
            "module_code",
            "slug",
        )

        if code:
            normalized_code = str(code).strip().lower()

            if normalized_code not in module_codes:
                module_codes.append(normalized_code)

    return module_codes


def _build_initial_permissions(
    role: str,
    plan: dict[str, Any] | None,
    modules: list[str],
) -> dict[str, bool]:
    """
    Genera permisos iniciales.

    Posteriormente esta lógica se moverá y ampliará en
    permission_service.py.
    """

    normalized_role = str(role).strip().lower()

    if normalized_role in {
        "super_admin",
        "organization_admin",
        "admin",
    }:
        return {
            "can_export": True,
            "can_compare": True,
            "can_create_patient": True,
            "can_save_patient": True,
            "can_use_followup": True,
            "can_manage_users": True,
        }

    permissions = {
        "can_export": False,
        "can_compare": "pet_nutrition" in modules,
        "can_create_patient": "pet_nutrition" in modules,
        "can_save_patient": False,
        "can_use_followup": False,
        "can_manage_users": False,
    }

    if not plan:
        return permissions

    # Permite utilizar columnas booleanas del plan si existen.
    for permission_code in list(permissions):
        if permission_code in plan:
            permissions[permission_code] = bool(
                plan.get(permission_code)
            )

    return permissions


def _build_effective_limits(
    plan: dict[str, Any] | None,
    subscription: dict[str, Any] | None,
) -> dict[str, int | float | None]:
    """
    Combina límites del plan con posibles overrides de la suscripción.

    Solo incorpora columnas presentes en la base.
    """

    result: dict[str, int | float | None] = {}

    common_limits = [
        "max_patients",
        "max_users",
        "max_exports",
        "max_comparisons",
        "max_reports",
    ]

    for limit_code in common_limits:
        plan_value = (
            plan.get(limit_code)
            if plan
            else None
        )

        override_keys = [
            f"override_{limit_code}",
            f"{limit_code}_override",
        ]

        override_value = None

        if subscription:
            for override_key in override_keys:
                if subscription.get(override_key) is not None:
                    override_value = subscription.get(
                        override_key
                    )
                    break

        effective_value = (
            override_value
            if override_value is not None
            else plan_value
        )

        if effective_value is not None:
            result[limit_code] = effective_value

    return result


def _resolve_profile_active(
    profile: dict[str, Any] | None,
) -> bool:
    if not profile:
        return False

    if "active" in profile:
        return bool(profile.get("active"))

    if "is_active" in profile:
        return bool(profile.get("is_active"))

    # Si la tabla no posee una columna de estado, la existencia del
    # perfil se considera suficiente temporalmente.
    return True


def _resolve_full_name(
    profile: dict[str, Any] | None,
    email: str,
) -> str:
    if profile:
        full_name = _first_available(
            profile,
            "full_name",
            "name",
            "display_name",
        )

        if full_name:
            return str(full_name).strip()

        first_name = str(
            profile.get("first_name") or ""
        ).strip()

        last_name = str(
            profile.get("last_name") or ""
        ).strip()

        combined_name = " ".join(
            part
            for part in [first_name, last_name]
            if part
        )

        if combined_name:
            return combined_name

    return email


def _subscription_is_usable(
    subscription: dict[str, Any],
) -> bool:
    status = str(
        subscription.get("status") or ""
    ).strip().lower()

    if status not in ACTIVE_SUBSCRIPTION_STATUSES:
        return False

    starts_at = subscription.get("starts_at")

    if starts_at:
        parsed_start = _parse_datetime(starts_at)

        if (
            parsed_start is not None
            and parsed_start > datetime.now(timezone.utc)
        ):
            return False

    expires_at = subscription.get("expires_at")

    if expires_at:
        parsed_expiration = _parse_datetime(expires_at)

        if (
            parsed_expiration is None
            or parsed_expiration <= datetime.now(timezone.utc)
        ):
            return False

    return True


def _module_assignment_is_usable(
    assignment: dict[str, Any],
) -> bool:
    if assignment.get("active") is False:
        return False

    starts_at = assignment.get("starts_at")

    if starts_at:
        parsed_start = _parse_datetime(starts_at)

        if (
            parsed_start is not None
            and parsed_start > datetime.now(timezone.utc)
        ):
            return False

    expires_at = assignment.get("expires_at")

    if expires_at:
        parsed_expiration = _parse_datetime(expires_at)

        if (
            parsed_expiration is None
            or parsed_expiration <= datetime.now(timezone.utc)
        ):
            return False

    return True


def _response_rows(
    response: Any,
) -> list[dict[str, Any]]:
    data = getattr(response, "data", None)

    if not isinstance(data, list):
        return []

    return [
        row
        for row in data
        if isinstance(row, dict)
    ]


def _first_row(
    response: Any,
) -> dict[str, Any] | None:
    rows = _response_rows(response)

    if not rows:
        return None

    return rows[0]


def _get_value(
    source: Any,
    key: str,
    default: Any = None,
) -> Any:
    if isinstance(source, dict):
        return source.get(key, default)

    return getattr(source, key, default)


def _first_available(
    source: dict[str, Any] | None,
    *keys: str,
) -> Any:
    if not source:
        return None

    for key in keys:
        value = source.get(key)

        if value not in (None, ""):
            return value

    return None


def _as_optional_string(
    value: Any,
) -> str | None:
    if value is None:
        return None

    normalized = str(value).strip()

    return normalized or None


def _parse_datetime(
    value: Any,
) -> datetime | None:
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
