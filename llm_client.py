from __future__ import annotations
import os, textwrap, yaml, pathlib
from typing import Dict, Any

# Config loader
def load_settings() -> dict:
    cfg_path = pathlib.Path(__file__).parent / "config" / "settings.yaml"
    if cfg_path.exists():
        return yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    return {}

SETTINGS = load_settings()
USE_MOCK = os.getenv("RIPPLEWRITER_MOCK", "0") == "1" or SETTINGS.get("mock", False)
MODEL = os.getenv("RIPPLEWRITER_MODEL", SETTINGS.get("model", "gpt-4.1-mini"))

class LLMClient:
    def __init__(self):
        self.use_mock = USE_MOCK or (os.getenv("OPENAI_API_KEY") is None)
        if not self.use_mock:
            from openai import OpenAI  # lazy import
            self.client = OpenAI()

    def _mock(self, prompt: str) -> str:
        return textwrap.dedent(
            f"""
            [MOCKED DRAFT]\n{prompt[:240]}...\n\nLede: Op-eds can be both opinionated and honest when they show their work.\n\nBody: This piece argues for intention transparency via YAML → LLM → publish.\nIt lays out limits and cites a few sources by name.\n\nCounterpoints: LLMs hallucinate; editorial review remains essential.\n\nConclusion: Let's publish with receipts and iteration hooks.\n"""
        ).strip()

    def complete(self, system: str, user: str) -> str:
        if self.use_mock:
            return self._mock(user)
        resp = self.client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.6,
        )
        return resp.choices[0].message.content

    def write_post_sections(self, y: Dict[str, Any]) -> Dict[str, str]:
        system = (
            "You are RippleWriter, a concise op-ed drafter. Structure the text into"
            " distinct sections labeled: Lede:, Body:, Counterpoints:, Conclusion:."
            " Respect the supplied thesis, tone, audience, and outline. Keep it 700-1100 words."
        )
        user = (
            "Title: {title}\nThesis: {thesis}\nAudience: {audience}\nTone: {tone}"
            "\nOutline: {outline}\nClaims: {claims}"
        ).format(
            title=y.get("title"),
            thesis=y.get("thesis"),
            audience=y.get("audience"),
            tone=y.get("tone"),
            outline="; ".join(y.get("outline", [])),
            claims="; ".join([c.get("claim", "") for c in y.get("claims", [])]),
        )
        full = self.complete(system, user)
        sections = {"lede": "", "body": "", "counterpoints": "", "conclusion": ""}
        current = None
        for line in full.splitlines():
            low = line.strip().lower()
            if low.startswith("lede:"): current = "lede"; sections[current] += line.split(":",1)[1].strip() + "\n"; continue
            if low.startswith("body:"): current = "body"; sections[current] += line.split(":",1)[1].strip() + "\n"; continue
            if low.startswith("counterpoints:"): current = "counterpoints"; sections[current] += line.split(":",1)[1].strip() + "\n"; continue
            if low.startswith("conclusion:"): current = "conclusion"; sections[current] += line.split(":",1)[1].strip() + "\n"; continue
            if current:
                sections[current] += line + "\n"
        return {k: v.strip() for k, v in sections.items()}