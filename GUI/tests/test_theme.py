from unittest.mock import patch

import theme


def test_inject_cockpit_css_writes_styles():
    with patch("theme.st.markdown") as mock_markdown:
        theme.inject_cockpit_css()

    mock_markdown.assert_called_once()
    args, kwargs = mock_markdown.call_args
    css = args[0]
    # Markdown must be rendered as raw HTML for the CSS to take effect.
    assert kwargs.get("unsafe_allow_html") is True
    assert "<style>" in css
    # A few representative cockpit selectors should be present.
    assert ".stApp" in css
    assert ".alert-master" in css
    assert "master-pulse" in css
