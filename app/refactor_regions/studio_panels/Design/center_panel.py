# ==========================================================
#  RippleWriter Studio — Design Tab (Center Panel)
#  Draft Builder • YAML Templates • Metadata Editor
# ==========================================================

import streamlit as st
import yaml
from app.utils.yaml_tools import save_yaml, load_yaml, list_yaml_files
from datetime import date

# ----------------------------------------------------------
# Helper: Safe YAML loader/dumper
# ----------------------------------------------------------
def pretty_yaml(data: dict) -> str:
    return yaml.dump(data, sort_keys=False, allow_unicode=True)


# ----------------------------------------------------------
# Render Center Panel
# ----------------------------------------------------------
def render_design_center(colB):
    with colB:
        st.header("Design: YAML Draft Builder")

        # --------------------------------------------------
        # Draft Selector
        # --------------------------------------------------
        st.subheader("Select or Create Draft")

        try:
            drafts = list_yaml_files()
        except:
            drafts = []

        draft_choice = st.selectbox(
            "Choose Draft",
            ["(new)"] + drafts,
            key="design_center_draft_choice"
        )

        if draft_choice == "(new)":
            current_yaml = {}
        else:
            current_yaml = load_yaml(draft_choice)

        st.markdown("---")

        # --------------------------------------------------
        # Template Type Selector
        # --------------------------------------------------
        st.subheader("Template Type")

        template_type = st.selectbox(
            "Choose Template",
            [
                "None",
                "Academic Article",
                "Op-Ed",
                "Legal Brief",
                "Investigative Report",
                "RippleTruth Fact File",
                "MarketMind Narrative",
            ],
            key="design_template_type"
        )

        if st.button("Generate Template Structure", key="design_generate_template"):
            if template_type == "Academic Article":
                current_yaml = {
                    "title": "Untitled Academic Article",
                    "authors": ["Kevin Day"],
                    "date": str(date.today()),
                    "abstract": "",
                    "sections": [
                        {"title": "Introduction", "content": ""},
                        {"title": "Background", "content": ""},
                        {"title": "Methods", "content": ""},
                        {"title": "Results", "content": ""},
                        {"title": "Discussion", "content": ""},
                        {"title": "Conclusion", "content": ""}
                    ],
                    "references": [],
                }

            elif template_type == "Op-Ed":
                current_yaml = {
                    "title": "Untitled Op-Ed",
                    "deck": "",
                    "author": "Kevin Day",
                    "date": str(date.today()),
                    "argument": "",
                    "evidence": [],
                    "sections": [
                        {"title": "Opening Framing", "content": ""},
                        {"title": "Central Argument", "content": ""},
                        {"title": "Contrasting Viewpoints", "content": ""},
                        {"title": "Conclusion", "content": ""}
                    ],
                }

            elif template_type == "Legal Brief":
                current_yaml = {
                    "title": "Untitled Legal Brief",
                    "author": "Kevin Day",
                    "date": str(date.today()),
                    "jurisdiction": "",
                    "parties": "",
                    "issues": [],
                    "facts": "",
                    "arguments": [],
                    "conclusion": "",
                }

            elif template_type == "Investigative Report":
                current_yaml = {
                    "title": "Untitled Investigative Report",
                    "author": "Kevin Day",
                    "date": str(date.today()),
                    "lede": "",
                    "evidence_summary": "",
                    "timeline": [],
                    "sections": [],
                }

            elif template_type == "RippleTruth Fact File":
                current_yaml = {
                    "title": "RippleTruth Fact File",
                    "claim": "",
                    "verdict": "",
                    "supporting_evidence": [],
                    "sources": [],
                    "intention_equation": "",
                }

            elif template_type == "MarketMind Narrative":
                current_yaml = {
                    "title": "MarketMind Narrative",
                    "ticker": "",
                    "sector": "",
                    "intention_signals": {},
                    "fils_score": "",
                    "ucip_strength": "",
                    "sections": [
                        {"title": "Story Trigger", "content": ""},
                        {"title": "Intention Analysis", "content": ""},
                        {"title": "Market Impact", "content": ""},
                        {"title": "Forward Projections", "content": ""},
                    ],
                }

            st.success("Template structure created or updated.")

        st.markdown("---")

        # --------------------------------------------------
        # Metadata Editor
        # --------------------------------------------------
        st.subheader("Metadata")

        title = st.text_input("Title", value=current_yaml.get("title", ""))
        author = st.text_input("Author", value=current_yaml.get("author", "Kevin Day"))
        date_val = st.date_input("Date", value=date.today())

        current_yaml["title"] = title
        current_yaml["author"] = author
        current_yaml["date"] = str(date_val)

        st.markdown("---")

        # --------------------------------------------------
        # YAML Editor
        # --------------------------------------------------
        st.subheader("YAML Editor (Full Structure)")

        yaml_text = st.text_area(
            "Edit YAML",
            value=pretty_yaml(current_yaml),
            height=350,
            key="yaml_editor_design"
        )

        # Parse updated YAML
        try:
            current_yaml = yaml.safe_load(yaml_text) or {}
            yaml_valid = True
        except Exception as e:
            yaml_valid = False
            st.error(f"YAML syntax error: {e}")

        # --------------------------------------------------
        # Save Controls
        # --------------------------------------------------
        st.markdown("---")
        st.subheader("Save Draft")

        new_filename = st.text_input(
            "Save as filename (e.g., article.yaml)",
            value=draft_choice if draft_choice != "(new)" else "",
            key="design_save_name"
        )

        if st.button("💾 Save YAML Draft", key="design_save_yaml_btn"):
            if not new_filename.endswith(".yaml"):
                st.error("Filename must end with .yaml")
            else:
                save_yaml(new_filename, current_yaml)
                st.success(f"Draft saved as {new_filename}")

        # --------------------------------------------------
        # Footer
        # --------------------------------------------------
        st.caption("Design Center — Structured Draft Builder")
