# ======================== UYWA PET NUTRITION STUDIO ========================
from __future__ import annotations

import streamlit as st

from auth import authenticate_user
from profile import load_profile, save_profile
from utils.ui_components import inject_global_css, render_app_title
from utils.ui_theme import inject_uywa_theme

from uywa_pages.profile_page import show_profile_page
from uywa_pages.analysis_page import show_analysis_page
from uywa_pages.compare_page import show_compare_page
from uywa_pages.summary_page import show_summary_page
from uywa_pages.followup_page import show_followup_page


st.set_page_config(
    page_title="UYWA Nutritional Diagnostics",
    layout="wide",
)

inject_global_css()
inject_uywa_theme()


def login() -> None:
    st.title("Iniciar sesión")
    st.markdown("Ingresa tus credenciales para acceder al sistema de diagnóstico nutricional.")

    username = st.text_input("Usuario", key="login_usuario")
    password = st.text_input("Contraseña", type="password", key="login_password")

    if st.button("Entrar", use_container_width=True):
        authenticated, user_data, message = authenticate_user(username, password)

        if authenticated:
            username_clean = str(username or "").strip().lower()
            st.session_state["logged_in"] = True
            st.session_state["usuario"] = username_clean
            st.session_state["user"] = user_data
            st.success(f"Bienvenido, {user_data.get('name', username_clean)}.")
            st.rerun()
        else:
            st.error(message or "Usuario o contraseña incorrectos.")

    if not st.session_state.get("logged_in", False):
        st.warning("Por favor, inicia sesión para acceder al contenido.")


def render_sidebar(user: dict | None) -> None:
    with st.sidebar:
        st.image("assets/logo.png", use_container_width=True)

        st.markdown(
            """
            <div style="text-align:center;margin-bottom:20px;">
                <h1 style="font-family:Montserrat,sans-serif;margin:0;color:#fff;font-size:1.45rem;">
                    UYWA Nutrition
                </h1>
                <p style="font-size:0.9rem;margin:0;color:#fff;">
                    Nutrición de Precisión Basada en Evidencia
                </p>
                <br>
                <hr style="border:1px solid #fff;">
                <p style="font-size:0.85rem;color:#fff;margin:0;">📧 uywasas@gmail.com</p>
                <p style="font-size:0.75rem;color:#fff;margin:0;">Derechos reservados © 2026</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if user:
            plan = user.get("plan", "Sin plan")
            expires = user.get("expires", None)

            st.success(f"Acceso {plan} activado")

            if expires:
                st.caption(f"Válido hasta: {expires}")

            if st.button("Cerrar sesión", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        else:
            st.warning("Por favor, inicia sesión.")


def update_and_save_profile(user: dict, updated_profile: dict) -> None:
    saved = save_profile(user, updated_profile)

    if saved is False:
        st.error("No se pudo guardar el perfil.")
        return

    st.session_state["profile"] = updated_profile
    st.success("Perfil actualizado exitosamente.")


def reset_species_dependent_state() -> None:
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
        st.session_state.pop(key, None)

    for key in list(st.session_state.keys()):
        if any(key.startswith(prefix) for prefix in prefixes):
            del st.session_state[key]


if not st.session_state.get("logged_in", False):
    render_sidebar(st.session_state.get("user"))
    login()
    st.stop()


user = st.session_state.get("user")

if not user:
    st.error("El usuario no está autenticado.")
    st.stop()


render_sidebar(user)

profile = load_profile(user) or {}
profile.setdefault(
    "mascota",
    {
        "nombre": "",
        "especie": "perro",
        "edad": 1.0,
        "peso": 12.0,
        "etapa": "adulto",
        "bcs": 5,
    },
)
st.session_state["profile"] = profile


render_app_title()

PAGINAS = [
    "Perfil de Mascota",
    "Análisis",
    "Comparador",
    "Resumen y Exportar",
    "Seguimiento del Paciente",
]

if "pagina_activa_principal" not in st.session_state:
    st.session_state["pagina_activa_principal"] = PAGINAS[0]

if st.session_state["pagina_activa_principal"] not in PAGINAS:
    st.session_state["pagina_activa_principal"] = PAGINAS[0]

pagina_activa = st.radio(
    "Navegación principal",
    PAGINAS,
    index=PAGINAS.index(st.session_state["pagina_activa_principal"]),
    horizontal=True,
    label_visibility="collapsed",
    key="pagina_activa_principal",
)

st.markdown(
    """
    <style>
    div[data-testid="stHorizontalBlock"] div[data-testid="column"] button {
        min-height: 58px !important;
        border-radius: 16px !important;
        font-size: 1rem !important;
        font-weight: 800 !important;
        border: 1px solid #DDE7F3 !important;
        background: rgba(255,255,255,0.82) !important;
        color: #0F172A !important;
        box-shadow: 0 8px 20px rgba(15,23,42,0.06) !important;
    }
    div[data-testid="stHorizontalBlock"] div[data-testid="column"] button:hover {
        border-color: #2563EB !important;
        transform: translateY(-1px);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

nav_cols = st.columns(len(PAGINAS))

for col, (page_key, icon, label) in zip(nav_cols, NAV_ITEMS):
    is_active = st.session_state["pagina_activa_principal"] == page_key

    with col:
        if st.button(
            f"{icon} {label}",
            key=f"nav_{page_key}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state["pagina_activa_principal"] = page_key
            st.rerun()

pagina_activa = st.session_state["pagina_activa_principal"]

st.markdown("---")
if pagina_activa == "Perfil de Mascota":
    show_profile_page(
        profile=profile,
        update_and_save_profile=lambda updated_profile: update_and_save_profile(user, updated_profile),
        reset_species_dependent_state=reset_species_dependent_state,
    )

elif pagina_activa == "Análisis":
    show_analysis_page()

elif pagina_activa == "Comparador":
    show_compare_page()

elif pagina_activa == "Resumen y Exportar":
    show_summary_page()

elif pagina_activa == "Seguimiento del Paciente":
    show_followup_page()
