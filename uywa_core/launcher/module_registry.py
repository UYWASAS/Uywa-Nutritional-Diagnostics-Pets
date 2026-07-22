from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PlatformModule:
    """
    Representa un módulo disponible dentro de Uywa Platform.
    """

    code: str
    title: str
    description: str
    icon: str
    status: str = "available"
    button_text: str = "Abrir módulo"
    route: Optional[str] = None

    @property
    def is_available(self) -> bool:
        """
        Indica si el módulo está disponible para abrirse.
        """

        return self.status == "available"

    @property
    def is_coming_soon(self) -> bool:
        """
        Indica si el módulo se encuentra en desarrollo.
        """

        return self.status == "coming_soon"


PLATFORM_MODULES: tuple[PlatformModule, ...] = (
    PlatformModule(
        code="pet_nutrition",
        title="Uywa Pet Nutrition",
        description=(
            "Evaluación nutricional, cálculo energético, análisis de "
            "alimentos y seguimiento de pacientes."
        ),
        icon="🐶",
        status="available",
        button_text="Abrir Pet Nutrition",
        route="pet_nutrition",
    ),
    PlatformModule(
        code="formulation_plus",
        title="Uywa Formulation Plus",
        description=(
            "Formulación de alimentos mediante programación lineal para "
            "aves, cerdos y rumiantes."
        ),
        icon="⚖️",
        status="coming_soon",
        button_text="Próximamente",
        route="formulation_plus",
    ),
    PlatformModule(
        code="farm_analytics",
        title="Uywa Farm Analytics",
        description=(
            "Análisis técnico y nutricional para sistemas de producción "
            "animal."
        ),
        icon="🐄",
        status="coming_soon",
        button_text="Próximamente",
        route="farm_analytics",
    ),
    PlatformModule(
        code="reports",
        title="Uywa Reports",
        description=(
            "Generación y administración de reportes técnicos para "
            "pacientes, dietas y evaluaciones nutricionales."
        ),
        icon="📊",
        status="coming_soon",
        button_text="Próximamente",
        route="reports",
    ),
    PlatformModule(
        code="ai_assistant",
        title="Uywa AI Assistant",
        description=(
            "Asistente especializado para apoyar la interpretación y "
            "gestión de información nutricional."
        ),
        icon="🤖",
        status="coming_soon",
        button_text="Próximamente",
        route="ai_assistant",
    ),
)


def get_platform_modules() -> tuple[PlatformModule, ...]:
    """
    Devuelve todos los módulos registrados en Uywa Platform.
    """

    return PLATFORM_MODULES


def get_module_by_code(
    module_code: str,
) -> PlatformModule | None:
    """
    Busca un módulo por su código interno.
    """

    normalized_code = str(module_code or "").strip().lower()

    for module in PLATFORM_MODULES:
        if module.code == normalized_code:
            return module

    return None
