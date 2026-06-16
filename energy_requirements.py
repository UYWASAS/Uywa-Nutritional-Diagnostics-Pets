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
