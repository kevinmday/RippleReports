import os
import sys
import pathlib
import subprocess
from typing import List, Dict, Any
import time
import yaml
import streamlit as st
from datetime import date
from git import Repo, GitCommandError
from streamlit_paste_button import paste_image_button

# Ensure parent folder is on sys.path so we can import llm_client.py
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from llm_client import LLMClient

# Define key directories
ARTICLES_DIR = ROOT / "articles"
OUTPUT_DIR   = ROOT / "output"

st.set_page_config(page_title="RippleWriter Studio", page_icon="📝", layout="wide")

# ---------- helpers ----------
def list_yaml_files() -> List[pathlib.Path]:
    files: List[pathlib.Path] = []
    files.extend(ARTICLES_DIR.glob("*.yml"))
    files.extend(ARTICLES_DIR.glob("*.yaml"))
    return sorted(files)

def load_yaml(p: pathlib.Path) -> Dict[str, Any]:
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception as e:
        st.error(f"Failed to load YAML: {e}")
        return {}

def save_yaml(p: pathlib.Path, data: Dict[str, Any]) -> None:
    p.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")

def render_selected(paths: List[str], env_vars: Dict[str, str]) -> subprocess.CompletedProcess:
    # render.py already accepts file globs; we pass paths (or nothing to render all)
    cmd = [sys.executable, str(ROOT / "render.py")]
    cmd.extend(paths)
    env = os.environ.copy()
    env.update(env_vars or {})
    return subprocess.run(cmd, cwd=str(ROOT), env=env, capture_output=True, text=True)

def commit_and_push(repo_path: pathlib.Path, message: str, branch: str = "main") -> str:
    repo = Repo(str(repo_path))
    repo.git.add("-A")
    if repo.is_dirty():
        repo.index.commit(message)
    # ensure branch exists and is checked out
    try:
        repo.git.fetch("origin", branch)
    except GitCommandError:
        pass
    try:
        repo.git.checkout(branch)
    except GitCommandError:
        pass
    try:
        repo.git.push("origin", branch)
        return f"Pushed to origin/{branch} successfully."
    except GitCommandError as e:
        return f"Push failed: {e}"

def default_article() -> Dict[str, Any]:
    return {
        "title": "Untitled",
        "author": "RippleWriter AI",
        "date": str(date.today()),
        "slug": "untitled",
        "thesis": "One-line thesis of the op-ed.",
        "audience": "general readers",
        "tone": "plain-spoken",
        "outline": [
            "Lede: hook, why now",
            "Body: main points",
            "Counterpoints & limits",
            "Conclusion"
        ],
        "claims": [],
        "images": [],
        "publish": {"draft": False, "category": "oped", "tags": ["ripplewriter"]},
    }

def article_from_source_text(
    text: str,
    *,
    title: str = "Untitled",
    author: str = "RippleWriter AI",
    thesis_hint: str | None = None,
    audience: str = "general readers",
    tone: str = "plain-spoken",
    openai_key: str | None = None,
    mock_mode: bool = False,
) -> Dict[str, Any]:
    """
    Turn raw source text into an Article YAML dict.
    Uses LLMClient.write_post_sections() to produce lede/body/counterpoints/conclusion.
    """
    base = default_article()
    base["title"] = title or base["title"]
    base["author"] = author or base["author"]
    base["audience"] = audience or base["audience"]
    base["tone"] = tone or base["tone"]

    inferred_thesis = thesis_hint
    try:
        llm = LLMClient()
        if mock_mode:
            os.environ["RIPPLEWRITER_MOCK"] = "1"
        elif openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key

        if not inferred_thesis:
            inferred_thesis = llm.complete(
                system=(
                    "You infer concise op-ed theses. "
                    "Return a single sentence (<=25 words) that captures the central claim."
                ),
                user=f"Source:\n{text[:4000]}\n\nReturn only the thesis sentence."
            ).strip()

        base["thesis"] = inferred_thesis or base["thesis"]

        sections = llm.write_post_sections(
            {
                "title": base["title"],
                "thesis": base["thesis"],
                "audience": base["audience"],
                "tone": base["tone"],
                "outline": base.get("outline", []),
                "claims": [],
            }
        )
        base["generated_sections"] = sections

    except Exception as e:
        base["thesis"] = inferred_thesis or base["thesis"]
        base["generated_sections"] = {
            "lede": "Draft lede from source.",
            "body": text[:1200],
            "counterpoints": "List a few limitations and counterarguments.",
            "conclusion": "Close with next steps or call to action.",
        }
        st.warning(f"LLM error; used fallback sections. ({e})")

    base["slug"] = "".join(c.lower() if c.isalnum() else "-" for c in base["title"]).strip("-") or "untitled"
    return base

# --- Image ingest UI (paste + drag/drop) used ONLY on Source→Draft ---
def ui_image_ingest():
    st.markdown("### Paste or drop screenshots (images)")

    # Ensure session image list exists
    if "rw_images" not in st.session_state:
        st.session_state["rw_images"] = []

    st.caption(
        "1) Click the button below to focus it, then press **Ctrl+V** to paste from your clipboard. "
        "2) Or drag & drop image files into the box underneath."
    )

    # Clipboard paste
    _res = paste_image_button(label="📌 Paste image from clipboard", key="rw_pastebtn")
    pasted_img = None
    try:
        if _res is not None and getattr(_res, "image_data", None) is not None:
            pasted_img = _res.image_data  # wrapper case
    except Exception:
        if _res is not None:
            pasted_img = _res  # direct PIL.Image

    if pasted_img is not None:
        images_dir = ARTICLES_DIR / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        fname = f"pasted_{int(time.time())}.png"
        save_path = images_dir / fname
        pasted_img.save(save_path, format="PNG")
        st.session_state["rw_images"].append({"filename": fname, "path": str(save_path)})
        st.success(f"📸 Pasted image saved → articles/images/{fname}")
        st.image(pasted_img, width=160, caption=fname)

    st.markdown("---")

    # Drag & drop uploader
    st.caption("Or drag & drop image files (PNG/JPG/WEBP) below, or click **Browse files**.")
    img_uploads = st.file_uploader(
        "Drag and drop files here",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
        key="rw_image_drop",
        label_visibility="visible",
    )

    if img_uploads:
        captured = []
        images_dir = ARTICLES_DIR / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        for f in img_uploads:
            try:
                safe = pathlib.Path(f.name).name
                dest = images_dir / safe
                dest.write_bytes(f.getbuffer())
                captured.append({"filename": safe, "path": str(dest)})
            except Exception as e:
                st.warning(f"⚠️ Could not save image {f.name}: {e}")
        if captured:
            st.session_state["rw_images"].extend(captured)
            st.success(f"✅ Saved {len(captured)} image(s).")
            for e in captured:
                st.image(e["path"], width=160, caption=e["filename"])

# ---------- load YAML format templates ----------
FORMATS_FILE = ROOT / "config" / "formats.yaml"

def load_format_templates() -> Dict[str, Any]:
    if not FORMATS_FILE.exists():
        st.warning("⚠️ No format templates found in /config/formats.yaml")
        return {}
    try:
        return yaml.safe_load(FORMATS_FILE.read_text(encoding="utf-8")) or {}
    except Exception as e:
        st.error(f"Error reading formats.yaml: {e}")
        return {}

FORMAT_TEMPLATES = load_format_templates()

# ---------- sidebar ----------
st.sidebar.header("RippleWriter Studio")
openai_key = st.sidebar.text_input("OpenAI API key (optional)", type="password")
mock_mode = st.sidebar.checkbox("Mock mode (no API calls)", value=not bool(openai_key))
commit_msg = st.sidebar.text_input("Commit message", value="Publish via RippleWriter Studio")
branch = st.sidebar.text_input("Branch", value="main")

st.sidebar.markdown("---")
st.sidebar.caption("Repo: " + str(ROOT))
if st.sidebar.button("Open output folder"):
    st.sidebar.write(str(OUTPUT_DIR))

# ---------- main UI ----------
st.title("📝 RippleWriter Studio")

tab_compose, tab_source = st.tabs(["Compose (YAML)", "Source → Draft"])

# Tab 1: Compose (YAML)
# -------------------------
with tab_compose:
    colL, colR = st.columns([2, 3])

    with colL:
        st.subheader("Drafts (YAML)")

        # Always have a data dict so we don't reference-before-assign
        data: Dict[str, Any] = {}

        files = list_yaml_files()
        names = [f.name for f in files]
        choice = st.selectbox("Select draft", ["(new)"] + names, index=0)

        # ---- shared option lists (used for new + existing) ----
        format_options = [
            "Op-Ed", "Academic Paper", "Technical Report", "Press Release",
            "Social Media Post", "Legal Brief", "Lesson Plan",
            "Engineering Design Doc", "Zoology Field Note",
            "Dissertation Proposal", "Product Spec", "Grant Proposal"
        ]
        intention_options = [
            "None",
            "Clarity × Credibility × Evidence",
            "Problem → Insight → Outcome",
            "Risk–Reward Matrix",
            "Causal Chain",
            "5W1H",
            "Narrative Arc (Setup → Conflict → Resolution)"
        ]

        if choice == "(new)":
            new_name = st.text_input("New file name", value="new-article.yaml")

            # NEW: format & intention equation for new drafts
            new_format = st.selectbox(
                "Format",
                format_options,
                index=0,
                help="Choose the document pattern to prefill structure/expectations."
            )
            new_equation = st.selectbox(
                "Intention Equation",
                intention_options,
                index=0,
                help="Pick the intention framework to apply later in meta-analysis."
            )

            create_btn = st.button("Create draft from template")
            if create_btn:
                p = ARTICLES_DIR / new_name
                if p.exists():
                    st.warning("File already exists.")
                else:
                    payload = default_article()
                    payload["format"] = new_format
                    payload["intention_equation"] = new_equation
                    save_yaml(p, payload)
                    st.success(f"Created {p.name}. Select it from the list above.")
                    st.stop()

            st.info("Choose an existing draft from the dropdown, or create a new one.")

        else:
            current_path = ARTICLES_DIR / choice
            data = load_yaml(current_path)

            # Existing draft fields
            st.text_input("Title", value=data.get("title", ""), key="title")
            st.text_input("Author", value=data.get("author", "RippleWriter AI"), key="author")
            st.text_input("Slug", value=data.get("slug", ""), key="slug")
            st.text_area("Thesis", value=data.get("thesis", ""), height=100, key="thesis")
            st.text_input("Audience", value=data.get("audience", "general readers"), key="audience")
            st.text_input("Tone", value=data.get("tone", "plain-spoken"), key="tone")
            st.text_area(
                "Outline (one per line)",
                value="\n".join(data.get("outline", [])),
                height=120,
                key="outline_text"
            )

            # NEW: format & intention equation for existing drafts
            cur_format = data.get("format", format_options[0])
            cur_equation = data.get("intention_equation", intention_options[0])
            data["format"] = st.selectbox(
                "Format",
                format_options,
                index=max(0, format_options.index(cur_format) if cur_format in format_options else 0),
                key="format_select",
                help="Document pattern used for this draft."
            )
            data["intention_equation"] = st.selectbox(
                "Intention Equation",
                intention_options,
                index=max(0, intention_options.index(cur_equation) if cur_equation in intention_options else 0),
                key="intention_select",
                help="Intention framework to guide meta-analysis."
            )

            if st.button("💾 Save YAML"):
                data["title"] = st.session_state["title"]
                data["author"] = st.session_state["author"]
                data["slug"] = st.session_state["slug"]
                data["thesis"] = st.session_state["thesis"]
                data["audience"] = st.session_state["audience"]
                data["tone"] = st.session_state["tone"]
                data["outline"] = [
                    line.strip() for line in st.session_state["outline_text"].splitlines() if line.strip()
                ]
                # keep / backfill standard fields
                for k in ("claims", "images", "publish", "date"):
                    if k not in data:
                        if k == "publish":
                            data[k] = {"draft": False, "category": "oped", "tags": ["ripplewriter"]}
                        else:
                            data[k] = [] if k in ("claims", "images") else str(date.today())

                save_yaml(current_path, data)
                st.success("Saved.")

        st.markdown("---")
        st.subheader("Assistant")

        # Generate sections (only if a draft is open)
        gen_cols = st.columns(2)
        with gen_cols[0]:
            if st.button("✍️ Generate sections with LLM", disabled=(choice == "(new)")):
                try:
                    llm = LLMClient()
                    if mock_mode:
                        os.environ["RIPPLEWRITER_MOCK"] = "1"
                    elif openai_key:
                        os.environ["OPENAI_API_KEY"] = openai_key

                    to_send = default_article()
                    # Only copy keys present in the currently loaded draft
                    for k in ("title", "thesis", "audience", "tone", "outline", "claims",
                              "format", "intention_equation"):
                        if k in data:
                            to_send[k] = data[k]

                    sections = llm.write_post_sections(to_send)
                    data["generated_sections"] = sections
                    if choice != "(new)":
                        save_yaml(ARTICLES_DIR / choice, data)
                    st.success("Sections generated and saved into YAML (generated_sections).")
                    st.json(sections)
                except Exception as e:
                    st.error(f"LLM error: {e}")

        with gen_cols[1]:
            # If no specific file selected, render all articles
            paths_arg = [str(ARTICLES_DIR / choice)] if choice != "(new)" else []
            if st.button("🛠️ Render this draft", disabled=(choice == "(new)")):
                env_vars = {}
                if openai_key:
                    env_vars["OPENAI_API_KEY"] = openai_key
                if mock_mode:
                    env_vars["RIPPLEWRITER_MOCK"] = "1"

                proc = render_selected(paths_arg, env_vars)
                if proc.returncode == 0:
                    st.success("Rendered successfully to /output.")
                else:
                    st.error("Render failed.")
                with st.expander("Render logs"):
                    st.code(proc.stdout + "\n" + proc.stderr)

    with colR:
        st.subheader("Preview (latest build)")
        if OUTPUT_DIR.exists():
            idx = OUTPUT_DIR / "index.html"
            if idx.exists():
                st.markdown(f"[Open site index (local file)]({idx.as_uri()})")
        st.write("After rendering, find your pages in `/output`. The GitHub Pages site will update after you push.")

        st.markdown("---")
        st.subheader("Commit & Push")
        st.caption("This stages everything (including /output), commits, and pushes to origin.")
        if st.button("🚀 Commit & Push"):
            try:
                msg = commit_msg or "Publish via RippleWriter Studio"
                result = commit_and_push(ROOT, msg, branch=branch)
                st.success(result)
            except Exception as e:
                st.error(f"Git push failed: {e}")
                st.info("If this is the first push on this machine, make sure you’re signed in to Git and have permission to push (Git Credential Manager will usually prompt on Windows).")

# -------------------------
# Tab 2: Source → Draft
# -------------------------
with tab_source:
    st.subheader("Source → Draft (paste or drop files)")
    colA, colB = st.columns([2, 1])  # keep colB for future metadata/actions

    # ---- left: inputs ----
    with colA:
        paste_text = st.text_area(
            "Paste source text (notes, transcript, links, etc.)",
            height=240,
            placeholder="Paste raw material here…",
        )

        files_up = st.file_uploader(
            "Or drop text files (txt, md) — contents are concatenated",
            type=["txt", "md"],
            accept_multiple_files=True,
        )

        # Build combined text from paste + files
        file_texts: List[str] = []
        if files_up:
            for f in files_up:
                try:
                    file_texts.append(f.read().decode("utf-8", errors="ignore"))
                except Exception:
                    pass
        combined_text = "\n\n".join([t for t in [paste_text] + file_texts if t])

        # 🔽 Single, unified image ingest UI (paste + drag/drop)
        ui_image_ingest()


 
 