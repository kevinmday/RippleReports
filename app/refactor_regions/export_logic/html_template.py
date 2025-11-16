HTML_WRAPPER = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8" />
<title>{title}</title>
<style>
body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    margin: 40px;
    background: #0d1117;
    color: #e6edf3;
    line-height: 1.6;
}}
h1, h2, h3 {{
    color: #58a6ff;
}}
hr {{
    border: 1px solid #30363d;
}}
</style>
</head>
<body>
{content}
</body>
</html>
"""
