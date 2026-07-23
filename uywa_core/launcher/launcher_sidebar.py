from __future__ import annotations

import html
from pathlib import Path

import streamlit as st

from uywa_core.current_user import CurrentUser
from uywa_core.theme.html_utils import clean_html


DEFAULT_LOGO_PATH = "assets/logo.png"

PLATFORM_VIEW_KEY = "uywa_platform_view"
SELECTED_MODULE_KEY = "uywa_selected_module"

VIEW_LAUNCHER = "launcher"
VIEW_ACCOUNT = "account"


def _get_profile_value(
    current_user: CurrentUser,
    *keys: str,
) -> str | None:
    """
    Busca un valor en las propiedades directas del usuario,
    en profile y en metadata.
    """

    for key in keys:
        direct_value = getattr(
            current_user,
            key,
            None,
        )

        if direct_value not in (None, ""):
            return str(direct_value)

    profile = getattr(
        current_user,
        "profile",
        None,
    )

    if isinstance(profile, dict):
        for key in keys:
            value = profile.get(key)

            if value not in (None, ""):
                return str(value)

    metadata = getattr(
        current_user,
        "metadata",
        None,
    )

    if isinstance(metadata, dict):
        for key in keys:
            value = metadata.get(key)

            if value not in (None, ""):
                return str(value)

    return None


def _get_user_display_name(
    current_user: CurrentUser,
) -> str:
    """
    Obtiene el nombre visible del usuario.
    """

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
    """
    Obtiene el correo electrónico del usuario.
    """

    return (
        _get_profile_value(
            current_user,
            "email",
        )
        or "Correo no disponible"
    )


def _get_user_role(
    current_user: CurrentUser,
) -> str:
    """
    Obtiene y normaliza el rol del usuario.
    """

    role = (
        _get_profile_value(
            current_user,
            "role",
            "user_role",
        )
        or "Usuario"
    )

    return role.replace(
        "_",
        " ",
    ).title()


def _get_plan_name(
    current_user: CurrentUser,
) -> str:
    """
    Obtiene el nombre o código del plan contratado.
    """

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
    """
    Obtiene y normaliza la fecha de finalización
    de la suscripción.
    """

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
                subscription_value = subscription.get(
                    key
                )

                if subscription_value not in (
                    None,
                    "",
                ):
                    value = str(
                        subscription_value
                    )
                    break

    if not value:
        return None

    value_text = str(value)

    if "T" in value_text:
        return value_text.split(
            "T",
            1,
        )[0]

    return value_text[:10]


def _subscription_is_active(
    current_user: CurrentUser,
) -> bool:
    """
    Determina si la suscripción está activa.
    """

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
            subscription.get(
                "status",
                "",
            )
            or ""
        ).strip().lower()

        if status:
            return status in {
                "active",
                "trial",
                "demo",
                "enabled",
            }

        if "active" in subscription:
            return bool(
                subscription["active"]
            )

    return bool(
        getattr(
            current_user,
            "active",
            False,
        )
    )


def _get_current_platform_view() -> str:
    """
    Obtiene la vista principal activa de la plataforma.
    """

    current_view = st.session_state.get(
        PLATFORM_VIEW_KEY,
        VIEW_LAUNCHER,
    )

    if current_view not in {
        VIEW_LAUNCHER,
        VIEW_ACCOUNT,
    }:
        current_view = VIEW_LAUNCHER

        st.session_state[
            PLATFORM_VIEW_KEY
        ] = current_view

    return str(current_view)


def _go_to_launcher() -> None:
    """
    Regresa al Launcher y abandona cualquier módulo
    seleccionado.
    """

    st.session_state[
        PLATFORM_VIEW_KEY
    ] = VIEW_LAUNCHER

    st.session_state.pop(
        SELECTED_MODULE_KEY,
        None,
    )


def _go_to_account() -> None:
    """
    Abre la vista Mi cuenta y abandona cualquier módulo
    seleccionado.
    """

    st.session_state[
        PLATFORM_VIEW_KEY
    ] = VIEW_ACCOUNT

    st.session_state.pop(
        SELECTED_MODULE_KEY,
        None,
    )


def _render_html(
    content: str,
) -> None:
    """
    Renderiza un fragmento HTML compacto.

    Los componentes visibles deben enviarse sin
    indentaciones que Markdown pueda interpretar
    como bloques de código.
    """

    st.markdown(
        content,
        unsafe_allow_html=True,
    )


def inject_sidebar_styles() -> None:
    """
    Inserta los estilos propios de la barra lateral.
    """

    styles = clean_html(
        """
        <style>
            .uywa-sidebar-brand {
                margin-top: 1.15rem;
                margin-bottom: 1.1rem;
                text-align: center;
            }

            .uywa-sidebar-brand-title {
                color: #FFFFFF;
                font-size: 1.5rem;
                font-weight: 800;
                line-height: 1.2;
            }

            .uywa-sidebar-brand-subtitle {
                max-width: 245px;
                margin: 0.55rem auto 0;
                color: rgba(255, 255, 255, 0.82);
                font-size: 0.77rem;
                line-height: 1.45;
            }

            .uywa-sidebar-divider {
                height: 1px;
                margin: 1.05rem 0;
                background: rgba(255, 255, 255, 0.20);
            }

            .uywa-sidebar-user-card {
                padding: 1rem;
                border: 1px solid rgba(255, 255, 255, 0.18);
                border-radius: 15px;
                background: rgba(255, 255, 255, 0.07);
                box-shadow: 0 8px 22px rgba(0, 0, 0, 0.08);
            }

            .uywa-sidebar-user-label {
                margin-bottom: 0.5rem;
                color: rgba(255, 255, 255, 0.67);
                font-size: 0.66rem;
                font-weight: 800;
                letter-spacing: 0.12em;
            }

            .uywa-sidebar-user-name {
                color: #FFFFFF;
                font-size: 0.98rem;
                font-weight: 780;
                line-height: 1.35;
                overflow-wrap: anywhere;
            }

            .uywa-sidebar-user-email {
                margin-top: 0.22rem;
                color: rgba(255, 255, 255, 0.69);
                font-size: 0.71rem;
                line-height: 1.4;
                overflow-wrap: anywhere;
            }

            .uywa-sidebar-user-role {
                margin-top: 0.7rem;
                color: #65BEC6;
                font-size: 0.73rem;
                font-weight: 750;
                text-transform: capitalize;
            }

            .uywa-sidebar-plan-row {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                gap: 0.65rem;
                margin-top: 0.85rem;
                padding-top: 0.75rem;
                border-top: 1px solid rgba(255, 255, 255, 0.13);
                color: rgba(255, 255, 255, 0.70);
                font-size: 0.74rem;
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
                margin-top: 0.75rem;
                font-size: 0.74rem;
                font-weight: 750;
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

            .uywa-license-active .uywa-sidebar-license-dot {
                background: #59D2A2;
                box-shadow: 0 0 0 3px rgba(89, 210, 162, 0.14);
            }

            .uywa-license-inactive {
                color: #F5BABA;
            }

            .uywa-license-inactive .uywa-sidebar-license-dot {
                background: #E17777;
                box-shadow: 0 0 0 3px rgba(225, 119, 119, 0.14);
            }

            .uywa-sidebar-expiration {
                margin-top: 0.65rem;
                color: rgba(255, 255, 255, 0.70);
                font-size: 0.71rem;
                text-align: center;
            }

            .uywa-sidebar-expiration strong {
                color: #FFFFFF;
            }

            .uywa-sidebar-navigation {
                margin-top: 1.15rem;
            }

            .uywa-sidebar-section-label {
                margin-bottom: 0.48rem;
                color: rgba(255, 255, 255, 0.57);
                font-size: 0.64rem;
                font-weight: 800;
                letter-spacing: 0.13em;
            }

            section[data-testid="stSidebar"]
            div[data-testid="stButton"]
            button {
                min-height: 43px !important;
                border-radius: 11px !important;
                font-size: 0.8rem !important;
                font-weight: 750 !important;
                transition:
                    border-color 0.15s ease,
                    background 0.15s ease,
                    transform 0.15s ease;
            }

            section[data-testid="stSidebar"]
            div[data-testid="stButton"]
            button:hover {
                transform: translateY(-1px);
            }

            .uywa-sidebar-logout-separator {
                height: 1px;
                margin: 1rem 0 0.85rem;
                background: rgba(255, 255, 255, 0.15);
            }

            .uywa-sidebar-footer {
                margin-top: 1.2rem;
                padding-top: 0.9rem;
                border-top: 1px solid rgba(255, 255, 255, 0.18);
                color: rgba(255, 255, 255, 0.80);
                font-size: 0.73rem;
                line-height: 1.7;
                text-align: center;
            }

            .uywa-sidebar-support-email {
                overflow-wrap: anywhere;
            }

            .uywa-sidebar-copyright {
                margin-top: 0.1rem;
                color: rgba(255, 255, 255, 0.56);
                font-size: 0.66rem;
            }
        </style>
        """
    )

    st.markdown(
        styles,
        unsafe_allow_html=True,
    )


def _render_sidebar_brand() -> None:
    """
    Renderiza el nombre y eslogan de la plataforma.
    """

    brand_html = (
        '<div class="uywa-sidebar-brand">'
        '<div class="uywa-sidebar-brand-title">'
        "UYWA Nutrition"
        "</div>"
        '<div class="uywa-sidebar-brand-subtitle">'
        "Nutrición de Precisión Basada en Evidencia"
        "</div>"
        "</div>"
        '<div class="uywa-sidebar-divider"></div>'
    )

    _render_html(
        brand_html
    )


def _render_user_card(
    display_name: str,
    email: str,
    role: str,
    plan_name: str,
    license_text: str,
    license_class: str,
) -> None:
    """
    Renderiza la tarjeta de información del usuario.
    """

    user_card_html = (
        '<div class="uywa-sidebar-user-card">'
        '<div class="uywa-sidebar-user-label">'
        "USUARIO"
        "</div>"
        '<div class="uywa-sidebar-user-name">'
        f"{display_name}"
        "</div>"
        '<div class="uywa-sidebar-user-email">'
        f"{email}"
        "</div>"
        '<div class="uywa-sidebar-user-role">'
        f"{role}"
        "</div>"
        '<div class="uywa-sidebar-plan-row">'
        "<span>Plan</span>"
        f"<strong>{plan_name}</strong>"
        "</div>"
        f'<div class="uywa-sidebar-license {license_class}">'
        '<span class="uywa-sidebar-license-dot"></span>'
        f"<span>{license_text}</span>"
        "</div>"
        "</div>"
    )

    _render_html(
        user_card_html
    )


def _render_expiration_date(
    expiration_date: str,
) -> None:
    """
    Renderiza la fecha de vigencia de la licencia.
    """

    safe_expiration = html.escape(
        expiration_date
    )

    expiration_html = (
        '<div class="uywa-sidebar-expiration">'
        "Vigencia hasta: "
        f"<strong>{safe_expiration}</strong>"
        "</div>"
    )

    _render_html(
        expiration_html
    )


def _render_sidebar_navigation() -> None:
    """
    Renderiza las opciones de navegación general
    de la plataforma.
    """

    current_view = _get_current_platform_view()

    selected_module = st.session_state.get(
        SELECTED_MODULE_KEY
    )

    launcher_is_active = (
        current_view == VIEW_LAUNCHER
        and not selected_module
    )

    account_is_active = (
        current_view == VIEW_ACCOUNT
    )

    navigation_header = (
        '<div class="uywa-sidebar-navigation">'
        '<div class="uywa-sidebar-section-label">'
        "PLATAFORMA"
        "</div>"
        "</div>"
    )

    _render_html(
        navigation_header
    )

    launcher_clicked = st.button(
        "▦  Aplicaciones",
        key="uywa_sidebar_launcher",
        use_container_width=True,
        type=(
            "primary"
            if launcher_is_active
            else "secondary"
        ),
    )

    if launcher_clicked:
        _go_to_launcher()
        st.rerun()

    account_clicked = st.button(
        "⚙  Mi cuenta",
        key="uywa_sidebar_account",
        use_container_width=True,
        type=(
            "primary"
            if account_is_active
            else "secondary"
        ),
    )

    if account_clicked:
        _go_to_account()
        st.rerun()


def _render_sidebar_footer() -> None:
    """
    Renderiza la información de soporte y derechos.
    """

    footer_html = (
        '<div class="uywa-sidebar-footer">'
        '<div class="uywa-sidebar-support-email">'
        "📧 uywasas@gmail.com"
        "</div>"
        '<div class="uywa-sidebar-copyright">'
        "Derechos reservados © 2026"
        "</div>"
        "</div>"
    )

    _render_html(
        footer_html
    )


def render_platform_sidebar(
    current_user: CurrentUser,
    logo_path: str = DEFAULT_LOGO_PATH,
) -> bool:
    """
    Renderiza la barra lateral de Uywa Platform.

    Devuelve True únicamente cuando el usuario pulsa
    el botón Cerrar sesión.
    """

    inject_sidebar_styles()

    display_name = html.escape(
        _get_user_display_name(
            current_user
        )
    )

    email = html.escape(
        _get_user_email(
            current_user
        )
    )

    role = html.escape(
        _get_user_role(
            current_user
        )
    )

    plan_name = html.escape(
        _get_plan_name(
            current_user
        )
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
        logo_file = Path(
            logo_path
        )

        if logo_file.exists():
            st.image(
                str(logo_file),
                use_container_width=True,
            )
        else:
            st.warning(
                f"No se encontró el logo en {logo_path}"
            )

        _render_sidebar_brand()

        _render_user_card(
            display_name=display_name,
            email=email,
            role=role,
            plan_name=plan_name,
            license_text=license_text,
            license_class=license_class,
        )

        if expiration_date:
            _render_expiration_date(
                expiration_date
            )

        _render_sidebar_navigation()

        _render_html(
            '<div class="uywa-sidebar-logout-separator"></div>'
        )

        logout_clicked = st.button(
            "Cerrar sesión",
            key="uywa_platform_logout",
            use_container_width=True,
            type="secondary",
        )

        _render_sidebar_footer()

    return logout_clicked
