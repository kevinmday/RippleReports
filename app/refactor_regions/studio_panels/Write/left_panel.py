import streamlit as st

def render_left_panel(col):
    with col:
        st.subheader("✏️ Write Controls")

        st.markdown("#### Draft Manager")
        st.text_input("Draft Name", key="write_draft_name")

        st.markdown("#### Model Settings")
        st.selectbox(
            "Model",
            ["GPT-5 (default)", "GPT-4.1", "GPT-4.1-Turbo"],
            key="write_model"
        )
        st.checkbox("Use Streaming Mode", key="write_streaming")

        st.markdown("#### Generation Tools")
        st.button("Generate Draft Structure", key="btn_generate_structure")
        st.button("Write & Render Now", key="btn_write_now")
        st.button("Rewrite Selected Section", key="btn_rewrite_section")

        st.markdown("---")
        st.caption("Write tab control center (2025 modular architecture)")
