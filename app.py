# ======================== BLOQUE 1: IMPORTS, CONSTANTES Y UTILIDADES ========================
import base64
import datetime

import pandas as pd
import streamlit as st
from utils.ui_components import (
    inject_global_css,
    render_section_header,
    render_kpi_card,
    render_risk_card,
)

from utils.nutrient_reference import (
    NUTRIENTES_REFERENCIA_PERRO,
    NUTRIENTES_REFERENCIA_GATO,
)
from utils.fmt_tools import fmt2

from profile import load_profile, save_profile
from energy_requirements import calcular_rer
from auth import authenticate_user
from food_analysis import (
    show_food_analysis,
    get_foods_by_species,
    plot_energy_breakdown_stacked_with_edits,
    build_energy_breakdown_table_with_edits,
    show_energy_breakdown_cards,
)
from food_database import (
    FOODS,
    calculate_energy as calc_energy_food,
    calculate_ena as calc_ena_food,
    calculate_energy_breakdown,
)
from patient_followup import show_patient_followup
from export_tools import (
    generar_diagnostico_resumen,
    generar_recomendaciones,
    generar_decision_resumen,
    exportar_a_html,
    exportar_ficha_maestra_excel,
)
from clinical_state import (
    safe_float,
    get_current_clinical_state,
    clinical_state_is_ready,
)


# ======================== CONSTANTES GENERALES ========================

ENERGY_COVERAGE_THRESHOLD = 110
SENIOR_FACTOR = 0.85

RADAR_CHART_COLORS = [
    "#2176FF",
    "#FFB703",
    "#52B788",
    "#F4845F",
    "#8E9AAF",
    "#E74C3C",
]

RIESGO_COLORES = {
    "Bajo": "#52B788",
    "Moderado": "#FFB703",
    "Alto": "#F4845F",
}

RIESGO_ICONS = {
    "Bajo": "🟢",
    "Moderado": "🟠",
    "Alto": "🔴",
}


# ======================== FUNCIONES DE DIAGNÓSTICO ========================

def get_estado_corporal(bcs):
    """Devuelve el estado corporal textual según BCS 1–9."""
    if 1 <= bcs <= 3:
        return "Bajo peso"
    if bcs == 4:
        return "Ligeramente bajo"
    if bcs == 5:
        return "Condición ideal"
    if bcs == 6:
        return "Ligeramente sobrepeso"
    if bcs == 7:
        return "Sobrepeso"
    if 8 <= bcs <= 9:
        return "Obesidad"
    return "Desconocido"


def calcular_riesgo_nutricional(bcs, edad, condicion, etapa, aplicar_senior):
    """Calcula el nivel de riesgo nutricional del paciente."""
    if bcs == 5:
        riesgo = "Bajo"
    elif bcs in [4, 6]:
        riesgo = "Moderado"
    else:
        riesgo = "Alto"

    if aplicar_senior and bcs >= 6:
        riesgo = "Alto"

    if condicion == "Castrado" and bcs >= 6:
        riesgo = "Alto"

    if etapa == "cachorro" and condicion == "Destete a 4 meses":
        riesgo = "Moderado"

    if condicion in ["Gestación (Segunda mitad)", "Gestación (Final)", "Lactancia"]:
        riesgo = "Alto"

    return riesgo


def calcular_prioridad_nutricional(bcs, etapa, condicion, edad):
    """Devuelve prioridad nutricional y recomendación inicial."""
    if etapa == "cachorro":
        return "Sostener crecimiento", "Maximizar aporte nutricional balanceado"

    if condicion in ["Gestación (Segunda mitad)", "Gestación (Final)", "Lactancia"]:
        return "Cubrir alta demanda energética", "Aumentar frecuencia de alimentación y calidad"

    if bcs < 5:
        return "Recuperar condición corporal", "Aumentar gradualmente el aporte energético"

    if bcs > 5:
        return "Controlar peso y energía", "Reducir calorías y aumentar monitoreo"

    if edad >= 7:
        return "Mantener masa magra y prevenir sobrepeso", "Monitoreo frecuente cada 4–8 semanas"

    return "Mantener condición corporal", "Monitoreo regular cada 2–4 semanas"


def generar_interpretacion_diagnostico(
    nombre,
    bcs,
    estado,
    mer_final,
    prioridad,
    condicion,
    edad,
    aplicar_senior,
):
    """Genera diagnóstico textual automático."""
    texto = f"{nombre} presenta condición corporal {estado.lower()} (BCS {bcs}/9). "
    texto += f"Su requerimiento energético final estimado es {mer_final:.0f} kcal/día. "

    if bcs < 5:
        texto += (
            "La prioridad nutricional es recuperar condición corporal. "
            "Se recomienda aumentar gradualmente el aporte energético y monitorear peso cada 2–3 semanas."
        )
    elif bcs > 5:
        texto += (
            "La prioridad nutricional es controlar peso y energía. "
            "Se recomienda reducir calorías gradualmente y monitorear peso cada 1–2 semanas."
        )
    else:
        if edad >= 7 and aplicar_senior:
            texto += (
                "Como animal senior, la prioridad es mantener masa magra y prevenir sobrepeso. "
                "Se recomienda monitoreo frecuente cada 4–8 semanas."
            )
        elif condicion in ["Gestación (Segunda mitad)", "Gestación (Final)", "Lactancia"]:
            texto += (
                "La prioridad nutricional es cubrir la alta demanda energética. "
                "Se recomienda aumentar frecuencia de alimentación y monitoreo semanal."
            )
        else:
            texto += (
                "La prioridad es mantener la condición corporal actual. "
                "Se recomienda monitoreo regular cada 2–4 semanas."
            )

    return texto


# ======================== FACTORES ENERGÉTICOS ========================

FACTORES_CONDICION = {
    "perro": {
        "adulto": {
            "Castrado": 1.6,
            "Entero": 1.8,
            "Tendencia obesidad o inactivo": [1.2, 1.4],
            "Obeso": 1.0,
            "Bajo peso": [1.4, 1.6],
            "Gestación (Primera mitad)": 1.2,
            "Gestación (Segunda mitad)": 1.6,
            "Lactancia": [3.0, 6.0],
        },
        "cachorro": {
            "Destete a 4 meses": 3.0,
            "5 meses hasta adulto": 2.0,
        },
    },
    "gato": {
        "adulto": {
            "Castrado": 1.2,
            "Entero": 1.4,
            "Indoor": 1.0,
            "Tendencia obesidad": 1.0,
            "Obeso": 0.8,
            "Bajo peso": [1.2, 1.4],
            "Gestación (Inicio)": 1.6,
            "Gestación (Final)": 2.0,
            "Lactancia": [2.0, 6.0],
        },
        "cachorro": {
            "Destete a 4 meses": 3.0,
            "5 meses hasta adulto": 2.0,
        },
    },
}

CONDICIONES_GESTACION = {
    "Gestación (Primera mitad)",
    "Gestación (Segunda mitad)",
    "Gestación (Inicio)",
    "Gestación (Final)",
}

CONDICIONES_GESTACION_INICIAL = {
    "Gestación (Primera mitad)",
    "Gestación (Inicio)",
}

CONDICIONES_GESTACION_FINAL = {
    "Gestación (Segunda mitad)",
    "Gestación (Final)",
}


# ======================== BLOQUE 2: CONFIGURACIÓN Y ESTILO GLOBAL ========================

st.set_page_config(
    page_title="UYWA Nutritional Diagnostics",
    layout="wide",
)

inject_global_css()

# ======================== BLOQUE 3: SIDEBAR ========================

user = st.session_state.get("user", None)

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


# ======================== BLOQUE 4: LOGIN Y PERFIL ========================

def login():
    """
    Maneja autenticación de usuario.
    """
    st.title("Iniciar sesión")

    st.markdown(
        "Ingresa tus credenciales para acceder al sistema de diagnóstico nutricional."
    )

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


if not st.session_state.get("logged_in", False):
    login()
    st.stop()


user = st.session_state.get("user", None)

if not user:
    st.error("El usuario no está autenticado.")
    st.stop()


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


def update_and_save_profile(updated_profile):
    """
    Actualiza y guarda el perfil del usuario.
    """
    saved = save_profile(user, updated_profile)

    if saved is False:
        st.error("No se pudo guardar el perfil.")
        return

    st.session_state["profile"] = updated_profile
    st.success("Perfil actualizado exitosamente.")


def clean_state(keys_prefix, valid_names):
    """
    Limpia claves antiguas de session_state asociadas a listas dinámicas.
    """
    for key in list(st.session_state.keys()):
        for prefix in keys_prefix:
            if key.startswith(prefix):
                found = False

                for n in valid_names:
                    if key.endswith(f"{n}_incl_input") or key.endswith(f"{n}_input"):
                        found = True
                        break

                if not found:
                    del st.session_state[key]

# ======================== BLOQUE 5: TÍTULO Y TABS PRINCIPALES ========================

st.title("Gestión y Análisis de Dietas")

tabs = st.tabs([
    "Perfil de Mascota",
    "Análisis",
    "Comparador",
    "Resumen y Exportar",
    "Seguimiento del Paciente",
])

# ======================== BLOQUE 5.1: TAB PERFIL EDITABLE + CÁLCULOS COMPLETO ========================
with tabs[0]:
    st.header("🐾 Perfil Clínico-Nutricional")
    st.markdown(
        """
        <div style="background:#ffffff;border-left:5px solid #2176FF;
                    border-radius:10px;padding:14px 18px;margin-bottom:18px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);">
            <b>Objetivo:</b> registrar los datos del paciente, estimar sus requerimientos energéticos
            y generar una interpretación nutricional inicial.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Formulario de edición en expander ---
    mascota = profile.get("mascota", {})

    with st.expander("✏️ Editar perfil clínico del paciente", expanded=True):

        st.markdown("### 1. Datos básicos del paciente")

        ef_col1, ef_col2 = st.columns(2)

        with ef_col1:
            nombre_mascota = st.text_input(
                "Nombre de la mascota",
                value=mascota.get("nombre", "Mascota"),
                key="nombre_mascota",
            )

            especie = st.selectbox(
                "Especie",
                ["perro", "gato"],
                index=["perro", "gato"].index(
                    mascota.get("especie", "perro").lower()
                ),
                key="especie_mascota",
            )

            edad = st.number_input(
                "Edad en años",
                min_value=0.1,
                max_value=20.0,
                value=max(0.1, safe_float(mascota.get("edad", 1.0), 1.0)),
                step=0.1,
                key="edad_mascota",
            )

        with ef_col2:
            peso = st.number_input(
                "Peso en kg",
                min_value=0.1,
                max_value=200.0,
                value=max(0.1, safe_float(mascota.get("peso", 12.0), 12.0)),
                step=0.1,
                key="peso_mascota",
            )

            etapa = st.selectbox(
                "Etapa de vida",
                ["adulto", "cachorro"],
                index=["adulto", "cachorro"].index(
                    mascota.get("etapa", "adulto").lower()
                ),
                key="etapa_mascota",
            )

        st.markdown("---")
        st.markdown("### 2. Condición fisiológica")

        _especie_form_cond = st.session_state.get(
            "especie_mascota",
            mascota.get("especie", "perro"),
        )

        _etapa_actual_form = st.session_state.get(
            "etapa_mascota",
            mascota.get("etapa", "adulto"),
        )

        if _etapa_actual_form == "adulto":
            if _especie_form_cond == "perro":
                opciones_condicion = [
                    "Castrado",
                    "Entero",
                    "Gestación (Primera mitad)",
                    "Gestación (Segunda mitad)",
                    "Lactancia",
                ]
            else:
                opciones_condicion = [
                    "Castrado",
                    "Entero",
                    "Indoor",
                    "Tendencia obesidad",
                    "Obeso",
                    "Bajo peso",
                    "Gestación (Inicio)",
                    "Gestación (Final)",
                    "Lactancia",
                ]
        else:
            opciones_condicion = [
                "Destete a 4 meses",
                "5 meses hasta adulto",
            ]

        condicion_predeterminada = mascota.get("condicion", "Castrado")

        if condicion_predeterminada not in opciones_condicion:
            condicion_predeterminada = opciones_condicion[0]

        condicion = st.selectbox(
            "Condición fisiológica/productiva",
            opciones_condicion,
            index=opciones_condicion.index(condicion_predeterminada),
            key="condicion_mascota",
        )

        st.markdown("---")
        st.markdown("### 3. Estado corporal")

        bcs_disabled = (
            st.session_state.get(
                "etapa_mascota",
                mascota.get("etapa", "adulto"),
            ) == "cachorro"
            and condicion == "Destete a 4 meses"
        )

        bcs_val = max(
            1,
            min(
                9,
                int(safe_float(mascota.get("bcs", 5), 5)),
            ),
        )

        bcs = st.slider(
            "Condición Corporal (BCS 1–9)",
            min_value=1,
            max_value=9,
            value=bcs_val,
            key="bcs_mascota",
            disabled=bcs_disabled,
        )

        if bcs_disabled:
            st.info(
                "En cachorros destete a 4 meses, el BCS puede no ser el criterio principal "
                "para ajustar el requerimiento energético."
            )

        _etapa_form = st.session_state.get(
            "etapa_mascota",
            mascota.get("etapa", "adulto"),
        )

        _especie_form = st.session_state.get(
            "especie_mascota",
            mascota.get("especie", "perro"),
        )

        _edad_form = safe_float(
            st.session_state.get(
                "edad_mascota",
                mascota.get("edad", 1.0),
            ),
            1.0,
        )

        if _etapa_form == "adulto" and _especie_form in ("perro", "gato"):
            _stored_senior = mascota.get("aplicar_ajuste_senior")
            _senior_default = (
                bool(_stored_senior)
                if _stored_senior is not None
                else (_edad_form >= 7)
            )

            aplicar_ajuste_senior_form = st.checkbox(
                "👴 Aplicar ajuste energético Senior (-15%)",
                value=_senior_default,
                key="aplicar_ajuste_senior_mascota",
                help=(
                    "Reduce el MER en un 15% para mascotas adultas senior. "
                    "Puede aplicarse adicionalmente al ajuste por condición corporal bajo criterio veterinario."
                ),
            )

            if _edad_form >= 7:
                st.info("Recomendado para mascotas adultas mayores de 7 años.")
        else:
            aplicar_ajuste_senior_form = False

            if "aplicar_ajuste_senior_mascota" in st.session_state:
                del st.session_state["aplicar_ajuste_senior_mascota"]

        st.markdown("---")
        st.markdown("### 4. Foto del paciente")

        foto_upload = st.file_uploader(
            "Foto de la mascota (opcional)",
            type=["png", "jpg", "jpeg"],
            key="foto_mascota_upload",
        )

        if foto_upload is not None:
            st.session_state["mascota_foto_bytes"] = foto_upload.getvalue()

        if st.session_state.get("mascota_foto_bytes"):
            col_prev, col_del = st.columns([1, 3])

            with col_prev:
                st.image(
                    st.session_state["mascota_foto_bytes"],
                    width=120,
                    caption="Vista previa",
                )

            with col_del:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️ Eliminar foto", key="del_foto_perfil"):
                    del st.session_state["mascota_foto_bytes"]
                    st.rerun()

        st.markdown("---")

        if st.button(
            "💾 Guardar perfil de mascota",
            key="guardar_perfil_btn",
            use_container_width=True,
        ):
            mascota_actualizada = {
                "nombre": st.session_state["nombre_mascota"],
                "especie": st.session_state["especie_mascota"].lower(),
                "edad": st.session_state["edad_mascota"],
                "peso": st.session_state["peso_mascota"],
                "etapa": st.session_state["etapa_mascota"].lower(),
                "condicion": condicion,
                "bcs": st.session_state.get("bcs_mascota", 5),
                "aplicar_ajuste_senior": st.session_state.get(
                    "aplicar_ajuste_senior_mascota",
                    False,
                ),
            }

            profile["mascota"] = mascota_actualizada
            update_and_save_profile(profile)
            st.success("✅ Perfil actualizado correctamente.")
    mascota = profile.get("mascota", {})

    # Leer valores actuales (del estado de sesión si fueron modificados, o del perfil guardado)
    especie = st.session_state.get("especie_mascota", mascota.get("especie", "perro"))
    etapa = st.session_state.get("etapa_mascota", mascota.get("etapa", "adulto"))
    condicion = st.session_state.get("condicion_mascota", mascota.get("condicion", "Castrado"))
    bcs = max(1, min(9, int(safe_float(st.session_state.get("bcs_mascota", mascota.get("bcs", 5)), 5))))
    peso = max(0.1, safe_float(st.session_state.get("peso_mascota", mascota.get("peso", 12.0)), 12.0))
    edad = safe_float(st.session_state.get("edad_mascota", mascota.get("edad", 1.0)), 1.0)
    bcs_disabled = etapa == "cachorro" and condicion == "Destete a 4 meses"
   
    # Leer ajuste senior: desde session_state (widget) o desde perfil guardado
    if etapa == "adulto" and especie in ("perro", "gato"):
        _stored_senior = mascota.get("aplicar_ajuste_senior")
        _senior_profile_default = bool(_stored_senior) if _stored_senior is not None else (edad >= 7)
        aplicar_ajuste_senior = bool(st.session_state.get("aplicar_ajuste_senior_mascota", _senior_profile_default))
    else:
        aplicar_ajuste_senior = False

    # --- Cálculo del RER y MER (necesario antes del layout) ---
    try:
        energia_basal_actual = calcular_rer(peso)
        factores_etapa = FACTORES_CONDICION.get(especie, {}).get(etapa, {}).get(condicion, None)
        if factores_etapa is None:
            raise ValueError(f"Condición desconocida para '{especie}'.")
        factor_fisiologico = factores_etapa if isinstance(factores_etapa, (int, float)) else factores_etapa[0]
        mer_actual = energia_basal_actual * factor_fisiologico

        factores_bcs = {6: 0.9, 7: 0.8, 8: 0.7, 9: 0.6, 4: 1.1, 3: 1.2, 2: 1.3, 1: 1.4}

        # Determine if condition is gestación
        es_gestacion = condicion in CONDICIONES_GESTACION

        if es_gestacion and not bcs_disabled:
            # For gestating animals, BCS adjustment is only applied at extreme values (≤3 or ≥7).
            # BCS 4–6 is considered an acceptable range for a gestante; no adjustment is needed
            # because moderate variation in body condition is normal during pregnancy.
            bcs_gestacion_extremo = bcs <= 3 or bcs >= 7
            if bcs_gestacion_extremo:
                # BCS extreme: apply adjustment
                peso_objetivo = peso * factores_bcs.get(bcs, 1.0)
                energia_basal_objetivo = calcular_rer(peso_objetivo)
                mer_final = energia_basal_objetivo * factor_fisiologico
            else:
                # BCS 4–6: acceptable range for gestante, no BCS adjustment
                peso_objetivo = "-"
                energia_basal_objetivo = "-"
                mer_final = mer_actual
        elif not es_gestacion and bcs != 5 and not bcs_disabled:
            peso_objetivo = peso * factores_bcs.get(bcs, 1.0)
            energia_basal_objetivo = calcular_rer(peso_objetivo)
            mer_final = energia_basal_objetivo * factor_fisiologico
            bcs_gestacion_extremo = False
        else:
            peso_objetivo = "-"
            energia_basal_objetivo = "-"
            mer_final = mer_actual
            bcs_gestacion_extremo = False
        factor_condicion_val = round(mer_final / energia_basal_actual, 2) if energia_basal_actual > 1e-6 else "-"

        # --- Ajuste senior (paso final, después de todos los cálculos de BCS) ---
        senior_aplicado = False
        if (etapa == "adulto"
                and aplicar_ajuste_senior
                and not bcs_disabled):
            mer_final = mer_final * SENIOR_FACTOR
            senior_aplicado = True

        st.session_state["energia_actual"] = mer_final
        # Almacenar valores intermedios para Pestaña 3
        st.session_state["rer_actual"] = energia_basal_actual
        st.session_state["mer_base_actual"] = mer_actual
        st.session_state["factor_fisiologico_actual"] = factor_fisiologico
        st.session_state["senior_aplicado_actual"] = senior_aplicado

    except Exception as e:
        st.error(f"Error en cálculos energéticos: {str(e)}")
        st.stop()

    # ===================== LAYOUT DE 2 COLUMNAS =====================
    col_left, col_right = st.columns([3, 7])

    with col_left:
        # Icono de especie
        especie_icon = "🐕" if especie == "perro" else "🐈"
        nombre_display = st.session_state.get(
            "nombre_mascota",
            mascota.get("nombre", "Mascota")
        ) or "Mascota"

        # Foto circular o placeholder
        foto_bytes = st.session_state.get("mascota_foto_bytes")
        if foto_bytes:
            foto_b64 = base64.b64encode(foto_bytes).decode("utf-8")
            st.markdown(
                f"""
                <div class="profile-left">
                    <img src="data:image/png;base64,{foto_b64}" class="pet-photo-circle" alt="foto mascota"/>
                    <div class="pet-name">{nombre_display}</div>
                    <div style="font-size:32px; margin:4px 0;">{especie_icon}</div>
                    <span class="stage-badge {etapa}">{etapa.capitalize()}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="profile-left">
                    <div class="pet-photo-placeholder">{especie_icon}</div>
                    <div class="pet-name">{nombre_display}</div>
                    <div style="font-size:13px; color:#718096; margin:2px 0;">{especie.capitalize()}</div>
                    <span class="stage-badge {etapa}">{etapa.capitalize()}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col_right:
        # --- Datos Vitales en cards (2 por fila) ---
        edad_display = max(0.0, safe_float(st.session_state.get("edad_mascota", mascota.get("edad", 1.0)), 1.0))
        bcs_pct = int((bcs / 9) * 100)
        bcs_color = "#52b788" if 4 <= bcs <= 6 else ("#f4845f" if bcs > 6 else "#fbbf24")

        vc1, vc2 = st.columns(2)
        with vc1:
            st.markdown(
                f"""
                <div class="vital-card">
                    <span class="card-icon">🎂</span>
                    <div class="card-label">Edad</div>
                    <div class="card-value">{fmt2(edad_display)} años</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with vc2:
            st.markdown(
                f"""
                <div class="vital-card" style="border-left-color:#52b788;">
                    <span class="card-icon">⚖️</span>
                    <div class="card-label">Peso</div>
                    <div class="card-value">{fmt2(peso)} kg</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        vc3, vc4 = st.columns(2)
        with vc3:
            st.markdown(
                f"""
                <div class="vital-card" style="border-left-color:{bcs_color};">
                    <span class="card-icon">📏</span>
                    <div class="card-label">Condición Corporal (BCS)</div>
                    <div class="card-value">{bcs} / 9</div>
                    <div class="bcs-bar-container">
                        <div class="bcs-bar-fill" style="width:{bcs_pct}%; background:{bcs_color};"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with vc4:
            st.markdown(
                f"""
                <div class="vital-card" style="border-left-color:#8e9aaf;">
                    <span class="card-icon">🛠️</span>
                    <div class="card-label">Condición Fisiológica</div>
                    <div class="card-value" style="font-size:15px;">{condicion}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    # ===================== DASHBOARD EJECUTIVO DEL PERFIL =====================
    _estado_preview = get_estado_corporal(bcs)
    _riesgo_preview = calcular_riesgo_nutricional(
        bcs, edad, condicion, etapa, aplicar_ajuste_senior
    )

    dash1, dash2, dash3 = st.columns(3)

    with dash1:
        st.markdown(
            f"""
            <div style="background:#ffffff;border-radius:14px;padding:18px;
                        border-left:5px solid #2176FF;
                        box-shadow:0 2px 10px rgba(0,0,0,0.07);">
                <div style="font-size:0.85rem;color:#5a6e8c;font-weight:700;">PACIENTE</div>
                <div style="font-size:1.45rem;font-weight:800;color:#1f2d3d;">{nombre_display}</div>
                <div style="color:#5a6e8c;">{especie.capitalize()} · {etapa.capitalize()}</div>
                <div style="margin-top:6px;">{fmt2(peso)} kg · {fmt2(edad)} años</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with dash2:
        _risk_color = RIESGO_COLORES.get(_riesgo_preview, "#52B788")
        _risk_icon = RIESGO_ICONS.get(_riesgo_preview, "🟢")

        st.markdown(
            f"""
            <div style="background:#ffffff;border-radius:14px;padding:18px;
                        border-left:5px solid {_risk_color};
                        box-shadow:0 2px 10px rgba(0,0,0,0.07);">
                <div style="font-size:0.85rem;color:#5a6e8c;font-weight:700;">ESTADO CORPORAL</div>
                <div style="font-size:1.45rem;font-weight:800;color:#1f2d3d;">BCS {bcs}/9</div>
                <div style="color:#5a6e8c;">{_estado_preview}</div>
                <div style="margin-top:6px;">{_risk_icon} Riesgo {_riesgo_preview}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with dash3:
        st.markdown(
            f"""
            <div style="background:#ffffff;border-radius:14px;padding:18px;
                        border-left:5px solid #F4845F;
                        box-shadow:0 2px 10px rgba(0,0,0,0.07);">
                <div style="font-size:0.85rem;color:#5a6e8c;font-weight:700;">ENERGÍA FINAL</div>
                <div style="font-size:1.45rem;font-weight:800;color:#1f2d3d;">{fmt2(mer_final)} kcal/día</div>
                <div style="color:#5a6e8c;">MER ajustado</div>
                <div style="margin-top:6px;">Senior: {"Sí" if senior_aplicado else "No"}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
    # ===================== DIAGNÓSTICO NUTRICIONAL INICIAL (ANCHO COMPLETO) =====================
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="margin-top:18px;margin-bottom:10px;">
            <h3 style="color:#1f2d3d;margin-bottom:4px;">🩺 Estado corporal y diagnóstico inicial</h3>
            <p style="color:#5a6e8c;margin-top:0;">
                Interpretación automática basada en BCS, edad, etapa de vida y condición fisiológica.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _estado_corporal = get_estado_corporal(bcs)
    _riesgo = calcular_riesgo_nutricional(bcs, edad, condicion, etapa, aplicar_ajuste_senior)
    _prioridad, _recomendacion = calcular_prioridad_nutricional(bcs, etapa, condicion, edad)
    _interpretacion = generar_interpretacion_diagnostico(
        nombre_display, bcs, _estado_corporal, mer_final,
        _prioridad, condicion, edad, aplicar_ajuste_senior
    )

    _riesgo_class = {"Bajo": "low-risk", "Moderado": "moderate-risk", "Alto": "high-risk"}.get(_riesgo, "low-risk")
    _riesgo_icon = RIESGO_ICONS.get(_riesgo, "🟢")

    # Almacenar diagnóstico para Pestaña 3
    st.session_state["estado_corporal_tab1"] = _estado_corporal
    st.session_state["riesgo_nutricional_tab1"] = _riesgo
    st.session_state["prioridad_nutricional_tab1"] = _prioridad
    st.session_state["interpretacion_diagnostico_tab1"] = _interpretacion

    st.markdown(
        f"""
        <div class="diagnostic-card {_riesgo_class}">
            <div class="diagnostic-title">{_riesgo_icon} RIESGO {_riesgo.upper()}</div>
            <div class="diagnostic-state">Estado corporal: {_estado_corporal} (BCS {bcs}/9)</div>
            <div class="diagnostic-priority">🎯 Prioridad: {_prioridad}</div>
            <div class="diagnostic-priority" style="font-weight:400;">💡 {_recomendacion}</div>
            <div class="diagnostic-text">"{_interpretacion}"</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ===================== SECCIÓN ENERGÍA (ANCHO COMPLETO) =====================
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.markdown("**🔋 Requerimientos Energéticos**")

    ec1, ec2, ec3, ec4 = st.columns(4)
    with ec1:
        st.markdown(
            f"""
            <div class="energy-card">
                <div class="card-label">RER Actual</div>
                <div class="card-value">{fmt2(energia_basal_actual)}</div>
                <div style="font-size:11px; opacity:0.85;">kcal/día</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with ec2:
        st.markdown(
            f"""
            <div class="energy-card green">
                <div class="card-label">MER Adulto/Fisiológico</div>
                <div class="card-value">{fmt2(mer_actual)}</div>
                <div style="font-size:11px; opacity:0.85;">kcal/día</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with ec3:
        st.markdown(
            f"""
            <div class="energy-card orange">
                <div class="card-label">MER Ajustado Final</div>
                <div class="card-value">{fmt2(mer_final)}</div>
                <div style="font-size:11px; opacity:0.85;">kcal/día</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with ec4:
        _senior_card_class = "purple" if senior_aplicado else "purple-inactive"
        _senior_label = "×0.85 aplicado" if senior_aplicado else "No aplicado"
        st.markdown(
            f"""
            <div class="energy-card {_senior_card_class}">
                <div class="card-label">Factor Condición Final</div>
                <div class="card-value">{factor_condicion_val}</div>
                <div style="font-size:11px; opacity:0.85;">Senior: {_senior_label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Aviso cuando ajuste senior no se aplica por BCS ≠ 5
    if aplicar_ajuste_senior and not senior_aplicado and etapa == "adulto" and especie in ("perro", "gato"):
        st.warning("⚠️ Ajuste senior no aplicado porque el requerimiento fue priorizado por corrección de condición corporal.")

    # Mensajes informativos para gestación
    if es_gestacion and not bcs_disabled:
        if not bcs_gestacion_extremo:
            st.info("ℹ️ Ajuste BCS no aplicado: La gestante se encuentra en condición corporal aceptable. "
                    "El requerimiento se basa únicamente en el factor de gestación.")
        else:
            st.warning("⚠️ Condición corporal fuera de rango ideal. Se aplicará corrección adicional por BCS.")

    # Botón de edición
    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
    if st.button("✏️ Editar perfil", key="btn_editar_perfil_shortcut"):
        st.info("Usa el panel **✏️ Editar Perfil de la Mascota** en la parte superior para modificar los datos.")

    # ===================== TABLAS DETALLADAS (ANCHO COMPLETO) =====================
    try:
        # Descripción condicional para MER Actual según gestación
        if condicion in CONDICIONES_GESTACION_INICIAL:
            _desc_mer_actual = "Incremento energético asociado al desarrollo embrionario inicial y adaptación metabólica materna."
        elif condicion in CONDICIONES_GESTACION_FINAL:
            _desc_mer_actual = "Incremento energético elevado por crecimiento fetal acelerado y preparación para la lactancia."
        else:
            _desc_mer_actual = "Energía diaria necesaria según la condición productiva y fisiológica."

        # Tabla de energías calculadas
        _senior_valor = "Aplicado: ×0.85" if senior_aplicado else "No aplicado"
        energia_data = [
            {"Tipo": "RER Actual", "Valor": f"{fmt2(energia_basal_actual)} kcal/día", "Descripción": "Energía necesaria en reposo para mantener funciones básicas como respirar y digerir."},
            {"Tipo": "MER Actual (RER × Factor Fisiológico)", "Valor": f"{fmt2(mer_actual)} kcal/día", "Descripción": _desc_mer_actual},
            {"Tipo": "Peso Objetivo", "Valor": f"{fmt2(peso_objetivo)} kg" if peso_objetivo != "-" else "-", "Descripción": "Peso estimado para ajustar según la condición corporal (BCS)."},
            {"Tipo": "RER Objetivo", "Valor": f"{fmt2(energia_basal_objetivo)} kcal/día" if energia_basal_objetivo != "-" else "-", "Descripción": "Energía en reposo recalculada con el peso objetivo."},
            {"Tipo": "Ajuste senior", "Valor": _senior_valor, "Descripción": "Corrección energética opcional (-15%, ×0.85) para animales adultos senior (7+ años), usada solo cuando la condición corporal es ideal."},
            {"Tipo": "MER Ajustada Final", "Valor": f"{fmt2(mer_final)} kcal/día", "Descripción": "Energía total diaria necesaria tras ajustes por BCS y condición."},
        ]

        with st.expander("📋 Ver detalle del cálculo energético", expanded=False):
            html_table = "<table class='energy-table'><thead><tr><th>Tipo de Energía</th><th>Valor</th><th>Descripción</th></tr></thead><tbody>"
            for entry in energia_data:
                html_table += f"<tr><td>{entry['Tipo']}</td><td>{entry['Valor']}</td><td>{entry['Descripción']}</td></tr>"
            html_table += "</tbody></table>"
            st.markdown(html_table, unsafe_allow_html=True)

        # Tabla de nutrientes ajustados
        nutrientes_ref = NUTRIENTES_REFERENCIA_PERRO if especie == "perro" else NUTRIENTES_REFERENCIA_GATO
        nutrientes_especie_etapa = nutrientes_ref.get(etapa, {})
        kg_dieta_necesaria = mer_final / 4000.0

        requerimientos_ajustados = []
        _req_pb_g = None
        _req_ee_g = None
        for nutriente, valores in nutrientes_especie_etapa.items():
            unidad = valores.get("unit", "")
            min_valor = valores.get("min", None)
            max_valor = valores.get("max", None)

            if unidad == "%":
                min_ajustado = (min_valor / 100.0) * kg_dieta_necesaria * 1000 if min_valor is not None else None
                max_ajustado = (max_valor / 100.0) * kg_dieta_necesaria * 1000 if max_valor is not None else None
                nueva_unidad = "g"
                if nutriente == "Proteína" and min_ajustado is not None:
                    _req_pb_g = min_ajustado
                elif nutriente == "Grasa" and min_ajustado is not None:
                    _req_ee_g = min_ajustado
            elif unidad in ["mg/kg", "UI/kg", "IU/kg", "µg/kg"]:
                unidad_base = unidad.replace("/kg", "")
                min_ajustado = min_valor * kg_dieta_necesaria if min_valor is not None else None
                max_ajustado = max_valor * kg_dieta_necesaria if max_valor is not None else None
                nueva_unidad = unidad_base
            else:
                min_ajustado = min_valor
                max_ajustado = max_valor
                nueva_unidad = unidad if unidad else "-"

            requerimientos_ajustados.append({
                "Nutriente": nutriente,
                "Min Ajustado": fmt2(min_ajustado) if min_ajustado is not None else "-",
                "Max Ajustado": fmt2(max_ajustado) if max_ajustado is not None else "-",
                "Unidad": nueva_unidad,
            })

        st.session_state["req_pb_g"] = _req_pb_g
        st.session_state["req_ee_g"] = _req_ee_g

        df_nutrientes_ajustados = pd.DataFrame(requerimientos_ajustados)
        st.session_state["tabla_requerimientos_base"] = df_nutrientes_ajustados.copy()

        with st.expander("📋 Ver requerimientos nutricionales ajustados", expanded=False):
            st.markdown("<br>", unsafe_allow_html=True)
            st.caption(
                "Los requerimientos se ajustan según especie, etapa de vida y MER final estimado."
            )
            html_nutrientes = "<table class='nutrients-table'><thead><tr><th>Nutriente</th><th>Min Ajustado</th><th>Max Ajustado</th><th>Unidad</th></tr></thead><tbody>"
            for req in requerimientos_ajustados:
                html_nutrientes += f"<tr><td>{req['Nutriente']}</td><td>{req['Min Ajustado']}</td><td>{req['Max Ajustado']}</td><td>{req['Unidad']}</td></tr>"
            html_nutrientes += "</tbody></table>"
            st.markdown(html_nutrientes, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error en cálculos y ajustes: {str(e)}")
        st.stop()

# ======================== BLOQUE 6: ANÁLISIS NUTRICIONAL ========================
with tabs[1]:
    show_food_analysis()

# ======================== BLOQUE 7: COMPARADOR ========================
with tabs[2]:
    st.header("⚖️ Comparador Nutricional de Alimentos")

    st.markdown(
        """
        Compara alimentos por composición proximal, energía metabolizable,
        origen de la energía y principales fuentes nutricionales.
        """
    )

    state_comp = get_current_clinical_state()
    pet_comp = state_comp["pet"]
    energy_comp = state_comp["energy"]

    especie_comp = pet_comp.get("especie", "perro")
    mer_comp = energy_comp.get("mer_final", 0)

    alimentos_disponibles_comp = get_foods_by_species(especie_comp)

    st.caption(f"Especie activa: {especie_comp.capitalize()}")

    alimentos_comparar = st.multiselect(
        "Selecciona alimentos para comparar",
        alimentos_disponibles_comp,
        default=alimentos_disponibles_comp[:3],
        max_selections=6,
        key="comparador_alimentos_avanzado",
    )

    gramos_comp = st.number_input(
        "Gramos diarios para estimar aporte y cobertura",
        min_value=1.0,
        max_value=5000.0,
        value=100.0,
        step=10.0,
        key="comparador_gramos_avanzado",
    )

    if not alimentos_comparar:
        st.info("Selecciona al menos un alimento para iniciar la comparación.")
    else:
        st.subheader("📊 Origen de la Energía Metabolizable")

        st.plotly_chart(
            plot_energy_breakdown_stacked_with_edits(
                alimentos_comparar,
                edited_values_map=None,
            ),
            use_container_width=True,
        )

        st.subheader("🃏 Fuentes nutricionales por alimento")

        st.markdown(
            """
            Estas tarjetas muestran de qué proporción de nutrientes proviene la energía
            y, cuando está disponible en la base, las materias primas asociadas a proteína,
            grasa y fibra/carbohidratos.
            """
        )

        show_energy_breakdown_cards(alimentos_comparar)

        st.subheader("📋 Tabla comparativa energética")

        breakdown_df = build_energy_breakdown_table_with_edits(
            alimentos_comparar,
            edited_values_map=None,
        )

        filas_cobertura = []

        for alimento in alimentos_comparar:
            datos = FOODS.get(alimento, {})
            species_food = datos.get("species", especie_comp)
        
            energia = calc_energy_food(
                datos,
                species=species_food,
            )
        
            ena = calc_ena_food(datos)

            me = energia.get("ME", 0)
            aporte = (me / 100.0) * gramos_comp
            cobertura = (aporte / mer_comp * 100.0) if mer_comp and mer_comp > 0 else None

            filas_cobertura.append({
                "Alimento": alimento,
                "PB (%)": round(datos.get("PB", 0), 2),
                "EE (%)": round(datos.get("EE", 0), 2),
                "FC (%)": round(datos.get("FC", 0), 2),
                "ENA (%)": round(ena, 2),
                "ME (kcal/100g)": round(me, 2),
                "Aporte kcal/día": round(aporte, 1),
                "Cobertura energética (%)": round(cobertura, 1) if cobertura is not None else "Sin MER",
                "Fuente PB": datos.get("source_pb", ""),
                "Fuente EE": datos.get("source_ee", ""),
                "Fuente FC": datos.get("source_fc", ""),
            })

        df_cobertura = pd.DataFrame(filas_cobertura)

        st.dataframe(
            df_cobertura,
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("🏆 Ranking rápido")

        df_rank = df_cobertura.copy()
        df_rank["PB (%)"] = pd.to_numeric(df_rank["PB (%)"], errors="coerce")
        df_rank["EE (%)"] = pd.to_numeric(df_rank["EE (%)"], errors="coerce")
        df_rank["ENA (%)"] = pd.to_numeric(df_rank["ENA (%)"], errors="coerce")
        df_rank["ME (kcal/100g)"] = pd.to_numeric(df_rank["ME (kcal/100g)"], errors="coerce")

        mejor_me = df_rank.sort_values("ME (kcal/100g)", ascending=False).iloc[0]
        mejor_pb = df_rank.sort_values("PB (%)", ascending=False).iloc[0]
        menor_ena = df_rank.sort_values("ENA (%)", ascending=True).iloc[0]

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Mayor energía",
                mejor_me["Alimento"],
                f"{mejor_me['ME (kcal/100g)']} kcal/100g",
            )

        with c2:
            st.metric(
                "Mayor proteína",
                mejor_pb["Alimento"],
                f"{mejor_pb['PB (%)']}% PB",
            )

        with c3:
            st.metric(
                "Menor ENA",
                menor_ena["Alimento"],
                f"{menor_ena['ENA (%)']}% ENA",
            )

        if mer_comp and mer_comp > 0:
            st.success(f"Comparación ajustada al MER actual: {mer_comp:.1f} kcal/día.")
        else:
            st.warning(
                "No hay MER calculado. Completa el Perfil para estimar cobertura energética."
            )
            
# ======================== BLOQUE 9: RESUMEN Y EXPORTAR ========================
with tabs[3]:
    st.header("📋 Resumen y Exportación")

    ready, ready_message = clinical_state_is_ready(require_food=False)
    state = get_current_clinical_state()

    pet = state["pet"]
    energy = state["energy"]
    food = state["food"]

    _nombre3 = pet.get("nombre", "—")
    _especie3 = pet.get("especie", "perro")
    _edad3 = pet.get("edad", 0.0)
    _peso3 = pet.get("peso", 0.0)
    _etapa3 = pet.get("etapa", "adulto")
    _condicion3 = pet.get("condicion", "Castrado")
    _bcs3 = pet.get("bcs", 5)

    _mer_final3 = energy.get("mer_final", 0.0)
    _rer3 = energy.get("rer", 0.0)
    _mer_base3 = energy.get("mer_base", 0.0)
    _factor_fis3 = energy.get("factor_fisiologico", 0.0)
    _senior3 = energy.get("senior_aplicado", False)
    _estado_corp3 = energy.get("estado_corporal", get_estado_corporal(_bcs3))
    _riesgo3 = energy.get("riesgo_nutricional", "—")
    _prioridad3 = energy.get("prioridad_nutricional", "—")
    _aplicar_senior3 = pet.get("aplicar_ajuste_senior", False)

    _food_name3 = food.get("alimento", "—")
    _food_data3 = food.get("food_data_edited", {}) or {}

    if not _food_data3 and _food_name3 in FOODS:
        _food_data3 = FOODS.get(_food_name3, {})

    _gramos3 = food.get("gramos", 0.0)

    if _food_data3:
        _species_food3 = _food_data3.get("species", _especie3)
    
        _food_energy3 = calc_energy_food(
            _food_data3,
            species=_species_food3,
        )
    
        _food_ena3 = calc_ena_food(_food_data3)
    
        _food_eb3 = calculate_energy_breakdown(
            _food_data3,
            species=_species_food3,
        )
    else:
        _food_energy3 = {}
        _food_ena3 = 0.0
        _food_eb3 = {}

    _me3 = food.get("me", 0.0) or _food_energy3.get("ME", 0.0)
    _aporte3 = food.get("energia_aportada", 0.0)

    if not _aporte3 and _me3 > 0 and _gramos3 > 0:
        _aporte3 = (_me3 / 100.0) * _gramos3

    _req_pb3 = energy.get("req_pb_g", None)
    _req_ee3 = energy.get("req_ee_g", None)

    _gramos_pb3 = (_food_data3.get("PB", 0) / 100.0) * _gramos3 if _food_data3 else 0.0
    _gramos_ee3 = (_food_data3.get("EE", 0) / 100.0) * _gramos3 if _food_data3 else 0.0

    _datos_completos = (
        _mer_final3 is not None
        and _mer_final3 > 0
        and _food_name3 not in [None, "", "—"]
        and _me3 > 0
    )

    if _datos_completos:
        _cobertura3 = (_aporte3 / _mer_final3) * 100.0
        _gramos_rec3 = (_mer_final3 / (_me3 / 100.0)) if _me3 > 0 else 0.0
        _dif_g3 = _gramos_rec3 - _gramos3
        _cob_pb3 = (_gramos_pb3 / _req_pb3 * 100.0) if (_req_pb3 and _req_pb3 > 0) else None
        _cob_ee3 = (_gramos_ee3 / _req_ee3 * 100.0) if (_req_ee3 and _req_ee3 > 0) else None
    else:
        _cobertura3 = 0.0
        _gramos_rec3 = 0.0
        _dif_g3 = 0.0
        _cob_pb3 = None
        _cob_ee3 = None

    _diagnostico3 = generar_diagnostico_resumen(
        _nombre3,
        _bcs3,
        _estado_corp3,
        _mer_final3 or 0.0,
        _prioridad3,
        _condicion3,
        _edad3,
        _aplicar_senior3,
    )

    if _datos_completos:
        _resultado3, _dif_kcal3, _interpretacion3 = generar_decision_resumen(
            _cobertura3,
            _aporte3,
            _mer_final3 or 0.0,
            _gramos3,
            _gramos_rec3,
            _cob_pb3,
            _cob_ee3,
        )
    else:
        _resultado3, _dif_kcal3, _interpretacion3 = (
            "—",
            0.0,
            "Complete el perfil y el análisis de alimento.",
        )

    _recomendaciones3 = generar_recomendaciones(
        _estado_corp3,
        _bcs3,
        _edad3,
        _condicion3,
        _cobertura3 if _datos_completos else None,
        _cob_pb3,
        _cob_ee3,
    )

    st.subheader("👤 Resumen del Paciente")

    if ready:
        st.success("Perfil energético completo.")
    else:
        st.warning(ready_message)

    _rc1, _rc2 = st.columns(2)

    with _rc1:
        st.markdown(f"**Nombre:** {_nombre3}")
        st.markdown(f"**Especie:** {_especie3.capitalize()}")
        st.markdown(f"**Edad:** {_edad3:.1f} años")
        st.markdown(f"**Peso actual:** {_peso3:.1f} kg")

    with _rc2:
        st.markdown(f"**Etapa de vida:** {_etapa3.capitalize()}")
        st.markdown(f"**Condición fisiológica:** {_condicion3}")
        st.markdown(f"**BCS:** {_bcs3}/9")
        st.markdown(f"**Estado corporal:** {_estado_corp3}")
        st.markdown(f"**Riesgo nutricional:** {_riesgo3}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🩺 Diagnóstico Nutricional")
    st.info(_diagnostico3)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("⚡ Requerimiento Energético")

    if _mer_final3 and _mer_final3 > 0:
        _ec1, _ec2, _ec3, _ec4 = st.columns(4)

        with _ec1:
            st.metric("🔋 RER", f"{_rer3:.1f} kcal/día")

        with _ec2:
            st.metric("📊 MER base", f"{_mer_base3:.1f} kcal/día")

        with _ec3:
            st.metric("🎯 MER final", f"{_mer_final3:.1f} kcal/día")

        with _ec4:
            _sen_adj = "Sí" if _senior3 else "No"
            st.metric("👴 Senior aplicado", _sen_adj)

        with st.expander("Ver detalle energético", expanded=False):
            st.markdown(f"**Factor fisiológico:** {_factor_fis3:.2f}")
            st.markdown(f"**Ajuste senior:** {'Sí' if _senior3 else 'No'}")
            st.markdown(f"**Diagnóstico base:** {energy.get('diagnostico', '—')}")
    else:
        st.warning("Completa primero la pestaña Perfil de Mascota.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🍽️ Análisis del Alimento")

    if _food_name3 not in [None, "", "—"] and _food_data3:
        _fa1, _fa2 = st.columns(2)

        with _fa1:
            st.markdown(f"**Alimento seleccionado:** {_food_name3}")
            st.metric("⚡ ME", f"{_me3:.2f} kcal/100g")
            st.metric("🥣 Gramos evaluados", f"{_gramos3:.0f} g/día")
            st.metric("🔥 Energía aportada", f"{_aporte3:.1f} kcal/día")

        with _fa2:
            _comp_rows = [
                ("Proteína Bruta (PB %)", _food_data3.get("PB", 0)),
                ("Grasa (EE %)", _food_data3.get("EE", 0)),
                ("Cenizas (%)", _food_data3.get("Ash", 0)),
                ("Humedad (%)", _food_data3.get("Humidity", 0)),
                ("Fibra Cruda (FC %)", _food_data3.get("FC", 0)),
                ("ENA (%)", round(_food_ena3, 2)),
            ]

            for _n, _v in _comp_rows:
                st.markdown(f"**{_n}:** {_v:.2f}")

            if _food_data3.get("ingredients"):
                st.caption(f"Ingredientes: {_food_data3.get('ingredients')}")
    else:
        st.warning("Selecciona y analiza un alimento en la pestaña Análisis.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("✅ Decisión Nutricional")

    if _datos_completos:
        if _cobertura3 < 90:
            st.warning(_resultado3)
        elif _cobertura3 <= 110:
            st.success(_resultado3)
        else:
            st.error(_resultado3)

        st.markdown(_interpretacion3)

        _cq1, _cq2, _cq3 = st.columns(3)

        with _cq1:
            st.metric("Cobertura energética", f"{_cobertura3:.1f}%")

        with _cq2:
            st.metric("Gramos recomendados", f"{_gramos_rec3:.0f} g/día")

        with _cq3:
            _signo_g = "+" if _dif_g3 > 0 else ""
            st.metric("Diferencia vs evaluado", f"{_signo_g}{_dif_g3:.0f} g")
    else:
        st.info("Complete perfil y análisis del alimento para generar decisión nutricional.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("💡 Recomendaciones")

    if _recomendaciones3:
        for _rec in _recomendaciones3:
            st.markdown(f"✓ {_rec}")
    else:
        st.info("Las recomendaciones se generan automáticamente al completar el análisis.")

    st.markdown("---")
    st.subheader("📥 Descargar Informes")

    _fecha3 = datetime.date.today()
    _nombre_archivo3 = _nombre3.replace(" ", "_") if _nombre3 != "—" else "Mascota"

    _datos_energeticos3 = {
        "edad": _edad3,
        "peso": _peso3,
        "bcs": _bcs3,
        "etapa": _etapa3,
        "estado_corporal": _estado_corp3,
        "riesgo_nutricional": _riesgo3,
        "condicion": _condicion3,
        "rer": _rer3 or 0.0,
        "mer_base": _mer_base3 or 0.0,
        "diagnostico": _diagnostico3,
        "recomendaciones": _recomendaciones3,
    }

    _rng_min_exp = _gramos_rec3 * 0.9 if _datos_completos else 0.0
    _rng_max_exp = _gramos_rec3 * 1.1 if _datos_completos else 0.0

    _datos_alimento3 = {
        "alimento": _food_name3 or "—",
        "marca": _food_data3.get("brand", ""),
        "especie_comercial": _food_data3.get("species", ""),
        "etapa_comercial": _food_data3.get("life_stage", ""),
        "ingredientes": _food_data3.get("ingredients", ""),
        "fuente_pb": _food_data3.get("source_pb", ""),
        "fuente_ee": _food_data3.get("source_ee", ""),
        "fuente_fc": _food_data3.get("source_fc", ""),
        "me": _me3,
        "gramos": _gramos3,
        "aporte": _aporte3,
        "cobertura": _cobertura3,
        "recomendados": _gramos_rec3,
        "rango_min": _rng_min_exp,
        "rango_max": _rng_max_exp,
        "decision": _resultado3,
        "interpretacion": _interpretacion3,
        "pb": _food_data3.get("PB", 0) if _food_data3 else 0,
        "ee": _food_data3.get("EE", 0) if _food_data3 else 0,
        "ash": _food_data3.get("Ash", 0) if _food_data3 else 0,
        "humidity": _food_data3.get("Humidity", 0) if _food_data3 else 0,
        "fc": _food_data3.get("FC", 0) if _food_data3 else 0,
        "ena": _food_ena3,
        "ms": _food_energy3.get("MS", 0) if _food_energy3 else 0,
        "ge": _food_eb3.get("GE", 0) if _food_eb3 else 0,
        "de_pct": _food_energy3.get("DE_pct", 0) if _food_energy3 else 0,
        "de": _food_energy3.get("DE", 0) if _food_energy3 else 0,
    }

    _mascota_export3 = {
        "nombre": _nombre3,
        "especie": _especie3,
    }

    if not _datos_completos:
        st.warning("Para descargar informes completos, primero completa Perfil y Análisis.")

    _col_xlsx, _col_html = st.columns(2)

    with _col_xlsx:
        try:
            _nutrientes_ref3 = (
                NUTRIENTES_REFERENCIA_PERRO
                if _especie3 == "perro"
                else NUTRIENTES_REFERENCIA_GATO
            )

            _xlsx_bytes = exportar_ficha_maestra_excel(
                mascota=_mascota_export3,
                datos_energeticos=_datos_energeticos3,
                datos_alimento=_datos_alimento3,
                mer_final=_mer_final3 or 0.0,
                senior_applied=_senior3,
                recomendaciones=_recomendaciones3,
                nutrientes_ref=_nutrientes_ref3,
                cob_pb=_cob_pb3,
                cob_ee=_cob_ee3,
            )

            st.download_button(
                label="📥 Descargar ficha maestra de seguimiento (.xlsx)",
                data=_xlsx_bytes,
                file_name=f"UYWA_Ficha_Nutricional_{_nombre_archivo3}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="download_ficha_maestra",
                disabled=not _datos_completos,
            )

        except Exception as _e:
            st.error(f"Error al generar ficha maestra: {_e}")

    with _col_html:
        try:
            _html_str = exportar_a_html(
                _mascota_export3,
                _datos_energeticos3,
                _datos_alimento3,
                _mer_final3 or 0.0,
                _diagnostico3,
                _recomendaciones3,
            )

            st.download_button(
                label="📄 Descargar informe visual de hoy (HTML)",
                data=_html_str,
                file_name=f"UYWA_Informe_{_nombre_archivo3}_{_fecha3.strftime('%d%m%Y')}.html",
                mime="text/html",
                use_container_width=True,
                key="download_html_informe",
                disabled=not _datos_completos,
            )

        except Exception as _e:
            st.error(f"Error al generar informe HTML: {_e}")

# ======================== BLOQUE 5.4: TAB SEGUIMIENTO DEL PACIENTE ========================
with tabs[4]:
    show_patient_followup()
