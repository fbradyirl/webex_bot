def quote_info(text):
    return f"<blockquote class=info>{text}</blockquote>"


def quote_warning(text):
    return f"<blockquote class=warning>{text}</blockquote>"


def quote_danger(text):
    return f"<blockquote class=danger>{text}</blockquote>"


def code(text):
    return f"<code>{text}</code>"


def html_link(link_text, url):
    return f"<a href='{url}'>{link_text}</a>"
