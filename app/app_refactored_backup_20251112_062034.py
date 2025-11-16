# ==========================================================
#  RippleWriter Studio – Modular Refactor (Router Layer)
# ==========================================================
import streamlit as st
from pathlib import Path
import sys

# ----------------------------------------------------------
#  Path Setup
# ----------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))
    print(f"✅ RippleWriter root added to sys.path: {ROOT_DIR}")

# ----------------------------------------------------------
#  Streamlit Config (must be first Streamlit call)
# ----------------------------------------------------------
st.set_page_config(
    page_title="RippleWriter Studio",
    page_icon="🪶",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# Region Imports (Phase 2 Modular Refactor)
# ---------------------------------------------------------
try:
    # --- Core Tab Regions (each drives colB) ---
    from refactor_regions.compose_region import render_compose_panel
    from refactor_regions.input_region import render_input_panel
    from refactor_regions.analyze_region import render_analyze_panel
    from refactor_regions.preview_region import render_preview_panel

    # --- Shared Regions (colA + colC used by all tabs) ---
    from refactor_regions.controls_region import render_controls_panel
    from refactor_regions.monitor_region import render_monitor_panel

except Exception as e:
    st.error(f"⚠️ Region imports incomplete: {e}")

# ----------------------------------------------------------
#  Branding + Header
# ----------------------------------------------------------
st.title("🪶 RippleWriter Studio")
st.caption("Refactored modular build — 4-tab architecture")

# ----------------------------------------------------------
#  Tabs
# ----------------------------------------------------------
tab_compose, tab_input, tab_analyze, tab_preview = st.tabs(
    ["Compose", "Input", "Analyze", "Preview"]
)

# ----------------------------------------------------------
#  Global Layout Styling (Force Full-Height Columns)
# ----------------------------------------------------------
st.markdown("""
<style>
[data-testid="stHorizontalBlock"] {
    align-items: stretch !important;
}
[data-testid="column"] {
    display: flex !important;
    flex-direction: column !important;
    min-height: 100vh !important;
    justify-content: flex-start !important;
}
</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------------
#  Shared Layout Columns
# ----------------------------------------------------------
colA, colB, colC = st.columns([1, 2, 1])

# ----------------------------------------------------------
#  Tab Routing with Shared Columns
# ----------------------------------------------------------
with tab_compose:
    try:
        render_compose_panel(colA, colB, colC)
    except Exception as e:
        st.error(f"Compose Panel Error: {e}")

with tab_input:
    try:
        render_input_panel(colA, colB, colC)
    except Exception as e:
        st.error(f"Input Panel Error: {e}")

with tab_analyze:
    try:
        render_analyze_panel(colA, colB, colC)
    except Exception as e:
        st.error(f"Analyze Panel Error: {e}")

with tab_preview:
    try:
        render_preview_panel(colA, colB, colC)
    except Exception as e:
        st.error(f"Preview Panel Error: {e}")


# ----------------------------------------------------------
#  Footer
# ----------------------------------------------------------
st.markdown("---")
st.caption("RippleWriter © Kevin Day – Modular Refactor 2025 Build")
