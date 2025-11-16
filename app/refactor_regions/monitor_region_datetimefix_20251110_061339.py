import streamlit as st

def render_monitor_panel():
    # ================== BEGIN MONITOR PANEL ====================
        # --- Article Status ---
        st.markdown("### Article Status")
        with st.container(border=True):
            st.write(f"**File:** {st.session_state.get('current_file', 'new-article.yaml')}")
            st.write(f"**Date/Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            st.write(f"**Author:** {st.session_state.get('author_name', 'Kevin Day')}")
            st.write(f"**Equation:** {st.session_state.get('selected_equation', 'None')}")
            st.caption("Auto-updates when scaffold changes")
    
        # --- RSS / Webhook Monitor ---
        st.markdown("### RSS / Webhook Monitor")  

# ================== END MONITOR PANEL ======================
