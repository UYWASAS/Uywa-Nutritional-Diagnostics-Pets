from __future__ import annotations

import html
from pathlib import Path

import streamlit as st

from uywa_core.current_user import CurrentUser


DEFAULT_LOGO_PATH = "assets/logo.png"


def _get_user_display_name(current_user: CurrentUser) -> str:
    """
    Obtiene el nombre disponible sin depender de una única propiedad.
    """

    full_name = getattr(current_user, "full_name", None)
    name = getattr(current_user, "name", None)
    email = getattr(current_user, "email", None)

    return str(
        full_name
        or name
        or email
        or "Usuario"
    )


def _get_plan_name(current_user: CurrentUser) -> str:
    plan_name = getattr(current_user, "plan_name", None)
    plan_code = getattr(current_user, "plan_code", None)

    return str(
        plan_name
        or plan_code
        or "Sin plan asignado"
    )


def _format_expiration_date(current_user: CurrentUser) -> str | None:
    """
    Devuelve una versión sencilla de la fecha de expiración.
    """

    expires_at = getattr(
        current_user,
        "subscription_expires_at",
        None,
    )

    if not expires_at:
        return None

    value = str(expires_at)

    if "T" in value:
        return value.split("T", maxsplit=1)[0]

    return value


def render_platform_sidebar(
    current_user: CurrentUser,
    logo_path: str = DEFAULT_LOGO_PATH,
) -> bool:
    """
    Renderiza la barra lateral corporativa.

    Retorna True cuando el usuario pulsa 'Cerrar sesión'.
    """

    display_name = html.escape(
        _get_user_display_name(current_user)
    )

    role = html.escape(
        str(
            getattr(current_user, "role", None)
            or "Usuario"
        )
    )

    plan_name = html.escape(
        _get_plan_name(current_user)
    )

    expiration_date = _format_expiration_date(
        current_user
    )

    subscription_active = bool(
        getattr(
            current_user,
            "subscription_is_active",
            False,
        )
    )

    license_text = (
        "Licencia activa"
        if subscription_active
        else "Licencia no activa"
    )

    license_class = (
        "uywa-license-active"
        if subscription_active
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
                f"No se encontró el logo en: {logo_path}"
            )

        st.markdown(
            """
            <div class="uywa-sidebar-brand">
                <div class="uywa-sidebar-brand-title">
                    UYWA Nutrition
                </div>
                <div class="uywa-sidebar-brand-subtitle">
                    Nutrición de Precisión Basada en Evidencia
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="uywa-sidebar-divider"></div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="uywa-sidebar-user-card">
                <div class="uywa-sidebar-user-label">
                    USUARIO
                </div>

                <div class="uywa-sidebar-user-name">
                    {display_name}
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
            """,
            unsafe_allow_html=True,
        )

        if expiration_date:
            safe_expiration = html.escape(
                expiration_date
            )

            st.markdown(
                f"""
                <div class="uywa-sidebar-expiration">
                    Vigencia hasta:
                    <strong>{safe_expiration}</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            """
            <div class="uywa-sidebar-spacer"></div>
            """,
            unsafe_allow_html=True,
        )

        logout_clicked = st.button(
            "Cerrar sesión",
            key="uywa_platform_logout",
            use_container_width=True,
        )

        st.markdown(
            """
            <div class="uywa-sidebar-footer">
                <div>📧 uywasas@gmail.com</div>
                <div class="uywa-sidebar-copyright">
                    Derechos reservados © 2026
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <style>
                .uywa-sidebar-brand {
                    text-align: center;
                    margin-top: 1.5rem;
                    margin-bottom: 1.3rem;
                }

                .uywa-sidebar-brand-title {
                    color: #FFFFFF;
                    font-size: 1.65rem;
                    line-height: 1.2;
                    font-weight: 800;
                    letter-spacing: -0.02em;
                }

                .uywa-sidebar-brand-subtitle {
                    max-width: 245px;
                    margin: 0.75rem auto 0 auto;
                    color: rgba(255, 255, 255, 0.86);
                    font-size: 0.82rem;
                    line-height: 1.5;
                }

                .uywa-sidebar-divider {
                    width: 100%;
                    height: 1px;
                    margin: 1.25rem 0;
                    background: rgba(255, 255, 255, 0.26);
                }

                .uywa-sidebar-user-card {
                    padding: 1rem;
                    border: 1px solid rgba(255, 255, 255, 0.17);
                    border-radius: 14px;
                    background: rgba(255, 255, 255, 0.07);
                }

                .uywa-sidebar-user-label {
                    margin-bottom: 0.4rem;
                    color: #65BEC6;
                    font-size: 0.68rem;
                    font-weight: 800;
                    letter-spacing: 0.12em;
                }

                .uywa-sidebar-user-name {
                    color: #FFFFFF;
                    font-size: 1rem;
                    font-weight: 750;
                    line-height: 1.35;
                    word-break: break-word;
                }

                .uywa-sidebar-user-role {
                    margin-top: 0.2rem;
                    color: rgba(255, 255, 255, 0.66);
                    font-size: 0.77rem;
                    text-transform: capitalize;
                }

                .uywa-sidebar-plan-row {
                    display: flex;
                    justify-content: space-between;
                    gap: 0.75rem;
                    margin-top: 1rem;
                    padding-top: 0.8rem;
                    border-top: 1px solid rgba(255, 255, 255, 0.13);
                    color: rgba(255, 255, 255, 0.76);
                    font-size: 0.78rem;
                }

                .uywa-sidebar-plan-row strong {
                    color: #FFFFFF;
                    text-align: right;
                }

                .uywa-sidebar-license {
                    display: flex;
                    align-items: center;
                    gap: 0.45rem;
                    margin-top: 0.8rem;
                    font-size: 0.77rem;
                    font-weight: 700;
                }

                .uywa-sidebar-license-dot {
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                }

                .uywa-license-active {
                    color: #8CE1C0;
                }

                .uywa-license-active
                .uywa-sidebar-license-dot {
                    background: #59D2A2;
                    box-shadow:
                        0 0 0 4px rgba(89, 210, 162, 0.15);
                }

                .uywa-license-inactive {
                    color: #F5BABA;
                }

                .uywa-license-inactive
                .uywa-sidebar-license-dot {
                    background: #E17777;
                }

                .uywa-sidebar-expiration {
                    margin-top: 0.65rem;
                    color: rgba(255, 255, 255, 0.63);
                    font-size: 0.72rem;
                    text-align: center;
                }

                .uywa-sidebar-expiration strong {
                    color: rgba(255, 255, 255, 0.88);
                }

                .uywa-sidebar-spacer {
                    height: 1rem;
                }

                .uywa-sidebar-footer {
                    margin-top: 1.6rem;
                    padding-top: 1.1rem;
                    border-top: 1px solid rgba(255, 255, 255, 0.24);
                    color: rgba(255, 255, 255, 0.92);
                    font-size: 0.78rem;
                    line-height: 1.8;
                    text-align: center;
                }

                .uywa-sidebar-copyright {
                    color: rgba(255, 255, 255, 0.66);
                    font-size: 0.68rem;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

    return logout_clicked
