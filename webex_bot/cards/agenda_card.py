# Adaptive Card Design Schema for a sample form.
# To learn more about designing and working with buttons and cards,
# checkout https://developer.webex.com/docs/api/guides/cards
AGENDA_CARD_CONTENT = {
    "type": "AdaptiveCard",
    "body": [
        {
            "type": "ColumnSet",
            "horizontalAlignment": "Center",
            "columns": [
                {
                    "type": "Column",
                    "items": [
                        {
                            "type": "ColumnSet",
                            "horizontalAlignment": "Center",
                            "columns": [
                                {
                                    "type": "Column",
                                    "items": [
                                        {
                                            "type": "Image",
                                            "url": "https://messagecardplayground.azurewebsites.net/assets/LocationGreen_A.png"
                                        }
                                    ],
                                    "width": "auto"
                                },
                                {
                                    "type": "Column",
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": "**San Francisco**"
                                        },
                                        {
                                            "type": "TextBlock",
                                            "spacing": "None",
                                            "text": "8a - 12:30pm"
                                        }
                                    ],
                                    "width": "auto"
                                }
                            ]
                        }
                    ],
                    "width": 1
                },
                {
                    "type": "Column",
                    "spacing": "Large",
                    "separator": True,
                    "items": [
                        {
                            "type": "ColumnSet",
                            "horizontalAlignment": "Center",
                            "columns": [
                                {
                                    "type": "Column",
                                    "items": [
                                        {
                                            "type": "Image",
                                            "url": "https://messagecardplayground.azurewebsites.net/assets/LocationBlue_B.png"
                                        }
                                    ],
                                    "width": "auto"
                                },
                                {
                                    "type": "Column",
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": "**New York**"
                                        },
                                        {
                                            "type": "TextBlock",
                                            "spacing": "None",
                                            "text": "12:30 - 3pm"
                                        }
                                    ],
                                    "width": "auto"
                                }
                            ]
                        }
                    ],
                    "width": 1
                },
                {
                    "type": "Column",
                    "spacing": "Large",
                    "separator": True,
                    "items": [
                        {
                            "type": "ColumnSet",
                            "horizontalAlignment": "Center",
                            "columns": [
                                {
                                    "type": "Column",
                                    "items": [
                                        {
                                            "type": "Image",
                                            "url": "https://messagecardplayground.azurewebsites.net/assets/LocationRed_C.png"
                                        }
                                    ],
                                    "width": "auto"
                                },
                                {
                                    "type": "Column",
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": "**Amsterdam**"
                                        },
                                        {
                                            "type": "TextBlock",
                                            "spacing": "None",
                                            "text": "8pm"
                                        }
                                    ],
                                    "width": "auto"
                                }
                            ]
                        }
                    ],
                    "width": 1
                }
            ]
        },
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "items": [
                        {
                            "type": "ColumnSet",
                            "columns": [
                                {
                                    "type": "Column",
                                    "spacing": "None",
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": "2:00 PM"
                                        }
                                    ],
                                    "width": "stretch"
                                }
                            ]
                        },
                        {
                            "type": "TextBlock",
                            "spacing": "None",
                            "text": "1hr",
                            "isSubtle": True
                        }
                    ],
                    "width": "110px"
                },
                {
                    "type": "Column",
                    "backgroundImage": {
                        "url": "https://messagecardplayground.azurewebsites.net/assets/SmallVerticalLineGray.png",
                        "fillMode": "RepeatVertically",
                        "horizontalAlignment": "Center"
                    },
                    "items": [
                        {
                            "type": "Image",
                            "horizontalAlignment": "Center",
                            "url": "https://messagecardplayground.azurewebsites.net/assets/CircleGreen_coffee.png"
                        }
                    ],
                    "width": "auto",
                    "spacing": "None"
                },
                {
                    "type": "Column",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "**Cisco Live Amsterdam 2021**"
                        },
                        {
                            "type": "ColumnSet",
                            "spacing": "None",
                            "columns": [
                                {
                                    "type": "Column",
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": "Showroom 12"
                                        }
                                    ],
                                    "width": "stretch"
                                }
                            ]
                        },
                        {
                            "type": "ImageSet",
                            "spacing": "Small",
                            "imageSize": "Small",
                            "images": [
                                {
                                    "type": "Image",
                                    "url": "https://i.postimg.cc/fR0XZPjY/Screen-Shot-2020-04-29-at-1-40-1.png",
                                    "size": "Small"
                                },
                                {
                                    "type": "Image",
                                    "url": "https://i.postimg.cc/MHq2ZgQH/Screen-Shot-2020-04-29-at-1-43-1.png",
                                    "size": "Small"
                                },
                                {
                                    "type": "Image",
                                    "url": "https://i.postimg.cc/4y97Z7ps/Screen-Shot-2020-04-29-at-1-41-1.png",
                                    "size": "Small"
                                }
                            ]
                        },
                        {
                            "type": "ColumnSet",
                            "spacing": "Small",
                            "columns": [
                                {
                                    "type": "Column",
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": "**Webex Brand Guidelines** shared by **Chris Riggs**"
                                        }
                                    ],
                                    "width": "stretch"
                                }
                            ]
                        }
                    ],
                    "width": 40
                }
            ]
        },
        {
            "type": "ColumnSet",
            "spacing": "None",
            "columns": [
                {
                    "type": "Column",
                    "width": "110px"
                },
                {
                    "type": "Column",
                    "backgroundImage": {
                        "url": "https://messagecardplayground.azurewebsites.net/assets/SmallVerticalLineGray.png",
                        "fillMode": "RepeatVertically",
                        "horizontalAlignment": "Center"
                    },
                    "items": [
                        {
                            "type": "Image",
                            "horizontalAlignment": "Center",
                            "url": "https://messagecardplayground.azurewebsites.net/assets/Gray_Dot.png"
                        }
                    ],
                    "width": "auto",
                    "spacing": "None"
                },
                {
                    "type": "Column",
                    "items": [
                        {
                            "type": "ColumnSet",
                            "columns": [
                                {
                                    "type": "Column",
                                    "items": [
                                        {
                                            "type": "Image",
                                            "url": "https://messagecardplayground.azurewebsites.net/assets/car.png"
                                        }
                                    ],
                                    "width": "auto"
                                },
                                {
                                    "type": "Column",
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": "about 45 minutes",
                                            "isSubtle": True
                                        }
                                    ],
                                    "width": "stretch"
                                }
                            ]
                        }
                    ],
                    "width": 40
                }
            ]
        },
        {
            "type": "ColumnSet",
            "spacing": "None",
            "columns": [
                {
                    "type": "Column",
                    "items": [
                        {
                            "type": "TextBlock",
                            "spacing": "None",
                            "text": "8:00 PM"
                        },
                        {
                            "type": "TextBlock",
                            "spacing": "None",
                            "text": "1hr",
                            "isSubtle": True
                        }
                    ],
                    "width": "110px"
                },
                {
                    "type": "Column",
                    "backgroundImage": {
                        "url": "https://messagecardplayground.azurewebsites.net/assets/SmallVerticalLineGray.png",
                        "fillMode": "RepeatVertically",
                        "horizontalAlignment": "Center"
                    },
                    "items": [
                        {
                            "type": "Image",
                            "horizontalAlignment": "Center",
                            "url": "https://messagecardplayground.azurewebsites.net/assets/CircleBlue_flight.png"
                        }
                    ],
                    "width": "auto",
                    "spacing": "None"
                },
                {
                    "type": "Column",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "**KLM KL606 flight to Amsterdam**"
                        },
                        {
                            "type": "ColumnSet",
                            "spacing": "None",
                            "columns": [
                                {
                                    "type": "Column",
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": "Amsterdam Airport Schiphol (Evert van de Beekstraat 202, 1118 CP Schiphol, Netherlands)",
                                            "wrap": True
                                        }
                                    ],
                                    "width": "stretch"
                                }
                            ]
                        },
                        {
                            "type": "Image",
                            "url": "https://i.postimg.cc/QxqyGhrK/Screen-Shot-2020-04-29-at-2-03-32-PM.png",
                            "size": "Stretch"
                        }
                    ],
                    "width": 40
                }
            ]
        }
    ],
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.2"
}
