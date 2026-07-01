"""
Tema visual común para componentes UYWA Pets.

Este módulo centraliza colores, etiquetas y estilos reutilizables.
No contiene lógica nutricional.
"""

# Colores base
COLOR_TEXT = "#0F172A"
COLOR_MUTED = "#64748B"
COLOR_BORDER = "#E2E8F0"
COLOR_PANEL = "#FFFFFF"
COLOR_SOFT_BG = "#F8FAFC"

# Paleta nutricional fija
NUTRIENT_COLORS = {
    "PB": "#DC2626",        # Proteína
    "EE": "#F59E0B",        # Grasa
    "FC": "#16A34A",        # Fibra
    "ENA": "#2563EB",       # Carbohidratos/ENA
    "Ash": "#64748B",       # Cenizas
    "Humidity": "#38BDF8",  # Humedad
}

NUTRIENT_LABELS = {
    "PB": "Proteína",
    "EE": "Grasa",
    "FC": "Fibra",
    "ENA": "ENA",
    "Ash": "Cenizas",
    "Humidity": "Humedad",
}

STATUS_COLORS = {
    "low": "#2563EB",
    "ok": "#16A34A",
    "high": "#F97316",
    "neutral": "#64748B",
}

STATUS_BG = {
    "low": "#EFF6FF",
    "ok": "#ECFDF5",
    "high": "#FFF7ED",
    "neutral": "#F8FAFC",
}


def card_style(
    border_color: str = COLOR_BORDER,
    background: str = COLOR_PANEL,
    shadow: bool = True,
    radius: int = 18,
    padding: str = "16px 18px",
) -> str:
    box_shadow = "box-shadow:0 8px 22px rgba(15,23,42,0.06);" if shadow else ""
    return (
        f"background:{background};"
        f"border:1px solid {border_color};"
        f"border-radius:{radius}px;"
        f"padding:{padding};"
        f"{box_shadow}"
    )
