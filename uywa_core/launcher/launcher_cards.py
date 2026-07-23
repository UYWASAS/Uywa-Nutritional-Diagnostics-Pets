from __future__ import annotations

import html
from textwrap import dedent

import streamlit as st

from uywa_core.theme.html_utils import clean_html
from uywa_core.current_user import CurrentUser
from uywa_core.launcher.module_registry import PlatformModule
from uywa_core.theme.tokens import (
    COLOR_AQUA_PALE,
    COLOR_BACKGROUND,
    COLOR_BORDER,
    COLOR_DISABLED,
    COLOR_DISABLED_BACKGROUND,
    COLOR_SUCCESS,
    COLOR_SUCCESS_BACKGROUND,
    COLOR_SURFACE,
    COLOR_TEAL,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_WARNING,
    COLOR_WARNING_BACKGROUND,
    RADIUS_LARGE,
    RADIUS_PILL,
    SHADOW_CARD,
    SHADOW_CARD_HOVER,
)


def inject_launcher_card_styles() -> None:
    """
    Inserta los estilos de las tarjetas del Launcher.
    """

    st.markdown(
        dedent(
            f"""
            <style>
                .uywa-module-card {{
                    position: relative;
                    min-height: 282px;
                    padding: 1.55rem;
                    margin-bottom: 0.65rem;
                    border: 1px solid {COLOR_BORDER};
                    border-radius: {RADIUS_LARGE};
                    background:
                        linear-gradient(
                            145deg,
                            {COLOR_SURFACE} 0%,
                            #FBFCFE 100%
                        );
                    box-shadow: {SHADOW_CARD};
                    overflow: hidden;
                    transition:
                        transform 0.18s ease,
                        box-shadow 0.18s ease,
                        border-color 0.18s ease;
                }}

                .uywa-module-card::before {{
                    content: "";
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 5px;
                    background:
                        linear-gradient(
                            90deg,
                            {COLOR_TEAL},
                            #65BEC6
                        );
                }}

                .uywa-module-card:hover {{
                    transform: translateY(-3px);
                    border-color: rgba(40, 119, 126, 0.34);
                    box-shadow: {SHADOW_CARD_HOVER};
                }}

                .uywa-module-card-disabled {{
                    background:
                        linear-gradient(
                            145deg,
                            {COLOR_SURFACE},
                            {COLOR_BACKGROUND}
                        );
                }}

                .uywa-module-card-disabled::before {{
                    background: #B8C0CC;
                }}

                .uywa-module-icon-container {{
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    width: 54px;
                    height: 54px;
                    margin-bottom: 1.1rem;
                    border-radius: 15px;
                    background: {COLOR_AQUA_PALE};
                }}

                .uywa-module-card-disabled
                .uywa-module-icon-container {{
                    background: {COLOR_DISABLED_BACKGROUND};
                }}

                .uywa-module-icon {{
                    font-size: 1.85rem;
                    line-height: 1;
                }}

                .uywa-module-title {{
                    margin: 0 0 0.65rem 0;
                    color: {COLOR_TEXT_PRIMARY};
                    font-size: 1.22rem;
                    font-weight: 800;
                    letter-spacing: -0.02em;
                }}

                .uywa-module-description {{
                    min-height: 96px;
                    margin: 0;
                    color: {COLOR_TEXT_SECONDARY};
                    font-size: 0.91rem;
                    line-height: 1.58;
                }}

                .uywa-module-footer {{
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    gap: 0.75rem;
                    margin-top: 1.15rem;
                }}

                .uywa-module-status {{
                    display: inline-flex;
                    align-items: center;
                    gap: 0.38rem;
                    padding: 0.32rem 0.7rem;
                    border-radius: {RADIUS_PILL};
                    font-size: 0.72rem;
                    font-weight: 750;
                }}

                .uywa-module-status-dot {{
                    width: 7px;
                    height: 7px;
                    border-radius: 50%;
                }}

                .uywa-status-available {{
                    color: {COLOR_SUCCESS};
                    background: {COLOR_SUCCESS_BACKGROUND};
                }}

                .uywa-status-available
                .uywa-module-status-dot {{
                    background: {COLOR_SUCCESS};
                }}

                .uywa-status-restricted {{
                    color: {COLOR_WARNING};
                    background: {COLOR_WARNING_BACKGROUND};
                }}

                .uywa-status-restricted
                .uywa-module-status-dot {{
                    background: {COLOR_WARNING};
                }}

                .uywa-status-coming-soon {{
                    color: {COLOR_DISABLED};
                    background: {COLOR_DISABLED_BACKGROUND};
                }}

                .uywa-status-coming-soon
                .uywa-module-status-dot {{
                    background: {COLOR_DISABLED};
                }}

                .uywa-module-code {{
                    color: {COLOR_TEXT_MUTED};
                    font-size: 0.68rem;
                    font-weight: 650;
                    letter-spacing: 0.04em;
                    text-transform: uppercase;
                }}
            </style>
            """
        ),
        unsafe_allow_html=True,
    )


def user_can_access_module(
    current_user: CurrentUser,
    module: PlatformModule,
) -> bool:
    """
    Verifica el acceso efectivo del usuario a un módulo.
    """

    if not getattr(current_user, "authenticated", False):
        return False

    if not getattr(current_user, "active", False):
        return False

    role = str(
        getattr(current_user, "role", "") or ""
    ).lower()

    if (
        getattr(current_user, "is_admin", False)
        or role
        in {
            "admin",
            "administrator",
            "super_admin",
            "superadmin",
        }
    ):
        return True

    can_use = getattr(current_user, "can_use", None)

    if callable(can_use):
        return bool(can_use(module.code))

    return False


def _get_status_data(
    current_user: CurrentUser,
    module: PlatformModule,
) -> tuple[str, str]:
    if module.is_coming_soon:
        return (
            "Próximamente",
            "uywa-status-coming-soon",
        )

    if user_can_access_module(
        current_user=current_user,
        module=module,
    ):
        return (
            "Disponible",
            "uywa-status-available",
        )

    return (
        "Sin acceso",
        "uywa-status-restricted",
    )


def render_module_card(
    module: PlatformModule,
    current_user: CurrentUser,
    column_key: str,
) -> str | None:
    """
    Renderiza una tarjeta de módulo.
    """

    status_text, status_class = _get_status_data(
        current_user=current_user,
        module=module,
    )

    module_access = user_can_access_module(
        current_user=current_user,
        module=module,
    )

    button_disabled = (
        not module.is_available
        or not module_access
    )

    card_class = (
        "uywa-module-card"
        if not button_disabled
        else "uywa-module-card uywa-module-card-disabled"
    )

    title = html.escape(str(module.title))
    description = html.escape(str(module.description))
    icon = html.escape(str(module.icon))
    status = html.escape(str(status_text))
    module_code = html.escape(str(module.code))

    card_html = clean_html(
        f"""
        <div class="{card_class}">
            <div class="uywa-module-icon-container">
                <div class="uywa-module-icon">
                    {icon}
                </div>
            </div>
            <h3 class="uywa-module-title">
                {title}
            </h3>
            <p class="uywa-module-description">
                {description}
            </p>
            <div class="uywa-module-footer">
                <span class="uywa-module-status {status_class}">
                    <span class="uywa-module-status-dot"></span>
                    {status}
                </span>
                <span class="uywa-module-code">
                    {module_code}
                </span>
            </div>
        </div>
        """
    )
    
    st.markdown(
        card_html,
        unsafe_allow_html=True,
    )

    button_label = (
        module.button_text
        if module.is_available
        else "Próximamente"
    )

    clicked = st.button(
        button_label,
        key=(
            f"launcher_module_"
            f"{module.code}_"
            f"{column_key}"
        ),
        use_container_width=True,
        disabled=button_disabled,
    )

    if clicked:
        return module.code

    return None
