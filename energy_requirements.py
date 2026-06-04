import logging

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)

def calcular_rer(peso):
    """
    Calcula el Requerimiento Energético en Reposo (RER) de un animal.

    Fórmula: RER = 70 * peso^0.75

    Args:
        peso (float): Peso del animal en kilogramos.

    Returns:
        float: Requerimiento Energético en Reposo en kcal/día.
    """
    try:
        rer = 70 * (peso ** 0.75)
        logging.info(f"[RER] Calculado: {rer:.2f} kcal para peso: {peso:.2f} kg")
        return rer
    except Exception as e:
        logging.error(f"[RER] Error al calcular el RER: {e}")
        return None
