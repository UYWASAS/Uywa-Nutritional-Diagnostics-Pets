"""Herramientas de exportación y generación de informes clínico-nutricionales UYWA."""

import io
import uuid
import logging
import pandas as pd
from datetime import datetime
from html import escape


# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------

def _safe_float(value, default=0.0):
    """Convierte un valor a float de forma segura."""
    try:
        if value is None:
            return default
        if isinstance(value, str):
            value = value.strip().replace(",", ".")
            if value == "" or value.lower() == "nan":
                return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_text(value, default="—"):
    """Convierte a texto seguro."""
    value = str(value or "").strip()
    return value if value else default


def _add_unique(recomendaciones, texto):
    """Agrega recomendación evitando duplicados exactos."""
    texto = str(texto or "").strip()
    if texto and texto not in recomendaciones:
        recomendaciones.append(texto)


# ---------------------------------------------------------------------------
# Funciones de generación de texto
# ---------------------------------------------------------------------------

def generar_diagnostico_resumen(nombre, bcs, estado, mer_final,
                                 prioridad, condicion, edad, aplicar_senior):
    """
    Genera el párrafo de diagnóstico nutricional para el informe de resumen.
    """
    nombre = _safe_text(nombre, "El paciente")
    estado = _safe_text(estado, "estado corporal no definido")
    condicion = _safe_text(condicion, "condición fisiológica no especificada")
    prioridad = _safe_text(prioridad, "mantener seguimiento nutricional")

    texto = f"{nombre} presenta condición corporal {estado.lower()} (BCS {bcs}/9). "
    texto += f"Su requerimiento energético final estimado es de {mer_final:.1f} kcal/día. "
    texto += f"La prioridad nutricional es {prioridad.lower()}."

    if aplicar_senior and edad >= 7:
        texto += " Se considera ajuste senior dentro de la evaluación energética."

    condicion_lower = condicion.lower()
    if any(g in condicion_lower for g in ["gestaci", "lactancia"]):
        texto += " Animal en gestación/lactancia: requerimiento elevado por condición reproductiva."

    texto += " Se recomienda monitoreo periódico."
    return texto


def generar_recomendaciones(estado, bcs, edad, condicion, cobertura,
                             cob_pb=None, cob_ee=None):
    """
    Genera una lista mejorada de recomendaciones clínico-nutricionales.

    Considera:
    - Estado corporal / BCS.
    - Edad / posible paciente senior.
    - Condición fisiológica.
    - Cobertura energética.
    - Cobertura de proteína.
    - Cobertura de grasa.
    """
    recomendaciones = []

    estado = _safe_text(estado, "")
    condicion = _safe_text(condicion, "")
    condicion_lower = condicion.lower()
    edad = _safe_float(edad, 0)
    cobertura_val = None if cobertura is None else _safe_float(cobertura, None)
    cob_pb_val = None if cob_pb is None else _safe_float(cob_pb, None)
    cob_ee_val = None if cob_ee is None else _safe_float(cob_ee, None)

    # 1. Recomendaciones por BCS / estado corporal
    if bcs <= 3:
        _add_unique(
            recomendaciones,
            "El paciente presenta condición corporal baja; se recomienda incrementar el aporte energético de forma progresiva y monitorear peso corporal semanalmente."
        )
        _add_unique(
            recomendaciones,
            "Evaluar causas clínicas o de manejo asociadas a la baja condición corporal antes de realizar incrementos agresivos de la ración."
        )
    elif bcs == 4:
        _add_unique(
            recomendaciones,
            "El paciente se encuentra ligeramente por debajo de la condición ideal; se recomienda ajustar la ración hacia una recuperación gradual de peso."
        )
        _add_unique(
            recomendaciones,
            "Monitorear peso y BCS cada 2–3 semanas hasta alcanzar condición corporal ideal."
        )
    elif bcs == 5:
        _add_unique(
            recomendaciones,
            "Mantener la ración dentro del rango recomendado y controlar peso corporal cada 2–4 semanas para conservar la condición corporal ideal."
        )
    elif bcs == 6:
        _add_unique(
            recomendaciones,
            "El paciente presenta ligera tendencia al sobrepeso; evitar incrementos innecesarios de ración y reforzar el control de premios o extras."
        )
        _add_unique(
            recomendaciones,
            "Reevaluar peso y BCS en 2–4 semanas para confirmar estabilidad de la condición corporal."
        )
    elif bcs == 7:
        _add_unique(
            recomendaciones,
            "El paciente presenta sobrepeso; se recomienda reducir el aporte calórico de forma controlada y establecer seguimiento quincenal."
        )
        _add_unique(
            recomendaciones,
            "Considerar una estrategia de control de peso que combine ajuste de ración, mayor actividad física y control estricto de premios."
        )
    elif bcs >= 8:
        _add_unique(
            recomendaciones,
            "El paciente presenta obesidad; se recomienda implementar un plan de reducción de peso supervisado por el veterinario."
        )
        _add_unique(
            recomendaciones,
            "Evitar restricciones energéticas bruscas; ajustar la ración progresivamente y realizar seguimiento frecuente de peso, BCS y tolerancia."
        )

    # 2. Recomendaciones por cobertura energética
    if cobertura_val is not None:
        if cobertura_val < 80:
            _add_unique(
                recomendaciones,
                f"La ración evaluada cubre solo el {cobertura_val:.1f}% del requerimiento energético; se recomienda incrementar gradualmente la cantidad diaria hasta acercarse al MER objetivo."
            )
        elif cobertura_val < 90:
            _add_unique(
                recomendaciones,
                f"La cobertura energética es baja ({cobertura_val:.1f}%); ajustar la dosis diaria del alimento y controlar la respuesta clínica."
            )
        elif cobertura_val <= 110:
            _add_unique(
                recomendaciones,
                f"La cobertura energética se encuentra dentro del rango objetivo ({cobertura_val:.1f}%); mantener la dosis propuesta y monitorear evolución."
            )
        elif cobertura_val <= 130:
            _add_unique(
                recomendaciones,
                f"La ración excede moderadamente el requerimiento energético ({cobertura_val:.1f}%); considerar reducción de gramos diarios o selección de un alimento con menor densidad energética."
            )
        else:
            _add_unique(
                recomendaciones,
                f"La ración excede de forma importante el requerimiento energético ({cobertura_val:.1f}%); reducir la dosis diaria y reevaluar el plan para evitar ganancia de peso."
            )

    # 3. Recomendaciones por cobertura proteica
    if cob_pb_val is not None:
        if cob_pb_val < 90:
            _add_unique(
                recomendaciones,
                f"La cobertura proteica estimada es insuficiente ({cob_pb_val:.1f}%); considerar un alimento con mayor concentración proteica o ajustar la estrategia nutricional."
            )
        elif cob_pb_val <= 130:
            _add_unique(
                recomendaciones,
                f"La cobertura proteica estimada es adecuada ({cob_pb_val:.1f}%); mantener seguimiento según etapa de vida y condición corporal."
            )
        else:
            _add_unique(
                recomendaciones,
                f"La cobertura proteica estimada es elevada ({cob_pb_val:.1f}%); interpretar en función de la condición clínica, edad, función renal y objetivo nutricional."
            )

    # 4. Recomendaciones por cobertura de grasa
    if cob_ee_val is not None:
        if cob_ee_val < 90:
            _add_unique(
                recomendaciones,
                f"La cobertura de grasa estimada es baja ({cob_ee_val:.1f}%); evaluar aporte de ácidos grasos esenciales y calidad de la fuente lipídica."
            )
        elif cob_ee_val <= 130:
            _add_unique(
                recomendaciones,
                f"La cobertura de grasa estimada es adecuada ({cob_ee_val:.1f}%); mantener control según condición corporal y tolerancia digestiva."
            )
        else:
            _add_unique(
                recomendaciones,
                f"La cobertura de grasa estimada es elevada ({cob_ee_val:.1f}%); vigilar ganancia de peso, tolerancia digestiva y necesidad de reducir densidad energética."
            )

    # 5. Recomendaciones por edad
    if edad >= 7:
        _add_unique(
            recomendaciones,
            "Por tratarse de un paciente senior, realizar reevaluación nutricional cada 6–8 semanas y controlar masa muscular, peso y condición corporal."
        )
        _add_unique(
            recomendaciones,
            "En pacientes senior, considerar evaluación clínica complementaria si existen cambios de apetito, pérdida de masa muscular o variaciones rápidas de peso."
        )

    # 6. Recomendaciones por condición fisiológica
    if "castrado" in condicion_lower and bcs >= 6:
        _add_unique(
            recomendaciones,
            "Dado que el paciente está castrado y presenta tendencia al sobrepeso, mantener control estricto de calorías y evitar alimentación ad libitum."
        )

    if "indoor" in condicion_lower or "inactivo" in condicion_lower:
        _add_unique(
            recomendaciones,
            "Por el menor gasto energético asociado a un estilo de vida indoor/inactivo, controlar estrictamente la ración diaria y el aporte de premios."
        )

    if "obeso" in condicion_lower:
        _add_unique(
            recomendaciones,
            "La condición fisiológica declarada indica obesidad; priorizar un plan de reducción de peso con metas graduales y seguimiento programado."
        )

    if "bajo peso" in condicion_lower:
        _add_unique(
            recomendaciones,
            "La condición fisiológica indica bajo peso; aumentar la ración de forma gradual y descartar causas clínicas de pérdida de condición corporal."
        )

    if "gestaci" in condicion_lower:
        _add_unique(
            recomendaciones,
            "Realizar valoración nutricional preparto y ajustar el plan según etapa de gestación, condición corporal y ganancia de peso."
        )
        _add_unique(
            recomendaciones,
            "Preparar transición nutricional hacia lactancia, considerando el incremento esperado de demanda energética."
        )

    if "lactancia" in condicion_lower:
        _add_unique(
            recomendaciones,
            "Durante lactancia, aumentar la frecuencia de alimentación y ajustar la ración según tamaño de camada, condición corporal y producción láctea."
        )
        _add_unique(
            recomendaciones,
            "Monitorear peso corporal y BCS semanalmente durante lactancia para evitar pérdida excesiva de condición."
        )

    if "destete" in condicion_lower:
        _add_unique(
            recomendaciones,
            "En fase de destete, asegurar transición gradual del alimento y dividir la ración en varias tomas al día."
        )

    # 7. Recomendación general final
    _add_unique(
        recomendaciones,
        "Registrar consumo real, peso corporal, BCS y cambios clínicos para ajustar la ración en la siguiente evaluación."
    )

    return recomendaciones


def generar_decision_resumen(cobertura, energia_aportada, mer_final,
                              gramos_input, gramos_recomendados,
                              cob_pb=None, cob_ee=None):
    """
    Genera la decisión ejecutiva de la evaluación nutricional.
    """
    cobertura = _safe_float(cobertura, 0)
    energia_aportada = _safe_float(energia_aportada, 0)
    mer_final = _safe_float(mer_final, 0)
    gramos_input = _safe_float(gramos_input, 0)
    gramos_recomendados = _safe_float(gramos_recomendados, 0)

    if cobertura < 90:
        resultado = "No cubre el requerimiento energético"
    elif cobertura <= 110:
        resultado = "Cubre adecuadamente el requerimiento energético"
    else:
        resultado = "Excede el requerimiento energético"

    diferencia = energia_aportada - mer_final

    interpretacion = (
        f"Con la ración actual de {gramos_input:.0f} g/día, "
        f"el alimento aporta {energia_aportada:.0f} kcal "
        f"vs {mer_final:.0f} kcal requeridas, "
        f"lo que representa una cobertura del {cobertura:.1f}%. "
    )

    tolerancia_kcal = max(25.0, mer_final * 0.05)

    if abs(diferencia) <= tolerancia_kcal:
        interpretacion += "La ración está adecuadamente ajustada."
    elif diferencia < 0:
        interpretacion += f"Se recomienda aumentar a {gramos_recomendados:.0f} g/día."
    else:
        interpretacion += f"Se recomienda reducir a {gramos_recomendados:.0f} g/día."

    if cob_pb is not None:
        cob_pb = _safe_float(cob_pb, None)
        if cob_pb is not None:
            interpretacion += f" La cobertura proteica estimada es {cob_pb:.1f}%."

    if cob_ee is not None:
        cob_ee = _safe_float(cob_ee, None)
        if cob_ee is not None:
            interpretacion += f" La cobertura de grasa estimada es {cob_ee:.1f}%."

    return resultado, diferencia, interpretacion


# ---------------------------------------------------------------------------
# Ficha Maestra de Seguimiento Nutricional
# ---------------------------------------------------------------------------

def generar_id_visita():
    """Genera UUID único para cada visita."""
    return str(uuid.uuid4())


def generar_uuid_paciente(nombre_especie):
    """Genera UUID determinístico para el paciente."""
    key = str(nombre_especie).lower()
    return str(uuid.uuid5(uuid.NAMESPACE_OID, key))


def crear_visita_dict(mascota, datos_energeticos, datos_alimento,
                      mer_final, senior_applied, cob_pb, cob_ee,
                      recomendaciones=None, objetivo_nutricional=""):
    """
    Crea diccionario con campos para una visita.
    """
    if recomendaciones is None:
        recomendaciones = datos_energeticos.get("recomendaciones", [])

    ahora = datetime.now()
    timestamp_iso = ahora.isoformat()
    fecha_iso = ahora.strftime("%Y-%m-%d")

    bcs = datos_energeticos.get("bcs", 5)

    if objetivo_nutricional == "":
        if bcs < 5:
            objetivo_nutricional = "Recuperar"
        elif bcs > 5:
            objetivo_nutricional = "Reducir"
        else:
            objetivo_nutricional = "Mantener"

    recomendaciones_str = (
        " | ".join(recomendaciones)
        if isinstance(recomendaciones, list)
        else str(recomendaciones)
    )

    cobertura = _safe_float(datos_alimento.get("cobertura", 0))
    decision = datos_alimento.get("decision", "Revisar")

    visita = {
        "id_visita": generar_id_visita(),
        "timestamp_registro": timestamp_iso,
        "fecha_visita": fecha_iso,
        "nombre_paciente": mascota.get("nombre", "—"),
        "especie": mascota.get("especie", "—").lower(),
        "edad": round(_safe_float(datos_energeticos.get("edad", 0)), 1),
        "peso_kg": round(_safe_float(datos_energeticos.get("peso", 0)), 1),
        "bcs": int(bcs),
        "estado_corporal": datos_energeticos.get("estado_corporal", "—"),
        "riesgo_nutricional": datos_energeticos.get("riesgo_nutricional", "—"),
        "etapa_vida": datos_energeticos.get("etapa", "adulto").lower(),
        "condicion_fisiologica": datos_energeticos.get("condicion", "—"),
        "ajuste_senior": bool(senior_applied),
        "objetivo_nutricional": objetivo_nutricional,
        "rer_kcal_dia": round(_safe_float(datos_energeticos.get("rer", 0)), 1),
        "mer_base_kcal_dia": round(_safe_float(datos_energeticos.get("mer_base", 0)), 1),
        "mer_final_kcal_dia": round(_safe_float(mer_final), 1),
        "alimento_evaluado": datos_alimento.get("alimento", "—"),
        "fuente_energia_alimento": datos_alimento.get("fuente_me", datos_alimento.get("fuente_energia", "—")),
        "gramos_dia_evaluados": round(_safe_float(datos_alimento.get("gramos", 0)), 1),
        "me_kcal_100g": round(_safe_float(datos_alimento.get("me", 0)), 2),
        "energia_aportada_kcal_dia": round(_safe_float(datos_alimento.get("aporte", 0)), 1),
        "cobertura_energia_pct": round(cobertura, 1),
        "gramos_recomendados_dia": round(_safe_float(datos_alimento.get("recomendados", 0)), 0),
        "diferencia_gramos_dia": round(
            _safe_float(datos_alimento.get("recomendados", 0))
            - _safe_float(datos_alimento.get("gramos", 0)), 1
        ),
        "cobertura_proteina_pct": round(_safe_float(cob_pb), 1) if cob_pb is not None else "",
        "cobertura_grasa_pct": round(_safe_float(cob_ee), 1) if cob_ee is not None else "",
        "resultado_nutricional": decision,
        "decision_clinica": f"Cobertura {cobertura:.1f}% - {decision}",
        "diagnostico_nutricional": datos_energeticos.get("diagnostico", "—"),
        "recomendaciones": recomendaciones_str,
        "observaciones": "",
        "profesional_responsable": "",
        "version_modelo": "v1.1",
        "fuente_dato": "app",
        "permitir_edicion": True,
    }

    return visita


def exportar_ficha_maestra_excel(mascota, datos_energeticos, datos_alimento,
                                  mer_final, senior_applied, recomendaciones,
                                  nutrientes_ref, cob_pb, cob_ee):
    """
    Genera archivo Excel con hojas de seguimiento nutricional.
    """
    output = io.BytesIO()
    especie = mascota.get("especie", "perro").lower()
    etapa = datos_energeticos.get("etapa", "adulto").lower()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        workbook = writer.book

        header_fmt = workbook.add_format({
            "bg_color": "#2176FF",
            "font_color": "white",
            "bold": True,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
        })

        section_fmt = workbook.add_format({
            "bg_color": "#EAF2FF",
            "font_color": "#0F172A",
            "bold": True,
            "border": 1,
        })

        recs_str = (
            " | ".join(recomendaciones)
            if isinstance(recomendaciones, list)
            else str(recomendaciones)
        )

        resumen_labels = [
            "DATOS DEL PACIENTE",
            "Nombre",
            "Especie",
            "Edad",
            "Peso actual",
            "BCS",
            "Estado corporal",
            "",
            "REQUERIMIENTOS ENERGÉTICOS",
            "RER",
            "MER base",
            "MER final ajustado",
            "",
            "ALIMENTO EVALUADO",
            "Nombre alimento",
            "Marca",
            "Especie comercial",
            "Etapa comercial",
            "Fuente energética usada",
            "Ingredientes",
            "Gramos/día",
            "ME (kcal/100g)",
            "Energía aportada",
            "Cobertura energética",
            "Cobertura proteína",
            "Cobertura grasa",
            "Gramos recomendados",
            "Rango recomendado",
            "",
            "DIAGNÓSTICO",
            "Diagnóstico nutricional",
            "Decisión nutricional",
            "Interpretación",
            "Recomendaciones",
        ]

        resumen_values = [
            "",
            mascota.get("nombre", "—"),
            mascota.get("especie", "—").capitalize(),
            f"{_safe_float(datos_energeticos.get('edad', 0)):.1f} años",
            f"{_safe_float(datos_energeticos.get('peso', 0)):.1f} kg",
            f"{datos_energeticos.get('bcs', 5)}/9",
            datos_energeticos.get("estado_corporal", "—"),
            "",
            "",
            f"{_safe_float(datos_energeticos.get('rer', 0)):.1f} kcal/día",
            f"{_safe_float(datos_energeticos.get('mer_base', 0)):.1f} kcal/día",
            f"{_safe_float(mer_final):.1f} kcal/día",
            "",
            "",
            datos_alimento.get("alimento", "—"),
            datos_alimento.get("marca", ""),
            datos_alimento.get("especie_comercial", ""),
            datos_alimento.get("etapa_comercial", ""),
            datos_alimento.get("fuente_me", datos_alimento.get("fuente_energia", "")),
            datos_alimento.get("ingredientes", ""),
            f"{_safe_float(datos_alimento.get('gramos', 0)):.1f} g",
            f"{_safe_float(datos_alimento.get('me', 0)):.2f}",
            f"{_safe_float(datos_alimento.get('aporte', 0)):.1f} kcal/día",
            f"{_safe_float(datos_alimento.get('cobertura', 0)):.1f}%",
            f"{_safe_float(cob_pb):.1f}%" if cob_pb is not None else "—",
            f"{_safe_float(cob_ee):.1f}%" if cob_ee is not None else "—",
            f"{_safe_float(datos_alimento.get('recomendados', 0)):.0f} g/día",
            f"{_safe_float(datos_alimento.get('rango_min', 0)):.0f} – {_safe_float(datos_alimento.get('rango_max', 0)):.0f} g/día",
            "",
            "",
            datos_energeticos.get("diagnostico", "—"),
            datos_alimento.get("decision", "—"),
            datos_alimento.get("interpretacion", "—"),
            recs_str,
        ]

        df_resumen = pd.DataFrame({"Parámetro": resumen_labels, "Valor": resumen_values})
        df_resumen.to_excel(writer, sheet_name="RESUMEN_ACTUAL", index=False)
        ws_resumen = writer.sheets["RESUMEN_ACTUAL"]
        ws_resumen.set_column(0, 0, 35)
        ws_resumen.set_column(1, 1, 90)
        for col_idx, col_name in enumerate(df_resumen.columns):
            ws_resumen.write(0, col_idx, col_name, header_fmt)
        for row_idx, label in enumerate(resumen_labels, start=1):
            if label.isupper() and label != "":
                ws_resumen.write(row_idx, 0, label, section_fmt)

        visita_actual = crear_visita_dict(
            mascota, datos_energeticos, datos_alimento,
            mer_final, senior_applied, cob_pb, cob_ee,
            recomendaciones=recomendaciones,
        )

        df_visitas = pd.DataFrame([visita_actual])
        df_visitas.to_excel(writer, sheet_name="VISITAS_SEGUIMIENTO", index=False)
        ws_visitas = writer.sheets["VISITAS_SEGUIMIENTO"]
        for col_idx in range(len(df_visitas.columns)):
            ws_visitas.set_column(col_idx, col_idx, 24)
        for col_idx, col_name in enumerate(df_visitas.columns):
            ws_visitas.write(0, col_idx, col_name, header_fmt)

        id_visita_actual = visita_actual["id_visita"]

        alimento_data = {
            "id_visita": [id_visita_actual],
            "alimento": [datos_alimento.get("alimento", "—")],
            "marca": [datos_alimento.get("marca", "")],
            "especie_comercial": [datos_alimento.get("especie_comercial", "")],
            "etapa_comercial": [datos_alimento.get("etapa_comercial", "")],
            "ingredientes": [datos_alimento.get("ingredientes", "")],
            "fuente_energia": [datos_alimento.get("fuente_me", datos_alimento.get("fuente_energia", ""))],
            "fuente_pb": [datos_alimento.get("fuente_pb", "")],
            "fuente_ee": [datos_alimento.get("fuente_ee", "")],
            "fuente_fc": [datos_alimento.get("fuente_fc", "")],
            "proteina_bruta_pct": [datos_alimento.get("pb", "")],
            "grasa_ee_pct": [datos_alimento.get("ee", "")],
            "cenizas_pct": [datos_alimento.get("ash", "")],
            "humedad_pct": [datos_alimento.get("humidity", "")],
            "fibra_cruda_pct": [datos_alimento.get("fc", "")],
            "ena_pct": [datos_alimento.get("ena", "")],
            "materia_seca_pct": [datos_alimento.get("ms", "")],
            "energia_bruta_kcal_100g": [datos_alimento.get("ge", "")],
            "energia_digestible_kcal_100g": [datos_alimento.get("de", "")],
            "energia_metabolizable_kcal_100g": [datos_alimento.get("me", "")],
            "energia_aportada_kcal_dia": [datos_alimento.get("aporte", "")],
            "cobertura_energia_pct": [datos_alimento.get("cobertura", "")],
            "gramos_recomendados_dia": [datos_alimento.get("recomendados", "")],
        }

        df_alimento = pd.DataFrame(alimento_data)
        df_alimento.to_excel(writer, sheet_name="ANALISIS_ALIMENTO", index=False)
        ws_alimento = writer.sheets["ANALISIS_ALIMENTO"]
        for col_idx in range(len(df_alimento.columns)):
            ws_alimento.set_column(col_idx, col_idx, 24)
        for col_idx, col_name in enumerate(df_alimento.columns):
            ws_alimento.write(0, col_idx, col_name, header_fmt)

        requisitos_rows = []
        try:
            nutrientes_dict = nutrientes_ref.get(etapa, {})
            for nutriente, valores in nutrientes_dict.items():
                requisitos_rows.append({
                    "nutriente": nutriente,
                    "unidad": valores.get("unit", ""),
                    "valor_minimo": valores.get("min", ""),
                    "valor_maximo": valores.get("max", ""),
                    "especie": especie,
                    "etapa_vida": etapa,
                    "fuente_modelo": "NRC 2006",
                })
        except Exception as exc:
            logging.warning(
                "Error al extraer requerimientos técnicos para %s/%s: %s",
                especie,
                etapa,
                exc,
            )

        df_requisitos = pd.DataFrame(
            requisitos_rows,
            columns=[
                "nutriente",
                "unidad",
                "valor_minimo",
                "valor_maximo",
                "especie",
                "etapa_vida",
                "fuente_modelo",
            ],
        )
        df_requisitos.to_excel(writer, sheet_name="REQUERIMIENTOS_TECNICOS", index=False)
        ws_req = writer.sheets["REQUERIMIENTOS_TECNICOS"]
        for col_idx in range(len(df_requisitos.columns)):
            ws_req.set_column(col_idx, col_idx, 20)
        for col_idx, col_name in enumerate(df_requisitos.columns):
            ws_req.write(0, col_idx, col_name, header_fmt)

        recomendaciones_rows = []
        for idx, rec in enumerate(recomendaciones or [], start=1):
            recomendaciones_rows.append({
                "orden": idx,
                "recomendacion": rec,
                "tipo": "editable_veterinario",
            })

        df_recs = pd.DataFrame(recomendaciones_rows, columns=["orden", "recomendacion", "tipo"])
        df_recs.to_excel(writer, sheet_name="RECOMENDACIONES", index=False)
        ws_recs = writer.sheets["RECOMENDACIONES"]
        ws_recs.set_column(0, 0, 10)
        ws_recs.set_column(1, 1, 100)
        ws_recs.set_column(2, 2, 24)
        for col_idx, col_name in enumerate(df_recs.columns):
            ws_recs.write(0, col_idx, col_name, header_fmt)

        uuid_paciente = generar_uuid_paciente(
            f"{mascota.get('nombre', 'paciente')}_{especie}"
        )

        fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fecha_hoy_date = datetime.now().strftime("%Y-%m-%d")

        metadatos_labels = [
            "METADATOS DEL ARCHIVO",
            "id_paciente",
            "nombre_paciente",
            "especie",
            "fecha_creacion_archivo",
            "fecha_ultima_actualizacion",
            "ultima_visita_registrada",
            "numero_visitas",
            "version_app",
            "version_modelo_energia",
            "fuente_modelo_energia",
            "ultima_modificacion_por",
            "observacion_general",
        ]

        metadatos_values = [
            "",
            uuid_paciente,
            mascota.get("nombre", "—"),
            especie,
            fecha_hoy,
            fecha_hoy,
            fecha_hoy_date,
            1,
            "1.1.0",
            "FEDIAF/NRC especie-específico v2",
            "FEDIAF 2025 / NRC 2006",
            "Sistema UYWA",
            "Incluye recomendaciones editables por veterinario.",
        ]

        df_metadatos = pd.DataFrame({"Clave": metadatos_labels, "Valor": metadatos_values})
        df_metadatos.to_excel(writer, sheet_name="METADATOS", index=False)
        ws_meta = writer.sheets["METADATOS"]
        ws_meta.set_column(0, 0, 35)
        ws_meta.set_column(1, 1, 60)
        for col_idx, col_name in enumerate(df_metadatos.columns):
            ws_meta.write(0, col_idx, col_name, header_fmt)

        config_labels = [
            "CONFIGURACIÓN DE LA APP",
            "usar_ajuste_senior",
            "usar_ajuste_bcs",
            "umbral_cobertura_minima",
            "umbral_cobertura_maxima",
        ]

        config_values = [
            "",
            True,
            True,
            90,
            110,
        ]

        df_config = pd.DataFrame({"Clave": config_labels, "Valor": config_values})
        df_config.to_excel(writer, sheet_name="CONFIG_APP", index=False)
        ws_config = writer.sheets["CONFIG_APP"]
        ws_config.set_column(0, 0, 35)
        ws_config.set_column(1, 1, 20)
        for col_idx, col_name in enumerate(df_config.columns):
            ws_config.write(0, col_idx, col_name, header_fmt)

    return output.getvalue()


# ---------------------------------------------------------------------------
# Exportación a HTML
# ---------------------------------------------------------------------------

def exportar_a_html(mascota, datos_energeticos, datos_alimento,
                    mer_final, diagnostico, recomendaciones):
    """
    Genera un HTML descargable profesional con el informe nutricional completo.
    """
    nombre = mascota.get("nombre", "—")
    especie = mascota.get("especie", "—").capitalize()
    edad = _safe_float(datos_energeticos.get("edad", 0))
    peso = _safe_float(datos_energeticos.get("peso", 0))
    bcs = datos_energeticos.get("bcs", 5)
    estado_corporal = datos_energeticos.get("estado_corporal", "—")
    condicion = datos_energeticos.get("condicion", "—")
    rer = _safe_float(datos_energeticos.get("rer", 0))
    mer_base = _safe_float(datos_energeticos.get("mer_base", 0))
    riesgo = datos_energeticos.get("riesgo_nutricional", "—")

    alimento = datos_alimento.get("alimento", "—")
    marca = datos_alimento.get("marca", "")
    fuente_me = datos_alimento.get("fuente_me", datos_alimento.get("fuente_energia", "—"))
    me = _safe_float(datos_alimento.get("me", 0))
    gramos = _safe_float(datos_alimento.get("gramos", 0))
    aporte = _safe_float(datos_alimento.get("aporte", 0))
    cobertura = _safe_float(datos_alimento.get("cobertura", 0))
    recomendados = _safe_float(datos_alimento.get("recomendados", 0))
    rango_min = _safe_float(datos_alimento.get("rango_min", 0))
    rango_max = _safe_float(datos_alimento.get("rango_max", 0))
    decision = datos_alimento.get("decision", "—")
    interpretacion = datos_alimento.get("interpretacion", "—")

    nombre_html = escape(str(nombre))
    especie_html = escape(str(especie))
    estado_corporal_html = escape(str(estado_corporal))
    condicion_html = escape(str(condicion))
    riesgo_html = escape(str(riesgo))
    alimento_html = escape(str(alimento))
    marca_html = escape(str(marca))
    fuente_me_html = escape(str(fuente_me))
    decision_html = escape(str(decision))
    diagnostico_html = escape(str(diagnostico))
    interpretacion_html = escape(str(interpretacion))

    recs_html = "\n".join(
        f"            <li>{escape(str(rec))}</li>"
        for rec in recomendaciones
    )

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>UYWA - Informe Nutricional</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #2c3e50;
            background: #f5f7fa;
            padding: 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            border-bottom: 3px solid #2176FF;
            padding-bottom: 20px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .header h1 {{ color: #2176FF; font-size: 28px; margin-bottom: 5px; }}
        .header p {{ color: #7f8c8d; font-size: 12px; }}
        .section {{ margin-bottom: 30px; page-break-inside: avoid; }}
        .section-title {{
            background: #ecf0f3;
            color: #2176FF;
            padding: 12px 16px;
            font-size: 16px;
            font-weight: 700;
            border-left: 4px solid #2176FF;
            margin-bottom: 15px;
        }}
        .data-row {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #ecf0f3;
        }}
        .data-row:last-child {{ border-bottom: none; }}
        .data-label {{ font-weight: 600; color: #2c3e50; }}
        .data-value {{ color: #34495e; text-align: right; max-width: 55%; }}
        .highlight {{
            background: #ecf0f3;
            padding: 12px;
            border-radius: 4px;
            margin: 10px 0;
        }}
        .diagnostic-box {{
            background: #f0f8ff;
            border-left: 4px solid #52B788;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
        }}
        .recommendations {{ list-style: none; margin: 15px 0; }}
        .recommendations li {{
            padding: 8px 0 8px 25px;
            position: relative;
            border-bottom: 1px solid #f0f0f0;
        }}
        .recommendations li:last-child {{ border-bottom: none; }}
        .recommendations li:before {{
            content: "\\2713";
            position: absolute;
            left: 0;
            color: #52B788;
            font-weight: bold;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f3;
            font-size: 11px;
            color: #7f8c8d;
        }}
        @media print {{
            body {{ background: white; }}
            .container {{ box-shadow: none; }}
        }}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>UYWA Nutrition</h1>
        <p>Informe Nutricional Personalizado</p>
    </div>

    <div class="section">
        <div class="section-title">&#128203; RESUMEN DEL PACIENTE</div>
        <div class="data-row"><span class="data-label">Nombre:</span><span class="data-value">{nombre_html}</span></div>
        <div class="data-row"><span class="data-label">Especie:</span><span class="data-value">{especie_html}</span></div>
        <div class="data-row"><span class="data-label">Edad:</span><span class="data-value">{edad:.1f} a&#241;os</span></div>
        <div class="data-row"><span class="data-label">Peso actual:</span><span class="data-value">{peso:.1f} kg</span></div>
        <div class="data-row"><span class="data-label">BCS:</span><span class="data-value">{bcs}/9</span></div>
        <div class="data-row"><span class="data-label">Estado corporal:</span><span class="data-value">{estado_corporal_html}</span></div>
        <div class="data-row"><span class="data-label">Condici&#243;n fisiol&#243;gica:</span><span class="data-value">{condicion_html}</span></div>
        <div class="data-row"><span class="data-label">Riesgo nutricional:</span><span class="data-value">{riesgo_html}</span></div>
    </div>

    <div class="section">
        <div class="section-title">&#129514; DIAGN&#211;STICO NUTRICIONAL</div>
        <div class="diagnostic-box">{diagnostico_html}</div>
    </div>

    <div class="section">
        <div class="section-title">&#9889; REQUERIMIENTOS ENERG&#201;TICOS</div>
        <div class="data-row"><span class="data-label">RER:</span><span class="data-value">{rer:.1f} kcal/d&#237;a</span></div>
        <div class="data-row"><span class="data-label">MER base:</span><span class="data-value">{mer_base:.1f} kcal/d&#237;a</span></div>
        <div class="data-row" style="background:#f0f8ff;font-weight:bold;"><span class="data-label">MER final ajustado:</span><span class="data-value">{mer_final:.1f} kcal/d&#237;a</span></div>
    </div>

    <div class="section">
        <div class="section-title">&#127869;&#65039; AN&#193;LISIS DEL ALIMENTO</div>
        <div class="data-row"><span class="data-label">Alimento:</span><span class="data-value">{alimento_html}</span></div>
        <div class="data-row"><span class="data-label">Marca:</span><span class="data-value">{marca_html}</span></div>
        <div class="data-row"><span class="data-label">Fuente de ME:</span><span class="data-value">{fuente_me_html}</span></div>
        <div class="data-row"><span class="data-label">ME:</span><span class="data-value">{me:.2f} kcal/100g</span></div>
        <div class="data-row"><span class="data-label">Gramos diarios:</span><span class="data-value">{gramos:.0f} g/d&#237;a</span></div>
        <div class="data-row"><span class="data-label">Energ&#237;a aportada:</span><span class="data-value">{aporte:.1f} kcal/d&#237;a</span></div>
        <div class="data-row"><span class="data-label">Cobertura energ&#233;tica:</span><span class="data-value">{cobertura:.1f}%</span></div>
    </div>

    <div class="section">
        <div class="section-title">&#9989; DECISI&#211;N NUTRICIONAL</div>
        <div class="highlight">
            <strong>{decision_html}</strong>
            <p style="margin-top:8px;font-size:14px;">{interpretacion_html}</p>
        </div>
    </div>

    <div class="section">
        <div class="section-title">&#128202; CANTIDAD RECOMENDADA</div>
        <div class="data-row"><span class="data-label">Gramos recomendados:</span><span class="data-value">{recomendados:.0f} g/d&#237;a</span></div>
        <div class="data-row"><span class="data-label">Rango aceptable (&#177;10%):</span><span class="data-value">{rango_min:.0f} &#8211; {rango_max:.0f} g/d&#237;a</span></div>
    </div>

    <div class="section">
        <div class="section-title">&#128161; RECOMENDACIONES DEL VETERINARIO</div>
        <ul class="recommendations">
{recs_html}
        </ul>
    </div>

    <div class="footer">
        <p>Este informe ha sido generado por UYWA Nutrition.</p>
        <p>Para m&#225;s informaci&#243;n: uywasas@gmail.com | &copy; 2026 Derechos reservados</p>
    </div>
</div>
</body>
</html>"""

    return html
