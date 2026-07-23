from __future__ import annotations

from textwrap import dedent


def clean_html(content: str) -> str:
    """
    Normaliza fragmentos HTML para utilizarlos con
    Streamlit (st.markdown(..., unsafe_allow_html=True)).

    La función únicamente:

    - elimina la indentación común generada por el código;
    - elimina espacios al inicio y final del contenido.

    No modifica el HTML interno, por lo que conserva
    correctamente:

    - etiquetas multilínea;
    - atributos (class, style, id, etc.);
    - bloques <style>;
    - SVG;
    - cualquier estructura HTML válida.

    Esto evita errores como:

        <divclass="...">

    producidos al concatenar líneas.
    """

    if not content:
        return ""

    return dedent(content).strip()
