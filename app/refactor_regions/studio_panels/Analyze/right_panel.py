import streamlit as st

def render_right_panel(col):
    with col:
        st.header("💡 Insights & Recommendations", divider="gray")

        # If no draft loaded
        if "analysis_data" not in st.session_state or not st.session_state.analysis_data:
            st.info("Load a draft and run an analysis to see insights.")
            return

        # If analysis not triggered yet
        if "analysis_trigger" not in st.session_state or not st.session_state.analysis_trigger:
            st.info("Run an analysis using the left panel to generate insights.")
            return

        # -------------------------------------------------------
        # INSIGHTS ENGINE (placeholder logic for now)
        # Will expand into RippleTruth + FILS + Structural/Force Maps
        # -------------------------------------------------------

        mode = st.session_state.get("analysis_mode", "RippleTruth Fact Scan")
        draft = st.session_state.analysis_data

        # Placeholder: Different insight blocks per analysis mode
        if mode == "RippleTruth Fact Scan":
            render_fact_scan_insights(draft)

        elif mode == "Intentionality Metrics (FILS / UCIP / Drift)":
            render_intention_insights(draft)

        elif mode == "Structural Coherence Map":
            render_structure_insights(draft)

        elif mode == "Narrative Force Analysis":
            render_narrative_force(draft)

        elif mode == "Full Composite Analysis":
            render_composite_insights(draft)

        # -------------------------------------------------------
        # Reset trigger after rendering so re-renders stay clean
        # -------------------------------------------------------
        st.session_state.analysis_trigger = False


# ================================================================
# ANALYSIS MODE: INSIGHT BLOCKS
# Future versions will connect to actual engines + RippleTruth API
# ================================================================

def render_fact_scan_insights(text):
    st.subheader("🔎 RippleTruth Fact Scan — Key Findings", divider="gray")

    st.warning("Fact-check engine not yet connected — using placeholder insights.")

    st.markdown("""
    **Potential Issues Identified:**
    - Statements requiring evidence.
    - Ambiguous claims implied without attribution.
    - Possible mixing of opinion with asserted fact.
    """)

    st.subheader("Suggested Fixes")
    st.markdown("""
    - Add sources where claims appear factual.
    - Clarify which parts are opinion vs. factual assertion.
    - Strengthen statements by using firm data instead of generalities.
    """)


def render_intention_insights(text):
    st.subheader("🌐 Intention Field Metrics (FILS / UCIP / Drift)", divider="gray")

    st.info("Intention analysis placeholder. Will integrate MarketMind engine later.")

    st.markdown("""
    **Early Interpretations:**
    - Draft shows mixed intention flow.
    - UCIP stabilization pending full engine integration.
    - Drift suggests narrative momentum is inconsistent.
    """)

    st.subheader("Recommendations")
    st.markdown("""
    - Reinforce narrative cohesion in key sections.
    - Align intention flow with the central claim of the draft.
    - Reduce chaotic transitions that break reader momentum.
    """)


def render_structure_insights(text):
    st.subheader("📐 Structural Coherence Map", divider="gray")

    st.info("Structural map engine placeholder.")

    st.markdown("""
    **Observations:**
    - Paragraph boundaries appear inconsistent.
    - Logical progression may jump in a few places.
    - Transitions could be smoother.

    **Recommendations:**
    - Reorganize sections to follow a problem → analysis → resolution arc.
    - Use section headers to clarify structure.
    """)


def render_narrative_force(text):
    st.subheader("⚡ Narrative Force Evaluation", divider="gray")

    st.info("Narrative force mapping placeholder.")

    st.markdown("""
    **Narrative Strengths:**
    - Strong thematic coherence.
    - Emotional resonance in key passages.

    **Weak Points:**
    - Force momentum drops around the midpoint.
    - Closing lacks a decisive narrative push.

    **Fixes:**
    - Add a reinforcing line to boost the ending arc.
    - Use contrast to increase narrative momentum.
    """)


def render_composite_insights(text):
    st.subheader("🧬 Full Composite Analysis", divider="gray")

    st.info("Composite engine placeholder — future hybrid of RippleTruth + FILS + Structure.")

    st.markdown("""
    **Summary of Findings:**
    - Several factual claims may require verification.
    - Intention flow oscillates between assertive and passive.
    - Narrative structure holds but lacks clarity in transitions.

    **Unified Recommendations:**
    - Add citations where needed.
    - Rewrite 2–3 paragraphs to unify authorial intention.
    - Increase clarity with stronger connective phrasing.
    """)

