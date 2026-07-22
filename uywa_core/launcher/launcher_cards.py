from __future__ import annotations

import html

import streamlit as st

from uywa_core.current_user import CurrentUser
from uywa_core.launcher.module_registry import PlatformModule


def inject_launcher_card_styles() -> None:
    """
    Inserta los estilos utilizados por las tarjetas del Launcher.
    """

    st.markdown(
        """
        <style>
            .uywa-module-card {
                min-height: 260px;
                padding: 1.45rem;
                margin-bottom: 1rem;
                border: 1px solid rgba(49, 88, 73, 0.18);
                border-radius: 18px;
                background:
                    linear-gradient(
                        145deg,
                        rgba(255, 255, 255, 0.98),
                        rgba(245, 249, 247, 0.98)
                    );
                box-shadow:
                    0 8px 24px rgba(25, 58, 46, 0.08);
            }

            .uywa-module-card:hover {
                border-color: rgba(49, 88, 73, 0.32);
                box-shadow:
                    0 12px 30px rgba(25, 58, 46, 0.12);
            }

            .uywa-module-icon {
                font-size: 2.35rem;
                line-height: 1;
                margin-bottom: 1rem;
            }

            .uywa-module-title {
                margin: 0 0 0.65rem 0;
                color: #1f3b31;
                font-size: 1.25rem;
                font-weight: 750;
            }

            .uywa-module-description {
                min-height: 92px;
                margin: 0;
                color: #52645d;
                font-size: 0.95rem;
                line-height: 1.55;
            }

            .uywa-module-status {
                display: inline-block;
                margin-top: 1.15rem;
                padding: 0.3rem 0.7rem;
                border-radius: 999px;
                font-size: 0.78rem;
                font-weight: 700;
            }

            .uywa-status-available {
                color: #1f694f;
                background: rgba(46, 160, 112, 0.13);
            }

            .uywa-status-restricted {
                color: #8a5a16;
                background: rgba(221, 157, 55, 0.14);
            }

            .uywa-status-coming-soon {
                color: #5d6470;
                background: rgba(104, 113, 128, 0.13);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def user_can_access_module(
    current_user: CurrentUser,
    module: PlatformModule,
) -> bool:
    """
    Verifica el acceso efectivo del usuario a un módulo.
    """

    if not current_user.authenticated:
        return False

    if not current_user.active:
        return False

    if current_user.is_admin:
        return True

    return current_user.can_use(module.code)


def _get_status_data(
    current_user: CurrentUser,
    module: PlatformModule,
) -> tuple[str, str]:
    """
    Determina el texto y la clase visual del estado del módulo.
    """

    if module.is_coming_soon:
        return "Próximamente", "uywa-status-coming-soon"

    if user_can_access_module(current_user, module):
        return "Disponible", "uywa-status-available"

    return "Sin acceso", "uywa-status-restricted"


def render_module_card(
    module: PlatformModule,
    current_user: CurrentUser,
    column_key: str,
) -> str | None:
    """
    Renderiza una tarjeta y devuelve el código del módulo seleccionado.

    Retorna None cuando el usuario no pulsa el botón.
    """

    status_text, status_class = _get_status_data(
        current_user=current_user,
        module=module,
    )

    title = html.escape(module.title)
    description = html.escape(module.description)
    icon = html.escape(module.icon)
    status = html.escape(status_text)

    st.markdown(
        f"""
        <div class="uywa-module-card">
            <div class="uywa-module-icon">{icon}</div>
            <h3 class="uywa-module-title">{title}</h3>
            <p class="uywa-module-description">{description}</p>
            <span class="uywa-module-status {status_class}">
                {status}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    module_access = user_can_access_module(
        current_user=current_user,
        module=module,
    )

    button_disabled = (
        not module.is_available
        or not module_access
    )

    button_label = (
        module.button_text
        if module.is_available
        else "Próximamente"
    )

    clicked = st.button(
        button_label,
        key=f"launcher_module_{module.code}_{column_key}",
        use_container_width=True,
        disabled=button_disabled,
    )

    if clicked:
        return module.code

    return None
