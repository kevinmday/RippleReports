import streamlit as st

def render_center_panel(col):
    with col:
        st.header("📚 Analysis Results", divider="gray")

        # Safety guard
        if "analysis_trigger" not in st.session_state or not st.session_state.analysis_trigger:
            st.info("Run an analysis using the left panel.")
            return

        if "analysis_data" not in st.session_state or not st.session_state.analysis_data:
            st.warning("No draft loaded.")
            return

        mode = st.session_state.get("analysis_mode", "RippleTruth Fact Scan")
        draft = st.session_state.analysis_data

        # Display mode
        st.markdown(f"**Selected Mode:** `{mode}`")
        st.markdown("---")

        # Placeholder for displayed results
        result_container = st.container()

        # ---------------------------------------------------------
        # MODE-SPECIFIC ANALYSIS (stub outputs)
        # ---------------------------------------------------------
        if mode == "RippleTruth Fact Scan":
            with result_container:
                st.subheader("🧪 RippleTruth Fact Scan")
                st.info("Running fact-scan using RippleTruth engine…")
                st.write("• (Future) Claim extraction engine will process this text.")
                st.write("• (Future) Evidence score, reliability, and RippleScore will show here.")

        elif mode == "Intentionality Metrics (FILS / UCIP / Drift)":
            with result_container:
                st.subheader("🌌 Intention Metrics")
                st.info("Computing FILS, UCIP, Drift from intention equations…")
                st.write("• (Future) FILS, UCIP amplitude, TTCF, Drift values will be displayed.")
                st.write("• (Future) Narrative force map using UCIP slope.")

        elif mode == "Structural Coherence Map":
            with result_container:
                st.subheader("🧩 Structural Coherence Map")
                st.info("Analyzing outline, structure, section cohesion…")
                st.write("• (Future) Section hierarchy + map visualization.")

        elif mode == "Narrative Force Analysis":
            with result_container:
                st.subheader("⚡ Narrative Force Analysis")
                st.info("Evaluating tone, momentum, pressure, and domain force.")
                st.write("• (Future) Ripple coherence, pressure vectors, strength.")

        elif mode == "Full Composite Analysis":
            with result_container:
                st.subheader("🌀 Full Composite RippleWriter Analysis")
                st.info("Running all modules: TruthScan + FILS + Drift + Coherence…")
                st.write("• (Future) Composite score, charts, and integrated map.")

        # ---------------------------------------------------------
        # NEW: STORE RESULTS FOR EXPORT (stub outputs)
        # ---------------------------------------------------------
        if mode == "RippleTruth Fact Scan":
            st.session_state.rippletruth_report = (
                "RippleTruth scan completed.\n"
                "(Future: claim extraction + evidence score + RippleScore)"
            )
            st.session_state.insights_text = ""
            st.session_state.intent_metrics = ""

        elif mode == "Intentionality Metrics (FILS / UCIP / Drift)":
            st.session_state.intent_metrics = (
                "Intention metrics computed (FILS/UCIP/Drift).\n"
                "(Future: full intention metrics calculation)"
            )
            st.session_state.insights_text = ""
            st.session_state.rippletruth_report = ""

        elif mode == "Narrative Force Analysis":
            st.session_state.insights_text = (
                "Narrative force analysis completed.\n"
                "(Future: tone, momentum, pressure vectors)"
            )
            st.session_state.rippletruth_report = ""
            st.session_state.intent_metrics = ""

        elif mode == "Structural Coherence Map":
            st.session_state.insights_text = (
                "Structural coherence map generated.\n"
                "(Future: section hierarchy + cohesion analysis)"
            )
            st.session_state.rippletruth_report = ""
            st.session_state.intent_metrics = ""

        elif mode == "Full Composite Analysis":
            st.session_state.insights_text = (
                "Composite insights generated.\n"
                "(Future: combined metrics & RippleForce map)"
            )
            st.session_state.rippletruth_report = (
                "RippleTruth module completed (composite mode)."
            )
            st.session_state.intent_metrics = (
                "Intention metrics computed (composite mode)."
            )

        # Reset trigger so page doesn’t re-run repeatedly
        st.session_state.analysis_trigger = False
