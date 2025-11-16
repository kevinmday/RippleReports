import streamlit as st

def render_left_panel(col):
    with col:
        st.header("🔍 Analysis Controls", divider="gray")

        # -------------------------------
        # Load Draft Area
        # -------------------------------
        st.subheader("Draft Source", divider="gray")
        draft_text = st.text_area(
            "Paste draft text to analyze",
            height=180,
            key="analysis_input_text"
        )

        if st.button("Load Into Analyzer", type="primary"):
            if draft_text.strip():
                st.session_state.analysis_data = draft_text.strip()
                st.success("Draft loaded into analysis engine.")
            else:
                st.warning("Please enter text first.")

        st.markdown("")

        # -------------------------------
        # Analysis Mode
        # -------------------------------
        st.subheader("Analysis Mode", divider="gray")

        mode = st.selectbox(
            "Choose analysis type",
            [
                "RippleTruth Fact Scan",
                "Intentionality Metrics (FILS / UCIP / Drift)",
                "Structural Coherence Map",
                "Narrative Force Analysis",
                "Full Composite Analysis"
            ],
            key="analysis_mode"
        )

        # IMPORTANT:
        # Do NOT set st.session_state.analysis_mode here.
        # The selectbox widget owns this key.
        # Streamlit will raise an exception if we try to overwrite it.

        st.markdown("")
        st.subheader("Run", divider="gray")

        if st.button("🧠 Run Analysis", use_container_width=True):
            if "analysis_data" not in st.session_state or not st.session_state.analysis_data:
                st.error("No draft loaded.")
            else:
                st.session_state.analysis_trigger = True
                st.success("Analysis queued.")

        st.markdown("---")
        st.caption("Analyze tab — left panel controls (2025 modular architecture)")
