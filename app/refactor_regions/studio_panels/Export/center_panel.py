# ==========================================================
#  Export → Center Panel
#  Builds the final export output (Markdown, HTML, DOCX)
#  and displays a preview for the user.
# ==========================================================

import streamlit as st

# Import the export builder
try:
    from app.refactor_regions.export_logic.export_builder import build_export_output
except Exception as e:
    st.error(f"Export builder import failed: {e}")
    build_export_output = None


def render_center_panel(col):
    """Render the export preview + export generation system."""
    with col:
        st.header("📝 Final Document Preview", divider="gray")

        # ------------------------------------------------------
        # 1. Determine source draft for export
        # ------------------------------------------------------
        # We normalize ALL drafts into draft_text at Write tab time.
        draft = (
            st.session_state.get("draft_text")
            or st.session_state.get("draft_content")
            or ""
        ).strip()

        if not draft:
            st.info("Draft is empty. Nothing to export.")
            return

        if build_export_output is None:
            st.error("Export system not available.")
            return

        # ------------------------------------------------------
        # 2. Read Metadata from Right Panel
        # ------------------------------------------------------
        metadata = {
            "title": st.session_state.get("export_title", "Untitled Document"),
            "subtitle": st.session_state.get("export_subtitle", ""),
        }

        # ------------------------------------------------------
        # 3. Read included sections from Left Panel toggles
        # ------------------------------------------------------
        include_final = st.session_state.get("include_final", True)
        include_insights = st.session_state.get("include_insights", True)
        include_rippletruth = st.session_state.get("include_rippletruth", False)
        include_metrics = st.session_state.get("include_intention_metrics", False)

        sections = {
            "final_draft": draft if include_final else "",
            "insights": st.session_state.get("insights_text", "") if include_insights else "",
            "rippletruth": st.session_state.get("rippletruth_report", "") if include_rippletruth else "",
            "intent_metrics": st.session_state.get("intent_metrics", "") if include_metrics else "",
        }

        # ------------------------------------------------------
        # 4. Export Format (HTML / DOCX / Markdown)
        # ------------------------------------------------------
        export_format = st.session_state.get("export_format", "HTML")

        # ------------------------------------------------------
        # 5. LIVE PREVIEW ENGINE (Step 4 wiring)
        # ------------------------------------------------------
        preview_md = ""
        preview_html = ""

        try:
            preview_md, preview_html = build_export_output(sections, metadata)
            st.session_state.preview_markdown = preview_md
            st.session_state.preview_html = preview_html
        except Exception as e:
            st.error(f"Live preview failed: {e}")
            return

        # ------------------------------------------------------
        # 6. Manual Export Trigger (Download Files Panel)
        # ------------------------------------------------------
        generate = st.button("Generate Export", type="primary", use_container_width=True)

        if generate:
            try:
                md_output, html_output = build_export_output(sections, metadata)

                # Save into session_state for download panel
                st.session_state.export_markdown = md_output
                st.session_state.export_html = html_output

                st.success("Export generated successfully!")

            except Exception as e:
                st.error(f"Export generation failed: {e}")
                return

        # ------------------------------------------------------
        # 7. Display Preview (always live)
        # ------------------------------------------------------
        st.markdown("---")
        st.subheader("Preview")

        if preview_md:
            # Show Markdown preview in the center
            st.markdown(preview_md)
        else:
            st.info("Preview not available.")

        # Footer
        st.markdown("---")
        st.caption("Export tab — center panel engine (2025 modular architecture)")
