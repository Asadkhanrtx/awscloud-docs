import markdown
from weasyprint import HTML, CSS
import re

with open("vpc-case-study.md", "r") as f:
    md_content = f.read()

# Remove the broken image reference (local image not accessible)
md_content = re.sub(r'!\[.*?\]\(.*?\.png\)', '', md_content)

html_body = markdown.markdown(
    md_content,
    extensions=["tables", "fenced_code", "codehilite", "toc"]
)

html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.7;
    color: #1a1a2e;
    background: #fff;
    padding: 40px 50px;
    max-width: 900px;
    margin: 0 auto;
  }}

  h1 {{
    font-size: 26pt;
    font-weight: 700;
    color: #0f3460;
    border-bottom: 4px solid #e94560;
    padding-bottom: 12px;
    margin-bottom: 20px;
    margin-top: 30px;
  }}

  h2 {{
    font-size: 17pt;
    font-weight: 700;
    color: #16213e;
    border-left: 5px solid #e94560;
    padding-left: 12px;
    margin-top: 36px;
    margin-bottom: 14px;
    page-break-after: avoid;
  }}

  h3 {{
    font-size: 13pt;
    font-weight: 600;
    color: #0f3460;
    margin-top: 24px;
    margin-bottom: 10px;
    page-break-after: avoid;
  }}

  h4 {{
    font-size: 11pt;
    font-weight: 600;
    color: #533483;
    margin-top: 18px;
    margin-bottom: 8px;
    page-break-after: avoid;
  }}

  p {{
    margin-bottom: 12px;
  }}

  blockquote {{
    background: #f0f4ff;
    border-left: 4px solid #0f3460;
    padding: 10px 16px;
    margin: 14px 0;
    border-radius: 0 6px 6px 0;
    font-style: italic;
    color: #333;
  }}

  code {{
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    font-size: 9pt;
    background: #f4f4f8;
    padding: 2px 5px;
    border-radius: 3px;
    color: #c0392b;
  }}

  pre {{
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    font-size: 8.5pt;
    background: #1a1a2e;
    color: #e0e0e0;
    padding: 16px 18px;
    border-radius: 8px;
    overflow-x: auto;
    margin: 14px 0;
    line-height: 1.5;
    page-break-inside: avoid;
    white-space: pre-wrap;
    word-wrap: break-word;
  }}

  pre code {{
    background: transparent;
    color: #e0e0e0;
    padding: 0;
    font-size: 8.5pt;
  }}

  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
    font-size: 10pt;
    page-break-inside: avoid;
  }}

  th {{
    background: #0f3460;
    color: #ffffff;
    padding: 9px 13px;
    text-align: left;
    font-weight: 600;
    font-size: 10pt;
  }}

  td {{
    padding: 8px 13px;
    border-bottom: 1px solid #e0e0e0;
    vertical-align: top;
  }}

  tr:nth-child(even) td {{
    background: #f8f9ff;
  }}

  ul, ol {{
    padding-left: 22px;
    margin-bottom: 12px;
  }}

  li {{
    margin-bottom: 5px;
  }}

  strong {{
    font-weight: 600;
    color: #0f3460;
  }}

  em {{
    color: #555;
  }}

  hr {{
    border: none;
    border-top: 1px solid #ddd;
    margin: 28px 0;
  }}

  a {{
    color: #0f3460;
    text-decoration: none;
  }}

  .toc {{
    background: #f8f9ff;
    border: 1px solid #dde;
    border-radius: 8px;
    padding: 18px 24px;
    margin-bottom: 30px;
  }}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

HTML(string=html, base_url="/home/user/awscloud-docs/").write_pdf(
    "vpc-case-study.pdf",
    stylesheets=[CSS(string="@page { size: A4; margin: 1.5cm 1.8cm; }")]
)

print("PDF created: vpc-case-study.pdf")
