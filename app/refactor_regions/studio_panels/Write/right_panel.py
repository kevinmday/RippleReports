import streamlit as st

def render_right_panel(container):
    """
    Basic Mode Right Panel:
    - Live Preview
    - Diagnostics placeholders
    - Intention metrics placeholder
    """

    with container:

        # ----------------------------------------------------------
        # Live Preview
        # ----------------------------------------------------------
        st.markdown("### 👁️ Live Preview")

        # This pulls from session_state (set by center_panel)
        draft_text = st.session_state.get("draft_text", "")

        if draft_text.strip():
            st.markdown(
                f"""
                <div style="
                    background-color:#0E1117;
                    border-radius:10px;
                    padding:18px;
                    border:1px solid #222;
                    font-size:1rem;
                ">
                    {draft_text}
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.info("Preview will appear here as you write.")

        st.markdown("---")

        # ----------------------------------------------------------
        # Diagnostics placeholders
        # ----------------------------------------------------------
        st.markdown("### 🧪 Diagnostics")

        st.markdown(
            """
            <div style="
                background-color:#3A3A1A;
                padding:12px;
                border-radius:8px;
                margin-bottom:10px;
            ">
                <strong>RippleTruth diagnostics</strong><br>
                <span style="opacity:0.8;">Diagnostics will appear here soon.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ----------------------------------------------------------
        # Intention Metrics placeholder
        # ----------------------------------------------------------
        st.markdown(
            """
            <div style="
                background-color:#153A5B;
                padding:12px;
                border-radius:8px;
                margin-bottom:10px;
            ">
                <strong>Intention Metrics</strong><br>
                FILS, UCIP, Drift will be integrated here.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption("Smart preview & diagnostics (2025 architecture)")
