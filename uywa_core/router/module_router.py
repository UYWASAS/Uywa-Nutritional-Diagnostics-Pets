from uywa_core.current_session import (
    get_current_user,
)
from uywa_modules.pet_nutrition import (
    build_platform_user_adapter,
    render_pet_nutrition,
)

from __future__ import annotations

import streamlit as st

from uywa_core.launcher.launcher_page import (
    clear_selected_module,
    get_selected_module,
)
from uywa_core.launcher.module_registry import (
    get_module_by_code,
)
from uywa_core.theme.html_utils import clean_html


def _render_back_button() -> bool:
    """
    Renderiza el botón para regresar al Launcher.

    Devuelve True cuando el usuario pulsa el botón.
    """

    return st.button(
        "← Volver a aplicaciones",
        key="uywa_router_back_to_launcher",
        use_container_width=False,
    )


def _render_module_header(
    module_code: str,
) -> None:
    """
    Muestra una cabecera básica del módulo seleccionado.
    """

    module = get_module_by_code(module_code)

    if module is None:
        return

    module_html = clean_html(
        f"""
        <div class="uywa-router-module-header">
            <div class="uywa-router-module-icon">
                {module.icon}
            </div>

            <div>
                <div class="uywa-router-module-label">
                    UYWA PLATFORM
                </div>

                <div class="uywa-router-module-title">
                    {module.title}
                </div>

                <div class="uywa-router-module-description">
                    {module.description}
                </div>
            </div>
        </div>
        """
    )

    st.markdown(
        module_html,
        unsafe_allow_html=True,
    )


def _inject_router_styles() -> None:
    """
    Inserta los estilos básicos del router.
    """

    styles = clean_html(
        """
        <style>
            .uywa-router-module-header {
                display: flex;
                align-items: flex-start;
                gap: 1rem;
                padding: 1.4rem;
                margin: 1rem 0 1.5rem 0;
                border: 1px solid #DDE3EC;
                border-radius: 18px;
                background: #FFFFFF;
                box-shadow:
                    0 8px 24px
                    rgba(23, 35, 63, 0.07);
            }

            .uywa-router-module-icon {
                display: flex;
                align-items: center;
                justify-content: center;
                flex: 0 0 58px;
                width: 58px;
                height: 58px;
                border-radius: 14px;
                background: #EFF8F8;
                font-size: 1.9rem;
            }

            .uywa-router-module-label {
                margin-bottom: 0.25rem;
                color: #28777E;
                font-size: 0.68rem;
                font-weight: 800;
                letter-spacing: 0.12em;
            }

            .uywa-router-module-title {
                color: #17233F;
                font-size: 1.65rem;
                font-weight: 800;
                line-height: 1.2;
            }

            .uywa-router-module-description {
                margin-top: 0.4rem;
                color: #536174;
                font-size: 0.9rem;
                line-height: 1.5;
            }
        </style>
        """
    )

    st.markdown(
        styles,
        unsafe_allow_html=True,
    )


def render_pet_nutrition_module() -> None:
    """
    Renderiza la aplicación real de Pet Nutrition.
    """

    current_user = get_current_user()

    if not getattr(
        current_user,
        "authenticated",
        False,
    ):
        st.error(
            "No existe un usuario autenticado."
        )
        return

    legacy_user = build_platform_user_adapter(
        current_user
    )

    render_pet_nutrition(
        user=legacy_user,
        apply_pet_theme=True,
        show_app_title=True,
    )


def render_formulation_placeholder() -> None:
    """
    Pantalla temporal del módulo Formulation Plus.
    """

    st.info(
        "Uywa Formulation Plus todavía no está integrado."
    )


def render_generic_placeholder(
    module_code: str,
) -> None:
    """
    Pantalla temporal para módulos aún no integrados.
    """

    st.info(
        f"El módulo '{module_code}' todavía no está integrado."
    )


def render_selected_module() -> bool:
    """
    Renderiza el módulo actualmente seleccionado.

    Retorna:
    - True: existe un módulo seleccionado y fue procesado.
    - False: no existe un módulo seleccionado.
    """

    selected_module = get_selected_module()

    if not selected_module:
        return False

    module = get_module_by_code(selected_module)

    if module is None:
        st.error(
            "El módulo seleccionado no está registrado."
        )

        if _render_back_button():
            clear_selected_module()
            st.rerun()

        return True

    _inject_router_styles()

    if _render_back_button():
        clear_selected_module()
        st.rerun()

    if selected_module == "pet_nutrition":
        render_pet_nutrition_module()
    
    else:
        _render_module_header(
            selected_module
        )
    
        if selected_module == "formulation_plus":
            render_formulation_placeholder()
        else:
            render_generic_placeholder(
                selected_module
            )

    return True
