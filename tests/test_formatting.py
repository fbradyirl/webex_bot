from webex_bot.formatting import quote_info, quote_warning, quote_danger, code, html_link


def test_quote_helpers():
    assert quote_info("hi") == "<blockquote class=info>hi</blockquote>"
    assert quote_warning("hi") == "<blockquote class=warning>hi</blockquote>"
    assert quote_danger("hi") == "<blockquote class=danger>hi</blockquote>"


def test_code_and_html_link():
    assert code("x") == "<code>x</code>"
    assert html_link("Label", "https://example.com") == "<a href='https://example.com'>Label</a>"
