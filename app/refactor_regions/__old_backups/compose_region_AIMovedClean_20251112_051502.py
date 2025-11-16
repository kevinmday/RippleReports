import streamlit as st
from datetime import datetime
import uuid
from app.utils.yaml_tools import save_yaml, load_yaml, list_yaml_files
from app.utils.sidebar_tools import render_right_sidebar

from pathlib import Path
ARTICLES_DIR = Path("articles")  # adjust path if your YAML files live elsewhere

def render_compose_panel(colA, colB, colC):
    with colA:
        st.write("Left panel – shared tools")
    with colB:
        st.markdown("## Compose Region Active")
    with colC:
        st.write("Right panel – helpers")


def render_compose_panel():
    # ================== BEGIN COMPOSE PANEL ==================
    # ---- LAYOUT SETUP (3 Columns + CSS Tweaks) ----
    st.markdown("### Compose: YAML Scaffold Builder")

# --- Compose (YAML) Layout Upgrade: Three Columns ---
with st.container():
    st.subheader("Compose: YAML Scaffold Builder")

    # Left = controls | Center = YAML fields | Right = feedback/monitor
    colL, colC, colR = st.columns([1.2, 2.8, 1])

# --- Extend right column height only (scoped to Compose area) ---
    st.markdown("""
    <style>
    /* Find Compose layout block, then extend its rightmost column */
    section[data-testid="stVerticalBlock"]:has(> div > div:has(> h3:contains('Compose: YAML Scaffold Builder'))) 
    div[data-testid="column"]:last-child {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 100vh !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ---- LEFT COLUMN: Draft Controls ----
    with colL:
        st.markdown("### Draft Controls")
        # You can later move draft selection dropdown or file options here
        # Example placeholder:
        st.text("Draft list and quick options will go here.")

# ---- CENTER COLUMN: Scaffold + AI Assistant ----
with colB:
    # --- Main scaffold area ---
    st.markdown("### Create Scaffold")
    article_type = st.selectbox("Choose Article Type (YAML)", ["(new)", "BlogPost.yaml", "OpEd.yaml"])

    
    st.markdown('### AI Assistant')
    st.caption('Generate article sections with AI help')
    if st.button('Generate Sections with AI Help'):
        st.success('? AI Assistance triggered � sections will be generated.')
    
    # --- Intention Equation (moved into center) ---
    intention_equation = st.selectbox(
        "Intention Equation",
        ["None", "Peace Vector", "Fractal Resonance", "UCIP Flow"],
    )


        st.success("✨ AI Assistance triggered — sections will be generated.")

    # --- YAML / Author summary ---
    st.info("Draft: (new)\nAuthor: Kevin Day")
    st.success("✅ YAML Valid — No critical errors detected.")

    # Placeholder for any follow-up tools
    st.markdown("*(Future: intention equation, ripple feedback, etc.)*")


# (inactive logic) # Default selection fallback
    if 'choice' not in locals():
        choice = "(new)"

    # --- Safe load / new scaffold handler ---


# --- Safe load / new scaffold handler ---
# Ensure draft_choice exists before using
try:
    choice = draft_choice
except NameError:
    draft_choice = "(new)"  # default selection if nothing defined
    choice = draft_choice

    if choice == "(new)":
        filename = "new-article.yaml"
        data = {
            "title": "",
            "author": "Kevin Day",
            "date": datetime.now().strftime("%Y/%m/%d"),
            "format": "Op-Ed",
            "intention_equation": "None"
        }
        st.info("Starting a new YAML scaffold.")
    else:
        current_path = ARTICLES_DIR / choice
        try:
            data = load_yaml(current_path)
            st.success(f"? Loaded existing draft: {choice}")
        except FileNotFoundError:
            st.error(f"File not found: {current_path}")
            data = {}

    # Share current selection across tabs
    st.session_state["rw_choice"] = choice
    st.session_state["rw_data"] = data

    # Show Ripple score if previously saved by Meta-Analysis
    meta = data.get("meta") or {}
    score = meta.get("ripple_score") if isinstance(meta, dict) else None
    if isinstance(score, (int, float)):
        st.metric("Ripple score", f"{score:.3f}")

        # Core YAML Fields go here:
        title = st.text_input("Title")
        author = st.text_input("Author", "Kevin Day")
        date = st.text_input("Date", value=datetime.now().strftime("%Y/%m/%d"))
# (inactive logic) format_choice = st.selectbox("Format", ["Op-Ed", "Feature", "Essay", "Report"])

# ---- SAVE YAML + NAVIGATION ----
    st.markdown("DEBUG: This is the ONLY Save YAML block executing.", unsafe_allow_html=True)

# ---- SAVE YAML + NAVIGATION ----
# Bottom-fixed YAML save container with session bridge + tab control
    with st.container():
        st.markdown("---")  # visual divider
        st.markdown("**YAML Actions**")
        st.write("Choose whether to stay and refine your YAML, or move straight into writing.")
    
        col1, col2 = st.columns(2)
    
        # --- SAVE YAML (Stay on Compose) ---
        with col1:
            if st.button("💾 Save YAML (Stay on Compose)", key="save_yaml_compose"):
                try:
                    save_yaml(filename, current_yaml_text)
                    st.success("✅ YAML saved successfully. Continue refining.")
    
                    # 🔄 Bridge: update session state for Preview tab sync
                    st.session_state["current_yaml_file"] = filename
                    st.session_state["current_yaml_text"] = current_yaml_text
                    st.session_state["preview_refresh_flag"] = True
    
                except Exception as e:
                    st.error(f"Save failed: {e}")
    
        # --- SAVE & MOVE TO INPUT TAB ---
        with col2:
            if st.button("➡️ Save & Move to Input", key="move_to_input_compose"):
                try:
                    save_yaml(filename, current_yaml_text)
                    st.success("✅ YAML saved and moved to Input tab.")
    
                    # 🔄 Bridge: update session state for cross-tab sync
                    st.session_state["current_yaml_file"] = filename
                    st.session_state["current_yaml_text"] = current_yaml_text
                    st.session_state["preview_refresh_flag"] = True
    
                    # Optional: auto-switch tab (depends on routing implementation)
                    st.session_state.active_tab = "Input"
    
                except Exception as e:
                    st.error(f"Save failed: {e}")
    
    # --- Meta-Analysis Tab ---
    # ---- META-ANALYSIS SECTION ----
import streamlit as st
from datetime import datetime
from app.utils.yaml_tools import save_yaml, load_yaml, list_yaml_files
from app.utils.sidebar_tools import render_right_sidebar
from pathlib import Path

ARTICLES_DIR = Path("articles")

# --------------------------------------------------
#  Compose Region Panel (Refactored)
# --------------------------------------------------
def render_compose_panel(tab_meta):
    """Render YAML compose + meta-analysis section inside the given tab."""
    with tab_meta:
        st.subheader("Meta-Analysis (Ripple Score)")

        choice = st.session_state.get("rw_choice")
        data = st.session_state.get("rw_data", {})

        files = list_yaml_files()
        names = [f.name for f in files]

        if not choice or choice == "(new)" or not names:
            st.info("Pick or create a draft in **Compose** first.")
            choice = st.selectbox("Choose Article", names, index=0 if names else None, key="meta_draft_fallback")
            if not choice:
                st.stop()
            data = load_yaml(ARTICLES_DIR / choice)

        st.write("✅ Meta-analysis loaded for:", choice)
        render_right_sidebar()

