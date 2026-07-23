from __future__ import annotations

import html
from collections.abc import Callable

import streamlit as st

from uywa_core.account import render_account_page
from uywa_core.current_session import get_current_user
from uywa_core.current_user import CurrentUser
from uywa_core.launcher.launcher_page import (
    clear_selected_module,
    get_selected_module,
)
from uywa_core.launcher.module_registry import (
    get_module_by_code,
)
from uywa_core.theme.html_utils import clean_html
from uywa_modules.pet_nutrition import (
    build_platform_user_adapter,
    render_pet_nutrition,
)


PLATFORM_VIEW_KEY = "uywa_platform_view"
SELECTED_MODULE_KEY = "uywa_selected_module"

VIEW_LAUNCHER = "launcher"
VIEW_ACCOUNT = "account"

MODULE_PET_NUTRITION = "pet_nutrition"
MODULE_FORMULATION_PLUS = "formulation_plus"


def _get_platform_view() -> str:
    """
    Obtiene la vista general seleccionada en la plataforma.

    Las vistas generales son páginas que no pertenecen
    directamente a un módulo, por ejemplo:

    - Launcher.
    - Mi cuenta.
    """

    current_view = st.session_state.get(
        PLATFORM_VIEW_KEY,
        VIEW_LAUNCHER,
    )

    allowed_views = {
        VIEW_LAUNCHER,
        VIEW_ACCOUNT,
    }

    if current_view not in allowed_views:
        current_view = VIEW_LAUNCHER

        st.session_state[
            PLATFORM_VIEW_KEY
        ] = current_view

    return str(current_view)


def _set_platform_view(
    view: str,
) -> None:
    """
    Cambia la vista general activa de la plataforma.
    """

    st.session_state[
        PLATFORM_VIEW_KEY
    ] = view


def _return_to_launcher() -> None:
    """
    Limpia el módulo seleccionado y regresa
    al Launcher principal.
    """

    clear_selected_module()

    st.session_state.pop(
        SELECTED_MODULE_KEY,
        None,
    )

    _set_platform_view(
        VIEW_LAUNCHER
    )


def _get_authenticated_user() -> CurrentUser | None:
    """
    Recupera el usuario autenticado actual.

    Devuelve None cuando no existe una sesión válida.
    """

    current_user = get_current_user()

    if current_user is None:
        return None

    if not getattr(
        current_user,
        "authenticated",
        False,
    ):
        return None

    return current_user


def _render_authentication_error() -> None:
    """
    Muestra un mensaje cuando no existe
    un usuario autenticado.
    """

    st.error(
        "No existe un usuario autenticado."
    )


def _render_back_button() -> bool:
    """
    Renderiza el botón para volver al Launcher.
    """

    return st.button(
        "← Volver a aplicaciones",
        key="uywa_router_back_to_launcher",
        use_container_width=False,
    )


def _inject_router_styles() -> None:
    """
    Inserta los estilos generales del router.
    """

    st.markdown(
        clean_html(
            """
            <style>
                .uywa-router-page {
                    padding-bottom: 1rem;
                }

                .uywa-router-module-header {
                    display: flex;
                    align-items: flex-start;
                    gap: 1rem;
                    padding: 1.4rem;
                    margin: 1rem 0 1.5rem;
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

                .uywa-router-module-content {
                    min-width: 0;
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
                    overflow-wrap: anywhere;
                }

                .uywa-router-module-description {
                    margin-top: 0.4rem;
                    color: #536174;
                    font-size: 0.9rem;
                    line-height: 1.5;
                    overflow-wrap: anywhere;
                }

                .uywa-router-placeholder {
                    padding: 1.2rem 1.3rem;
                    border: 1px solid #DDE3EC;
                    border-radius: 16px;
                    background: #F8FAFC;
                    color: #536174;
                    font-size: 0.88rem;
                    line-height: 1.6;
                }

                .uywa-router-placeholder strong {
                    color: #17233F;
                }

                @media (max-width: 720px) {
                    .uywa-router-module-header {
                        display: block;
                        padding: 1.15rem;
                    }

                    .uywa-router-module-icon {
                        margin-bottom: 0.8rem;
                    }

                    .uywa-router-module-title {
                        font-size: 1.4rem;
                    }
                }
            </style>
            """
        ),
        unsafe_allow_html=True,
    )


def _render_module_header(
    module_code: str,
) -> None:
    """
    Renderiza la cabecera del módulo indicado.
    """

    module = get_module_by_code(
        module_code
    )

    if module is None:
        return

    module_icon = html.escape(
        str(
            getattr(
                module,
                "icon",
                "▦",
            )
        )
    )

    module_title = html.escape(
        str(
            getattr(
                module,
                "title",
                module_code,
            )
        )
    )

    module_description = html.escape(
        str(
            getattr(
                module,
                "description",
                "",
            )
            or ""
        )
    )

    st.markdown(
        clean_html(
            f"""
            <div class="uywa-router-module-header">
                <div class="uywa-router-module-icon">
                    {module_icon}
                </div>

                <div class="uywa-router-module-content">
                    <div class="uywa-router-module-label">
                        UYWA PLATFORM
                    </div>

                    <div class="uywa-router-module-title">
                        {module_title}
                    </div>

                    <div
                        class="uywa-router-module-description"
                    >
                        {module_description}
                    </div>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def _render_unregistered_module_error(
    module_code: str,
) -> None:
    """
    Muestra el error correspondiente cuando el módulo
    seleccionado no existe en el registro.
    """

    safe_module_code = html.escape(
        module_code
    )

    st.error(
        "El módulo seleccionado no está registrado."
    )

    st.markdown(
        clean_html(
            f"""
            <div class="uywa-router-placeholder">
                No fue posible encontrar el módulo
                <strong>{safe_module_code}</strong>
                dentro del registro central de aplicaciones.
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def render_account_view() -> None:
    """
    Renderiza la página Mi cuenta.
    """

    current_user = _get_authenticated_user()

    if current_user is None:
        _render_authentication_error()
        return

    render_account_page(
        current_user
    )


def render_pet_nutrition_module() -> None:
    """
    Renderiza la aplicación Pet Nutrition integrada
    en Uywa Platform.
    """

    current_user = _get_authenticated_user()

    if current_user is None:
        _render_authentication_error()
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
    Renderiza la pantalla temporal de Formulation Plus.
    """

    st.markdown(
        clean_html(
            """
            <div class="uywa-router-placeholder">
                <strong>Uywa Formulation Plus</strong>
                todavía no está integrado dentro de la
                arquitectura modular de Uywa Platform.
                Su migración se realizará después de
                completar la organización del módulo
                Pet Nutrition.
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def render_generic_placeholder(
    module_code: str,
) -> None:
    """
    Renderiza una pantalla temporal para módulos
    registrados pero todavía no integrados.
    """

    module = get_module_by_code(
        module_code
    )

    module_title = (
        getattr(
            module,
            "title",
            None,
        )
        if module is not None
        else None
    )

    safe_module_name = html.escape(
        str(
            module_title
            or module_code
        )
    )

    st.markdown(
        clean_html(
            f"""
            <div class="uywa-router-placeholder">
                El módulo
                <strong>{safe_module_name}</strong>
                todavía no está integrado dentro de
                Uywa Platform.
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def _get_module_renderer(
    module_code: str,
) -> Callable[[], None] | None:
    """
    Devuelve la función encargada de renderizar
    un módulo integrado.

    Los nuevos módulos deberán incorporarse aquí
    mientras no exista un registro dinámico de
    renderizadores.
    """

    module_renderers: dict[
        str,
        Callable[[], None],
    ] = {
        MODULE_PET_NUTRITION:
            render_pet_nutrition_module,
        MODULE_FORMULATION_PLUS:
            render_formulation_placeholder,
    }

    return module_renderers.get(
        module_code
    )


def _render_module(
    module_code: str,
) -> None:
    """
    Renderiza el contenido correspondiente
    al módulo seleccionado.
    """

    module = get_module_by_code(
        module_code
    )

    if module is None:
        _render_unregistered_module_error(
            module_code
        )
        return

    renderer = _get_module_renderer(
        module_code
    )

    if module_code == MODULE_PET_NUTRITION:
        if renderer is not None:
            renderer()

        return

    _render_module_header(
        module_code
    )

    if renderer is not None:
        renderer()
        return

    render_generic_placeholder(
        module_code
    )


def _render_selected_module_view(
    selected_module: str,
) -> None:
    """
    Renderiza la vista de un módulo seleccionado,
    incluyendo su control de retorno.
    """

    _inject_router_styles()

    st.markdown(
        '<div class="uywa-router-page">',
        unsafe_allow_html=True,
    )

    if _render_back_button():
        _return_to_launcher()
        st.rerun()

    _render_module(
        selected_module
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


def render_platform_view() -> bool:
    """
    Resuelve y renderiza la vista activa de la plataforma.

    Devuelve:
        True:
            El router renderizó una vista o un módulo.

        False:
            No existe una vista especial ni un módulo
            seleccionado, por lo que el archivo principal
            debe mostrar el Launcher.
    """

    selected_module = get_selected_module()

    if selected_module:
        _set_platform_view(
            VIEW_LAUNCHER
        )

        _render_selected_module_view(
            str(selected_module)
        )

        return True

    current_view = _get_platform_view()

    if current_view == VIEW_ACCOUNT:
        render_account_view()
        return True

    return False


def render_selected_module() -> bool:
    """
    Mantiene compatibilidad con la implementación
    anterior del router.

    Esta función ahora resuelve tanto:

    - Vistas generales de la plataforma.
    - Módulos seleccionados.
    - Retorno al Launcher.

    Devuelve False únicamente cuando debe mostrarse
    el Launcher.
    """

    return render_platform_view()
