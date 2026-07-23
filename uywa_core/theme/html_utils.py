from __future__ import annotations

from textwrap import dedent


def clean_html(content: str) -> str:
    """
    Normaliza HTML para mostrarlo mediante st.markdown.

    Elimina:
    - indentación común;
    - espacios al inicio de cada línea;
    - líneas vacías;
    - saltos de línea que Markdown podría interpretar
      como bloques de código.
    """

    normalized = dedent(content)

    clean_lines = [
        line.strip()
        for line in normalized.splitlines()
        if line.strip()
    ]

    return "".join(clean_lines)
