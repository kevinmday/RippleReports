# ==========================================================
#  RippleWriter Studio – NEW Modular Router (safe parallel)
#  Version: Panel Architecture (Design / Write / Analyze / Export)
# ==========================================================
import streamlit as st
from pathlib import Path
import sys

# ----------------------------------------------------------
#  Path Setup (kept identical for safety)
# ----------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))
    print(f"✅ RippleWriter root added to sys.path: {ROOT_DIR}")


# ----------------------------------------------------------
#  Handle floating button JS callback (Write fullscreen exit)
# ----------------------------------------------------------
if st.session_state.get("write_fullscreen") and st.session_state.get("_component_value") == "exit":
    st.session_state.write_fullscreen = False
    st.session_state["_component_value"] = None
    st.rerun()


# ----------------------------------------------------------
#  Streamlit Config
# ----------------------------------------------------------
st.set_page_config(
    page_title="RippleWriter Studio",
    page_icon="🪶",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------
#  Initialize Canonical Session State Keys
# ----------------------------------------------------------
REQUIRED_KEYS = [
    "draft_text",
    "draft_yaml",

    "analysis_raw_output",
    "insights_text",
    "rippletruth_report",
    "intent_metrics",

    "export_title",
    "export_subtitle",
    "export_html",
    "export_markdown",

    "analysis_data",
    "analysis_mode",
    "analysis_trigger",

    "export_format",

    "include_final",
    "include_insights",
    "include_rippletruth",
    "include_intention_metrics",
    ]

for key in REQUIRED_KEYS:
    if key not in st.session_state:
        st.session_state[key] = ""

# ----------------------------------------------------------
# Branding + Header (NO LOGO)
# ----------------------------------------------------------

st.markdown(
    """
    <h1 style="margin-bottom: 0px; font-size: 2.6rem;">
        RippleWriter Studio
    </h1>
    <p style="margin-top: -8px; font-size: 1.1rem; color: #ccc;">
        New modular build — Design • Write • Analyze • Export
    </p>
    """,
    unsafe_allow_html=True
)

# ----------------------------------------------------------
# Tabs
# ----------------------------------------------------------
tab_design, tab_write, tab_analyze, tab_export = st.tabs(
    ["Design", "Write", "Analyze", "Export"]
)



# ----------------------------------------------------------
#  Global Column Styling
# ----------------------------------------------------------
st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)


# ----------------------------------------------------------
#  Safe Import Helper
# ----------------------------------------------------------
def safe_import(module_path, function_name):
    try:
        module = __import__(module_path, fromlist=[function_name])
        return getattr(module, function_name)
    except Exception as e:
        st.error(f"⚠️ Import error in {module_path}.{function_name}: {e}")
        return None


# ==========================================================
#  DESIGN TAB
# ==========================================================
with tab_design:
    colA, colB, colC = st.columns([1.2, 2.0, 1.2])

    left_panel   = safe_import("app.refactor_regions.studio_panels.Design.left_panel",   "render_design_left")
    center_panel = safe_import("app.refactor_regions.studio_panels.Design.center_panel", "render_design_center")
    right_panel  = safe_import("app.refactor_regions.studio_panels.Design.right_panel",  "render_design_right")

    if left_panel:   left_panel(colA)
    if center_panel: center_panel(colB)
    if right_panel:  right_panel(colC)


# ==========================================================
#  WRITE TAB — Hybrid Fullscreen Layout
# ==========================================================
with tab_write:

    if "write_fullscreen" not in st.session_state:
        st.session_state.write_fullscreen = False

    # ------------------------------------------------------
    # Fullscreen Mode
    # ------------------------------------------------------
    if st.session_state.write_fullscreen:

        container = st.container()

        center_panel = safe_import(
            "app.refactor_regions.studio_panels.Write.center_panel",
            "render_center_panel"
        )

        if center_panel:
            center_panel(container, fullscreen=True)

    # ------------------------------------------------------
    # Normal 3-column Mode
    # ------------------------------------------------------
    else:
        colA, colB, colC = st.columns([1.2, 2.0, 1.2])

        left_panel   = safe_import("app.refactor_regions.studio_panels.Write.left_panel",   "render_left_panel")
        center_panel = safe_import("app.refactor_regions.studio_panels.Write.center_panel", "render_center_panel")
        right_panel  = safe_import("app.refactor_regions.studio_panels.Write.right_panel",  "render_right_panel")

        if left_panel:   left_panel(colA)
        if center_panel: center_panel(colB, fullscreen=False)
        if right_panel:  right_panel(colC)


# ----------------------------------------------------------
# Analyze Tab
# ----------------------------------------------------------
with tab_analyze:

    # Initialize session state placeholder for analysis results
    if "analysis_data" not in st.session_state:
        st.session_state.analysis_data = None

    # Import modular panels
    left_panel = safe_import(
        "app.refactor_regions.studio_panels.Analyze.left_panel",
        "render_left_panel"
    )
    center_panel = safe_import(
        "app.refactor_regions.studio_panels.Analyze.center_panel",
        "render_center_panel"
    )
    right_panel = safe_import(
        "app.refactor_regions.studio_panels.Analyze.right_panel",
        "render_right_panel"
    )

    # Layout: three columns
    colA, colB, colC = st.columns([1.1, 2.0, 1.0])

    # Render left controls
    if left_panel:
        left_panel(colA)

    # Render main results
    if center_panel:
        center_panel(colB)

    # Render insights
    if right_panel:
        right_panel(colC)

with tab_export:

    colA, colB, colC = st.columns([1.1, 2.0, 1.0])

    left_panel = safe_import(
        "app.refactor_regions.studio_panels.Export.left_panel",
        "render_left_panel"
    )
    center_panel = safe_import(
        "app.refactor_regions.studio_panels.Export.center_panel",
        "render_center_panel"
    )
    right_panel = safe_import(
        "app.refactor_regions.studio_panels.Export.right_panel",
        "render_right_panel"
    )

    if left_panel: left_panel(colA)
    if center_panel: center_panel(colB)
    if right_panel: right_panel(colC)

# ----------------------------------------------------------
#  Footer
# ----------------------------------------------------------
st.markdown("---")
st.caption("RippleWriter © Kevin Day — New Modular Panel Build (2025)")

