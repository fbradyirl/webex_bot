# Adaptive Card Design Schema for a sample form.
# To learn more about designing and working with buttons and cards,
# checkout https://developer.webex.com/docs/api/guides/cards
BUSY_CARD_CONTENT = {
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "type": "AdaptiveCard",
    "version": "1.2",
    "body": [
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "width": 1,
                    "items": [
                        {
                            "type": "Image",
                            "url": "https://i.postimg.cc/2jMv5kqt/AS89975.jpg",
                            "size": "Stretch"
                        }
                    ]
                },
                {
                    "type": "Column",
                    "width": 1,
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "Working on it....",
                            "color": "Dark",
                            "weight": "Bolder",
                            "wrap": True,
                            "size": "default",
                            "horizontalAlignment": "Center"
                        },
                        {
                            "type": "TextBlock",
                            "text": "I am busy working on your request. Please continue to look busy while I do your work.",
                            "color": "Dark",
                            "height": "stretch",
                            "wrap": True
                        }
                    ]
                }
            ]
        }
    ]
}
