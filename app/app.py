import streamlit as st
import pathlib, yaml
from llm_client import LLMClient
from render import render_post, render_index

ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTICLES = ROOT / "articles"
OUTPUT = ROOT / "output"

st.set_page_config(page_title="RippleWriter", page_icon="🖋️", layout="centered")
st.title("RippleWriter – Local Preview")

# Sidebar: choose YAML
yamls = list(ARTICLES.glob("*.y*ml"))
choice = st.sidebar.selectbox("Select article YAML", yamls, format_func=lambda p: p.name)

with choice.open("r", encoding="utf-8") as f:
    y = yaml.safe_load(f)
st.subheader(y.get("title"))
st.caption(y.get("thesis"))

if st.button("Generate & Render"):
    llm = LLMClient()
    sections = llm.write_post_sections(y)
    meta = render_post(y, sections)
    render_index([meta])
    st.success(f"Rendered: {meta['slug']}")
    st.markdown(f"[Open post](../output/posts/{meta['slug']}.html)")
    st.markdown(f"[Open index](../output/index.html)")

st.info("Tip: Set OPENAI_API_KEY to use a live model; otherwise a mocked draft is produced.")