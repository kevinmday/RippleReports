import streamlit as st

# ----------------------------------------------------------
# Preview Region Panel
# ----------------------------------------------------------
def render_preview_panel(colA, colB, colC):
    """Render the Preview tab layout inside RippleWriter Studio."""

    # LEFT COLUMN (colA)
    with colA:
        st.subheader("Preview Controls")
        st.write("Review your final YAML and generated article.")
        st.button("🔄 Refresh Preview", key="refresh_preview_btn")

    # CENTER COLUMN (colB)
    with colB:
        st.subheader("Rendered Output")
        st.markdown("_Your rendered article will appear here._", unsafe_allow_html=True)
        st.info("💡 Tip: Once published, HTML and Markdown exports will appear here automatically.")

    # RIGHT COLUMN (colC)
    with colC:
        st.subheader("Context Panel")
        st.success("✅ Connected via colC → shared context panel.")
        st.markdown(
            """
            **Future integration ideas:**
            - Live HTML preview
            - RippleTruth confidence overlay
            - Media & image attachments
            - Export / publish to GitHub Pages
            """
        )
