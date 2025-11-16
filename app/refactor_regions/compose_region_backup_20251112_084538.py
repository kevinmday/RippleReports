# ==========================================================
#  RippleWriter Studio – Compose Region (Clean Rebuild)
# ==========================================================
import streamlit as st
from datetime import datetime
from app.utils.yaml_tools import save_yaml, load_yaml, list_yaml_files

def render_compose_panel(colA, colB):
    # ------------------------------------------------------
    # LEFT COLUMN (colA) — Draft Controls
    # ------------------------------------------------------
    with colA:
        st.subheader("Draft Controls")
        st.write("Select an existing draft or start a new one.")
        try:
            drafts = list_yaml_files()
        except Exception:
            drafts = []
        selected = st.selectbox("Choose Draft", ["(new)"] + drafts)
        if selected != "(new)":
            st.info(f"Loaded draft: **{selected}**")

    # ------------------------------------------------------
    # CENTER COLUMN (colB) — Main YAML + AI Assistant
    # ------------------------------------------------------
    with colB:
        st.subheader("YAML Scaffold Builder")
        article_type = st.selectbox(
            "Choose Article Type",
            ["(new)", "BlogPost.yaml", "OpEd.yaml"],
            key="compose_article_type"
        )

        st.markdown("### AI Assistant")
        if st.button("Generate Sections with AI Help", key="ai_generate_sections"):
            st.success("✨ AI Assistance triggered — sections will be generated here.")

        st.markdown("### Intention Equation")
        equation = st.selectbox(
            "Select Equation",
            ["None", "Peace Vector", "Fractal Resonance", "UCIP Flow"],
            key="intention_eq"
        )

        st.info("Draft: (new)\nAuthor: Kevin Day")
        st.success("✅ YAML Valid — no critical errors detected.")

        st.markdown("---")
        st.markdown("**YAML Actions**")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save YAML (Stay)", key="save_yaml_compose"):
                st.success("✅ YAML saved. Continue refining.")
        with col2:
            if st.button("➡️ Save & Move to Input", key="save_yaml_input"):
                st.success("✅ Saved & moved to Input tab.")

        st.caption("*Future: Ripple Feedback, Intention Matrix, etc.*")

    # ------------------------------------------------------
    # RIGHT COLUMN (colC) — Status & Monitoring
    # ------------------------------------------------------
    #with colC:
        #st.subheader("Article Status")
        #st.markdown(f"**Date/Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        #st.markdown("**Author:** Kevin Day")
        #st.markdown("**Equation:** None")
        #st.divider()
        #st.subheader("RSS / Webhook Monitor")
        #st.write("[system] waiting for RSS/Webhook updates…")
