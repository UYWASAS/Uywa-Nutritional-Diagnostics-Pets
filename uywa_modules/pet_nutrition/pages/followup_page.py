"""
Página de seguimiento del paciente para Uywa Pet Nutrition.

Incluye un módulo básico de seguimiento y utiliza el módulo
avanzado de patient_followup.py cuando está disponible.
"""

from __future__ import annotations

import datetime

import pandas as pd
import streamlit as st

from clinical_state import (
    clinical_state_is_ready,
    get_current_clinical_state,
)

try:
    from patient_followup import (
        show_patient_followup as _show_patient_followup,
    )
except ImportError:
    _show_patient_followup = None


FOLLOWUP_HISTORY_KEY = "uywa_followup_history"


def _local_followup() -> None:
    """
    Renderiza el módulo básico de seguimiento cuando el
    módulo avanzado no está disponible.
    """

    st.header("📈 Seguimiento del Paciente")

    ready, message = clinical_state_is_ready(
        require_food=False,
    )

    state = get_current_clinical_state()

    pet = state.get("pet", {})
    energy = state.get("energy", {})
    food = state.get("food", {})

    if not ready:
        st.warning(message)

    patient_name = (
        pet.get("nombre", "Mascota")
        or "Mascota"
    )

    st.subheader(
        f"Paciente: {patient_name}"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Peso actual",
            f"{float(pet.get('peso', 0) or 0):.1f} kg",
        )

    with c2:
        st.metric(
            "BCS",
            f"{pet.get('bcs', '—')}/9",
        )

    with c3:
        st.metric(
            "MER final",
            f"{float(energy.get('mer_final', 0) or 0):.1f} kcal/día",
        )

    with c4:
        st.metric(
            "Alimento",
            food.get("alimento", "—") or "—",
        )

    st.markdown("---")
    st.subheader(
        "➕ Registrar visita de seguimiento"
    )

    with st.form(
        "followup_visit_form"
    ):
        visit_date = st.date_input(
            "Fecha de visita",
            value=datetime.date.today(),
        )

        weight = st.number_input(
            "Peso observado (kg)",
            min_value=0.0,
            max_value=250.0,
            value=float(
                pet.get("peso", 0)
                or 0
            ),
            step=0.1,
        )

        current_bcs = int(
            pet.get("bcs", 5)
            or 5
        )

        current_bcs = max(
            1,
            min(
                9,
                current_bcs,
            ),
        )

        bcs = st.slider(
            "BCS observado",
            min_value=1,
            max_value=9,
            value=current_bcs,
        )

        grams = st.number_input(
            "Gramos/día indicados o consumidos",
            min_value=0.0,
            max_value=5000.0,
            value=float(
                food.get("gramos", 0)
                or 0
            ),
            step=10.0,
        )

        notes = st.text_area(
            "Notas clínicas / recomendaciones",
            placeholder=(
                "Ej.: ajustar ración, controlar peso en 2 semanas, "
                "valorar tolerancia digestiva..."
            ),
            height=120,
        )

        submitted = st.form_submit_button(
            "Guardar visita",
            use_container_width=True,
        )

    if submitted:
        record = {
            "fecha": visit_date.isoformat(),
            "paciente": patient_name,
            "especie": pet.get(
                "especie",
                "—",
            ),
            "peso_kg": weight,
            "bcs": bcs,
            "mer_kcal_dia": energy.get(
                "mer_final",
                0,
            ),
            "alimento": food.get(
                "alimento",
                "—",
            ),
            "gramos_dia": grams,
            "notas": notes,
        }

        st.session_state.setdefault(
            FOLLOWUP_HISTORY_KEY,
            [],
        )

        st.session_state[
            FOLLOWUP_HISTORY_KEY
        ].append(record)

        st.success(
            "Visita registrada correctamente."
        )

    history = st.session_state.get(
        FOLLOWUP_HISTORY_KEY,
        [],
    )

    st.markdown("---")
    st.subheader(
        "📋 Historial registrado"
    )

    if not history:
        st.info(
            "Aún no hay visitas registradas en esta sesión."
        )
        return

    history_df = pd.DataFrame(
        history
    )

    st.dataframe(
        history_df,
        use_container_width=True,
        hide_index=True,
    )

    csv_data = history_df.to_csv(
        index=False,
    ).encode("utf-8")

    safe_patient_name = (
        patient_name
        .strip()
        .replace(" ", "_")
    )

    st.download_button(
        label="Descargar seguimiento (.csv)",
        data=csv_data,
        file_name=(
            f"UYWA_Seguimiento_{safe_patient_name}.csv"
        ),
        mime="text/csv",
        use_container_width=True,
    )


def show_followup_page() -> None:
    """
    Renderiza el seguimiento avanzado cuando está disponible.
    En caso contrario utiliza el módulo básico local.
    """

    if _show_patient_followup is not None:
        try:
            _show_patient_followup()
            return

        except Exception as exc:
            st.warning(
                "No se pudo cargar el módulo avanzado "
                f"de seguimiento: {exc}"
            )

            st.info(
                "Se muestra el módulo básico de seguimiento."
            )

    _local_followup()
