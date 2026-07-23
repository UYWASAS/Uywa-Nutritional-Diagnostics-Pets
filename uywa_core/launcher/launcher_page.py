def _render_launcher_header(
    current_user: object,
) -> None:
    display_name = html.escape(
        _get_display_name(current_user)
    )

    st.markdown(
        dedent(
            f"""
            <div class="uywa-launcher-hero">
                <div class="uywa-launcher-eyebrow">
                    UYWA PLATFORM
                </div>

                <h1 class="uywa-launcher-title">
                    Bienvenido, {display_name}
                </h1>

                <p class="uywa-launcher-subtitle">
                    Selecciona una herramienta para comenzar.
                    Todos tus módulos están organizados dentro
                    de un mismo espacio de trabajo.
                </p>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )
