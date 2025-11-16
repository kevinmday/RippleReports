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
#from streamlit_paste_button import paste_image_button
import streamlit.components.v1 as components
# --- Compact layout (reduce top padding + hide Streamlit header/footer) ---
from datetime import datetime
import streamlit as st

st.set_page_config(
    page_title="RippleWriter Studio",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Compact vertical layout adjustments ---
st.markdown("""
    <style>
        /* Reduce top padding above the main block */
        div.block-container {
            padding-top: 0.5rem;
        }

        /* Tighten spacing between sections */
        .stSelectbox, .stMarkdown, .stTextInput, .stButton {
            margin-bottom: 0.5rem !important;
        }

        /* Optional: compress large empty vertical gaps */
        section.main > div {
            padding-top: 0.25rem;
            padding-bottom: 0.25rem;
        }
    </style>
""", unsafe_allow_html=True)

def render_right_sidebar(tab_name="main"):
    """Render shared right column elements across all tabs."""
# --- PANELS: MONITOR ---
render_monitor_panel()
# --- END MONITOR PANEL ---
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
    with st.container(border=True, height=250):
        if "rss_log" not in st.session_state:
            st.session_state["rss_log"] = ["[system] waiting for RSS/webhook updates..."]

        for msg in st.session_state["rss_log"][-10:]:
            st.markdown(f"- {msg}")

        # --- Refresh Feed Button ---
    
    import uuid
    refresh_key = f"refresh_feed_sidebar_{tab_name}_{st.session_state.get('active_tab', 'default')}_{uuid.uuid4().hex[:8]}"
    st.button("Refresh Feed", key=refresh_key)


st.markdown("""
    <style>
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 1rem !important;
    }

    header, footer {
        visibility: hidden;
    }

    /* Expand textarea width and height */
    textarea {
        width: 100% !important;
        min-width: 100% !important;
        height: 350px !important;
    }
    </style>
""", unsafe_allow_html=True)


import re
from pathlib import Path

# --- Define root path for RippleWriter ---
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent

# ---- Cross-tab session keys ----
CURRENT_DRAFT_KEY = "rw_current_draft"
CURRENT_EQ_KEY    = "rw_current_equation"

def ensure_session_defaults():
    if CURRENT_DRAFT_KEY not in st.session_state:
        st.session_state[CURRENT_DRAFT_KEY] = "(new)"
    if CURRENT_EQ_KEY not in st.session_state:
        st.session_state[CURRENT_EQ_KEY] = "none"  # or an id that exists in config/equations.yaml

ensure_session_defaults()

# Ensure parent folder is on sys.path so we can import llm_client.py
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# --- Define key directories ---
ARTICLES_DIR = ROOT / "articles"
OUTPUT_DIR = ROOT / "output"
CONFIG_DIR = ROOT / "config"

def get_draft_options() -> list[str]:
    files = ["(new)"]
    if (ROOT / "articles").exists():
        for p in sorted((ROOT / "articles").glob("*.yaml")):
            files.append(p.name)
    return files

def get_equation_options() -> list[tuple[str, str]]:
    cfg = yaml.safe_load((ROOT / "config" / "equations.yaml").read_text(encoding="utf-8")) or {}
    eqs = cfg.get("equations", []) or []
    # (id, display-name)
    return [(e["id"], e.get("name", e["id"])) for e in eqs]

def bind_draft_selectbox(label: str, key_prefix: str, help: str | None = None):
    opts = get_draft_options()
    cur  = st.session_state.get(CURRENT_DRAFT_KEY, "(new)")
    idx  = opts.index(cur) if cur in opts else 0

    def _on_change():
        st.session_state[CURRENT_DRAFT_KEY] = st.session_state[f"{key_prefix}_draft"]

    return st.selectbox(label, opts, index=idx, key=f"{key_prefix}_draft", on_change=_on_change, help=help)

def bind_equation_selectbox(label: str, key_prefix: str, help: str | None = None):
    pairs   = get_equation_options()           # [(id, name)]
    eq_ids  = [p[0] for p in pairs]
    eq_disp = [p[1] for p in pairs]
    cur     = st.session_state.get(CURRENT_EQ_KEY, eq_ids[0] if eq_ids else "none")
    idx     = eq_ids.index(cur) if cur in eq_ids else 0

    def _on_change():
        chosen_idx = st.session_state[f"{key_prefix}_eq_idx"]
        st.session_state[CURRENT_EQ_KEY] = eq_ids[chosen_idx]

    return st.selectbox(label, eq_disp, index=idx, key=f"{key_prefix}_eq_idx", on_change=_on_change, help=help)

def get_draft_filenames() -> list[str]:
    """Return list of YAML drafts in the /articles directory."""
    files = ["(new)"]
    if ARTICLES_DIR.exists():
        for p in sorted(ARTICLES_DIR.glob("*.yaml")):
            files.append(p.name)
    return files

# --- Import LLM client ---
from llm_client import LLMClient

# (inactive logic) Define key directories
ARTICLES_DIR = ROOT / "articles"
OUTPUT_DIR   = ROOT / "output"

# --- cross-tab state keys ---------------------------------
CURRENT_DRAFT_KEY = "rw_current_draft"

def set_current_draft(name: str) -> None:
    import streamlit as st
    st.session_state[CURRENT_DRAFT_KEY] = name

def get_current_draft(default: str = "(new)") -> str:
    import streamlit as st
    return st.session_state.get(CURRENT_DRAFT_KEY, default)

# --- Utility: list YAML drafts ---
def get_draft_filenames():
    """
    Return a list of YAML draft filenames in the /articles directory.
    Always includes '(new)' as the first option.
    """
    drafts = ["(new)"]
    if ARTICLES_DIR.exists():
        for path in sorted(ARTICLES_DIR.glob("*.yaml")):
            drafts.append(path.name)
    return drafts

# (inactive logic) Define brand assets
BRAND_DIR = ROOT / "app" / "static" / "branding"
LOGO_PNG  = BRAND_DIR / "ripple-logo.png"
LOGO_SVG  = BRAND_DIR / "ripple-logo.svg"

# at the top of file (near other constants)
CURRENT_DRAFT_KEY = "rw_current_draft"

# --- Compose (YAML) ---
draft_options = get_draft_filenames()  # e.g. ["(new)", "BlogPost.yaml", ...]
default_draft = st.session_state.get(CURRENT_DRAFT_KEY, "(new)")

#draft = st.selectbox(
#    "Choose an Article",
#    draft_options,
#    index=draft_options.index(default_draft) if default_draft in draft_options else 0,
#    key="compose_select_draft",
#)

draft = st.session_state.get(CURRENT_DRAFT_KEY, default_draft)

if st.session_state.get(CURRENT_DRAFT_KEY) != draft:
    st.session_state[CURRENT_DRAFT_KEY] = draft


# --- Branded header (logo + title) ---
def render_header():
    logo_exists = LOGO_PNG.exists()
    col_logo, col_title = st.columns([1, 12], vertical_alignment="center")
    with col_logo:
        if logo_exists:
            st.image(str(LOGO_PNG), width=180)
        else:
            st.markdown("### ")  # fallback
    with col_title:
        st.markdown(
            """
            <div style="display:flex;align-items:center;gap:0.5rem;">
              <h1 style="margin:0;">RippleWriter Studio</h1>
            </div>
            """,
            unsafe_allow_html=True,
        )

render_header()

# (cosmetic) ---------- helpers ----------
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
# ================== END COMPOSE PANEL ======================
    p.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")

# (cosmetic) ---------- equation loading helper ----------

def load_equations_yaml(p: pathlib.Path) -> Dict[str, Any]:
    """
    Load equations YAML and ALWAYS return {"equations": {...}}.
    Accepts:
      - {"equations": {NAME: {weights: {...}}}}
      - {NAME: {weights: {...}}}
      - [{"name": NAME, "weights": {...}}, ...]
    """
    try:
        raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    except Exception:
        return {"equations": {}}

    # Already in canonical shape
    if isinstance(raw, dict) and "equations" in raw and isinstance(raw["equations"], dict):
        return {"equations": raw["equations"]}

    # Dict of equations w/out the top-level "equations" key
    if isinstance(raw, dict):
        return {"equations": raw}

    # List form ? coerce into named dict
    if isinstance(raw, list):
        eqs: Dict[str, Any] = {}
        for i, item in enumerate(raw):
            if isinstance(item, dict):
                name = item.get("name") or f"eq_{i+1}"
                eqs[name] = item
        return {"equations": eqs}

    return {"equations": {}}


from typing import List, Dict, Any
from pathlib import Path
import yaml

ROOT         = Path(__file__).resolve().parent.parent
ARTICLES_DIR = ROOT / "articles"
CONFIG_DIR   = ROOT / "config"

def list_yaml_files() -> List[Path]:
    ARTICLES_DIR.mkdir(exist_ok=True)
    return sorted(ARTICLES_DIR.glob("*.yaml"))

def load_equations() -> List[Dict[str, Any]]:
    eq_path = CONFIG_DIR / "equations.yaml"
    with open(eq_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("equations", [])

#####def bind_draft_selectbox(label: str, key_prefix: str) -> None:
###    files   = list_yaml_files()
###    names   = [f.name for f in files]
###    current = st.session_state.get(CURRENT_DRAFT_KEY, "(new)")
###    choices = ["(new)"] + names
###    if current not in choices:
###        choices = ["(new)"] + sorted(set(names + [current]))
###    choice = st.selectbox(label, choices, index=choices.index(current), key=f"{key_prefix}_draft_sb")
###    st.session_state[CURRENT_DRAFT_KEY] = choice

def bind_equation_selectbox(label: str, key_prefix: str) -> None:
    eqs     = load_equations()
    options = [e["id"] for e in eqs] or ["none"]
    current = st.session_state.get(CURRENT_EQ_KEY, "none")
    if current not in options:
        options = [current] + options
    labels  = {e["id"]: f'{e["name"]} - {e.get("desc","")}'[:80] for e in eqs}
    shown   = [labels.get(opt, opt) for opt in options]
    idx     = options.index(current)
    sel     = st.selectbox(label, shown, index=idx, key=f"{key_prefix}_eq_sb")
    st.session_state[CURRENT_EQ_KEY] = options[shown.index(sel)]


def preview_yaml_box(data: Dict[str, Any], filename: str = "draft.yaml") -> None:
    """
    Show a YAML preview and a download button for the current in-memory draft.
    Safe to call even if `data` is empty.
    """
    try:
        yml_text = yaml.safe_dump(data or {}, sort_keys=False, allow_unicode=True)
    except Exception as e:
        st.warning(f"Could not serialize YAML for preview: {e}")
        yml_text = "# <serialization error>"

    st.markdown("#### YAML preview")
    st.code(yml_text, language="yaml")

    # Download as a file (no need to write to disk)
    st.download_button(
        label="Download YAML",
        data=yml_text.encode("utf-8"),
        file_name=filename,
        mime="text/yaml",
        use_container_width=True,
    )


# --- Equations helpers -------------------------------------------------

def normalize_equations_obj(eq_all: Any) -> Dict[str, Dict[str, Any]]:
    """
    Accepts multiple YAML shapes and returns a dict:
    { "EquationName": {"weights": {...}}, ... }
    """
    # Case A1: {"equations": {...}}   (already a dict)
    if isinstance(eq_all, dict) and isinstance(eq_all.get("equations"), dict):
        return eq_all["equations"]

    # Case A2: {"equations": [...]}   (list; normalize it)
    if isinstance(eq_all, dict) and isinstance(eq_all.get("equations"), list):
        return normalize_equations_obj(eq_all["equations"])

    # Case B: already a dict of equations
    if isinstance(eq_all, dict):
        return eq_all

    # Case C: list forms ? coerce to dict
    out: Dict[str, Dict[str, Any]] = {}
    if isinstance(eq_all, list):
        for item in eq_all:
            # [{id/name, weights}, ...]
            if isinstance(item, dict) and ("id" in item or "name" in item):
                key = str(item.get("id") or item.get("name"))
                out[key] = {"weights": item.get("weights", {})}
            # [{"EqName": {...}}]  OR [{"EqName": {"weights": {...}}}]
            elif isinstance(item, dict):
                for k, v in item.items():
                    if isinstance(v, dict):
                        out[str(k)] = v
    return out

# --- Intention meta guard (in-memory) ----------------------------------------
def ensure_meta_signals(
    data: Dict[str, Any],
    eq_path: pathlib.Path,
    selected_eq: str,
) -> Dict[str, Any]:
    """
    Enrich an in-memory YAML dict with intention meta:
      - Loads equations from eq_path and normalizes
      - Computes signals via extract_signals(data)
      - Applies weights from `selected_eq` (or equal weights if None)
      - Writes into data['meta'] = {signals, ripple_score, equation, weights}
      - Returns the updated dict (no file writes here)
    """
    # Ensure we have a dict to work with
    if not isinstance(data, dict):
        data = {}

    # Resolve which equation name to use (UI select > data['intention_equation'] > meta.equation)
    eq_name = (
        selected_eq
#         or data.get("intention_equation")
        or ((data.get("meta") or {}).get("equation"))
        or "none"
    )

    # Load equations via canonical loader (always returns {"equations": {...}} when possible)
    eq_raw = load_equations_yaml(eq_path)
    eq_dict: Dict[str, Dict[str, Any]] = {}

    if isinstance(eq_raw, dict):
        # Preferred canonical shape
        if isinstance(eq_raw.get("equations"), dict):
            eq_dict = eq_raw["equations"]
        else:
            # Be permissive: if it's already a mapping of equations, accept it
            if all(isinstance(v, dict) for v in eq_raw.values()):
                eq_dict = eq_raw

    # Compute normalized signals from current data
    signals: Dict[str, float] = extract_signals(data)

    # Choose weights (from chosen equation if present; fallback = equal weights)
    weights: Dict[str, float] = {}
    if isinstance(eq_dict, dict) and eq_name in eq_dict and isinstance(eq_dict[eq_name], dict):
        weights = (eq_dict[eq_name].get("weights") or {}) if isinstance(eq_dict[eq_name].get("weights"), dict) else {}
    if not weights:
        weights = {k: 1.0 for k in signals.keys()}

    # Compute score
    score = apply_equation(signals, weights)

    # Persist into the in-memory article dict
    meta = data.setdefault("meta", {})
    meta["signals"] = {k: float(v) for k, v in signals.items()}
    meta["ripple_score"] = float(score)
    meta["equation"] = str(eq_name)
    meta["weights"] = {k: float(v) for k, v in weights.items()}

    return data

def render_selected(paths: List[str], env_vars: Dict[str, str]) -> subprocess.CompletedProcess:
    # render.py already accepts file globs; we pass paths (or nothing to render all)
    cmd = [sys.executable, str(ROOT / "render.py")]
    cmd.extend(paths)
    env = os.environ.copy()
    env.update(env_vars or {})
    return subprocess.run(cmd, cwd=str(ROOT), env=env, capture_output=True, text=True)


# --- Output helpers ---------------------------------------------------------
def _guess_slug_from_yaml(data: Dict[str, Any]) -> str:
    # prefer explicit slug, else derive from title
    s = (data or {}).get("slug")
    if s:
        return "".join(c.lower() if c.isalnum() else "-" for c in s).strip("-")
    title = (data or {}).get("title", "") or "untitled"
    return "".join(c.lower() if c.isalnum() else "-" for c in title).strip("-")

def find_post_outputs(slug: str) -> tuple[pathlib.Path | None, pathlib.Path | None]:
    """Return (html_path, md_path) if present in /output/posts"""
    posts = OUTPUT_DIR / "posts"
    if not posts.exists():
        return None, None
    html = posts / f"{slug}.html"
    md   = posts / f"{slug}.md"
    return (html if html.exists() else None, md if md.exists() else None)

def write_render_refresh(choice: str | None,
                         data: Dict[str, Any],
                         openai_key: str | None,
                         mock_mode: bool) -> subprocess.CompletedProcess:
    """
    1) Generate sections with LLM based on current YAML (incl. intention_equation if present)
    2) Save YAML
    3) Render selected draft (or all if none)
    4) Return the render process so caller can show logs
    """
    llm = LLMClient()
    if mock_mode:
        os.environ["RIPPLEWRITER_MOCK"] = "1"
    elif openai_key:
        os.environ["OPENAI_API_KEY"] = openai_key

    to_send = default_article()
    for k in ("title", "thesis", "audience", "tone", "outline", "claims",
              "intention_equation", "format"):
        if k in data:
            to_send[k] = data[k]

    sections = llm.write_post_sections(to_send)
    data["generated_sections"] = sections

    if choice and choice != "(new)":
        save_yaml(ARTICLES_DIR / choice, data)

    env_vars = {}
    if openai_key:
        env_vars["OPENAI_API_KEY"] = openai_key
    if mock_mode:
        env_vars["RIPPLEWRITER_MOCK"] = "1"

    paths_arg = [str(ARTICLES_DIR / choice)] if (choice and choice != "(new)") else []
    return render_selected(paths_arg, env_vars)

# (cosmetic) -------- Inline Preview helpers --------------------------------------------
OUTPUT_DIR = (ROOT / "output").resolve()
POSTS_DIR = OUTPUT_DIR / "posts"

def _latest_post_html():
    """Return newest HTML in /output/posts or None."""
    if not POSTS_DIR.exists():
        return None
    htmls = sorted(POSTS_DIR.glob("*.html"), key=lambda p: p.stat().st_mtime, reverse=True)
    return htmls[0] if htmls else None

def _inject_base_href(html_text: str, base_uri: str) -> str:
    """Ensure relative links (css/img) work inside the preview iframe."""
    if re.search(r"<base[^>]*>", html_text, flags=re.I):
        return re.sub(r"<base[^>]*>", f"<base href='{base_uri}'>", html_text, flags=re.I)
    if re.search(r"(?i)<head>", html_text):
        return re.sub(r"(?i)<head>", f"<head><base href='{base_uri}'>", html_text, count=1)
    return f"<base href='{base_uri}'>\n{html_text}"

def load_html_for_preview(html_path: Path) -> str:
    html = html_path.read_text(encoding="utf-8")
    base_uri = OUTPUT_DIR.as_uri() + "/"
    return _inject_base_href(html, base_uri)
# (cosmetic) ---------------------------------------------------------------------------

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

# (cosmetic) ---------- path & preview helpers ----------

def _slugify(text: str) -> str:
    return "".join(c.lower() if c.isalnum() else "-" for c in (text or "")).strip("-") or "untitled"

def _guess_slug_from_yaml(data: Dict[str, Any]) -> str:
    # Prefer explicit slug; fallback to title-based slug
    slug = (data or {}).get("slug")
    if slug:
        return _slugify(slug)
    title = (data or {}).get("title", "untitled")
    return _slugify(title)

def find_post_outputs(slug: str):
    """Return (html_path, md_path) for a given slug inside /output/posts/."""
    posts_dir = OUTPUT_DIR / "posts"
    html = posts_dir / f"{slug}.html"
    md   = posts_dir / f"{slug}.md"
    return (html if html.exists() else None, md if md.exists() else None)

def expected_output_html(choice: str | None, data: Dict[str, Any]):
    """
    Best-guess path to the rendered HTML for the current draft.
    If a specific post HTML exists, return that; otherwise fall back to index.html.
    """
    try:
        slug = _guess_slug_from_yaml(data)
        html, _md = find_post_outputs(slug)
        if html:
            return html
    except Exception:
        pass
    # Fallback to site index so the preview still shows *something*
    return OUTPUT_DIR / "index.html"

# (cosmetic) ---------- Ripple score: load equations, extract signals, score ----------

def _safe_len(x) -> int:
    try:
        return len(x)
    except Exception:
        return 0

def extract_sections(article: Dict[str, Any]) -> Dict[str, str]:
    """Return a dict of key text buckets to analyze."""
    txt = []
    # Use generated sections if present; fallback to outline + thesis
    gen = article.get("generated_sections", {})
    for k in ("lede", "body", "counterpoints", "conclusion"):
        v = gen.get(k, "")
        if isinstance(v, list):  # some LLMs may return arrays
            v = "\n".join(v)
        txt.append(v or "")
    thesis = article.get("thesis", "")
    outline = "\n".join(article.get("outline", []))
    return {
        "thesis": thesis or "",
        "outline": outline or "",
        "content": "\n\n".join(txt).strip(),
    }

def _count_bullets(s: str) -> int:
    # quick proxy for structure/clarity: leading hyphens/numbers
    return sum(1 for line in s.splitlines() if line.strip().startswith(("-", "*", "*", "1.", "2.", "3.")))

def _count_citations(s: str) -> int:
    # quick proxy for evidence: markdown/linky bits
    hints = ["http://", "https://", "[", "](", "doi:", "arxiv.org", "source", "citation", "references"]
    return sum(s.lower().count(h) for h in hints)

def _count_unique_terms(s: str) -> int:
    import re
    toks = [t.lower() for t in re.findall(r"[a-zA-Z]{4,}", s)]
    return len(set(toks))

def extract_signals(article: Dict[str, Any]) -> Dict[str, float]:
    """
    Very light heuristics to get us started.
    Replace with your proper analyzers later (LLM checks, classifiers, etc.).
    """
    sec = extract_sections(article)
    content = sec["content"]
    thesis = sec["thesis"]
    outline = sec["outline"]

    words = _safe_len(content.split())
    coherence = min(1.0, (words / 800.0))  # longer ? more developed (proxy)
    evidence  = min(1.0, (_count_citations(content) / 6.0))
    clarity   = min(1.0, (_count_bullets(outline) / 8.0))
    novelty   = min(1.0, (_count_unique_terms(content) / 800.0))
    # sentiment proxy: neutral-ish = good; we'll keep 0.7 baseline for now
    sentiment = 0.7

    return {
        "coherence": coherence,
        "evidence": evidence,
        "novelty": novelty,
        "clarity": clarity,
        "sentiment": sentiment,
    }

def apply_equation(signals: Dict[str, float], weights: Dict[str, float]) -> float:
    # weighted sum over shared keys, then clamp to [0, 1]
    num = 0.0
    den = 0.0
    for k, w in weights.items():
        v = float(signals.get(k, 0.0))
        num += w * v
        den += abs(w)
    if den == 0:
        return 0.0
    return max(0.0, min(1.0, num / den))

def _guess_slug_from_yaml(article: Dict[str, Any]) -> str:
    slug = (article.get("slug") or article.get("title", "")).strip()
    if not slug:
        return "untitled"
    return "".join(c.lower() if c.isalnum() else "-" for c in slug).strip("-") or "untitled"


def _recent_built_posts(n: int = 10) -> list[pathlib.Path]:
    posts_dir = OUTPUT_DIR / "posts"
    if not posts_dir.exists():
        return []
    posts = list(posts_dir.glob("*.html"))
    return sorted(posts, key=lambda p: p.stat().st_mtime, reverse=True)[:n]

def _guess_output_html_for_draft(data: Dict[str, Any], current_choice: str | None) -> pathlib.Path | None:
    """Prefer /output/posts/<slug>.html if it exists; otherwise latest built page."""
    slug = (data or {}).get("slug")
    if slug:
        p = OUTPUT_DIR / "posts" / f"{slug}.html"
        if p.exists():
            return p
    # fallback to newest post
    recent = _recent_built_posts(1)
    return recent[0] if recent else None

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

# --- Image ingest UI (paste + drag/drop) used ONLY on Source?Draft ---
def ui_image_ingest():
    st.markdown("### Paste or drop screenshots (images)")

    # Ensure session image list exists
    if "rw_images" not in st.session_state:
        st.session_state["rw_images"] = []

    st.caption(
        "1) Click the button below to focus it, then press **Ctrl+V** to paste from your clipboard. "
        "2) Or drag & drop image files into the box underneath."
    )

    
    # Clipboard paste (disabled paste_image_button on Cloud)
    _res = None
    pasted_img = None
    # placeholder skip: clipboard paste temporarily disabled
    try:
        pass
    except Exception:
        pass

    # Clipboard paste
    #_res = paste_image_button(label="Paste image from clipboard", key="rw_pastebtn")
    #pasted_img = None
    #try:
# (inactive logic) #    if _res is not None and getattr(_res, "image_data", None) is not None:
    #        pasted_img = _res.image_data  # wrapper case
    #except Exception:
# (inactive logic) #    if _res is not None:
    #        pasted_img = _res  # direct PIL.Image

    if pasted_img is not None:
        images_dir = ARTICLES_DIR / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        fname = f"pasted_{int(time.time())}.png"
        save_path = images_dir / fname
        pasted_img.save(save_path, format="PNG")
        st.session_state["rw_images"].append({"filename": fname, "path": str(save_path)})
        st.success(f"Pasted image saved ? articles/images/{fname}")
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
                st.warning(f"Could not save image {f.name}: {e}")
        if captured:
            st.session_state["rw_images"].extend(captured)
            st.success(f"? Saved {len(captured)} image(s).")
            for e in captured:
                st.image(e["path"], width=160, caption=e["filename"])

# (cosmetic) ---------- load YAML format templates ----------
# (inactive logic) FORMATS_FILE = ROOT / "config" / "formats.yaml"

def load_format_templates() -> Dict[str, Any]:
    if not FORMATS_FILE.exists():
        st.warning("No format templates found in /config/formats.yaml")
        return {}
    try:
        return yaml.safe_load(FORMATS_FILE.read_text(encoding="utf-8")) or {}
    except Exception as e:
        st.error(f"Error reading formats.yaml: {e}")
        return {}

# (inactive logic) FORMAT_TEMPLATES = load_format_templates()

# (cosmetic) ---------- intention / meta-analysis helpers ----------

CONFIG_DIR = ROOT / "config"
EQUATIONS_PATH = CONFIG_DIR / "equations.yaml"

def load_equations() -> list[dict[str, Any]]:
    try:
        if EQUATIONS_PATH.exists():
            cfg = yaml.safe_load(EQUATIONS_PATH.read_text(encoding="utf-8")) or {}
            eqs = cfg.get("equations", [])
            for e in eqs:
                e.setdefault("id", e.get("name", "unnamed").lower().replace(" ", "-"))
                e.setdefault("name", e.get("id", "Unnamed").title())
                e.setdefault("desc", "")
                e.setdefault("weights", {})
            return eqs
    except Exception as e:
        st.warning(f"Could not load equations.yaml: {e}")
    return [{"id": "none", "name": "None", "desc": "", "weights": {}}]


def extract_claims_for_scoring(article: dict[str, Any]) -> list[str]:
    claims = [c for c in article.get("claims", []) if isinstance(c, str) and c.strip()]
    if not claims:
        outline = article.get("outline", [])
        claims.extend([o for o in outline if isinstance(o, str) and o.strip()])
    if not claims:
        gs = article.get("generated_sections", {})
        for k in ("lede", "body", "counterpoints", "conclusion"):
            txt = gs.get(k, "")
            if isinstance(txt, str) and txt.strip():
                claims.extend([s.strip() for s in txt.split(". ") if len(s.strip()) > 40][:3])
    return claims[:8]


def _score_signal(text: str, kind: str) -> float:
    if not text:
        return 0.0
    t = text.lower()
    if kind == "coherence":
        dots = t.count("...") + t.count("")
        return max(0.0, 1.0 - min(1.0, dots / 3.0))
    if kind == "evidence":
        digits = sum(ch.isdigit() for ch in t)
        refs = t.count("http") + t.count("doi") + t.count("source:")
        return min(1.0, (digits * 0.02) + (refs * 0.25))
    if kind == "novelty":
        toks = [w.strip(".,:;!?'\"()[]") for w in t.split()]
        uniq = len(set(toks))
        return min(1.0, uniq / max(8, len(toks)))
    if kind == "clarity":
        sents = [s for s in t.replace("?", ".").replace("!", ".").split(".") if s.strip()]
        if not sents:
            return 0.5
        lengths = [len(s.split()) for s in sents]
        avg = sum(lengths) / len(lengths)
        if 12 <= avg <= 22:
            return 1.0
        return max(0.0, 1.0 - (abs(avg - 17) / 25.0))
    if kind == "sentiment":
        pos = sum(w in t for w in ["excellent", "good", "clear", "strong", "improve", "win"])
        neg = sum(w in t for w in ["bad", "poor", "unclear", "weak", "worse", "lose"])
        total = pos + neg
        if total == 0:
            return 0.6
        return max(0.0, min(1.0, (pos - neg) / total * 0.5 + 0.5))
    return 0.5


def compute_intention_scores(article: dict[str, Any], equation: dict[str, Any]) -> dict[str, Any]:
    text_blob = " ".join(extract_claims_for_scoring(article))[:8000]
    weights = equation.get("weights", {})
    signals = {k: _score_signal(text_blob, k) for k in ("coherence", "evidence", "novelty", "clarity", "sentiment")}
    overall = 0.0
    total_w = 0.0
    for k, w in weights.items():
        overall += signals.get(k, 0.0) * float(w)
        total_w += float(w)
    ripple_score = overall / total_w if total_w > 0 else 0.0
    return {"signals": signals, "ripple_score": ripple_score}


# (cosmetic) ---------- sidebar ----------
st.sidebar.header("RippleWriter Studio")
openai_key = st.sidebar.text_input("OpenAI API key (optional)", type="password")
mock_mode = st.sidebar.checkbox("Mock mode (no API calls)", value=not bool(openai_key))
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
# ================== END CONTROLS PANEL ====================

---

### What to Expect
1. Build and auto-save YAML structure  
2. Generate a rendered preview in `/output`  
3. Commit/push to GitHub if enabled  
4. Auto-update your live site via GitHub Pages  
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.caption("Repo: " + str(ROOT))
if st.sidebar.button("Open output folder"):
    st.sidebar.write(str(OUTPUT_DIR))

# (cosmetic) ---------- main UI ----------
tab_compose, tab_source, tab_meta, tab_preview = st.tabs(
    ["Compose", "Input", "Analyze", "Preview"]
)

# (cosmetic) ---------- Tab 2: Input ----------
with tab_source:
    col_main, col_side = st.columns([2, 1])

    with col_main:
        # your source upload UI, paste box, etc.
        st.text_area("Paste raw material here")

    with col_side:
        render_right_sidebar("input")

with tab_meta:
    col_main, col_side = st.columns([2, 1])
    with col_main:
        # meta-analysis logic here
        pass
    with col_side:
        render_right_sidebar("analyze")

with tab_preview:
    col_main, col_side = st.columns([2, 1])
    with col_main:
        # preview layout or article display
        pass
    with col_side:
        render_right_sidebar("preview")

# (cosmetic) -------------------------
# Tab 1: Compose (YAML)
# (cosmetic) -------------------------

current_draft = st.session_state[CURRENT_DRAFT_KEY]
current_eq_id = st.session_state[CURRENT_EQ_KEY]

# (cosmetic) ---------- Compose Tab Layout ----------
colL, colR = st.columns([3.5, 1])

# --- Lock right column to top persistently ---
st.markdown("""
    <style>
    /* Target the Compose tab's two-column layout */
    div[data-testid="stVerticalBlock"]:has(> div > div > div > div[data-testid="stVerticalBlock"] h3:contains('Article Status')) {
        align-self: flex-start !important;
        justify-content: flex-start !important;
        margin-top: 0 !important;
        position: sticky !important;
        top: 0 !important;
        z-index: 2 !important;
    }

    /* Prevent Streamlit reflow from overriding this */
    [data-testid="stVerticalBlock"] {
        transition: none !important;
    }
    </style>
""", unsafe_allow_html=True)

with colL:
    st.subheader("Create Scaffold")

    # Simplified single UI
    files = list_yaml_files()
    names = [f.name for f in files]

    draft_choice = st.selectbox(
        "Choose Article Type (YAML)",
        ["(new)"] + names,
#         index=(["(new)"] + names).index(st.session_state.get("rw_current_draft", "(new)")),
        key="rw_select_compose",
    )

    #filename = st.text_input("Choose File Name", value="new-article.yaml", key="compose_filename")
# (inactive logic) #format_choice = st.selectbox("Choose Article Format", ["Op-Ed", "Feature", "Essay", "Report"], key="compose_format")

    #eq_choice = st.selectbox(
    #    "Choose Intention Equation (Optional)",
    #    ["None", "UCIP", "FILS", "Bell-Drake Threshold"],
    #    key="eq_choice_compose",
    #    help="Pick the intention framework to apply later in meta-analysis."
    #)

# (inactive logic) #st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)

    # One button only
    
# Right-hand column (status + monitors)
with colR:
    render_right_sidebar("compose")



# Ensure format_options exists
# (inactive logic) format_options = ["Op-Ed", "Feature", "Essay", "Report"]
# # cur_format = data.get("format", format_options[0])

# Ensure intention_options exists
intention_options = [
    "None",
    "Cosmic Intention Postulate (CIP)",
    "Unified Cosmic Intention Postulate (UCIP)",
    "Future Intention Likelihood Scale (FILS)",
    "RippleTruth Equation",
    "Custom",
]

# Ensure intention_options exists
#intention_options = [
#    "None",
#    "Cosmic Intention Postulate (CIP)",
#    "Unified Cosmic Intention Postulate (UCIP)",
#    "Future Intention Likelihood Scale (FILS)",
#    "RippleTruth Equation",
#    "Custom"
#]

# cur_equation = data.get("intention_equation", intention_options[0])

# (inactive logic) Format & intention equation for existing drafts
# # cur_format = data.get("format", format_options[0])
# cur_equation = data.get("intention_equation", intention_options[0])
# data["format"] = st.selectbox(
#                 "Format",
# (inactive logic) format_options,
#                 index=max(0, format_options.index(cur_format) if cur_format in format_options else 0),
#                 key="format_select",
#                help="Document pattern used for this draft."
#            )
# Ensure 'data' exists before assigning to it

if "data" not in locals():
    data = {}

# Intention Equation selector
data["intention_equation"] = st.selectbox(
    "Intention Equation",
    intention_options,
    key="intention_select",
    help="Intention framework to guide meta-analysis."
)

# Ensure default session_state keys exist
for key in ["title", "author", "slug", "thesis", "audience", "tone", "outline_text"]:
    if key not in st.session_state:
        st.session_state[key] = ""

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

# (inactive logic) save_yaml(current_path, data)
# (inactive logic) st.success("Saved.")

st.markdown("---")
st.subheader("AI Assistant")

        # Generate sections (only if a draft is open)
gen_cols = st.columns(2)
# Ensure 'choice' exists before using it in the button logic
choice = st.session_state.get("choice", "(new)")

with gen_cols[0]:
            if st.button("Generate Article Sections with AI Help", disabled=(choice == "(new)")):
                try:
                    llm = LLMClient()
                    if mock_mode:
                        os.environ["RIPPLEWRITER_MOCK"] = "1"
                    elif openai_key:
                        os.environ["OPENAI_API_KEY"] = openai_key

                    to_send = default_article()
                    # Only copy keys present in the currently loaded draft
                    for k in ("title", "thesis", "audience", "tone", "outline", "claims"):
#                               "format", "intention_equation"):
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
# (inactive logic) # If no specific file selected, render all articles
            # paths_arg = [str(ARTICLES_DIR / choice)] if choice != "(new)" else []
# (inactive logic) # if st.button("Render this draft", disabled=(choice == "(new)")):
            #    env_vars = {}
# (inactive logic) #    if openai_key:
            #        env_vars["OPENAI_API_KEY"] = openai_key
# (inactive logic) #    if mock_mode:
            #        env_vars["RIPPLEWRITER_MOCK"] = "1"

            #    proc = render_selected(paths_arg, env_vars)
# (inactive logic) #    if proc.returncode == 0:
# (inactive logic) #        st.success("Rendered successfully to /output.")
# (inactive logic) #    else:
# (inactive logic) #        st.error("Render failed.")
            #    with st.expander("Render logs"):
# (inactive logic) #        st.code(proc.stdout + "\n" + proc.stderr)
    pass  # ensures the block is valid
    

author = "Kevin Day"
last_render_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# --- YAML / structure check (stub logic - wire up later) ---
yaml_valid = True
missing_fields = []
intention_equation = "Peace Vector"
readiness_score = 0.91
coherence_score = 0.88

# --- Display results ---
st.info(
        f"**Draft:** `{current_draft}`  \n"
        f"**Author:** {author}"
    )

if yaml_valid:
        st.success("YAML Valid - No critical errors detected.")
else:
        st.error("YAML Invalid - please check your structure and indentation.")

st.markdown(f"""
    **Format:** Op-Ed  
    **Intention Equation:** {intention_equation}  
    **Coherence Score:** {coherence_score * 100:.0f}%  
    """)

st.progress(readiness_score)
st.caption(f"Structural Readiness: {readiness_score * 100:.0f}%")

    # --- Guidance tips ---
st.markdown("**Tip:** Add a 'nutgraf' summary for stronger coherence and clarity.")
if missing_fields:
        st.warning(f"Missing optional fields: {', '.join(missing_fields)}")

st.markdown("---")

st.caption(f"Last render: {last_render_time}  |  Output: `/output/{current_draft}.html`")
     
# --- Simplified Compose Flow ---

def ensure_meta_signals(data: dict, eq_path, selected_eq):
    """Merge chosen intention equation & RippleScore data into YAML meta."""
    try:
        import yaml
        with open(eq_path, "r", encoding="utf-8") as f:
            eq_data = yaml.safe_load(f) or {}
    except FileNotFoundError:
        eq_data = {}

    # Load equation values if valid
    signals = {}
    if selected_eq and selected_eq in eq_data:
        signals.update(eq_data[selected_eq])

    # Merge RippleScores or FILS/UCIP/TTCF if already present
    for k in ["RippleScore", "FILS", "UCIP", "TTCF"]:
        if k in data.get("meta", {}):
            signals[k] = data["meta"][k]

    # Attach to data meta
    data.setdefault("meta", {}).update(signals)
    return data

    # --- Live in-app article preview & quick render ---
    st.markdown("### Live article preview")
    html_path = expected_output_html(choice if 'choice' in locals() else None, data)

    if st.button("Quick render & refresh preview", key="rw_quick_render"):
        env_vars = {}
        if openai_key:
            env_vars["OPENAI_API_KEY"] = openai_key
        if mock_mode:
            env_vars["RIPPLEWRITER_MOCK"] = "1"
        paths_arg = [str(ARTICLES_DIR / choice)] if (choice and choice != "(new)") else []
        proc = render_selected(paths_arg, env_vars)
        if proc.returncode == 0:
            st.success("Rendered successfully.")
        else:
            st.error("Render failed.")
        with st.expander("Render logs"):
            st.code(proc.stdout + "\n" + proc.stderr)

    if html_path.exists():
        try:
            html_content = html_path.read_text(encoding="utf-8")
            components.html(html_content, height=900, scrolling=True)
            st.caption(f"Previewing: {html_path}")
        except Exception as e:
            st.warning(f"Could not embed preview ({e}). You can still open the output index above.")
    else:
        st.info(
            "No article HTML found yet for this draft. "
            "Use **Write & Render Now** or **Quick Render & Refresh Preview** above."
        )

    # --- Version Info Footer ---
    import subprocess
    try:
        version = subprocess.check_output(
            ["git", "describe", "--tags", "--always"], text=True
        ).strip()
        repo_url = "https://github.com/kevinmday/RippleWriter"
        st.markdown(
            f"**Current build:** [{version}]({repo_url}/tree/{version})",
            unsafe_allow_html=True,
        )
    except Exception:
        st.caption("**Current build:** (version unavailable)")

    # --- Live YAML preview & download ---
    st.markdown("---")
    st.subheader("YAML Preview")
    if choice != "(new)":
        preview_yaml_box(
            data,
            filename=choice if choice.endswith((".yml", ".yaml")) else f"{choice}.yaml",
        )
    else:
        preview_yaml_box(default_article(), filename="new-article.yaml")

    st.markdown("---")
    st.subheader("Commit & Push")
    st.caption("This stages everything (including /output), commits, and pushes to origin.")
    if st.button("Commit & Push"):
        try:
            msg = commit_msg or "Publish via RippleWriter Studio"
            result = commit_and_push(ROOT, msg, branch=branch)
            st.success(result)
        except Exception as e:
            st.error(f"Git push failed: {e}")
            st.info(
                "If this is the first push on this machine, make sure you-re signed in to Git "
                "and have permission to push (Git Credential Manager will usually prompt on Windows)."
            )

# (cosmetic) -------------------------
# Tab 2: Source Draft
# (cosmetic) -------------------------

with tab_source:
    st.subheader("Source Draft (paste or drop files)")
    colA, colB = st.columns([2, 1])  # keep colB for future metadata/actions

        # --- Align Right Column to Top (Compose/Source Tabs) ---
    st.markdown("""
    <style>
    div[data-testid="stVerticalBlock"] > div:nth-child(2) {
        align-self: flex-start !important;
        margin-top: 0 !important;
    }
    div[data-testid="stColumn"]:nth-child(2) {
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        align-items: flex-start;
    }
    </style>
    """, unsafe_allow_html=True)


    # ---- left: inputs ----
    with colA:
        paste_text = st.text_area(
            "Paste source text (notes, transcript, links, etc.)",
            height=240,
            placeholder="Paste raw material here-",
        )

        files_up = st.file_uploader(
            "Or drop text files (txt, md) - contents are concatenated",
            type=["txt", "md"],
            accept_multiple_files=True,
        )
      
        # --- Align Compose right column to top only ---
        st.markdown("""
        <style>
        div[data-testid="stVerticalBlock"]:has(> div > div:has(> h3:contains('Create Scaffold'))) 
        div[data-testid="stHorizontalBlock"] > div:nth-child(2) {
        align-self: flex-start !important;
        justify-content: flex-start !important;
        display: flex !important;
        flex-direction: column !important;
        margin-top: 0 !important;
        }
        </style>
        """, unsafe_allow_html=True)

        # Build combined text from paste + files
        file_texts: List[str] = []
        if files_up:
            for f in files_up:
                try:
                    file_texts.append(f.read().decode("utf-8", errors="ignore"))
                except Exception:
                    pass
        combined_text = "\n\n".join([t for t in [paste_text] + file_texts if t])

        # Unified image ingest UI (paste + drag/drop)
        ui_image_ingest()
        # ? Right column: global article status + RSS monitor
    with colB:
        render_right_sidebar()

# --- Compose (YAML) ---
with tab_compose:
# (cosmetic) # ---------- Compose Tab Layout ----------
    st.markdown("""
        <style>
            /* Adjust column flex ratios for Compose tab */
            div[data-testid="column"]:nth-of-type(1) {flex: 1.1;}
            div[data-testid="column"]:nth-of-type(2) {flex: 1.2;}
            div[data-testid="column"]:nth-of-type(3) {flex: 1.7;}
        </style>
    """, unsafe_allow_html=True)

# (inactive logic) # Define Compose column layout
    col1, col2, col3 = st.columns([1.1, 1.2, 1.7])


    if st.session_state.get("compose_rendered", False):
        st.stop()
    st.session_state["compose_rendered"] = True

# ================== BEGIN COMPOSE PANEL ====================
# ---- LAYOUT SETUP (3 Columns + CSS Tweaks) ----
    st.markdown("### Compose: YAML Scaffold Builder")

# --- Compose (YAML) Layout Upgrade: Three Columns ---
with st.container():
    st.subheader("Compose: YAML Scaffold Builder")

    # Left = controls | Center = YAML fields | Right = feedback/monitor
    colL, colC, colR = st.columns([1.2, 2.8, 1])

# --- Extend right column height only (scoped to Compose area) ---
    st.markdown("""
    <style>
    /* Find Compose layout block, then extend its rightmost column */
    section[data-testid="stVerticalBlock"]:has(> div > div:has(> h3:contains('Compose: YAML Scaffold Builder'))) 
    div[data-testid="column"]:last-child {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 100vh !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Pull Intention Equation + AI Assistant upward (center column only) ---
    st.markdown("""
    <style>
    /* Locate Compose container, then move the middle column upward */
    section[data-testid="stVerticalBlock"]:has(> div > div:has(> h3:contains('Compose: YAML Scaffold Builder')))
    div[data-testid="stHorizontalBlock"] div[data-testid="stVerticalBlock"]:nth-of-type(2) {
    margin-top: -6rem !important;
    }

    /* Tighten spacing between Intention Equation dropdown and AI Assistant header */
    section[data-testid="stVerticalBlock"]:has(> div > div:has(> h3:contains('Compose: YAML Scaffold Builder')))
    h3:contains("AI Assistant") {
    margin-top: -2.5rem !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ---- LEFT COLUMN: Draft Controls ----
    with colL:
        st.markdown("### Draft Controls")
        # You can later move draft selection dropdown or file options here
        # Example placeholder:
        st.text("Draft list and quick options will go here.")

# ---- CENTER COLUMN: YAML Fields + AI Assistant ----
    with colC:
        st.markdown("### YAML Fields")
            # Info note for draft creation / selection
    st.info("Choose an existing draft from the dropdown, or create a new one.")

# (inactive logic) # Default selection fallback
    if 'choice' not in locals():
        choice = "(new)"

    # --- Safe load / new scaffold handler ---
    choice = draft_choice  # ensure continuity from selectbox above

    if choice == "(new)":
        filename = "new-article.yaml"
        data = {
            "title": "",
            "author": "Kevin Day",
            "date": datetime.now().strftime("%Y/%m/%d"),
            "format": "Op-Ed",
            "intention_equation": "None"
        }
        st.info("Starting a new YAML scaffold.")
    else:
        current_path = ARTICLES_DIR / choice
        try:
            data = load_yaml(current_path)
            st.success(f"? Loaded existing draft: {choice}")
        except FileNotFoundError:
            st.error(f"File not found: {current_path}")
            data = {}

    # Share current selection across tabs
    st.session_state["rw_choice"] = choice
    st.session_state["rw_data"] = data

    # Show Ripple score if previously saved by Meta-Analysis
    meta = data.get("meta") or {}
    score = meta.get("ripple_score") if isinstance(meta, dict) else None
    if isinstance(score, (int, float)):
        st.metric("Ripple score", f"{score:.3f}")

        # Core YAML Fields go here:
        title = st.text_input("Title")
        author = st.text_input("Author", "Kevin Day")
        date = st.text_input("Date", value=datetime.now().strftime("%Y/%m/%d"))
# (inactive logic) format_choice = st.selectbox("Format", ["Op-Ed", "Feature", "Essay", "Report"])
        intention_equation = st.selectbox(
            "Intention Equation",
            ["None", "Peace Vector", "Fractal Resonance", "UCIP Flow"],
        )

# ---- SAVE YAML + NAVIGATION ----
    st.markdown("DEBUG: This is the ONLY Save YAML block executing.", unsafe_allow_html=True)


# ---- SAVE YAML + NAVIGATION ----
# --- Save YAML Actions (bottom-fixed container, outside tab_compose) ---
with st.container():
    st.markdown("---")  # visual divider
    st.markdown("**YAML Actions**")
    st.write("Choose whether to stay and refine your YAML, or move straight into writing.")

    col1, col2 = st.columns(2)
    with col1:
# ---- SAVE YAML + NAVIGATION ----
        if st.button("Save YAML (Stay on Compose)", key="save_yaml_bottom"):
            save_yaml(filename, current_yaml_text)
            st.success("YAML saved successfully. Continue refining.")

    with col2:
        if st.button("Save & Move to Input", key="move_to_input_bottom"):
            save_yaml(filename, current_yaml_text)
            st.session_state.active_tab = "Input"
            st.success("YAML saved and moved to Input tab.")


# --- Meta-Analysis Tab ---
# ---- META-ANALYSIS SECTION ----
with tab_meta:
    st.subheader("Meta-Analysis (Ripple score)")

    # Prefer the selection from Compose
    choice = st.session_state.get("rw_choice")
    data = st.session_state.get("rw_data", {})

    files = list_yaml_files()
    names = [f.name for f in files]

    # Fallback picker if user hasn't visited Compose yet
    if not choice or choice == "(new)" or not names:
        st.info("Pick or create a draft in **Compose** first. (Or select one below.)")
        choice = st.selectbox("Choose an Article", names, index=0 if names else None, key="meta_draft_fallback")
        if not choice:
            st.stop()
        data = load_yaml(ARTICLES_DIR / choice)

    # ? Right column: global article status + RSS monitor
    with colB:
        render_right_sidebar()
