import pytest
from app.core.security import sanitize_html, wrap_sandboxed_html_document

def test_sanitize_html_strips_malicious_scripts():
    dangerous_input = "<p>Hello</p><script>alert('xss')</script><img src='x' onerror='alert(1)'>"
    sanitized = sanitize_html(dangerous_input)
    assert "<script>" not in sanitized
    assert "onerror" not in sanitized
    assert "<p>Hello</p>" in sanitized

def test_sandboxed_wrapper_has_strict_csp():
    wrapped = wrap_sandboxed_html_document("<div>Interactive Calculator</div>", "Test Calc")
    assert "Content-Security-Policy" in wrapped
    assert "default-src 'none'" in wrapped
    assert "Interactive Calculator" in wrapped
