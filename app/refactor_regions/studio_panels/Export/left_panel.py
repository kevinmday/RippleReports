import streamlit as st

def render_left_panel(col):
    with col:
        st.header("📦 Export Controls", divider="gray")

        # -----------------------------------------------------------
        # Export Format
        # -----------------------------------------------------------
        st.subheader("Export Format", divider="gray")

        format_choice = st.selectbox(
            "Choose format",
            ["HTML", "Markdown (MD)", "JSON", "YAML"],
            key="export_format_select"
        )

        st.session_state.export_format = format_choice

        st.markdown("")

        # -----------------------------------------------------------
        # Section Toggles
        # -----------------------------------------------------------
        st.subheader("Include Sections", divider="gray")

        include_final = st.checkbox(
            "Include Final Draft",
            value=True,
            key="export_include_final"
        )
        st.session_state.include_final = include_final

        include_insights = st.checkbox(
            "Include Insights & Recommendations",
            value=True,
            key="export_include_insights"
        )
        st.session_state.include_insights = include_insights

        include_rippletruth = st.checkbox(
            "Include RippleTruth Report",
            value=False,
            key="export_include_rippletruth"
        )
        st.session_state.include_rippletruth = include_rippletruth

        include_intention = st.checkbox(
            "Include Intention Metrics (FILS, UCIP, Drift)",
            value=False,
            key="export_include_intention"
        )
        st.session_state.include_intention = include_intention

        st.markdown("")

        # -----------------------------------------------------------
        # Generate Export Button
        # -----------------------------------------------------------
        if st.button("Generate Export", use_container_width=True, key="export_generate_button"):
            st.session_state.export_trigger = True
            st.success("Export generated.")

        st.markdown("---")
        st.caption("Export tab — left panel controls (2025 modular architecture)")
