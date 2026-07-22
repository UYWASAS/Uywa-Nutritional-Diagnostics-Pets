from __future__ import annotations

import streamlit as st

from uywa_core.current_session import get_current_user
from uywa_core.launcher.launcher_cards import (
    inject_launcher_card_styles,
    render_module_card,
)
from uywa_core.launcher.module_registry import (
    get_platform_modules,
)


LAUNCHER_SELECTED_MODULE_KEY = "uywa_selected_module"


def initialize_launcher_state() -> None:
    """
    Inicializa las variables utilizadas por el Launcher.
    """

    if LAUNCHER_SELECTED_MODULE_KEY not in st.session_state:
        st.session_state[LAUNCHER_SELECTED_MODULE_KEY] = None


def select_module(module_code: str) -> None:
    """
    Registra el módulo seleccionado por el usuario.
    """

    st.session_state[LAUNCHER_SELECTED_MODULE_KEY] = module_code


def get_selected_module() -> str | None:
    """
    Devuelve el código del módulo seleccionado.
    """

    value = st.session_state.get(
        LAUNCHER_SELECTED_MODULE_KEY
    )

    if not value:
        return None

    return str(value)


def clear_selected_module() -> None:
    """
    Regresa al Launcher.
    """

    st.session_state[LAUNCHER_SELECTED_MODULE_KEY] = None


def _render_launcher_header() -> None:
    """
    Muestra el encabezado principal del Launcher.
    """

    st.title("Uywa Platform")

    st.caption(
        "Herramientas digitales para nutrición y producción animal."
    )


def _render_user_summary() -> None:
    """
    Muestra un resumen del usuario autenticado.
    """

    current_user = get_current_user()

    display_name = (
        current_user.full_name
        or current_user.email
        or "Usuario"
    )

    plan_name = (
        current_user.plan_name
        or current_user.plan_code
        or "Sin plan asignado"
    )

    left_column, right_column = st.columns(
        [2, 1]
    )

    with left_column:
        st.subheader(f"Bienvenido, {display_name}")

        st.write(
            "Selecciona una herramienta para comenzar."
        )

    with right_column:
        st.markdown(
            f"""
            **Rol:** {current_user.role or "No disponible"}  
            **Plan:** {plan_name}
            """
        )


def _render_module_grid() -> None:
    """
    Renderiza los módulos en una cuadrícula de dos columnas.
    """

    current_user = get_current_user()
    modules = get_platform_modules()

    for row_start in range(0, len(modules), 2):
        row_modules = modules[row_start : row_start + 2]
        columns = st.columns(2, gap="large")

        for column_index, module in enumerate(row_modules):
            with columns[column_index]:
                selected_module = render_module_card(
                    module=module,
                    current_user=current_user,
                    column_key=(
                        f"{row_start}_{column_index}"
                    ),
                )

                if selected_module:
                    select_module(selected_module)
                    st.rerun()


def render_launcher() -> str | None:
    """
    Renderiza la pantalla principal de Uywa Platform.

    Retorna el código del módulo seleccionado. En esta primera etapa
    todavía no carga directamente la aplicación correspondiente.
    """

    initialize_launcher_state()
    inject_launcher_card_styles()

    current_user = get_current_user()

    if not current_user.authenticated:
        st.error(
            "No existe un usuario autenticado para mostrar "
            "Uywa Platform."
        )
        return None

    if not current_user.active:
        st.warning(
            "El perfil se encuentra inactivo. Contacta al "
            "administrador de la plataforma."
        )
        return None

    selected_module = get_selected_module()

    if selected_module:
        st.success(
            f"Módulo seleccionado: `{selected_module}`"
        )

        st.info(
            "La selección funciona correctamente. En la siguiente "
            "etapa conectaremos este código con la aplicación real."
        )

        if st.button(
            "← Regresar a Uywa Platform",
            use_container_width=True,
        ):
            clear_selected_module()
            st.rerun()

        return selected_module

    _render_launcher_header()
    _render_user_summary()

    st.divider()

    st.subheader("Aplicaciones")

    _render_module_grid()

    return None
