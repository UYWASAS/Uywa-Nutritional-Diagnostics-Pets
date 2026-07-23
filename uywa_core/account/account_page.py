from __future__ import annotations

import html
from typing import Any, Iterable

import streamlit as st

from uywa_core.current_user import CurrentUser
from uywa_core.theme.html_utils import clean_html


def _has_value(value: Any) -> bool:
    """
    Determina si un valor puede mostrarse.
    """

    return value not in (
        None,
        "",
        [],
        {},
        (),
        set(),
    )


def _get_value(
    current_user: CurrentUser,
    *keys: str,
) -> Any:
    """
    Busca un valor en:

    1. Propiedades directas de CurrentUser.
    2. El diccionario profile.
    3. El diccionario metadata.
    """

    for key in keys:
        direct_value = getattr(
            current_user,
            key,
            None,
        )

        if _has_value(direct_value):
            return direct_value

    profile = getattr(
        current_user,
        "profile",
        None,
    )

    if isinstance(profile, dict):
        for key in keys:
            profile_value = profile.get(key)

            if _has_value(profile_value):
                return profile_value

    metadata = getattr(
        current_user,
        "metadata",
        None,
    )

    if isinstance(metadata, dict):
        for key in keys:
            metadata_value = metadata.get(key)

            if _has_value(metadata_value):
                return metadata_value

    return None


def _safe_text(
    value: Any,
    fallback: str = "No disponible",
) -> str:
    """
    Convierte un valor en texto seguro para HTML.
    """

    if not _has_value(value):
        return html.escape(fallback)

    return html.escape(
        str(value)
    )


def _normalize_label(
    value: Any,
    fallback: str = "No disponible",
) -> str:
    """
    Convierte códigos internos en etiquetas legibles.
    """

    if not _has_value(value):
        return fallback

    return (
        str(value)
        .strip()
        .replace("_", " ")
        .replace("-", " ")
        .title()
    )


def _format_date(
    value: Any,
    fallback: str = "No disponible",
) -> str:
    """
    Normaliza una fecha ISO para mostrar solo YYYY-MM-DD.
    """

    if not _has_value(value):
        return fallback

    value_text = str(value).strip()

    if "T" in value_text:
        return value_text.split(
            "T",
            1,
        )[0]

    if " " in value_text:
        possible_date = value_text.split(
            " ",
            1,
        )[0]

        if len(possible_date) >= 10:
            return possible_date[:10]

    return value_text[:10]


def _get_user_name(
    current_user: CurrentUser,
) -> str:
    """
    Obtiene el nombre visible del usuario.
    """

    return str(
        _get_value(
            current_user,
            "full_name",
            "display_name",
            "name",
        )
        or _get_value(
            current_user,
            "email",
        )
        or "Usuario"
    )


def _get_user_email(
    current_user: CurrentUser,
) -> str:
    """
    Obtiene el correo del usuario.
    """

    return str(
        _get_value(
            current_user,
            "email",
        )
        or "Correo no disponible"
    )


def _get_user_role(
    current_user: CurrentUser,
) -> str:
    """
    Obtiene el rol del usuario.
    """

    role = _get_value(
        current_user,
        "role",
        "user_role",
    )

    return _normalize_label(
        role,
        "Usuario",
    )


def _get_organization(
    current_user: CurrentUser,
) -> str:
    """
    Obtiene la organización o institución del usuario.
    """

    organization = _get_value(
        current_user,
        "organization_name",
        "organization",
        "company",
        "company_name",
        "institution",
        "institution_name",
    )

    return str(
        organization
        or "Sin organización registrada"
    )


def _get_plan_name(
    current_user: CurrentUser,
) -> str:
    """
    Obtiene el nombre o código del plan.
    """

    direct_plan = _get_value(
        current_user,
        "plan_name",
        "plan_code",
    )

    if _has_value(direct_plan):
        return str(direct_plan)

    plan = getattr(
        current_user,
        "plan",
        None,
    )

    if isinstance(plan, dict):
        return str(
            plan.get("name")
            or plan.get("title")
            or plan.get("code")
            or "Sin plan asignado"
        )

    if plan is not None:
        return str(
            getattr(plan, "name", None)
            or getattr(plan, "title", None)
            or getattr(plan, "code", None)
            or "Sin plan asignado"
        )

    return "Sin plan asignado"


def _get_subscription_status(
    current_user: CurrentUser,
) -> str:
    """
    Obtiene el estado visible de la suscripción.
    """

    subscription = getattr(
        current_user,
        "subscription",
        None,
    )

    if isinstance(subscription, dict):
        status = subscription.get(
            "status"
        )

        if _has_value(status):
            normalized_status = str(
                status
            ).strip().lower()

            status_labels = {
                "active": "Activa",
                "trial": "Prueba",
                "demo": "Demo",
                "enabled": "Activa",
                "inactive": "No activa",
                "disabled": "Desactivada",
                "expired": "Vencida",
                "cancelled": "Cancelada",
                "canceled": "Cancelada",
                "pending": "Pendiente",
            }

            return status_labels.get(
                normalized_status,
                _normalize_label(
                    status,
                    "No activa",
                ),
            )

        if "active" in subscription:
            return (
                "Activa"
                if bool(subscription["active"])
                else "No activa"
            )

    explicit_status = _get_value(
        current_user,
        "subscription_status",
    )

    if _has_value(explicit_status):
        return _normalize_label(
            explicit_status,
            "No activa",
        )

    explicit_active = getattr(
        current_user,
        "subscription_is_active",
        None,
    )

    if explicit_active is not None:
        return (
            "Activa"
            if bool(explicit_active)
            else "No activa"
        )

    active = getattr(
        current_user,
        "active",
        None,
    )

    if active is not None:
        return (
            "Activa"
            if bool(active)
            else "No activa"
        )

    return "No disponible"


def _get_expiration(
    current_user: CurrentUser,
) -> str:
    """
    Obtiene la fecha de finalización de la suscripción.
    """

    possible_keys = (
        "subscription_expires_at",
        "expires_at",
        "end_date",
        "subscription_end_date",
        "valid_until",
    )

    direct_value = _get_value(
        current_user,
        *possible_keys,
    )

    if _has_value(direct_value):
        return _format_date(
            direct_value
        )

    subscription = getattr(
        current_user,
        "subscription",
        None,
    )

    if isinstance(subscription, dict):
        for key in possible_keys:
            subscription_value = subscription.get(
                key
            )

            if _has_value(subscription_value):
                return _format_date(
                    subscription_value
                )

    return "No disponible"


def _get_subscription_start(
    current_user: CurrentUser,
) -> str:
    """
    Obtiene la fecha inicial de la suscripción.
    """

    possible_keys = (
        "subscription_starts_at",
        "starts_at",
        "start_date",
        "subscription_start_date",
        "valid_from",
    )

    direct_value = _get_value(
        current_user,
        *possible_keys,
    )

    if _has_value(direct_value):
        return _format_date(
            direct_value
        )

    subscription = getattr(
        current_user,
        "subscription",
        None,
    )

    if isinstance(subscription, dict):
        for key in possible_keys:
            subscription_value = subscription.get(
                key
            )

            if _has_value(subscription_value):
                return _format_date(
                    subscription_value
                )

    return "No disponible"


def _extract_module_name(
    module: Any,
) -> str | None:
    """
    Extrae el nombre visible de un módulo.
    """

    if isinstance(module, str):
        return module.strip() or None

    if isinstance(module, dict):
        value = (
            module.get("name")
            or module.get("title")
            or module.get("display_name")
            or module.get("code")
            or module.get("module_code")
        )

        if _has_value(value):
            return str(value)

        nested_module = module.get(
            "module"
        )

        if nested_module is not None:
            return _extract_module_name(
                nested_module
            )

        return None

    value = (
        getattr(module, "name", None)
        or getattr(module, "title", None)
        or getattr(module, "display_name", None)
        or getattr(module, "code", None)
        or getattr(module, "module_code", None)
    )

    if _has_value(value):
        return str(value)

    nested_module = getattr(
        module,
        "module",
        None,
    )

    if nested_module is not None:
        return _extract_module_name(
            nested_module
        )

    return None


def _normalize_module_source(
    source: Any,
) -> Iterable[Any]:
    """
    Convierte distintas estructuras de módulos en
    una colección iterable.
    """

    if not _has_value(source):
        return []

    if isinstance(source, dict):
        if any(
            key in source
            for key in (
                "name",
                "title",
                "code",
                "module_code",
                "module",
            )
        ):
            return [source]

        return list(
            source.values()
        )

    if isinstance(
        source,
        (list, tuple, set),
    ):
        return source

    return [source]


def _get_enabled_modules(
    current_user: CurrentUser,
) -> list[str]:
    """
    Obtiene los módulos habilitados del usuario.
    """

    possible_sources = (
        getattr(
            current_user,
            "modules",
            None,
        ),
        getattr(
            current_user,
            "enabled_modules",
            None,
        ),
        getattr(
            current_user,
            "subscription_modules",
            None,
        ),
        _get_value(
            current_user,
            "modules",
            "enabled_modules",
            "subscription_modules",
        ),
    )

    module_names: list[str] = []

    for source in possible_sources:
        for module in _normalize_module_source(
            source
        ):
            module_name = _extract_module_name(
                module
            )

            if not module_name:
                continue

            normalized_name = (
                module_name
                .strip()
                .replace("_", " ")
            )

            if normalized_name:
                module_names.append(
                    normalized_name
                )

    unique_modules: list[str] = []
    known_modules: set[str] = set()

    for module_name in module_names:
        module_key = module_name.casefold()

        if module_key in known_modules:
            continue

        known_modules.add(
            module_key
        )

        unique_modules.append(
            module_name
        )

    return unique_modules


def _inject_account_styles() -> None:
    """
    Inserta los estilos de la página Mi cuenta.
    """

    st.markdown(
        clean_html(
            """
            <style>
                .uywa-account-page {
                    padding-bottom: 1rem;
                }

                .uywa-account-hero {
                    position: relative;
                    overflow: hidden;
                    padding: 1.7rem 1.85rem;
                    margin-bottom: 1.4rem;
                    border:
                        1px solid
                        rgba(255, 255, 255, 0.10);
                    border-radius: 21px;
                    background:
                        linear-gradient(
                            135deg,
                            #17233F 0%,
                            #22485B 58%,
                            #28777E 100%
                        );
                    box-shadow:
                        0 14px 34px
                        rgba(23, 35, 63, 0.15);
                }

                .uywa-account-hero::after {
                    content: "";
                    position: absolute;
                    top: -85px;
                    right: -65px;
                    width: 225px;
                    height: 225px;
                    border-radius: 50%;
                    background:
                        rgba(101, 190, 198, 0.12);
                }

                .uywa-account-hero-content {
                    position: relative;
                    z-index: 1;
                }

                .uywa-account-eyebrow {
                    color: #8FD5DA;
                    font-size: 0.7rem;
                    font-weight: 850;
                    letter-spacing: 0.14em;
                }

                .uywa-account-title {
                    margin-top: 0.32rem;
                    color: #FFFFFF;
                    font-size: 2rem;
                    font-weight: 850;
                    line-height: 1.18;
                }

                .uywa-account-subtitle {
                    max-width: 660px;
                    margin-top: 0.58rem;
                    color:
                        rgba(255, 255, 255, 0.80);
                    font-size: 0.89rem;
                    line-height: 1.55;
                }

                .uywa-account-card {
                    min-height: 100%;
                    padding: 1.25rem 1.3rem;
                    border: 1px solid #DDE3EC;
                    border-radius: 17px;
                    background: #FFFFFF;
                    box-shadow:
                        0 8px 24px
                        rgba(23, 35, 63, 0.06);
                }

                .uywa-account-card-label {
                    margin-bottom: 0.82rem;
                    color: #28777E;
                    font-size: 0.69rem;
                    font-weight: 850;
                    letter-spacing: 0.12em;
                }

                .uywa-account-row {
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    gap: 1rem;
                    padding: 0.72rem 0;
                    border-bottom: 1px solid #EDF1F5;
                    color: #667085;
                    font-size: 0.82rem;
                    line-height: 1.45;
                }

                .uywa-account-row:last-child {
                    border-bottom: none;
                }

                .uywa-account-row span {
                    flex: 0 0 38%;
                }

                .uywa-account-row strong {
                    flex: 1;
                    color: #17233F;
                    font-weight: 750;
                    text-align: right;
                    overflow-wrap: anywhere;
                }

                .uywa-account-status {
                    display: inline-flex;
                    align-items: center;
                    justify-content: flex-end;
                    gap: 0.4rem;
                }

                .uywa-account-status-dot {
                    width: 8px;
                    height: 8px;
                    flex: 0 0 8px;
                    border-radius: 50%;
                    background: #59D2A2;
                    box-shadow:
                        0 0 0 3px
                        rgba(89, 210, 162, 0.14);
                }

                .uywa-account-modules {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 0.48rem;
                }

                .uywa-account-module {
                    display: inline-flex;
                    align-items: center;
                    padding: 0.43rem 0.74rem;
                    border:
                        1px solid
                        rgba(40, 119, 126, 0.13);
                    border-radius: 999px;
                    background: #EFF8F8;
                    color: #28777E;
                    font-size: 0.75rem;
                    font-weight: 750;
                    line-height: 1.25;
                }

                .uywa-account-empty {
                    padding: 0.2rem 0;
                    color: #667085;
                    font-size: 0.83rem;
                    line-height: 1.55;
                }

                .uywa-account-support {
                    display: flex;
                    align-items: flex-start;
                    gap: 0.8rem;
                    margin-top: 1rem;
                    padding: 1rem 1.15rem;
                    border: 1px solid #DDE7F3;
                    border-radius: 15px;
                    background: #F8FAFC;
                    color: #536174;
                    font-size: 0.84rem;
                    line-height: 1.6;
                }

                .uywa-account-support-icon {
                    flex: 0 0 auto;
                    font-size: 1.1rem;
                }

                .uywa-account-support strong {
                    color: #17233F;
                }

                .uywa-account-support-email {
                    color: #28777E;
                    font-weight: 750;
                    overflow-wrap: anywhere;
                }

                @media (max-width: 800px) {
                    .uywa-account-hero {
                        padding: 1.35rem;
                    }

                    .uywa-account-title {
                        font-size: 1.65rem;
                    }

                    .uywa-account-row {
                        display: block;
                    }

                    .uywa-account-row span,
                    .uywa-account-row strong {
                        display: block;
                        width: 100%;
                    }

                    .uywa-account-row strong {
                        margin-top: 0.2rem;
                        text-align: left;
                    }

                    .uywa-account-status {
                        justify-content: flex-start;
                    }
                }
            </style>
            """
        ),
        unsafe_allow_html=True,
    )


def _render_personal_data_card(
    name: str,
    email: str,
    role: str,
    organization: str,
) -> None:
    """
    Renderiza la tarjeta de datos personales.
    """

    st.markdown(
        clean_html(
            f"""
            <div class="uywa-account-card">
                <div class="uywa-account-card-label">
                    DATOS PERSONALES
                </div>

                <div class="uywa-account-row">
                    <span>Nombre</span>
                    <strong>{name}</strong>
                </div>

                <div class="uywa-account-row">
                    <span>Correo</span>
                    <strong>{email}</strong>
                </div>

                <div class="uywa-account-row">
                    <span>Rol</span>
                    <strong>{role}</strong>
                </div>

                <div class="uywa-account-row">
                    <span>Organización</span>
                    <strong>{organization}</strong>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def _render_subscription_card(
    plan_name: str,
    subscription_status: str,
    subscription_start: str,
    expiration: str,
) -> None:
    """
    Renderiza la tarjeta de plan y licencia.
    """

    status_is_active = (
        subscription_status.strip().lower()
        in {
            "activa",
            "active",
            "prueba",
            "trial",
            "demo",
        }
    )

    if status_is_active:
        status_html = clean_html(
            f"""
            <span class="uywa-account-status">
                <span
                    class="uywa-account-status-dot"
                ></span>
                {subscription_status}
            </span>
            """
        )
    else:
        status_html = subscription_status

    st.markdown(
        clean_html(
            f"""
            <div class="uywa-account-card">
                <div class="uywa-account-card-label">
                    PLAN Y LICENCIA
                </div>

                <div class="uywa-account-row">
                    <span>Plan</span>
                    <strong>{plan_name}</strong>
                </div>

                <div class="uywa-account-row">
                    <span>Estado</span>
                    <strong>{status_html}</strong>
                </div>

                <div class="uywa-account-row">
                    <span>Inicio</span>
                    <strong>{subscription_start}</strong>
                </div>

                <div class="uywa-account-row">
                    <span>Vigencia</span>
                    <strong>{expiration}</strong>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def _render_modules_card(
    modules: list[str],
) -> None:
    """
    Renderiza los módulos habilitados.
    """

    if modules:
        modules_html = "".join(
            clean_html(
                f"""
                <span class="uywa-account-module">
                    {html.escape(module)}
                </span>
                """
            )
            for module in modules
        )

        content_html = clean_html(
            f"""
            <div class="uywa-account-modules">
                {modules_html}
            </div>
            """
        )

    else:
        content_html = clean_html(
            """
            <div class="uywa-account-empty">
                No se encontraron módulos asociados
                directamente al objeto de usuario.
                Los módulos disponibles continúan
                mostrándose en el Launcher.
            </div>
            """
        )

    st.markdown(
        clean_html(
            f"""
            <div class="uywa-account-card">
                <div class="uywa-account-card-label">
                    MÓDULOS HABILITADOS
                </div>

                {content_html}
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def render_account_page(
    current_user: CurrentUser,
) -> None:
    """
    Renderiza el centro de cuenta de Uywa Platform.
    """

    _inject_account_styles()

    name = _safe_text(
        _get_user_name(
            current_user
        )
    )

    email = _safe_text(
        _get_user_email(
            current_user
        )
    )

    role = _safe_text(
        _get_user_role(
            current_user
        )
    )

    organization = _safe_text(
        _get_organization(
            current_user
        )
    )

    plan_name = _safe_text(
        _get_plan_name(
            current_user
        )
    )

    subscription_status = _safe_text(
        _get_subscription_status(
            current_user
        )
    )

    subscription_start = _safe_text(
        _get_subscription_start(
            current_user
        )
    )

    expiration = _safe_text(
        _get_expiration(
            current_user
        )
    )

    modules = _get_enabled_modules(
        current_user
    )

    st.markdown(
        clean_html(
            """
            <div class="uywa-account-page">
                <div class="uywa-account-hero">
                    <div class="uywa-account-hero-content">
                        <div class="uywa-account-eyebrow">
                            UYWA PLATFORM
                        </div>

                        <div class="uywa-account-title">
                            Mi cuenta
                        </div>

                        <div class="uywa-account-subtitle">
                            Consulta tus datos de usuario,
                            organización, plan, vigencia y
                            módulos habilitados.
                        </div>
                    </div>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    left_column, right_column = st.columns(
        2,
        gap="large",
    )

    with left_column:
        _render_personal_data_card(
            name=name,
            email=email,
            role=role,
            organization=organization,
        )

    with right_column:
        _render_subscription_card(
            plan_name=plan_name,
            subscription_status=subscription_status,
            subscription_start=subscription_start,
            expiration=expiration,
        )

    st.write("")

    _render_modules_card(
        modules
    )

    st.markdown(
        clean_html(
            """
            <div class="uywa-account-support">
                <div class="uywa-account-support-icon">
                    ✉
                </div>

                <div>
                    <strong>
                        Soporte Uywa Nutrition
                    </strong>
                    <br>

                    Para consultas sobre acceso,
                    licencia o módulos:
                    <span
                        class="uywa-account-support-email"
                    >
                        uywasas@gmail.com
                    </span>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )
