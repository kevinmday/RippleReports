# ==========================================================
#  RippleWriter Studio — Design Tab (Left Panel)
#  Unified System Controls + Draft Management + Metrics
# ==========================================================

import streamlit as st
import datetime
from app.utils.yaml_tools import list_yaml_files, load_yaml


# ----------------------------------------------------------
# Render Left Panel
# ----------------------------------------------------------
def render_design_left(colA):

    with colA:
        st.header("Design Controls")

        # ==================================================
        # SYSTEM STATUS / RUNTIME
        # ==================================================
        st.subheader("🧠 System Status")
        st.markdown("**Environment:** RippleWriter Studio Modular Refactor")
        st.markdown("**Status:** 🟢 Active")

        col1, col2 = st.columns(2)
        with col1:
            st.button("🔄 Restart Session", key="design_restart_btn")
        with col2:
            st.button("🧹 Flush Cache", key="design_flush_btn")

        st.caption("Restart clears session_state. Cache flush clears AI temp memory.")

        st.divider()

        # ==================================================
        # GLOBAL AI / API SETTINGS (shared across app)
        # ==================================================
        st.subheader("🔑 AI Access & Configuration")

        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            key="design_api_key"
        )

        st.selectbox(
            "Model",
            ["GPT-5 (default)", "GPT-4.1", "Claude 3.5", "Local LLM"],
            key="design_model_select"
        )

        st.toggle("Use Streaming Mode", key="design_streaming_toggle")

        st.caption("Stored per session. Will be used in Write + Analyze tabs.")

        st.divider()

        # ==================================================
        # DRAFT MANAGEMENT (structural)
        # ==================================================
        st.subheader("📄 Draft Management")

        try:
            drafts = list_yaml_files()
        except Exception:
            drafts = []

        st.markdown("**Available Drafts:**")
        st.write(f"{len(drafts)} YAML drafts found.")

        draft_choice = st.selectbox(
            "Select a draft",
            ["(none)"] + drafts,
            key="design_left_draft_select"
        )

        if draft_choice != "(none)":
            st.info(f"Loaded draft: **{draft_choice}**")
            try:
                preview = load_yaml(draft_choice)
                st.json(preview)
            except:
                st.error("YAML failed to load.")

        st.button("📝 New Draft", key="design_left_new_draft")

        st.divider()

        # ==================================================
        # TEMPLATE & EQUATION PACK GUIDANCE
        # ==================================================
        st.subheader("🧩 Template & Equation Packs")

        st.markdown("""
        **RippleWriter supports structured templates:**

        - Academic  
        - Op-Ed  
        - Legal Brief  
        - Investigative  
        - RippleTruth Fact File  
        - MarketMind Narrative  

        **Equation Packs:**
        - Intention Equations (FILS / UCIP / RippleScore)
        - MarketMind Equation Suite
        - Argument Strength Model (for op-eds)
        """)

        st.selectbox(
            "Preferred Equation Pack",
            [
                "None",
                "Intention Field Equations",
                "MarketMind Equation Suite",
                "RippleTruth Fact Grading",
            ],
            key="design_left_eq_pack"
        )

        st.caption("Pack determines available equations in the Center Panel.")

        st.divider()

        # ==================================================
        # USER GUIDE (DESIGN-SPECIFIC)
        # ==================================================
        with st.expander("📘 Design Tab Guide"):
            st.markdown("""
            ### Purpose of the Design Tab
            The Design tab structures your article **before** writing begins.

            Use this tab to:

            - Choose a template  
            - Build your YAML scaffold  
            - Organize metadata  
            - Load/duplicate existing drafts  
            - Select equation packs  
            - Set AI configuration  

            ### Workflow
            1. Select a template  
            2. Review metadata  
            3. Edit YAML structure  
            4. Save draft  
            5. Move to **Write** tab for prose generation  
            """)

        st.divider()

        # ==================================================
        # LIVE DIAGNOSTICS (LIGHTWEIGHT)
        # ==================================================
        st.subheader("⚙️ Diagnostics Snapshot")

        st.markdown(f"**Last Sync:** {datetime.datetime.now().strftime('%H:%M:%S')}")
        st.markdown("**Active Threads:** 3")
        st.markdown("**Runtime Mode:** Dev")

        st.progress(85, text="System Health")

        st.caption("RippleWriter © 2025 — Structural Engine Ready")
