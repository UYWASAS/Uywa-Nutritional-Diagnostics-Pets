from __future__ import annotations

from textwrap import dedent


def clean_html(content: str) -> str:
    """
    Normaliza fragmentos HTML para mostrarlos mediante:

        st.markdown(
            clean_html(html_content),
            unsafe_allow_html=True,
        )

    La función:

    - elimina la indentación común;
    - elimina líneas vacías;
    - elimina espacios al inicio y final de cada línea;
    - une las líneas utilizando un espacio;
    - conserva la separación necesaria entre etiquetas
      y atributos HTML.

    Ejemplo:

        <div
            class="uywa-card"
        >

    se convierte en:

        <div class="uywa-card" >

    Esto evita dos problemas:

    1. Que Streamlit interprete líneas indentadas como
       bloques de código Markdown.
    2. Que las etiquetas se conviertan erróneamente en
       expresiones como <divclass="...">.
    """

    if not content:
        return ""

    normalized = dedent(content)

    clean_lines = [
        line.strip()
        for line in normalized.splitlines()
        if line.strip()
    ]

    return " ".join(clean_lines)
