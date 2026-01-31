from webexpythonsdk.models.cards import AdaptiveCard

from webex_bot.models.response import Response, response_from_adaptive_card


def test_response_as_dict_filters_empty():
    response = Response()
    response.markdown = "hello"
    response.files = "file-1"
    response.attachments = {"contentType": "application/vnd.microsoft.card.adaptive", "content": {}}
    result = response.as_dict()
    assert result["markdown"] == "hello"
    assert result["files"] == ["file-1"]
    assert result["attachments"] == [
        {"contentType": "application/vnd.microsoft.card.adaptive", "content": {}}
    ]
    assert "roomId" not in result


def test_response_from_adaptive_card_populates_attachment():
    card = AdaptiveCard(body=[], actions=[])
    response = response_from_adaptive_card(card)
    assert response.text == "This bot requires a client which can render cards."
    assert response.markdown == "This bot requires a client which can render cards."
    assert response.attachments[0]["contentType"] == "application/vnd.microsoft.card.adaptive"


def test_response_json_and_html_property():
    response = Response(attributes={"text": "hello"})
    response.html = "<b>hi</b>"
    assert response.html == "<b>hi</b>"
    assert '"text": "hello"' in response.json()
