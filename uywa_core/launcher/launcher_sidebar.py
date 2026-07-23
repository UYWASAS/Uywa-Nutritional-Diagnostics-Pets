from __future__ import annotations

import html
from pathlib import Path
from textwrap import dedent

import streamlit as st

from uywa_core.current_user import CurrentUser
from uywa_core.theme.html_utils import clean_html


DEFAULT_LOGO_PATH = "assets/logo.png"


def _get_profile_value(
    current_user: CurrentUser,
    *keys: str,
) -> str | None:
    """
    Busca un valor tanto en propiedades directas como
    en profile y metadata.
    """

    for key in keys:
        direct_value = getattr(
            current_user,
            key,
            None,
        )

        if direct_value:
            return str(direct_value)

    profile = getattr(
        current_user,
        "profile",
        None,
    )

    if isinstance(profile, dict):
        for key in keys:
            value = profile.get(key)

            if value:
                return str(value)

    metadata = getattr(
        current_user,
        "metadata",
        None,
    )

    if isinstance(metadata, dict):
        for key in keys:
            value = metadata.get(key)

            if value:
                return str(value)

    return None


def _get_user_display_name(
    current_user: CurrentUser,
) -> str:
    return (
        _get_profile_value(
            current_user,
            "full_name",
            "display_name",
            "name",
        )
        or _get_profile_value(
            current_user,
            "email",
        )
        or "Usuario"
    )


def _get_user_email(
    current_user: CurrentUser,
) -> str:
    return (
        _get_profile_value(
            current_user,
            "email",
        )
        or "Correo no disponible"
    )


def _get_plan_name(
    current_user: CurrentUser,
) -> str:
    direct_name = _get_profile_value(
        current_user,
        "plan_name",
        "plan_code",
    )

    if direct_name:
        return direct_name

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


def _get_expiration_date(
    current_user: CurrentUser,
) -> str | None:
    possible_values = (
        "subscription_expires_at",
        "expires_at",
        "end_date",
        "subscription_end_date",
    )

    value = _get_profile_value(
        current_user,
        *possible_values,
    )

    if not value:
        subscription = getattr(
            current_user,
            "subscription",
            None,
        )

        if isinstance(subscription, dict):
            for key in possible_values:
                if subscription.get(key):
                    value = str(
                        subscription[key]
                    )
                    break

    if not value:
        return None

    if "T" in value:
        return value.split("T", 1)[0]

    return value[:10]


def _subscription_is_active(
    current_user: CurrentUser,
) -> bool:
    explicit_value = getattr(
        current_user,
        "subscription_is_active",
        None,
    )

    if explicit_value is not None:
        return bool(explicit_value)

    subscription = getattr(
        current_user,
        "subscription",
        None,
    )

    if isinstance(subscription, dict):
        status = str(
            subscription.get("status", "")
            or ""
        ).lower()

        if status:
            return status in {
                "active",
                "trial",
                "demo",
                "enabled",
            }

        if "active" in subscription:
            return bool(subscription["active"])

    return bool(
        getattr(current_user, "active", False)
    )


def inject_sidebar_styles() -> None:
    st.markdown(
        clean_html(
            """
            <style>
                .uywa-sidebar-brand {
                    margin-top: 1.35rem;
                    margin-bottom: 1.2rem;
                    text-align: center;
                }

                .uywa-sidebar-brand-title {
                    color: #FFFFFF;
                    font-size: 1.55rem;
                    font-weight: 800;
                    line-height: 1.2;
                }

                .uywa-sidebar-brand-subtitle {
                    max-width: 245px;
                    margin: 0.65rem auto 0;
                    color: rgba(255, 255, 255, 0.84);
                    font-size: 0.79rem;
                    line-height: 1.5;
                }

                .uywa-sidebar-divider {
                    height: 1px;
                    margin: 1.15rem 0;
                    background: rgba(255, 255, 255, 0.22);
                }

                .uywa-sidebar-user-card {
                    padding: 1rem;
                    border: 1px solid rgba(255, 255, 255, 0.20);
                    border-radius: 14px;
                    background: rgba(255, 255, 255, 0.07);
                }

                .uywa-sidebar-user-label {
                    margin-bottom: 0.55rem;
                    color: #FFFFFF;
                    font-size: 0.69rem;
                    font-weight: 800;
                    letter-spacing: 0.10em;
                }

                .uywa-sidebar-user-name {
                    color: #FFFFFF;
                    font-size: 1rem;
                    font-weight: 750;
                    line-height: 1.35;
                    overflow-wrap: anywhere;
                }

                .uywa-sidebar-user-email {
                    margin-top: 0.25rem;
                    color: rgba(255, 255, 255, 0.72);
                    font-size: 0.72rem;
                    overflow-wrap: anywhere;
                }

                .uywa-sidebar-user-role {
                    margin-top: 0.75rem;
                    color: #65BEC6;
                    font-size: 0.75rem;
                    font-weight: 700;
                    text-transform: capitalize;
                }

                .uywa-sidebar-plan-row {
                    display: flex;
                    justify-content: space-between;
                    gap: 0.65rem;
                    margin-top: 0.9rem;
                    padding-top: 0.8rem;
                    border-top: 1px solid rgba(255, 255, 255, 0.13);
                    color: rgba(255, 255, 255, 0.72);
                    font-size: 0.76rem;
                }

                .uywa-sidebar-plan-row strong {
                    color: #FFFFFF;
                    text-align: right;
                    overflow-wrap: anywhere;
                }

                .uywa-sidebar-license {
                    display: flex;
                    align-items: center;
                    gap: 0.45rem;
                    margin-top: 0.8rem;
                    font-size: 0.76rem;
                    font-weight: 700;
                }

                .uywa-sidebar-license-dot {
                    width: 8px;
                    height: 8px;
                    flex: 0 0 8px;
                    border-radius: 50%;
                }

                .uywa-license-active {
                    color: #8CE1C0;
                }

                .uywa-license-active
                .uywa-sidebar-license-dot {
                    background: #59D2A2;
                }

                .uywa-license-inactive {
                    color: #F5BABA;
                }

                .uywa-license-inactive
                .uywa-sidebar-license-dot {
                    background: #E17777;
                }

                .uywa-sidebar-expiration {
                    margin-top: 0.7rem;
                    color: rgba(255, 255, 255, 0.72);
                    font-size: 0.72rem;
                    text-align: center;
                }

                .uywa-sidebar-expiration strong {
                    color: #FFFFFF;
                }

                .uywa-sidebar-footer {
                    margin-top: 1.4rem;
                    padding-top: 1rem;
                    border-top: 1px solid rgba(255, 255, 255, 0.20);
                    color: rgba(255, 255, 255, 0.84);
                    font-size: 0.75rem;
                    line-height: 1.7;
                    text-align: center;
                }

                .uywa-sidebar-copyright {
                    color: rgba(255, 255, 255, 0.60);
                    font-size: 0.68rem;
                }
            </style>
            """
        ),
        unsafe_allow_html=True,
    )


def render_platform_sidebar(
    current_user: CurrentUser,
    logo_path: str = DEFAULT_LOGO_PATH,
) -> bool:
    """
    Renderiza la barra lateral y devuelve True al cerrar sesión.
    """

    inject_sidebar_styles()

    display_name = html.escape(
        _get_user_display_name(current_user)
    )

    email = html.escape(
        _get_user_email(current_user)
    )

    role = html.escape(
        str(
            getattr(current_user, "role", None)
            or "Usuario"
        ).replace("_", " ").title()
    )

    plan_name = html.escape(
        _get_plan_name(current_user)
    )

    expiration_date = _get_expiration_date(
        current_user
    )

    is_active = _subscription_is_active(
        current_user
    )

    license_text = (
        "Licencia activa"
        if is_active
        else "Licencia no activa"
    )

    license_class = (
        "uywa-license-active"
        if is_active
        else "uywa-license-inactive"
    )

    with st.sidebar:
        logo_file = Path(logo_path)

        if logo_file.exists():
            st.image(
                str(logo_file),
                use_container_width=True,
            )
        else:
            st.warning(
                f"No se encontró el logo en {logo_path}"
            )

        st.markdown(
            clean_html(
                """
                <div class="uywa-sidebar-brand">
                    <div class="uywa-sidebar-brand-title">
                        UYWA Nutrition
                    </div>

                    <div class="uywa-sidebar-brand-subtitle">
                        Nutrición de Precisión Basada en Evidencia
                    </div>
                </div>

                <div class="uywa-sidebar-divider"></div>
                """
            ),
            unsafe_allow_html=True,
        )

        user_card_html = dedent(
            f"""
            <div class="uywa-sidebar-user-card">
                <div class="uywa-sidebar-user-label">
                    USUARIO
                </div>

                <div class="uywa-sidebar-user-name">
                    {display_name}
                </div>

                <div class="uywa-sidebar-user-email">
                    {email}
                </div>

                <div class="uywa-sidebar-user-role">
                    {role}
                </div>

                <div class="uywa-sidebar-plan-row">
                    <span>Plan</span>
                    <strong>{plan_name}</strong>
                </div>

                <div class="uywa-sidebar-license {license_class}">
                    <span class="uywa-sidebar-license-dot"></span>
                    {license_text}
                </div>
            </div>
            """
        )

        st.markdown(
            user_card_html,
            unsafe_allow_html=True,
        )

        if expiration_date:
            safe_expiration = html.escape(
                expiration_date
            )

            st.markdown(
                clean_html(
                    f"""
                    <div class="uywa-sidebar-expiration">
                        Vigencia hasta:
                        <strong>{safe_expiration}</strong>
                    </div>
                    """
                ),
                unsafe_allow_html=True,
            )

        st.write("")

        logout_clicked = st.button(
            "Cerrar sesión",
            key="uywa_platform_logout",
            use_container_width=True,
        )

        st.markdown(
            clean_html(
                """
                <div class="uywa-sidebar-footer">
                    <div>📧 uywasas@gmail.com</div>
                    <div class="uywa-sidebar-copyright">
                        Derechos reservados © 2026
                    </div>
                </div>
                """
            ),
            unsafe_allow_html=True,
        )

    return logout_clicked
