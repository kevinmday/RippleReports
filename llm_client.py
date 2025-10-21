import os
import textwrap
import yaml
import pathlib
from typing import Dict, Any

# --------------------------------------
# Config loader
# --------------------------------------
def load_settings() -> dict:
    """Load YAML config if available, else return empty dict."""
    cfg_path = pathlib.Path(__file__).parent / "config" / "settings.yaml"
    if cfg_path.exists():
        try:
            return yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
        except Exception as e:
            print(f"[WARN] Failed to read settings.yaml: {e}")
    return {}

SETTINGS = load_settings()
USE_MOCK = os.getenv("RIPPLEWRITER_MOCK", "0") == "1" or SETTINGS.get("mock", False)
MODEL = os.getenv("RIPPLEWRITER_MODEL", SETTINGS.get("model", "gpt-4.1-mini"))

# --------------------------------------
# LLM Client Class
# --------------------------------------
class LLMClient:
    """Handles text generation with OpenAI or mock fallback."""

    def __init__(self):
        self.use_mock = USE_MOCK or (os.getenv("OPENAI_API_KEY") is None)
        if not self.use_mock:
            from openai import OpenAI  # lazy import
            self.client = OpenAI()
            print(f"[INIT] Using OpenAI model: {MODEL}")
        else:
            print("[INIT] Using mock mode (no API key detected)")

    # --------------------------
    # Mock Mode
    # --------------------------
    def _mock(self, prompt: str) -> str:
        """Return a deterministic mock draft for offline testing."""
        return textwrap.dedent(f"""
        [MOCKED DRAFT]
        {prompt[:240]}...
        
        Lede: Op-eds can be both opinionated and honest when they show their work.

        Body: This piece argues for intention transparency via YAML → LLM → publish. 
        It lays out limits and cites a few sources by name.

        Counterpoints: LLMs hallucinate; editorial review remains essential.

        Conclusion: Let's publish with receipts and iteration hooks.
        """).strip()

    # --------------------------
    # Real Mode
    # --------------------------
    def complete(self, system: str, user: str) -> str:
        """Send structured system/user messages to the model."""
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
        return resp.choices[0].message.content.strip()

    # --------------------------
    # RippleWriter Section Builder
    # --------------------------
    def write_post_sections(self, y: Dict[str, Any]) -> Dict[str, str]:
        """Generate structured op-ed sections based on YAML input."""
        system = (
            "You are RippleWriter, a concise op-ed drafter. Structure output as:\n"
            "Lede:\nBody:\nCounterpoints:\nConclusion:\n"
            "Follow the provided thesis, tone, audience, and outline. Keep between 700–1100 words."
        )

        user = (
            f"Title: {y.get('title')}\n"
            f"Thesis: {y.get('thesis')}\n"
            f"Audience: {y.get('audience')}\n"
            f"Tone: {y.get('tone')}\n"
            f"Outline: {'; '.join(y.get('outline', []))}\n"
            f"Claims: {'; '.join([c.get('claim', '') for c in y.get('claims', [])])}"
        )

        full = self.complete(system, user)
        sections = {"lede": "", "body": "", "counterpoints": "", "conclusion": ""}
        current = None

        for line in full.splitlines():
            low = line.strip().lower()
            if low.startswith("lede:"):
                current = "lede"
                sections[current] += line.split(":", 1)[1].strip() + "\n"
                continue
            if low.startswith("body:"):
                current = "body"
                sections[current] += line.split(":", 1)[1].strip() + "\n"
                continue
            if low.startswith("counterpoints:"):
                current = "counterpoints"
                sections[current] += line.split(":", 1)[1].strip() + "\n"
                continue
            if low.startswith("conclusion:"):
                current = "conclusion"
                sections[current] += line.split(":", 1)[1].strip() + "\n"
                continue
            if current:
                sections[current] += line + "\n"

        return {k: v.strip() for k, v in sections.items()}
