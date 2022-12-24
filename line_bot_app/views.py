from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage

import pandas as pd
from ckiptagger import WS, POS, NER
from collections import defaultdict
import pprint
from gensim import corpora
import spacy
from spacy.matcher import PhraseMatcher

# Create your views here.
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

# training sentence
input_list = ["租文山區的房子，最好少於10000元", "買文山區的房子，最好少於10000000元", "買新房子", "租新房子", "租附近有車站的房子", "買附近有車站的房子", "租不要押金的房子，不然我快沒錢了",
              "租不用管理費的房子", "買不用管理費的房子", "租十坪到十五坪的房子", "買十坪到十五坪的房子", "買公設比低於 40%", "買每坪低於 70 萬的房子", "租屋有付電器的租屋處", "附近有學校的租屋處，因為我有小孩要上學"]

# CKIPtagger model
ws = WS(r'/Users/fei/Projects/line-bot/data')
ner = NER(r'/Users/fei/Projects/line-bot/data')
pos = POS(r'/Users/fei/Projects/line-bot/data')

# word segmentation
ckipResults = []
for m in input_list:
    ws_results = ws([m])
    ckipResults.append(ws_results[0])

# count word frequencies
frequency = defaultdict(int)
for text in ckipResults:
    for token in text:
        frequency[token] += 1

# keep words that appear more than 5
processed_corpus = [
    [token for token in text if frequency[token] > 5] for text in ckipResults]

dictionary = corpora.Dictionary(processed_corpus)
stop_word = ["我", "需要", "的"]

print('init done')


def model(words):
    if len(words) < 1:
        return '喵'
    wordList = [words]

    print('start model')
    for i in range(len(wordList)):
        for j in stop_word:
            if j in wordList[i]:
                removed_stop_word = wordList[i].replace(j, '')
                wordList[i] = removed_stop_word

    new_ckip = ws(wordList)
    # print(new_ckip[0])  # ['租', '文山區', '，', '最好', '少於', '1w']
    new_vec = dictionary.doc2bow(new_ckip[0])
    # print(new_vec)  # [(2, 1)]

    nlp = spacy.load("zh_core_web_sm")
    print('load')
    matcher = PhraseMatcher(nlp.vocab)

    phrases = ["松山區", "信義區", "中山區", "大安區", "內湖區",
               "北投區", "士林區", "中正區", "南港區", "文山區", "萬華區", "大同區"]

    # Create Doc Objects For The Phrases
    patterns = [nlp(text) for text in phrases]
    matcher.add("PatternList", patterns)

    ner_dict = dict()

    # Find Matches
    n = ''
    doc = nlp(words)
    matches = matcher(doc)
    for match_id, start, end in matches:
        span = doc[start:end]
        if len(span.text) > len(n):
            n = span.text
    if n != '':
        ner_dict["SEC"] = n
    print(ner_dict)

    # NER
    for m in new_ckip:
        pos_results = pos([m])
        ner_results = ner([m], pos_results)

    for r in ner_results:
        for x in r:
            if x[3] != n:
                ner_dict[x[2]] = x[3]

    print(ner_dict)
    print('-' * 10)

    # if new_vec[0][0] == 2:
    #     rent_df = pd.read_csv('clean_rent.csv')
    #     print(rent_df)
    # elif new_vec[0][0] == 3:
    #     newhouse_df = pd.read_csv('newhouse.csv')
    #     print(newhouse_df)

    return ner_dict


@csrf_exempt
def callback(request):

    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            if isinstance(event, MessageEvent):
                print('event.message.text', event.message.text)
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=str(model(event.message.text)))
                )
        return HttpResponse()
    else:
        return HttpResponseBadRequest()
