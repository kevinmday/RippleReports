import os
import sys
import pathlib
import subprocess
from typing import List, Dict, Any
import yaml
import streamlit as st
from datetime import date
from git import Repo, GitCommandError  # GitPython

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

# -------------------------
# Tab 1: Compose (YAML)
# -------------------------
with tab_compose:
    colL, colR = st.columns([2, 3])

    with colL:
        st.subheader("Drafts (YAML)")
        files = list_yaml_files()
        names = [f.name for f in files]
        choice = st.selectbox("Select draft", ["(new)"] + names, index=0)

        if choice == "(new)":
            new_name = st.text_input("New file name", value="new-article.yaml")
            create_btn = st.button("Create draft from template")
            if create_btn:
                p = ARTICLES_DIR / new_name
                if p.exists():
                    st.warning("File already exists.")
                else:
                    data = default_article()
                    save_yaml(p, data)
                    st.success(f"Created {p.name}. Select it from the list above.")
                    st.stop()
            st.info("Choose an existing draft from the dropdown, or create a new one.")
        else:
            current_path = ARTICLES_DIR / choice
            data = load_yaml(current_path)

            st.text_input("Title", value=data.get("title", ""), key="title")
            st.text_input("Author", value=data.get("author", "RippleWriter AI"), key="author")
            st.text_input("Slug", value=data.get("slug", ""), key="slug")
            st.text_area("Thesis", value=data.get("thesis", ""), height=100, key="thesis")
            st.text_input("Audience", value=data.get("audience", "general readers"), key="audience")
            st.text_input("Tone", value=data.get("tone", "plain-spoken"), key="tone")
            st.text_area("Outline (one per line)", value="\n".join(data.get("outline", [])), height=120, key="outline_text")

            if st.button("💾 Save YAML"):
                data["title"] = st.session_state["title"]
                data["author"] = st.session_state["author"]
                data["slug"] = st.session_state["slug"]
                data["thesis"] = st.session_state["thesis"]
                data["audience"] = st.session_state["audience"]
                data["tone"] = st.session_state["tone"]
                data["outline"] = [line.strip() for line in st.session_state["outline_text"].splitlines() if line.strip()]
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
        gen_cols = st.columns(2)
        with gen_cols[0]:
            if st.button("✍️ Generate sections with LLM"):
                try:
                    llm = LLMClient()
                    if mock_mode:
                        os.environ["RIPPLEWRITER_MOCK"] = "1"
                    elif openai_key:
                        os.environ["OPENAI_API_KEY"] = openai_key

                    to_send = default_article()
                    for k in ("title", "thesis", "audience", "tone", "outline", "claims"):
                        if k in data:
                            to_send[k] = data[k]

                    sections = llm.write_post_sections(to_send)
                    data["generated_sections"] = sections
                    save_yaml(current_path, data)
                    st.success("Sections generated and saved into YAML (generated_sections).")
                    st.json(sections)
                except Exception as e:
                    st.error(f"LLM error: {e}")

        with gen_cols[1]:
            if choice != "(new)":
                paths_arg = [str(ARTICLES_DIR / choice)]
            else:
                paths_arg = []
            if st.button("🛠️ Render this draft"):
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
    colA, colB = st.columns([2, 1])

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

        st.markdown("### Paste or drop screenshots (images)")
        st.caption("Click the area below, then press **Ctrl+V** to paste a screenshot. Drag & drop works too.")
        img_uploads = st.file_uploader(
            "Paste or drop images",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key="rw_image_uploader",
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

    # --- Paste/Drop screenshots (images) ---


st.markdown("### Paste or drop screenshots (images)")
st.caption("Click inside the gray box below, then press **Ctrl+V** to paste a screenshot directly from your clipboard. You can also drag & drop images.")

img_uploads = st.file_uploader(
    "📎 Paste or drop screenshots here",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=True,
    key="rw_image_pastebox",
    label_visibility="visible"   # forces the visible box
)

# Keep a session list so images pasted *before* 'Analyze & Draft' aren't lost
if "rw_images" not in st.session_state:
    st.session_state["rw_images"] = []

image_folder = ARTICLES_DIR / "images"
image_folder.mkdir(exist_ok=True)

# Save any pasted/dropped files immediately
if img_uploads:
    captured = []
    for f in img_uploads:
        # Use a safe name, write to disk, and record metadata
        safe_name = pathlib.Path(f.name).name
        dest = image_folder / safe_name
        dest.write_bytes(f.getbuffer())

        entry = {
            "filename": safe_name,
            "path": str(dest)
        }
        captured.append(entry)

    st.session_state["rw_images"].extend(captured)

    st.success(f"✅ Captured {len(captured)} image(s) from clipboard or drag/drop.")
    for e in captured:
        st.image(e["path"], width=160, caption=e["filename"])


    # ---- right: metadata + action ----
    with colB:
        st.write("Draft metadata")
        s_title  = st.text_input("Title", value="Untitled")
        s_author = st.text_input("Author", value="RippleWriter AI")
        s_aud    = st.text_input("Audience", value="general readers")
        s_tone   = st.text_input("Tone", value="plain-spoken")
        s_thesis = st.text_input("Thesis hint (optional)", value="")

        go_cols = st.columns([1, 1])
        with go_cols[0]:
            run_btn = st.button("🔎 Analyze & Draft")
        with go_cols[1]:
            save_as = st.text_input("Save as (YAML filename)", value="from-source.yaml")

    st.markdown("---")

    # ---- pipeline ----
    if run_btn:
        if not combined_text.strip():
            st.warning("Please paste text or drop at least one file.")
        else:
            with st.spinner("Analyzing and drafting…"):
                # 1) Build article from source text
                article = article_from_source_text(
                    combined_text,
                    title=s_title,
                    author=s_author,
                    thesis_hint=(s_thesis or None),
                    audience=s_aud,
                    tone=s_tone,
                    openai_key=(openai_key or None),
                    mock_mode=mock_mode,
                )

                # 2) Save images (if any) under articles/images/ and record entries
                if img_uploads:
                    image_folder = ARTICLES_DIR / "images"
                    image_folder.mkdir(exist_ok=True)

                    image_metadata: List[Dict[str, str]] = []
                    for img_file in img_uploads:
                        try:
                            img_path = image_folder / img_file.name
                            with open(img_path, "wb") as f:
                                f.write(img_file.getbuffer())
                            image_metadata.append(
                                {
                                    "filename": img_file.name,
                                    "path": str(img_path),
                                }
                            )
                        except Exception as e:
                            st.warning(f"⚠️ Could not save image {img_file.name}: {e}")

                    article["images"] = image_metadata

                # 3) Save YAML
                target = ARTICLES_DIR / save_as
                save_yaml(target, article)
                st.success(f"Draft saved to articles/{save_as}")

                # 4) Optional: preview sections
                if "generated_sections" in article:
                    with st.expander("Generated sections"):
                        st.json(article["generated_sections"])

                # 5) Render immediately
                env_vars: Dict[str, str] = {}
                if openai_key:
                    env_vars["OPENAI_API_KEY"] = openai_key
                if mock_mode:
                    env_vars["RIPPLEWRITER_MOCK"] = "1"

                proc = render_selected([str(target)], env_vars)
                if proc.returncode == 0:
                    st.success("Rendered successfully to /output.")
                    idx = OUTPUT_DIR / "index.html"
                    if idx.exists():
                        st.markdown(f"[Open site index (local file)]({idx.as_uri()})")
                else:
                    st.error("Render failed.")
                with st.expander("Render logs"):
                    st.code(proc.stdout + "\n" + proc.stderr)
