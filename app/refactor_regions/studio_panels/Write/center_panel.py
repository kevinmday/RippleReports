import streamlit as st
import yaml
import json

# ----------------------------------------------------------
# Write Engine: Center Panel
# ----------------------------------------------------------

def render_center_panel(col, fullscreen=False):
    """
    Core Write Engine panel.
    Renders inside either the fullscreen container or the center column.
    """

    with col:

        # ----------------------------------------------------------
        # Draft Editor Header
        # ----------------------------------------------------------
        st.markdown(
            """
            <h2 style="margin-bottom: 0px;">📝 Draft Editor</h2>
            <p style="margin-top: -6px; color: #aaa;">Write, generate, and structure your content.</p>
            """,
            unsafe_allow_html=True
        )

        # ----------------------------------------------------------
        # Session State Initialization
        # ----------------------------------------------------------
        if "draft_text" not in st.session_state:
            st.session_state.draft_text = ""

        if "yaml_text" not in st.session_state:
            st.session_state.yaml_text = ""

        if "selected_section" not in st.session_state:
            st.session_state.selected_section = None

        # ----------------------------------------------------------
        # Draft Editor (main text area)
        # ----------------------------------------------------------
        st.subheader("Draft Content")
        st.session_state.draft_text = st.text_area(
            "Write your content here:",
            value=st.session_state.draft_text,
            height=300
        )

        # ----------------------------------------------------------
        # Generation Tools
        # ----------------------------------------------------------
        st.markdown("---")
        st.subheader("Generation Tools")

        colA, colB, colC = st.columns([1, 1, 1])

        with colA:
            gen_structure = st.button("Generate Draft Structure")

        with colB:
            write_render = st.button("Write & Render Now")

        with colC:
            rewrite_section = st.button("Rewrite Selected Section")

        # ----------------------------------------------------------
        # ACTION: Generate Draft Structure
        # ----------------------------------------------------------
        if gen_structure:
            st.session_state.yaml_text = generate_structure(st.session_state.draft_text)
            st.success("Draft structure generated.")

        # ----------------------------------------------------------
        # ACTION: Write & Render Now
        # ----------------------------------------------------------
        if write_render:
            st.session_state.draft_text, st.session_state.yaml_text = write_and_render(
                st.session_state.draft_text
            )
            st.success("Draft written & rendered.")

        # ----------------------------------------------------------
        # ACTION: Rewrite Selected Section
        # ----------------------------------------------------------
        if rewrite_section:
            if st.session_state.selected_section:
                st.session_state.draft_text = rewrite_section_logic(
                    st.session_state.draft_text,
                    st.session_state.selected_section
                )
                st.success(f"Section '{st.session_state.selected_section}' rewritten.")
            else:
                st.warning("No section selected.")

        # ----------------------------------------------------------
        # YAML SECTION
        # ----------------------------------------------------------
        st.markdown("---")
        st.subheader("YAML (Optional)")

        st.session_state.yaml_text = st.text_area(
            "YAML View / Edit",
            value=st.session_state.yaml_text,
            height=250
        )

        # ----------------------------------------------------------
        # Footer
        # ----------------------------------------------------------
        st.markdown(
            """
            <p style="color: #666; font-size: 0.8rem; margin-top: 10px;">
            Write tab control center (2025 modular architecture)
            </p>
            """,
            unsafe_allow_html=True
        )


# ----------------------------------------------------------
# CORE LOGIC FUNCTIONS
# ----------------------------------------------------------

def generate_structure(draft_text: str) -> str:
    """
    Turn rough text into a structured YAML skeleton.
    This is where the content model actually begins.
    """

    # Placeholder logic — later connect to LLM
    structure = {
        "title": "Untitled Draft",
        "deck": "",
        "tags": [],
        "sections": [
            {
                "heading": "Introduction",
                "content": draft_text[:200] + "..."
            },
            {
                "heading": "Main Analysis",
                "content": "..."
            },
            {
                "heading": "Conclusion",
                "content": "..."
            }
        ]
    }

    return yaml.safe_dump(structure, sort_keys=False)


def write_and_render(draft_text: str):
    """
    Full write + render pipeline.
    Calls model (later replaced with real pipeline).
    """

    # Placeholder
    rendered = draft_text + "\n\n[Rendered output placeholder]"
    yaml_out = generate_structure(draft_text)

    return rendered, yaml_out


def rewrite_section_logic(draft_text: str, section_name: str) -> str:
    """
    Rewrite selected section with ripple-aware improvements.
    """

    # Placeholder rewrite logic
    updated = draft_text.replace(
        section_name,
        section_name + " (rewritten with RippleWriter logic)"
    )
    return updated
