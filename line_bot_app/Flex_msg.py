from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *


def house(result_text):
    print(result_text)
    contents=dict()
    contents['type']='carousel'
    bubbles=[]
    # datas = House.objects.filter(uid=uid)
    for i in range(len(result_text)):
        house_name = result_text[i][0] #第0個位置表標題
        url = result_text[i][1] #第1個位置表圖片
        pic = result_text[i][2] #第2個位置表圖片
        print(pic, url, house_name)
        print(str(pic))
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
                                        "text": "Place",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 1,
                                        "wrap": True
                                    },
                                    {
                                        "type": "text",
                                        "text": "Miraina Tower, 4-1-6 Shinjuku, Tokyo",
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
                                        "text": "Time",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 1,
                                        "wrap": True
                                    },
                                    {
                                        "type": "text",
                                        "text": "10:00 - 23:00",
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
    contents['contents']=bubbles
    message=FlexSendMessage(alt_text='工作進度',contents=contents)
    return message