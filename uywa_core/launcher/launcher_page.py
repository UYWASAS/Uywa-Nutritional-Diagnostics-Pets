from __future__ import annotations

import html

import streamlit as st

from uywa_core.current_session import get_current_user
from uywa_core.launcher.launcher_cards import (
    inject_launcher_card_styles,
    render_module_card,
)
from uywa_core.launcher.module_registry import (
    get_module_by_code,
    get_platform_modules,
)


LAUNCHER_SELECTED_MODULE_KEY = (
    "uywa_selected_module"
)


def initialize_launcher_state() -> None:
    """
    Inicializa las variables de sesión utilizadas por el Launcher.
    """

    if (
        LAUNCHER_SELECTED_MODULE_KEY
        not in st.session_state
    ):
        st.session_state[
            LAUNCHER_SELECTED_MODULE_KEY
        ] = None


def select_module(
    module_code: str,
) -> None:
    """
    Guarda el módulo seleccionado.
    """

    st.session_state[
        LAUNCHER_SELECTED_MODULE_KEY
    ] = module_code


def get_selected_module() -> str | None:
    """
    Recupera el código del módulo seleccionado.
    """

    selected_module = st.session_state.get(
        LAUNCHER_SELECTED_MODULE_KEY
    )

    if not selected_module:
        return None

    return str(selected_module)


def clear_selected_module() -> None:
    """
    Elimina la selección de módulo actual.
    """

    st.session_state[
        LAUNCHER_SELECTED_MODULE_KEY
    ] = None


def _get_display_name(
    current_user: object,
) -> str:
    """
    Obtiene el nombre visible del usuario utilizando las
    propiedades disponibles en CurrentUser.
    """

    profile = getattr(
        current_user,
        "profile",
        None,
    )

    profile_name = None

    if isinstance(profile, dict):
        profile_name = (
            profile.get("full_name")
            or profile.get("name")
            or profile.get("display_name")
        )

    metadata = getattr(
        current_user,
        "metadata",
        None,
    )

    metadata_name = None

    if isinstance(metadata, dict):
        metadata_name = (
            metadata.get("full_name")
            or metadata.get("name")
            or metadata.get("display_name")
        )

    return str(
        getattr(current_user, "full_name", None)
        or getattr(current_user, "name", None)
        or profile_name
        or metadata_name
        or getattr(current_user, "email", None)
        or "Usuario"
    )


def _get_plan_name(
    current_user: object,
) -> str:
    """
    Recupera el nombre del plan sin depender de una sola
    estructura de CurrentUser.
    """

    plan = getattr(
        current_user,
        "plan",
        None,
    )

    plan_name = None

    if isinstance(plan, dict):
        plan_name = (
            plan.get("name")
            or plan.get("code")
        )
    elif plan is not None:
        plan_name = (
            getattr(plan, "name", None)
            or getattr(plan, "code", None)
        )

    return str(
        getattr(current_user, "plan_name", None)
        or getattr(current_user, "plan_code", None)
        or plan_name
        or "Sin plan asignado"
    )


def _is_admin(
    current_user: object,
) -> bool:
    """
    Verifica si el usuario tiene un rol administrativo.
    """

    role = str(
        getattr(current_user, "role", "")
        or ""
    ).lower()

    return bool(
        getattr(current_user, "is_admin", False)
        or role in {
            "admin",
            "administrator",
            "super_admin",
            "superadmin",
        }
    )


def _render_launcher_header(
    current_user: object,
) -> None:
    """
    Renderiza la cabecera principal.
    """

    display_name = html.escape(
        _get_display_name(current_user)
    )

    st.markdown(
        f"""
        <div class="uywa-launcher-hero">
            <div class="uywa-launcher-eyebrow">
                UYWA PLATFORM
            </div>

            <h1 class="uywa-launcher-title">
                Bienvenido, {display_name}
            </h1>

            <p class="uywa-launcher-subtitle">
                Selecciona una herramienta para comenzar.
                Todos tus módulos están organizados dentro
                de un mismo espacio de trabajo.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_platform_summary(
    current_user: object,
) -> None:
    """
    Presenta un resumen del plan, rol y acceso.
    """

    role = str(
        getattr(current_user, "role", None)
        or "Usuario"
    )

    plan_name = _get_plan_name(
        current_user
    )

    modules = getattr(
        current_user,
        "modules",
        [],
    )

    if isinstance(modules, dict):
        enabled_modules = len(modules)
    elif isinstance(modules, (list, tuple, set)):
        enabled_modules = len(modules)
    else:
        enabled_modules = 0

    if _is_admin(current_user):
        access_text = "Administrativo"
    else:
        access_text = (
            f"{enabled_modules} módulos"
        )

    column_1, column_2, column_3 = st.columns(
        3
    )

    with column_1:
        st.metric(
            label="Plan actual",
            value=plan_name,
        )

    with column_2:
        st.metric(
            label="Rol",
            value=role.replace(
                "_",
                " ",
            ).title(),
        )

    with column_3:
        st.metric(
            label="Acceso",
            value=access_text,
        )


def _render_module_grid(
    current_user: object,
) -> None:
    """
    Renderiza los módulos registrados en una cuadrícula
    de dos columnas.
    """

    modules = get_platform_modules()

    if not modules:
        st.info(
            "No existen módulos registrados en la plataforma."
        )
        return

    for row_start in range(
        0,
        len(modules),
        2,
    ):
        row_modules = modules[
            row_start : row_start + 2
        ]

        columns = st.columns(
            2,
            gap="large",
        )

        for column_index, module in enumerate(
            row_modules
        ):
            with columns[column_index]:
                selected_module = render_module_card(
                    module=module,
                    current_user=current_user,
                    column_key=(
                        f"{row_start}_"
                        f"{column_index}"
                    ),
                )

                if selected_module:
                    select_module(
                        selected_module
                    )
                    st.rerun()


def _render_selected_module_placeholder(
    selected_module_code: str,
) -> None:
    """
    Renderiza temporalmente la pantalla del módulo elegido
    hasta que se conecten las aplicaciones reales.
    """

    module = get_module_by_code(
        selected_module_code
    )

    if module is None:
        st.error(
            "El módulo seleccionado no está registrado."
        )

        if st.button(
            "← Regresar a Uywa Platform",
            key="launcher_back_invalid_module",
            use_container_width=True,
        ):
            clear_selected_module()
            st.rerun()

        return

    module_icon = html.escape(
        str(module.icon)
    )

    module_title = html.escape(
        str(module.title)
    )

    module_description = html.escape(
        str(module.description)
    )

    st.markdown(
        f"""
        <div class="uywa-selected-module-header">
            <div class="uywa-selected-module-icon">
                {module_icon}
            </div>

            <div>
                <div class="uywa-selected-module-label">
                    MÓDULO SELECCIONADO
                </div>

                <h1>
                    {module_title}
                </h1>

                <p>
                    {module_description}
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.success(
        "La selección del módulo funciona correctamente."
    )

    st.info(
        "Esta es una pantalla temporal. En la siguiente "
        "etapa se conectará con la aplicación real."
    )

    if st.button(
        "← Regresar a Uywa Platform",
        key="launcher_back_to_platform",
        use_container_width=True,
    ):
        clear_selected_module()
        st.rerun()


def inject_launcher_page_styles() -> None:
    """
    Inserta los estilos específicos de la página Launcher.
    """

    st.markdown(
        """
        <style>
            .uywa-launcher-hero {
                position: relative;
                padding: 2rem 2.1rem;
                margin-bottom: 1.5rem;
                border-radius: 20px;
                background:
                    linear-gradient(
                        130deg,
                        #17233F 0%,
                        #243454 60%,
                        #28777E 120%
                    );
                box-shadow:
                    0 12px 32px
                    rgba(23, 35, 63, 0.16);
                overflow: hidden;
            }

            .uywa-launcher-hero::after {
                content: "";
                position: absolute;
                top: -100px;
                right: -80px;
                width: 260px;
                height: 260px;
                border-radius: 50%;
                background:
                    rgba(101, 190, 198, 0.14);
            }

            .uywa-launcher-eyebrow {
                position: relative;
                z-index: 1;
                margin-bottom: 0.65rem;
                color: #65BEC6;
                font-size: 0.72rem;
                font-weight: 800;
                letter-spacing: 0.14em;
            }

            .uywa-launcher-title {
                position: relative;
                z-index: 1;
                margin: 0;
                color: #FFFFFF;
                font-size:
                    clamp(
                        1.8rem,
                        4vw,
                        2.7rem
                    );
                font-weight: 800;
            }

            .uywa-launcher-subtitle {
                position: relative;
                z-index: 1;
                max-width: 720px;
                margin: 0.8rem 0 0 0;
                color:
                    rgba(
                        255,
                        255,
                        255,
                        0.78
                    );
                font-size: 0.96rem;
                line-height: 1.65;
            }

            .uywa-section-heading {
                margin-top: 2rem;
                margin-bottom: 1rem;
            }

            .uywa-section-heading h2 {
                margin-bottom: 0.25rem;
            }

            .uywa-section-heading p {
                margin-top: 0;
                color: #7C8798;
            }

            .uywa-selected-module-header {
                display: flex;
                align-items: flex-start;
                gap: 1.4rem;
                padding: 2rem;
                margin-bottom: 1.4rem;
                border: 1px solid #DDE3EC;
                border-radius: 20px;
                background: #FFFFFF;
                box-shadow:
                    0 8px 24px
                    rgba(23, 35, 63, 0.08);
            }

            .uywa-selected-module-icon {
                display: flex;
                align-items: center;
                justify-content: center;
                flex: 0 0 70px;
                width: 70px;
                height: 70px;
                border-radius: 18px;
                background: #EFF8F8;
                font-size: 2.4rem;
            }

            .uywa-selected-module-label {
                color: #28777E;
                font-size: 0.7rem;
                font-weight: 800;
                letter-spacing: 0.12em;
            }

            .uywa-selected-module-header h1 {
                margin:
                    0.3rem
                    0
                    0.45rem
                    0;
            }

            .uywa-selected-module-header p {
                margin: 0;
            }

            @media (max-width: 700px) {
                .uywa-launcher-hero {
                    padding: 1.5rem;
                }

                .uywa-selected-module-header {
                    flex-direction: column;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_launcher() -> str | None:
    """
    Renderiza la página principal de Uywa Platform.
    """

    initialize_launcher_state()
    inject_launcher_card_styles()
    inject_launcher_page_styles()

    current_user = get_current_user()

    if not getattr(
        current_user,
        "authenticated",
        False,
    ):
        st.error(
            "No existe un usuario autenticado."
        )
        return None

    if not getattr(
        current_user,
        "active",
        False,
    ):
        st.warning(
            "El perfil se encuentra inactivo. "
            "Contacta al administrador de la plataforma."
        )
        return None

    selected_module = get_selected_module()

    if selected_module:
        _render_selected_module_placeholder(
            selected_module
        )
        return selected_module

    _render_launcher_header(
        current_user
    )

    _render_platform_summary(
        current_user
    )

    st.markdown(
        """
        <div class="uywa-section-heading">
            <h2>Aplicaciones</h2>

            <p>
                Herramientas disponibles dentro de tu cuenta.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _render_module_grid(
        current_user
    )

    return None
