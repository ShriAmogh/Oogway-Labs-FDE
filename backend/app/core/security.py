import bleach
import re
from typing import Tuple

# Allowed tags for rendered markdown/rich content (DOMPurify-like server sanitization)
ALLOWED_TAGS = [
    'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol',
    'strong', 'ul', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'pre', 'hr',
    'br', 'div', 'span', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'img',
    'button', 'section', 'article', 'header', 'footer', 'nav', 'main', 'svg',
    'path', 'circle', 'rect', 'line', 'polyline', 'polygon'
]

ALLOWED_ATTRIBUTES = {
    '*': ['class', 'style', 'id', 'data-*', 'aria-*', 'role'],
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    'th': ['scope', 'colspan', 'rowspan'],
    'td': ['colspan', 'rowspan'],
    'button': ['type', 'onclick', 'data-action'],
    'svg': ['viewbox', 'width', 'height', 'fill', 'stroke', 'xmlns'],
    'path': ['d', 'fill', 'stroke', 'stroke-width']
}

ALLOWED_PROTOCOLS = ['http', 'https', 'mailto', 'data']

def sanitize_html(html_content: str) -> str:
    """
    Sanitizes HTML content by stripping unsafe scripts and iframe escapes,
    allowing safe UI rendering.
    """
    if not html_content:
        return ""
    
    # Strip dangerous top-level scripts or outer document wrappers if passed as snippet
    cleaned = bleach.clean(
        html_content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True
    )
    return cleaned

def wrap_sandboxed_html_document(html_body: str, title: str = "Artifact Preview") -> str:
    """
    Wraps standalone HTML snippet in a secure document scaffold with Content-Security-Policy.
    Used for serving sandboxed iframes.
    """
    csp_meta = (
        '<meta http-equiv="Content-Security-Policy" content="'
        "default-src 'none'; "
        "style-src 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
        "font-src https://fonts.gstatic.com; "
        "script-src 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src data: https: http:; "
        "connect-src 'none'; "
        '">'
    )
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    {csp_meta}
    <title>{title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #0f172a;
            color: #f8fafc;
            padding: 1.5rem;
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    {html_body}
</body>
</html>"""
