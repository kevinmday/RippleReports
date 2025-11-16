import streamlit as st

def render_controls_panel():
    # ================== BEGIN CONTROLS PANEL ==================
    commit_msg = st.sidebar.text_input("Commit message", value="Publish via RippleWriter Studio")
    branch = st.sidebar.text_input("Branch", value="main")

    # --- RippleWriter Studio Sidebar Guide (Streamlit Expander) ---
    with st.sidebar.expander("RippleWriter Studio Guide"):
        st.markdown("""
**Purpose:**  
RippleWriter Studio is your AI-assisted writing environment for composing, analyzing, and publishing articles powered by Intention Frameworks *(FILS, UCIP, RippleScore)*.  
It transforms structured YAML inputs into full narrative builds.

---

### Writing Flow
1. **Compose (YAML)** - create or select a draft and format  
2. **Source + Draft** - add your text; merges with YAML metadata  
3. **Meta-Analysis** - analyze tone, coherence, and RippleScore  
4. **Preview** - review and publish your rendered article  

---

### Key Controls
- **OpenAI API key** - enable live AI generation  
- **Mock mode** - safe offline testing  
- **Commit message** - Git label when publishing  
- **Branch** - defaults to `main`  
- **Open output folder** - opens the `/output` directory  
""")
    # ================== END CONTROLS PANEL ====================
