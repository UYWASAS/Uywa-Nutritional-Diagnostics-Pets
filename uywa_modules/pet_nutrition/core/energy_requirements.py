import logging

logging.basicConfig(level=logging.INFO)


def validar_peso(peso):
    """
    Valida el peso ingresado.

    Retorna:
        float
    """
    try:
        peso = float(peso)

        if peso <= 0:
            raise ValueError("El peso debe ser mayor que cero.")

        return peso

    except Exception as e:
        raise ValueError(f"Peso inválido: {e}")


def calcular_rer(peso):
    """
    Calcula el Requerimiento Energético en Reposo (RER).

    Fórmula NRC:
        RER = 70 × peso^0.75

    Parámetros:
        peso (float): peso vivo en kg

    Retorna:
        float: kcal/día
    """
    try:
        peso = validar_peso(peso)

        rer = 70.0 * (peso ** 0.75)

        logging.info(
            "[RER] Peso %.2f kg -> %.2f kcal/día",
            peso,
            rer,
        )

        return round(rer, 2)

    except Exception as e:
        logging.error("[RER] %s", e)

        return 0.0

def calcular_mer_gato_fediaf(peso, condicion="Castrado"):
    """
    Calcula MER base para gatos adultos según FEDIAF.

    Gato indoor / castrado / tendencia obesidad:
        MER = 75 × peso^0.67

    Gato activo / entero / bajo peso:
        MER = 100 × peso^0.67

    Retorna:
        tuple: (mer_base, factor_equivalente, descripcion)
    """
    try:
        peso = validar_peso(peso)
        condicion_txt = str(condicion or "").strip().lower()

        condiciones_bajas = [
            "castrado",
            "indoor",
            "tendencia obesidad",
            "obeso",
        ]

        if any(c in condicion_txt for c in condiciones_bajas):
            k = 75.0
            descripcion = "FEDIAF gato adulto indoor/castrado"
        else:
            k = 100.0
            descripcion = "FEDIAF gato adulto activo/entero"

        mer = k * (peso ** 0.67)

        rer_clinico = calcular_rer(peso)
        factor_equivalente = mer / rer_clinico if rer_clinico > 0 else 0.0

        logging.info(
            "[MER FEDIAF GATO] Peso %.2f kg | k %.1f -> %.2f kcal/día",
            peso,
            k,
            mer,
        )

        return round(mer, 2), round(factor_equivalente, 2), descripcion

    except Exception as e:
        logging.error("[MER FEDIAF GATO] %s", e)
        return 0.0, 0.0, "Error en cálculo FEDIAF gato"
