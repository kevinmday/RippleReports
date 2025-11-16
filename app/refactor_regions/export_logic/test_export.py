from export_builder import build_export_output
from html_template import HTML_WRAPPER

print("Running export logic test...")

md, html = build_export_output(
    title="Test Title",
    subtitle="Test Subtitle",
    include_final=True,
    include_insights=True,
    include_rippletruth=False,
    include_intention_metrics=False,
    final_text="This is the final draft.",
    insights_text="These are insights.",
    rippletruth_text="",
    intention_text="",
    export_format="HTML"
)

print("Markdown output:")
print(md[:200], "...")

wrapped = HTML_WRAPPER.format(title="Test Title", content=html)
print("\nHTML wrapped (first 200 chars):")
print(wrapped[:200], "...")
