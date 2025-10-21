from __future__ import annotations
import os, sys, glob, pathlib, datetime
from typing import Dict, Any, List
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import BaseModel, Field, ValidationError
from llm_client import LLMClient

ROOT = pathlib.Path(__file__).parent
ARTICLES = ROOT / "articles"
OUTPUT = ROOT / "output"
TEMPLATES = ROOT / "templates"
POSTS_DIR = OUTPUT / "posts"
CONFIG = ROOT / "config" / "settings.yaml"

env = Environment(
    loader=FileSystemLoader(str(TEMPLATES)),
    autoescape=select_autoescape(["html", "xml", "md"])
)

OUTPUT.mkdir(exist_ok=True)
POSTS_DIR.mkdir(parents=True, exist_ok=True)

class Article(BaseModel):
    title: str
    author: str | None = None
    date: str | None = None
    slug: str | None = None
    thesis: str
    audience: str | None = None
    tone: str | None = None
    outline: List[str] = Field(default_factory=list)
    claims: List[Dict[str, Any]] = Field(default_factory=list)
    images: List[Dict[str, Any]] = Field(default_factory=list)
    publish: Dict[str, Any] = Field(default_factory=dict)

def load_yaml(p: pathlib.Path) -> Dict[str, Any]:
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_settings() -> Dict[str, Any]:
    return load_yaml(CONFIG) if CONFIG.exists() else {}

def slugify(s: str) -> str:
    return "".join(c.lower() if c.isalnum() else "-" for c in s).strip("-")

def render_post(y: Dict[str, Any], sections: Dict[str, str]) -> Dict[str, Any]:
    template = env.get_template("post.md.j2")
    ctx = {**y, **sections}
    md = template.render(**ctx)

    date = y.get("date") or datetime.date.today().isoformat()
    slug = y.get("slug") or slugify(y.get("title", "post"))

    md_path = POSTS_DIR / f"{slug}.md"
    md_path.write_text(md, encoding="utf-8")

    # Escape newlines BEFORE putting into f-string to avoid backslash issues
    def esc(text: str) -> str:
        return text.replace("\\n", "<br/>").replace("\n", "<br/>")

    lede = esc(sections.get("lede", ""))
    body = esc(sections.get("body", ""))
    counter = esc(sections.get("counterpoints", ""))
    concl = esc(sections.get("conclusion", ""))

    html = f"""<!doctype html>
<html><head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>{y.get('title')}</title>
  <link rel='stylesheet' href='../styles.css' />
</head>
<body>
  <main>
    <p><a href='../index.html'>← Back</a></p>
    <h1>{y.get('title')}</h1>
    <p><small>{date} — {y.get('author','')}</small></p>
    <article>
      <h2>Lede</h2>
      <p>{lede}</p>
      <h2>Body</h2>
      <p>{body}</p>
      <h2>Counterpoints & Limits</h2>
      <p>{counter}</p>
      <h2>Conclusion</h2>
      <p>{concl}</p>
      <hr/>
      <h3>Notes & Sources</h3>
      <ul>
        <li>Audience: {y.get('audience','')}</li>
        <li>Tone: {y.get('tone','')}</li>
      </ul>
    </article>
  </main>
</body></html>"""

    html_path = POSTS_DIR / f"{slug}.html"
    html_path.write_text(html, encoding="utf-8")

    return {"title": y.get("title"), "date": date, "slug": slug}

def render_index(posts: List[Dict[str, Any]]):
    template = env.get_template("index.html.j2")
    posts = sorted(posts, key=lambda p: p["date"], reverse=True)
    html = template.render(posts=posts)
    (OUTPUT / "index.html").write_text(html, encoding="utf-8")
    (OUTPUT / "styles.css").write_text((TEMPLATES / "styles.css").read_text(encoding="utf-8"), encoding="utf-8")

def main(paths: List[str] | None = None):
    _ = load_settings()
    llm = LLMClient()

    yaml_files: List[str] = []
    if paths:
        for p in paths:
            yaml_files += glob.glob(p)
    else:
        yaml_files = glob.glob(str(ARTICLES / "*.yml")) + glob.glob(str(ARTICLES / "*.yaml"))

    posts_meta: List[Dict[str, Any]] = []
    for yf in yaml_files:
        raw = load_yaml(pathlib.Path(yf))
        try:
            art = Article(**raw)
        except ValidationError as ve:
            print(f"Validation error in {yf}: {ve}")
            continue
        y = art.model_dump()
        sections = llm.write_post_sections(y)
        meta = render_post(y, sections)
        posts_meta.append(meta)

    render_index(posts_meta)
    print(f"Rendered {len(posts_meta)} post(s) to {OUTPUT}")

if __name__ == "__main__":
    args = sys.argv[1:]
    main(args if args else None)
