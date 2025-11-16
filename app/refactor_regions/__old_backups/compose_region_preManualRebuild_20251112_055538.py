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
    

# ---- CENTER COLUMN: Main Work Area (colB) ----
with colB:
    # 1️⃣ --- YAML Scaffold Builder ---
    st.markdown("### Create Scaffold")
    article_type = st.selectbox(
        "Choose Article Type (YAML)",
        ["(new)", "BlogPost.yaml", "OpEd.yaml"]
    )

    # 2️⃣ --- AI Assistant (immediately below Scaffold) ---
    st.markdown("### AI Assistant")
    st.caption("Generate article sections with AI help")

    if st.button("Generate Sections with AI Help"):
        st.success("✨ AI Assistance triggered — sections will be generated.")

    # 3️⃣ --- Intention Equation ---
    st.markdown("### Intention Equation")
    intention_equation = st.selectbox(
        "Select Equation",
        ["None", "Peace Vector", "Fractal Resonance", "UCIP Flow"]
    )

    # 4️⃣ --- YAML / Author Summary ---
    st.info("Draft: (new)\nAuthor: Kevin Day")
    st.success("✅ YAML Valid — No critical errors detected.")

    # 5️⃣ --- YAML Save + Navigation ---
    st.markdown("---")  # Divider
    st.markdown("**YAML Actions**")
    st.write("Choose whether to stay and refine your YAML, or move straight into writing.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Save YAML (Stay on Compose)", key="save_yaml_compose"):
            try:
                save_yaml(filename, current_yaml_text)
                st.success("✅ YAML saved successfully. Continue refining.")
                st.session_state["current_yaml_file"] = filename
                st.session_state["current_yaml_text"] = current_yaml_text
                st.session_state["preview_refresh_flag"] = True
            except Exception as e:
                st.error(f"Save failed: {e}")

    with col2:
        if st.button("➡️ Save & Move to Input", key="save_yaml_input"):
            try:
                save_yaml(filename, current_yaml_text)
                st.session_state["active_tab"] = "Input"
                st.success("✅ Saved & moved to Input tab.")
            except Exception as e:
                st.error(f"Navigation failed: {e}")

    # 6️⃣ --- Footer Placeholder for future center tools ---
    st.markdown("*Future: intention matrix, ripple feedback, etc.*")
