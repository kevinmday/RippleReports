# ==========================================================
#  Export Builder — Markdown + HTML generator
#  Modernized for 2025 modular panels
# ==========================================================

import markdown
from datetime import datetime


def build_export_output(sections: dict, metadata: dict):
    """
    sections = {
        "final_draft": "...",
        "insights": "...",
        "rippletruth": "...",
        "intent_metrics": "..."
    }

    metadata = {
        "title": "...",
        "subtitle": "..."
    }
    """

    title = metadata.get("title", "Untitled Document")
    subtitle = metadata.get("subtitle", "")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # ------------------------------------------------------
    # Build Markdown
    # ------------------------------------------------------
    md = f"# {title}\n"
    if subtitle:
        md += f"### {subtitle}\n"
    md += f"**Generated:** {timestamp}  \n\n"

    # Final Draft
    if sections.get("final_draft", "").strip():
        md += "## Final Draft\n\n"
        md += sections["final_draft"] + "\n\n"

    # Insights
    if sections.get("insights", "").strip():
        md += "## Insights & Recommendations\n\n"
        md += sections["insights"] + "\n\n"

    # RippleTruth
    if sections.get("rippletruth", "").strip():
        md += "## RippleTruth Report\n\n"
        md += sections["rippletruth"] + "\n\n"

    # Intention Metrics
    if sections.get("intent_metrics", "").strip():
        md += "## Intention Metrics (FILS / UCIP / Drift)\n\n"
        md += sections["intent_metrics"] + "\n\n"

    # ------------------------------------------------------
    # Convert Markdown → HTML
    # ------------------------------------------------------
    html_body = markdown.markdown(md)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8" />
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 40px;
            line-height: 1.6;
        }}
        h1, h2, h3 {{
            color: #e3e3e3;
        }}
    </style>
    </head>
    <body>
    {html_body}
    </body>
    </html>
    """

    return md, html
