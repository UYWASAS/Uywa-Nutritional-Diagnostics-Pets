from __future__ import annotations

from textwrap import dedent


def clean_html(content: str) -> str:
    """
    Limpia el HTML antes de enviarlo a Streamlit.

    Streamlit puede interpretar líneas con cuatro espacios
    como bloques de código Markdown, incluso cuando se usa
    unsafe_allow_html=True.

    Esta función:
    - aplica dedent;
    - elimina la indentación de cada línea;
    - elimina líneas vacías;
    - devuelve HTML continuo y seguro para st.markdown.
    """

    normalized = dedent(content)

    clean_lines = [
        line.strip()
        for line in normalized.splitlines()
        if line.strip()
    ]

    return "\n".join(clean_lines)
