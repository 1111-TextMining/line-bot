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
                "style": "secondary",
                "height": "md",
                "action": {
                "type": "message",
                "label": "查看筆記",
                "text": "查看筆記"
                }
            },
            {
                "type": "button",
                "style": "secondary",
                "height": "md",
                "action": {
                "type": "message",
                "label": "新增筆記",
                "text": "新增筆記"
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

def warm_reminder():
    contents = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
            {
                "type": "text",
                "text": "小叮嚀",
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
                        "text": "租屋買房小叮嚀！",
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
                "height": "md",
                "action": {
                "type": "message",
                "label": "租屋小叮嚀",
                "text": "租屋小叮嚀"
                }
            },
            {
                "type": "button",
                "style": "link",
                "height": "md",
                "action": {
                "type": "message",
                "label": "買房小叮嚀",
                "text": "買房小叮嚀"
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
    return FlexSendMessage(alt_text='小叮嚀', contents=contents)

def warm_reminder_rent():
    contents = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
            {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                {
                    "type": "image",
                    "url": "https://scdn.line-apps.com/n/channel_devcenter/img/flexsnapshot/clip/clip4.jpg",
                    "size": "full",
                    "aspectMode": "cover",
                    "aspectRatio": "150:196",
                    "gravity": "center",
                    "flex": 1
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "image",
                        "url": "https://scdn.line-apps.com/n/channel_devcenter/img/flexsnapshot/clip/clip5.jpg",
                        "size": "full",
                        "aspectMode": "cover",
                        "aspectRatio": "150:98",
                        "gravity": "center"
                    },
                    {
                        "type": "image",
                        "url": "https://scdn.line-apps.com/n/channel_devcenter/img/flexsnapshot/clip/clip6.jpg",
                        "size": "full",
                        "aspectMode": "cover",
                        "aspectRatio": "150:98",
                        "gravity": "center"
                    }
                    ],
                    "flex": 1
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                    {
                        "type": "text",
                        "text": "租屋",
                        "size": "xs",
                        "color": "#ffffff",
                        "align": "center",
                        "gravity": "center",

                    }
                    ],
                    "backgroundColor": "#EC3D44",
                    "paddingAll": "2px",
                    "paddingStart": "4px",
                    "paddingEnd": "4px",
                    "flex": 0,
                    "position": "absolute",
                    "offsetStart": "18px",
                    "offsetTop": "18px",
                    "cornerRadius": "100px",
                    "width": "48px",
                    "height": "25px"
                }
                ]
            }
            ],
            "paddingAll": "0px"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "text",
                        "contents": [],
                        "size": "xl",
                        "wrap": True,
                        "text": "租屋小叮嚀",
                        "color": "#ffffff",
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": "租房子有很多需要注意的事情，歡迎參考！",
                        "color": "#ffffffcc",
                        "size": "sm",
                        "wrap": True
                    }
                    ],
                    "spacing": "sm"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                        {
                            "type": "text",
                            "contents": [],
                            "size": "sm",
                            "wrap": True,
                            "margin": "lg",
                            "color": "#ffffffde",
                            "text": "1.\n記得確認簽約人的身分 po 租屋廣告的是屋主？仲介？還是現任租客？\n\n如果是仲介，要確認他有取得屋主的書面授權，不然很有可能簽約後付了租押金，卻發現房東不知情，甚至一屋多租、不認帳。\n如果是現任租客，由於法規規定，除非房東和租客在租約明定「禁止轉租或分租」，不然現任租客是可以將房子轉租或分租擔任二房東。\n簽約前確認簽約人的身分，請他提供權狀、授權書或和房東的租約，確保自己的權益。\n\n"+
                                    "2.\n有無其他額外的費用需要負擔\n\n合約上雖然會明定房租價格，但這個價格包含哪些項目，也需要在合約上寫清楚。\n這個價個含稅嗎？是由房東還是租客來繳？房租是否包含第四台、網路、水電、天然氣、管理費、清潔費等？\n\n"+
                                    "3.\n押金最多 2 個月\n\n為了防止房東向房客要求過高的押金，不管簽約幾年，法規有規定租屋的押金最高只能收 2 個月喔！超過的部分可以用來抵付房租，也就是，你可以將某一期要繳的租金扣除房東多收的押金後，再付給房東。\n\n"+
                                    "4.\n註明可提前解約的事項\n\n許多租屋糾紛都是發生在入住之後，發現跟房東允諾的不一樣，這個在雅房出租或隔套收租特別常見。例如：本來房東允諾整層只租給女生，搬進去後卻發現有其他男性房客；或是本來是禁菸、禁寵物，卻開始有房客違反規定；此外，有些房東簽約後就對房子的修繕責任置之不理。為了避免因此推租還有被扣押金的爭議，簽約時就在合約上寫清楚，註明可以提前解約的事項。\n\n"+
                                    "5.\n點交清單\n\n有些房東會提供部分家具、家電，簽約時一定要當面點交清楚，退租時再一一核對。如之後有點交爭議，房東可能扣留部分押金。此外，房東提供的家具、家電如經正常使用仍然故障的話，需由房東負責修繕責任，房東不可為此扣留押金。為了避免這樣的爭議，除了點交清楚外，如家具、家電有故障的情況，記得第一時間就反映，不要等到要退租時才說。\n\n"+
                                    "6.\n買賣不破租賃、法拍也不破租賃\n\n由於「買賣不破租賃」，在租約期間，就算屋主把房子賣掉，新屋主也不能要求你解約或提高租金。除了買賣外，其實「法拍」也不破租賃喔，如果屋主因為房貸或其他債務問題導致房子被拍賣，新屋主也不能強迫你搬家。​​不需要特別寫在合約上，反而如果屋主可能要賣屋需要你配合於賣出後提早解約退租，需要取得你的同意，並註明在合約上"

                        }
                        ]
                    }
                    ],
                    "paddingAll": "13px",
                    "backgroundColor": "#ffffff1A",
                    "cornerRadius": "2px",
                    "margin": "xl"
                }
                ]
            }
            ],
            "paddingAll": "20px",
            "backgroundColor": "#464F69"
        }
    }
    return FlexSendMessage(alt_text='租屋小叮嚀', contents=contents)

def warm_reminder_buy():
    contents = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
            {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                {
                    "type": "image",
                    "url": "https://scdn.line-apps.com/n/channel_devcenter/img/flexsnapshot/clip/clip4.jpg",
                    "size": "full",
                    "aspectMode": "cover",
                    "aspectRatio": "150:196",
                    "gravity": "center",
                    "flex": 1
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "image",
                        "url": "https://scdn.line-apps.com/n/channel_devcenter/img/flexsnapshot/clip/clip5.jpg",
                        "size": "full",
                        "aspectMode": "cover",
                        "aspectRatio": "150:98",
                        "gravity": "center"
                    },
                    {
                        "type": "image",
                        "url": "https://scdn.line-apps.com/n/channel_devcenter/img/flexsnapshot/clip/clip6.jpg",
                        "size": "full",
                        "aspectMode": "cover",
                        "aspectRatio": "150:98",
                        "gravity": "center"
                    }
                    ],
                    "flex": 1
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                    {
                        "type": "text",
                        "text": "買房",
                        "size": "xs",
                        "color": "#ffffff",
                        "align": "center",
                        "gravity": "center",

                    }
                    ],
                    "backgroundColor": "#EC3D44",
                    "paddingAll": "2px",
                    "paddingStart": "4px",
                    "paddingEnd": "4px",
                    "flex": 0,
                    "position": "absolute",
                    "offsetStart": "18px",
                    "offsetTop": "18px",
                    "cornerRadius": "100px",
                    "width": "48px",
                    "height": "25px"
                }
                ]
            }
            ],
            "paddingAll": "0px"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "text",
                        "contents": [],
                        "size": "xl",
                        "wrap": True,
                        "text": "買房小叮嚀",
                        "color": "#ffffff",
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": "買房子有很多需要注意的事情，歡迎參考！",
                        "color": "#ffffffcc",
                        "size": "sm",
                        "wrap": True
                    }
                    ],
                    "spacing": "sm"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                        {
                            "type": "text",
                            "contents": [],
                            "size": "sm",
                            "wrap": True,
                            "margin": "lg",
                            "color": "#ffffffde",
                            "text": "1.\n要約書與斡旋金\n\n簡單說明「要約書」和「斡旋金」的差異，就是在簽訂「要約書」時，並不需要先付錢，只不過是告訴屋主，有興趣買他的房子以及你的出價，這是內政部公定的版本。至於斡旋金則是仲介想出來的辦法，主要目的是希望你先付錢、拿出「誠意」，以便他們代為向賣方進行議價之交涉。\n\n"+
                                    "2.\n履約保證的陷阱\n\n目前房地產交易中，常有所謂的「履約保證」受到詬病，因為目前仲介的作法都不算保證，而只是凍結買賣價金的支付而已。所謂「履約保證」，就是保證履約，亦即讓買賣契約繼續完成至買方全部給付價金，賣方完全交屋及產權登記完竣為止，實務上若發生買方因故未能如期付款，保證者應該先行墊付價金，或者是先將房子辦理過戶（日後再和買方求償），或者是以違約論處，沒收買方價金，並解除契約。因此，產權發生瑕疵、或經查封及假扣押、或契約發生爭議、或買方無能力付款，或是貸款金額、付款方式、利率發生爭議，或是住戶規約有所限制等，均只是「協助」處理，並非保證處理至完善。房屋買賣契約中的每項條文，都必須詳加閱讀，這關係到全家人的健康和幸福。\n\n"+
                                    "3.\n買賣簽約的原則\n\n簽約應注意事項，涉及龐大的專業，但消費者首要重視的為：切記在簽署契約時，絕對不能使用不確定或不明確的文字，如此才不會模稜兩可，導致後來糾紛頻頻。\n\n"+
                                    "4.\n擁有自己的代書\n\n建議不論是買賣雙方都應該各自找代書，如此買賣雙方的代書才能各盡其責，將相關的稅費問題、產權調查與分析做到最好。事實上，代書除了可以做一般的登記移轉外，他們還可以用專業做好產權調查、產權分析、契約簽訂、辦理產權登記、監督交屋"

                        }
                        ]
                    }
                    ],
                    "paddingAll": "13px",
                    "backgroundColor": "#ffffff1A",
                    "cornerRadius": "2px",
                    "margin": "xl"
                }
                ]
            }
            ],
            "paddingAll": "20px",
            "backgroundColor": "#464F69"
        }
    }
    return FlexSendMessage(alt_text='買房小叮嚀', contents=contents)