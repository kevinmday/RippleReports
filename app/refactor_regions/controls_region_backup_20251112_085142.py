import streamlit as st
import uuid
from app.utils.yaml_tools import save_yaml, load_yaml, list_yaml_files
from app.utils.sidebar_tools import render_right_sidebar

def render_controls_panel():
    # ================== BEGIN CONTROLS PANEL ==================
    st.markdown("### 🧭 RippleWriter Controls")

    # Generate short unique suffix per render
    uid = uuid.uuid4().hex[:6]

    # --- Input Fields ---
    commit_msg = st.text_input(
        "Commit message",
        value="Publish via RippleWriter Studio",
        key=f"commit_message_col1_{uid}"
    )

    branch = st.text_input(
        "Branch",
        value="main",
        key=f"branch_col1_{uid}"
    )

    # --- RippleWriter Studio Guide ---
    with st.expander("📘 RippleWriter Studio Guide"):
        st.markdown(
            """
            - **Commit message**: Git commit label used when publishing drafts  
            - **Branch**: Select or confirm which branch is active (default: main)  
            - **Open output folder**: Opens `/output` directory for review  
            """
        )

    st.button("Open output folder", key=f"open_folder_col1_{uid}")

    return commit_msg, branch
