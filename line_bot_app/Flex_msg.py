from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *


def house(result_text):
    contents = dict()
    contents['type'] = 'carousel'
    bubbles = []
    for i in range(len(result_text)):
        section = result_text[i][0]  # 第0個位置表低區
        house_name = result_text[i][1]  # 第1個位置表標題
        price = result_text[i][2]  # 第2個位置表價格
        layout = result_text[i][3]  # 第3個位置表幾房幾廳
        area = result_text[i][4]  # 第4個位置表坪數
        url = result_text[i][5]  # 第5個位置表591url
        pic = result_text[i][6]  # 第6個位置表圖片
        bubble = {
            "type": "bubble",
            "size": "micro",
            "hero": {
                "type": "image",
                "url": pic,
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover",
                "action": {
                    "type": "uri",
                    "uri": "http://linecorp.com/"
                }
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": house_name,
                        "weight": "bold",
                        "size": "xl",
                        "wrap": True
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "地區",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 2,
                                        "wrap": True
                                    },
                                    {
                                        "type": "text",
                                        "text": section,
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 5,
                                        "wrap": True
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "價格",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 2,
                                        "wrap": True
                                    },
                                    {
                                        "type": "text",
                                        "text": str(int(price)),
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 5,
                                        "wrap": True
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "格局",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 2,
                                        "wrap": True
                                    },
                                    {
                                        "type": "text",
                                        "text": layout,
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 5,
                                        "wrap": True
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "坪數",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 2,
                                        "wrap": True
                                    },
                                    {
                                        "type": "text",
                                        "text": area,
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 5,
                                        "wrap": True
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                            "type": "uri",
                            "label": "591官網",
                            "uri": url
                        }
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [],
                        "margin": "sm"
                    }
                ],
                "flex": 0
            }

        }
        bubbles.append(bubble)
    contents['contents'] = bubbles
    return FlexSendMessage(alt_text='租屋推薦', contents=contents)

def house_note():
    contents = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
            {
                "type": "text",
                "text": "看房筆記",
                "weight": "bold",
                "size": "xl"
            },
            {
                "type": "box",
                "layout": "vertical",
                "margin": "lg",
                "spacing": "sm",
                "contents": [
                {
                    "type": "box",
                    "layout": "baseline",
                    "spacing": "sm",
                    "contents": [
                    {
                        "type": "text",
                        "text": "歡迎紀錄下來自己的看房筆記，以下功能歡迎點選！",
                        "wrap": True,
                        "color": "#666666",
                        "size": "sm",
                        "flex": 5
                    }
                    ]
                }
                ]
            }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
            {
                "type": "button",
                "style": "link",
                "height": "sm",
                "action": {
                "type": "uri",
                "label": "查看筆記",
                "uri": "https://linecorp.com"
                }
            },
            {
                "type": "button",
                "style": "link",
                "height": "sm",
                "action": {
                "type": "uri",
                "label": "新增筆記",
                "uri": "https://linecorp.com"
                }
            },
            {
                "type": "button",
                "style": "link",
                "height": "sm",
                "action": {
                "type": "uri",
                "label": "筆記推薦房子",
                "uri": "https://linecorp.com"
                }
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [],
                "margin": "sm"
            }
            ],
            "flex": 0
        }
    }
    return FlexSendMessage(alt_text='看房筆記', contents=contents)