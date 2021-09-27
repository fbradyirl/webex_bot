# Adaptive Card Design Schema for a sample form.
# To learn more about designing and working with buttons and cards,
# checkout https://developer.webex.com/docs/api/guides/cards
HELP_CARD_CONTENT = {
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "type": "AdaptiveCard",
    "version": "1.2",
    "body": [
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "width": 2,
                    "items": [
                        {"type": "TextBlock", "text": "Ops Bot"},
                        {
                            "type": "TextBlock",
                            "text": "Command List",
                            "weight": "Bolder",
                            "size": "ExtraLarge",
                            "spacing": "None"
                        },
                        {
                            "type": "TextBlock",
                            "text": "This bot provides the following commands. Simply enter one of the below"
                                    "words to be prompted with the card to help you get the task done.",
                            "size": "Small",
                            "wrap": True
                        },
                        {
                            "type": "TextBlock",
                            "text": "Enter one of the following commands:",
                            "isSubtle": True,
                            "spacing": "None"
                        }
                    ]
                },
                {
                    "type": "Column",
                    "width": 1,
                    "items": [
                        {
                            "type": "Image",
                            "url": "https://i.postimg.cc/Lshc93gL/dim-sum.jpg",
                            "size": "auto"
                        }
                    ]
                }
            ]
        }
    ],
    "actions": [
        {
            "type": "Action.OpenUrl",
            "title": "More Info",
            "url": "https://developer.webex.com/docs/bots"
        }
    ]
}
