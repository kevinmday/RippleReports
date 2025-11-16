# ==========================================================
#  RippleWriter Studio — Design Tab (Right Panel)
#  Context • Structural Diagnostics • Outline Preview
# ==========================================================

import streamlit as st
import yaml
from app.utils.yaml_tools import load_yaml
from datetime import datetime

# ----------------------------------------------------------
# Safety YAML parser
# ----------------------------------------------------------
def safe_parse_yaml(yaml_text: str):
    try:
        return yaml.safe_load(yaml_text), None
    except Exception as e:
        return None, str(e)


# ----------------------------------------------------------
# Render Right Panel
# ----------------------------------------------------------
def render_design_right(colC):
    with colC:
        st.header("Design Context Panel")

        st.caption("Structural insights, outline previews, and template diagnostics.")

        # ==================================================
        # PULL YAML FROM CENTER PANEL
        # ==================================================
        yaml_text = st.session_state.get("yaml_editor_design", "")
        parsed_yaml, yaml_error = safe_parse_yaml(yaml_text)

        if yaml_error:
            st.error("⚠️ YAML syntax issue detected.")
            st.code(yaml_error)
            return

        if not parsed_yaml:
            st.info("No YAML loaded yet. Begin building your draft in the center panel.")
            return

        # ==================================================
        # OUTLINE / SECTION MAP
        # ==================================================
        st.subheader("📑 Outline / Section Map")

        if "sections" in parsed_yaml and isinstance(parsed_yaml["sections"], list):
            for sec in parsed_yaml["sections"]:
                st.markdown(f"- **{sec.get('title', '(untitled section)')}**")
        else:
            st.caption("No sections defined in YAML scaffold.")

        st.divider()

        # ==================================================
        # METADATA DIAGNOSTICS
        # ==================================================
        st.subheader("🔍 Metadata Diagnostics")

        required_fields = ["title", "author", "date"]
        missing_fields = [f for f in required_fields if not parsed_yaml.get(f)]

        if missing_fields:
            st.error("⚠️ Missing required fields:")
            for field in missing_fields:
                st.markdown(f"- `{field}`")
        else:
            st.success("All core metadata fields present.")

        # --------------------------------------------------
        # Additional helpful metadata checks
        # --------------------------------------------------
        if "tags" in parsed_yaml and isinstance(parsed_yaml.get("tags"), list):
            st.markdown(f"**Tags:** {', '.join(parsed_yaml['tags'])}")
        else:
            st.caption("No tags found. Tags help classification later.")

        st.divider()

        # ==================================================
        # TEMPLATE COMPLETENESS CHECK
        # ==================================================
        st.subheader("🧩 Template Completeness")

        completeness_score = 0
        checks = [
            ("title", 20),
            ("author", 15),
            ("sections", 40),
            ("date", 10),
            ("argument", 15),   # op-ed templates
        ]

        for field, weight in checks:
            if field in parsed_yaml and parsed_yaml[field]:
                completeness_score += weight

        completeness_score = min(completeness_score, 100)

        st.progress(completeness_score, text=f"{completeness_score}% Complete")

        if completeness_score < 50:
            st.warning("Draft structure is still very early. Add sections or metadata.")
        elif completeness_score < 80:
            st.info("Draft forming well — add argument/evidence/sections to strengthen.")
        else:
            st.success("Draft structure ready for the Write tab.")

        st.divider()

        # ==================================================
        # EQUATION / INTENTION FRAMEWORK PREVIEW
        # ==================================================
        st.subheader("🧠 Intention Equation Preview")

        eq = parsed_yaml.get("intention_equation", "")

        if not eq:
            st.caption("No intention-equation selected yet.")
        else:
            st.info(f"Selected equation: **{eq}**")

            if eq.lower() in ["fils", "f.i.l.s", "intention field"]:
                st.markdown("""
                **FILS Equation Detected**  
                The FILS value influences:
                - argument strength  
                - narrative framing  
                - tension curves  
                - bias correction  
                """)
            elif "ucip" in eq.lower():
                st.markdown("""
                **UCIP Flow Selected**  
                UCIP influences:
                - signal ignition  
                - fractal transitions  
                - semantic drift  
                """)
            else:
                st.caption("Equation recognized but not yet mapped. Expand later.")

        st.divider()

        # ==================================================
        # EARLY RIPPLETRUTH CHECKS (STRUCTURAL ONLY)
        # ==================================================
        st.subheader("🛡️ RippleTruth Pre-Flight")

        flags = []

        if "sources" not in parsed_yaml or not parsed_yaml.get("sources"):
            flags.append("No sources listed — RippleTruth cannot evaluate claims yet.")

        if "evidence" in parsed_yaml and len(parsed_yaml["evidence"]) < 1:
            flags.append("Evidence list is empty — factual grounding is weak.")

        if "claim" in parsed_yaml and not parsed_yaml.get("claim"):
            flags.append("Claim field is empty (RippleTruth Fact File).")

        if flags:
            st.warning("⚠️ Issues found:")
            for f in flags:
                st.markdown(f"- {f}")
        else:
            st.success("RippleTruth is compatible with this draft structure.")

        st.divider()

        # ==================================================
        # TIMESTAMP / FOOTER
        # ==================================================
        st.caption(f"Diagnostics updated: {datetime.now().strftime('%H:%M:%S')}")
        st.caption("Design Context Panel — RippleWriter Studio 2025")
