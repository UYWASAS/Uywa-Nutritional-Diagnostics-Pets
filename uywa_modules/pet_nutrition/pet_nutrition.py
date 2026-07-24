from __future__ import annotations

from typing import Any

import streamlit as st

from services.profile_manager import load_profile, save_profile
from utils.ui_components import (
    inject_global_css,
    render_app_title,
)
from utils.ui_theme import inject_uywa_theme

from .pages.analysis_page import show_analysis_page
from .pages.compare_page import show_compare_page
from .pages.followup_page import show_followup_page
from .pages.profile_page import show_profile_page
from .pages.summary_page import show_summary_page


PET_STATE_PREFIX = "uywa_pet_"

PET_ACTIVE_PAGE_KEY = (
    f"{PET_STATE_PREFIX}active_page"
)

PET_PROFILE_KEY = "profile"

PET_NAV_ITEMS = [
    (
        "Perfil de Mascota",
        "🐾",
        "Perfil de Mascota",
    ),
    (
        "Análisis",
        "🔬",
        "Análisis",
    ),
    (
        "Comparador",
        "⚖️",
        "Comparador",
    ),
    (
        "Resumen y Exportar",
        "📋",
        "Resumen y Exportar",
    ),
    (
        "Seguimiento del Paciente",
        "📈",
        "Seguimiento del Paciente",
    ),
]


def initialize_pet_ui() -> None:
    """
    Aplica los estilos propios de Pet Nutrition.

    No ejecuta st.set_page_config(), porque esta
    responsabilidad corresponde al contenedor principal.
    """

    inject_global_css()
    inject_uywa_theme()


def build_platform_user_adapter(
    current_user: object,
) -> dict[str, Any]:
    """
    Convierte CurrentUser en un diccionario compatible
    con las funciones heredadas de Pet Nutrition.
    """

    metadata = getattr(
        current_user,
        "metadata",
        None,
    )

    if not isinstance(metadata, dict):
        metadata = {}

    profile = getattr(
        current_user,
        "profile",
        None,
    )

    if not isinstance(profile, dict):
        profile = {}

    plan = getattr(
        current_user,
        "plan",
        None,
    )

    if isinstance(plan, dict):
        plan_name = (
            plan.get("name")
            or plan.get("code")
        )

    elif plan is not None:
        plan_name = (
            getattr(
                plan,
                "name",
                None,
            )
            or getattr(
                plan,
                "code",
                None,
            )
        )

    else:
        plan_name = None

    subscription = getattr(
        current_user,
        "subscription",
        None,
    )

    subscription_expiration = None

    if isinstance(subscription, dict):
        subscription_expiration = (
            subscription.get(
                "expires_at"
            )
            or subscription.get(
                "end_date"
            )
            or subscription.get(
                "subscription_expires_at"
            )
        )

    user_id = (
        getattr(
            current_user,
            "id",
            None,
        )
        or getattr(
            current_user,
            "user_id",
            None,
        )
        or getattr(
            current_user,
            "auth_user_id",
            None,
        )
        or metadata.get(
            "user_id"
        )
        or metadata.get(
            "sub"
        )
    )

    email = (
        getattr(
            current_user,
            "email",
            None,
        )
        or profile.get(
            "email"
        )
        or metadata.get(
            "email"
        )
        or ""
    )

    display_name = (
        getattr(
            current_user,
            "full_name",
            None,
        )
        or getattr(
            current_user,
            "display_name",
            None,
        )
        or getattr(
            current_user,
            "name",
            None,
        )
        or profile.get(
            "full_name"
        )
        or profile.get(
            "display_name"
        )
        or profile.get(
            "name"
        )
        or metadata.get(
            "full_name"
        )
        or metadata.get(
            "name"
        )
        or email
        or "Usuario"
    )

    role = (
        getattr(
            current_user,
            "role",
            None,
        )
        or profile.get(
            "role"
        )
        or "user"
    )

    expiration = (
        getattr(
            current_user,
            "subscription_expires_at",
            None,
        )
        or getattr(
            current_user,
            "expires_at",
            None,
        )
        or subscription_expiration
    )

    resolved_plan = (
        getattr(
            current_user,
            "plan_name",
            None,
        )
        or getattr(
            current_user,
            "plan_code",
            None,
        )
        or plan_name
        or "Sin plan"
    )

    return {
        "id": user_id,
        "user_id": user_id,
        "uid": user_id,
        "email": str(email),
        "username": str(email),
        "usuario": str(email),
        "name": str(display_name),
        "full_name": str(
            display_name
        ),
        "role": str(role),
        "plan": str(
            resolved_plan
        ),
        "expires": expiration,
        "source": "uywa_platform",
    }


def _default_pet_profile() -> dict[str, Any]:
    """
    Devuelve el perfil inicial de una mascota.
    """

    return {
        "mascota": {
            "nombre": "",
            "especie": "perro",
            "edad": 1.0,
            "peso": 12.0,
            "etapa": "adulto",
            "bcs": 5,
        }
    }


def load_pet_profile_once(
    user: dict[str, Any],
) -> dict[str, Any]:
    """
    Carga el perfil una sola vez por sesión.

    Evita sobrescrituras en cada rerun y conserva
    la página interna seleccionada.
    """

    if PET_PROFILE_KEY not in st.session_state:
        loaded_profile = (
            load_profile(user)
            or {}
        )

        if not isinstance(
            loaded_profile,
            dict,
        ):
            loaded_profile = {}

        loaded_profile.setdefault(
            "mascota",
            _default_pet_profile()[
                "mascota"
            ],
        )

        st.session_state[
            PET_PROFILE_KEY
        ] = loaded_profile

    profile = st.session_state.get(
        PET_PROFILE_KEY,
        {},
    )

    if not isinstance(
        profile,
        dict,
    ):
        profile = (
            _default_pet_profile()
        )

        st.session_state[
            PET_PROFILE_KEY
        ] = profile

    return profile


def update_and_save_profile(
    user: dict[str, Any],
    updated_profile: dict[str, Any],
) -> None:
    """
    Guarda el perfil y actualiza el estado local.
    """

    saved = save_profile(
        user,
        updated_profile,
    )

    if saved is False:
        st.error(
            "No se pudo guardar el perfil."
        )
        return

    st.session_state[
        PET_PROFILE_KEY
    ] = updated_profile

    st.success(
        "Perfil actualizado exitosamente."
    )


def reset_species_dependent_state() -> None:
    """
    Limpia estados dependientes de la especie seleccionada.
    """

    keys_exact = [
        "analysis_food_selector_card",
        "analysis_food_card_page",
        "food_search_input",
        "alimento_seleccionado",
        "food_name",
        "analysis_food_name_edited",
        "analysis_food_data_edited",
        "analysis_food_proximal_sum",
        "me_alimento_actual",
        "energia_aportada_actual",
        "fuente_me_actual",
        "me_formula_uywa_actual",
        "me_manufacturer_actual",
        "me_inferred_manufacturer_actual",
        "cobertura_energia_actual",
        "gramos_recomendados_actual",
        "cobertura_proteina_actual",
        "cobertura_grasa_actual",
        "compare_sources_selector",
        "comparador_alimentos_avanzado_v2",
        "comparador_fuente_me",
        "comparador_gramos_avanzado_v2",
        "recomendaciones_signature",
        "recomendaciones_veterinario_texto",
        "condicion_mascota",
        "food_search_input_perro",
        "food_search_input_gato",
        "analysis_food_card_perro_page",
        "analysis_food_card_gato_page",
        "analysis_food_card_perro_selected",
        "analysis_food_card_gato_selected",
    ]

    prefixes = [
        "comp_data_",
        "comp_editor_",
        "gramos_alimento_",
        "fuente_me_",
        "analysis_food_card_",
    ]

    for key in keys_exact:
        st.session_state.pop(
            key,
            None,
        )

    session_keys = list(
        st.session_state.keys()
    )

    for key in session_keys:
        if any(
            key.startswith(prefix)
            for prefix in prefixes
        ):
            st.session_state.pop(
                key,
                None,
            )


def clear_pet_module_state() -> None:
    """
    Elimina el estado principal del módulo Pet Nutrition.

    Puede utilizarse al cerrar sesión o cuando se necesite
    reiniciar completamente el módulo.
    """

    st.session_state.pop(
        PET_PROFILE_KEY,
        None,
    )

    st.session_state.pop(
        PET_ACTIVE_PAGE_KEY,
        None,
    )

    reset_species_dependent_state()


def _inject_pet_navigation_styles() -> None:
    """
    Inserta estilos limitados a la navegación interna.
    """

    st.markdown(
        """
        <style>
            div[data-testid="stHorizontalBlock"]
            div[data-testid="column"]
            div[data-testid="stButton"]
            button[kind="primary"],
            div[data-testid="stHorizontalBlock"]
            div[data-testid="column"]
            div[data-testid="stButton"]
            button[kind="secondary"] {
                min-height: 58px !important;
                border-radius: 16px !important;
                font-size: 1rem !important;
                font-weight: 800 !important;
                border:
                    1px solid #DDE7F3 !important;
                box-shadow:
                    0 8px 20px
                    rgba(
                        15,
                        23,
                        42,
                        0.06
                    ) !important;
            }

            div[data-testid="stHorizontalBlock"]
            div[data-testid="column"]
            div[data-testid="stButton"]
            button:hover {
                border-color:
                    #2563EB !important;
                transform:
                    translateY(-1px);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _initialize_pet_navigation() -> None:
    """
    Inicializa y valida la página activa.
    """

    valid_pages = [
        page_key
        for page_key, _, _ in PET_NAV_ITEMS
    ]

    current_page = st.session_state.get(
        PET_ACTIVE_PAGE_KEY
    )

    if current_page not in valid_pages:
        st.session_state[
            PET_ACTIVE_PAGE_KEY
        ] = PET_NAV_ITEMS[0][0]


def _render_pet_navigation() -> str:
    """
    Renderiza los botones de navegación y devuelve
    la página activa.
    """

    _initialize_pet_navigation()

    nav_columns = st.columns(
        len(PET_NAV_ITEMS)
    )

    for column, item in zip(
        nav_columns,
        PET_NAV_ITEMS,
    ):
        page_key, icon, label = item

        with column:
            is_active = (
                st.session_state[
                    PET_ACTIVE_PAGE_KEY
                ]
                == page_key
            )

            clicked = st.button(
                f"{icon} {label}",
                key=(
                    f"{PET_STATE_PREFIX}"
                    f"nav_btn_{page_key}"
                ),
                use_container_width=True,
                type=(
                    "primary"
                    if is_active
                    else "secondary"
                ),
            )

            if clicked:
                st.session_state[
                    PET_ACTIVE_PAGE_KEY
                ] = page_key

                st.rerun()

    return str(
        st.session_state[
            PET_ACTIVE_PAGE_KEY
        ]
    )


def _render_active_pet_page(
    active_page: str,
    profile: dict[str, Any],
    user: dict[str, Any],
) -> None:
    """
    Renderiza la página interna seleccionada.
    """

    if active_page == "Perfil de Mascota":
        show_profile_page(
            profile=profile,
            update_and_save_profile=(
                lambda updated_profile:
                update_and_save_profile(
                    user,
                    updated_profile,
                )
            ),
            reset_species_dependent_state=(
                reset_species_dependent_state
            ),
        )

    elif active_page == "Análisis":
        show_analysis_page()

    elif active_page == "Comparador":
        show_compare_page()

    elif active_page == "Resumen y Exportar":
        show_summary_page()

    elif active_page == (
        "Seguimiento del Paciente"
    ):
        show_followup_page()

    else:
        st.error(
            "La página solicitada no está disponible."
        )


def render_pet_nutrition(
    user: dict[str, Any],
    *,
    apply_pet_theme: bool = True,
    show_app_title: bool = True,
) -> None:
    """
    Renderiza la aplicación completa de Pet Nutrition.

    No contiene:

    - autenticación;
    - sidebar;
    - cierre de sesión;
    - st.set_page_config().

    Estas responsabilidades pertenecen al contenedor.
    """

    if not isinstance(
        user,
        dict,
    ) or not user:
        st.error(
            "No se recibió un usuario válido para "
            "Uywa Pet Nutrition."
        )
        return

    if apply_pet_theme:
        initialize_pet_ui()

    profile = load_pet_profile_once(
        user
    )

    if show_app_title:
        render_app_title()

    _inject_pet_navigation_styles()

    active_page = (
        _render_pet_navigation()
    )

    st.markdown("---")

    _render_active_pet_page(
        active_page=active_page,
        profile=profile,
        user=user,
    )
