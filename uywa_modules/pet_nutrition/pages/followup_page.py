"""
Página Seguimiento del Paciente para UYWA Pets.

Incluye un módulo mínimo funcional de seguimiento:
- Lee el estado clínico actual.
- Permite registrar una visita.
- Guarda temporalmente en st.session_state.
- Si existe patient_followup.show_patient_followup(), lo usa como módulo avanzado.
"""

from __future__ import annotations

import datetime
import pandas as pd
import streamlit as st

from clinical_state import get_current_clinical_state, clinical_state_is_ready

try:
    from patient_followup import show_patient_followup as _show_patient_followup
except Exception:
    _show_patient_followup = None


def _local_followup() -> None:
    st.header("📈 Seguimiento del Paciente")

    ready, message = clinical_state_is_ready(require_food=False)
    state = get_current_clinical_state()
    pet = state["pet"]
    energy = state["energy"]
    food = state["food"]

    if not ready:
        st.warning(message)

    patient_name = pet.get("nombre", "Mascota") or "Mascota"
    st.subheader(f"Paciente: {patient_name}")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Peso actual", f"{pet.get('peso', 0):.1f} kg")
    with c2:
        st.metric("BCS", f"{pet.get('bcs', '—')}/9")
    with c3:
        st.metric("MER final", f"{energy.get('mer_final', 0):.1f} kcal/día")
    with c4:
        st.metric("Alimento", food.get("alimento", "—"))

    st.markdown("---")
    st.subheader("➕ Registrar visita de seguimiento")

    with st.form("followup_visit_form"):
        visit_date = st.date_input("Fecha de visita", value=datetime.date.today())
        weight = st.number_input(
            "Peso observado (kg)",
            min_value=0.0,
            max_value=250.0,
            value=float(pet.get("peso", 0) or 0),
            step=0.1,
        )
        bcs = st.slider(
            "BCS observado",
            min_value=1,
            max_value=9,
            value=int(pet.get("bcs", 5) or 5),
        )
        grams = st.number_input(
            "Gramos/día indicados o consumidos",
            min_value=0.0,
            max_value=5000.0,
            value=float(food.get("gramos", 0) or 0),
            step=10.0,
        )
        notes = st.text_area(
            "Notas clínicas / recomendaciones",
            placeholder="Ej.: ajustar ración, controlar peso en 2 semanas, valorar tolerancia digestiva...",
            height=120,
        )

        submitted = st.form_submit_button("Guardar visita", use_container_width=True)

    if submitted:
        record = {
            "fecha": visit_date.isoformat(),
            "paciente": patient_name,
            "especie": pet.get("especie", "—"),
            "peso_kg": weight,
            "bcs": bcs,
            "mer_kcal_dia": energy.get("mer_final", 0),
            "alimento": food.get("alimento", "—"),
            "gramos_dia": grams,
            "notas": notes,
        }

        history_key = "uywa_followup_history"
        st.session_state.setdefault(history_key, [])
        st.session_state[history_key].append(record)
        st.success("Visita registrada correctamente.")

    history = st.session_state.get("uywa_followup_history", [])

    st.markdown("---")
    st.subheader("📋 Historial registrado")

    if history:
        df = pd.DataFrame(history)
        st.dataframe(df, use_container_width=True, hide_index=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Descargar seguimiento (.csv)",
            data=csv,
            file_name=f"UYWA_Seguimiento_{patient_name.replace(' ', '_')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.info("Aún no hay visitas registradas en esta sesión.")


def show_followup_page() -> None:
    if _show_patient_followup is not None:
        try:
            _show_patient_followup()
            return
        except Exception as exc:
            st.warning(f"No se pudo cargar el módulo avanzado de seguimiento: {exc}")
            st.info("Se muestra el módulo básico de seguimiento.")

    _local_followup()
