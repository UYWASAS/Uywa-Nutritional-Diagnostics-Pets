from __future__ import annotations

import html
from typing import Any

import streamlit as st

from uywa_core.current_user import CurrentUser
from uywa_core.theme.html_utils import clean_html


def _get_value(
    current_user: CurrentUser,
    *keys: str,
) -> Any:
    """
    Busca un valor en el usuario, profile y metadata.
    """

    for key in keys:
        value = getattr(
            current_user,
            key,
            None,
        )

        if value not in (None, ""):
            return value

    profile = getattr(
        current_user,
        "profile",
        None,
    )

    if isinstance(profile, dict):
        for key in keys:
            value = profile.get(key)

            if value not in (None, ""):
                return value

    metadata = getattr(
        current_user,
        "metadata",
        None,
    )

    if isinstance(metadata, dict):
        for key in keys:
            value = metadata.get(key)

            if value not in (None, ""):
                return value

    return None


def _safe_text(
    value: Any,
    fallback: str = "No disponible",
) -> str:
    """
    Convierte un valor a texto seguro para HTML.
    """

    if value in (None, ""):
        return fallback

    return html.escape(
        str(value)
    )


def _get_plan_name(
    current_user: CurrentUser,
) -> str:
    """
    Obtiene el nombre del plan.
    """

    direct_plan = _get_value(
        current_user,
        "plan_name",
        "plan_code",
    )

    if direct_plan:
        return str(direct_plan)

    plan = getattr(
        current_user,
        "plan",
        None,
    )

    if isinstance(plan, dict):
        return str(
            plan.get("name")
            or plan.get("code")
            or "Sin plan asignado"
        )

    if plan is not None:
        return str(
            getattr(plan, "name", None)
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

        if status:
            return str(status).replace(
                "_",
                " ",
            ).title()

        if subscription.get("active"):
            return "Activa"

    explicit_status = _get_value(
        current_user,
        "subscription_status",
        "status",
    )

    if explicit_status:
        return str(explicit_status).replace(
            "_",
            " ",
        ).title()

    if getattr(
        current_user,
        "subscription_is_active",
        False,
    ):
        return "Activa"

    return "No activa"


def _get_expiration(
    current_user: CurrentUser,
) -> str:
    """
    Obtiene la fecha de vigencia.
    """

    value = _get_value(
        current_user,
        "subscription_expires_at",
        "expires_at",
        "end_date",
        "subscription_end_date",
    )

    if not value:
        subscription = getattr(
            current_user,
            "subscription",
            None,
        )

        if isinstance(subscription, dict):
            value = (
                subscription.get("expires_at")
                or subscription.get("end_date")
                or subscription.get(
                    "subscription_end_date"
                )
            )

    if not value:
        return "No disponible"

    value_text = str(value)

    if "T" in value_text:
        return value_text.split("T", 1)[0]

    return value_text[:10]


def _get_enabled_modules(
    current_user: CurrentUser,
) -> list[str]:
    """
    Obtiene los módulos habilitados del usuario.
    """

    possible_sources = [
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
    ]

    modules: list[str] = []

    for source in possible_sources:
        if not source:
            continue

        if isinstance(source, dict):
            source = list(
                source.values()
            )

        if not isinstance(
            source,
            (list, tuple, set),
        ):
            continue

        for item in source:
            if isinstance(item, str):
                name = item

            elif isinstance(item, dict):
                name = (
                    item.get("name")
                    or item.get("title")
                    or item.get("code")
                )

            else:
                name = (
                    getattr(item, "name", None)
                    or getattr(item, "title", None)
                    or getattr(item, "code", None)
                )

            if name:
                modules.append(
                    str(name)
                )

    return list(
        dict.fromkeys(modules)
    )


def _inject_account_styles() -> None:
    """
    Inserta los estilos de la página.
    """

    st.markdown(
        clean_html(
            """
            <style>
                .uywa-account-hero {
                    padding: 1.65rem 1.8rem;
                    margin-bottom: 1.4rem;
                    border-radius: 20px;
                    background:
                        linear-gradient(
                            135deg,
                            #17233F 0%,
                            #22485B 100%
                        );
                    box-shadow:
                        0 14px 34px
                        rgba(23, 35, 63, 0.15);
                }

                .uywa-account-eyebrow {
                    color: #65BEC6;
                    font-size: 0.72rem;
                    font-weight: 800;
                    letter-spacing: 0.13em;
                }

                .uywa-account-title {
                    margin-top: 0.3rem;
                    color: #FFFFFF;
                    font-size: 2rem;
                    font-weight: 850;
                    line-height: 1.2;
                }

                .uywa-account-subtitle {
                    margin-top: 0.55rem;
                    color: rgba(255, 255, 255, 0.78);
                    font-size: 0.9rem;
                    line-height: 1.5;
                }

                .uywa-account-card {
                    min-height: 100%;
                    padding: 1.25rem;
                    border: 1px solid #DDE3EC;
                    border-radius: 17px;
                    background: #FFFFFF;
                    box-shadow:
                        0 8px 24px
                        rgba(23, 35, 63, 0.06);
                }

                .uywa-account-card-label {
                    margin-bottom: 0.9rem;
                    color: #28777E;
                    font-size: 0.7rem;
                    font-weight: 850;
                    letter-spacing: 0.11em;
                }

                .uywa-account-row {
                    display: flex;
                    justify-content: space-between;
                    gap: 1rem;
                    padding: 0.72rem 0;
                    border-bottom: 1px solid #EDF1F5;
                    color: #667085;
                    font-size: 0.83rem;
                }

                .uywa-account-row:last-child {
                    border-bottom: none;
                }

                .uywa-account-row strong {
                    color: #17233F;
                    text-align: right;
                    overflow-wrap: anywhere;
                }

                .uywa-account-module {
                    display: inline-block;
                    margin: 0.2rem 0.25rem 0.2rem 0;
                    padding: 0.4rem 0.7rem;
                    border-radius: 999px;
                    background: #EFF8F8;
                    color: #28777E;
                    font-size: 0.76rem;
                    font-weight: 750;
                }

                .uywa-account-empty {
                    color: #667085;
                    font-size: 0.84rem;
                    line-height: 1.5;
                }

                .uywa-account-support {
                    margin-top: 1rem;
                    padding: 1rem 1.15rem;
                    border: 1px solid #DDE7F3;
                    border-radius: 15px;
                    background: #F8FAFC;
                    color: #536174;
                    font-size: 0.85rem;
                    line-height: 1.6;
                }

                .uywa-account-support strong {
                    color: #17233F;
                }
            </style>
            """
        ),
        unsafe_allow_html=True,
    )


def render_account_page(
    current_user: CurrentUser,
) -> None:
    """
    Renderiza el centro de cuenta de la plataforma.
    """

    _inject_account_styles()

    name = _safe_text(
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

    email = _safe_text(
        _get_value(
            current_user,
            "email",
        )
    )

    role = _safe_text(
        str(
            _get_value(
                current_user,
                "role",
            )
            or "Usuario"
        )
        .replace("_", " ")
        .title()
    )

    organization = _safe_text(
        _get_value(
            current_user,
            "organization",
            "company",
            "institution",
            "organization_name",
        ),
        "Sin organización registrada",
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

    expiration = _safe_text(
        _get_expiration(
            current_user
        )
    )

    st.markdown(
        clean_html(
            f"""
            <div class="uywa-account-hero">
                <div class="uywa-account-eyebrow">
                    UYWA PLATFORM
                </div>

                <div class="uywa-account-title">
                    Mi cuenta
                </div>

                <div class="uywa-account-subtitle">
                    Consulta tus datos de usuario,
                    organización, plan y módulos habilitados.
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

    with right_column:
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
                        <strong>{subscription_status}</strong>
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

    st.write("")

    modules = _get_enabled_modules(
        current_user
    )

    if modules:
        modules_html = "".join(
            (
                '<span class="uywa-account-module">'
                f"{html.escape(module)}"
                "</span>"
            )
            for module in modules
        )
    else:
        modules_html = """
        <div class="uywa-account-empty">
            No se encontraron módulos asociados directamente
            al objeto de usuario. Los módulos disponibles
            continúan mostrándose en el Launcher.
        </div>
        """

    st.markdown(
        clean_html(
            f"""
            <div class="uywa-account-card">
                <div class="uywa-account-card-label">
                    MÓDULOS HABILITADOS
                </div>

                <div>
                    {modules_html}
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        clean_html(
            """
            <div class="uywa-account-support">
                <strong>Soporte Uywa Nutrition</strong><br>
                Para consultas sobre acceso, licencia o módulos:
                uywasas@gmail.com
            </div>
            """
        ),
        unsafe_allow_html=True,
    )
