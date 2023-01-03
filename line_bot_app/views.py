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
import random
from line_bot_app.Flex_msg import *
from line_bot_app.output_data import *

# Create your views here.
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

# training sentence
train_sentences = ['租文山區的房子，最好少於10000元', '買文山區的房子，最好少於10000000元', '買新房子', '租新房子', '租附近有車站的房子', '買附近有車站的房子', '租不要押金的房子，不然我快沒錢了',
                   '租不用管理費的房子', '買不用管理費的房子', '租十坪到十五坪的房子', '買十坪到十五坪的房子', '買公設比低於 40%', '買每坪低於 70 萬的房子', '租屋有付電器的租屋處', '附近有學校的租屋處，因為我有小孩要上學']

# CKIPtagger model
ws = WS(r'/Users/fei/Projects/line-bot/data')
pos = POS(r'/Users/fei/Projects/line-bot/data')
ner = NER(r'/Users/fei/Projects/line-bot/data')

# word segmentation
train_sentences_ws_results = []
for sentence in train_sentences:
    ws_result = ws([sentence])
    train_sentences_ws_results.append(ws_result[0])

# count word frequencies
freq = defaultdict(int)
for result in train_sentences_ws_results:
    for token in result:
        freq[token] += 1

# keep words that appear more than 5
processed_corpus = [
    [token for token in result if freq[token] > 5] for result in train_sentences_ws_results]

dictionary = corpora.Dictionary(processed_corpus)
stop_word = ['我', '需要', '的']
rent = pd.read_csv('clean_rent.csv')
nlp = spacy.load('zh_core_web_sm')

print('init done')


def model(words):
    if len(words) < 1:
        return '喵'

    wordsList = [words]

    print('start model')

    for i in range(len(wordsList)):
        for j in stop_word:
            if j in wordsList[i]:
                removed_stop_word = wordsList[i].replace(j, '')
                wordsList[i] = removed_stop_word

    words_ws_result = ws(wordsList)
    print(words_ws_result[0])  # ['租', '文山區', '，', '最好', '少於', '1w']
    words_vec = dictionary.doc2bow(words_ws_result[0])
    # print(words_vec)  # [(2, 1)]

    print('start spacy')

    section_matcher = PhraseMatcher(nlp.vocab)
    sections = ['松山區', '信義區', '中山區', '大安區', '內湖區',
                '北投區', '士林區', '中正區', '南港區', '文山區', '萬華區', '大同區']
    section_patterns = [nlp(text) for text in sections]
    section_matcher.add('SectionList', section_patterns)

    request_matcher = PhraseMatcher(nlp.vocab)
    requests = ['公車站', '管理費', '電器', '小學', '中學', '大學', '餐廳', '地鐵站', '押金']
    request_patterns = [nlp(text) for text in requests]
    request_matcher.add('RequestList', request_patterns)

    ner_dict = dict()

    # Find Matches
    words_with_space = ''
    for word in words_ws_result[0]:
        words_with_space += word + ' '

    doc = nlp(words_with_space)
    section_matches = section_matcher(doc)
    request_matches = request_matcher(doc)

    sec = []
    request = []

    for match_id, start, end in section_matches:
        span = doc[start:end]
        sec.append(span.text)
    if len(sec) != 0:
        ner_dict['SEC'] = sec

    for match_id, start, end in request_matches:
        span = doc[start:end]
        request.append(span.text)
    if len(request) > 0:
        ner_dict['REQ'] = request

    # NER
    ner_list = []
    for x in words_ws_result:
        pos_results = pos([x])
        ner_results = ner([x], pos_results)
        ner_list = list(ner_results[0])
        for nt in range(len(ner_list)):
            ner_list[nt] = list(ner_list[nt])
        for nl in ner_list:
            for s in sec:
                if s == nl[3]:
                    ner_list.remove(nl)

    for n in ner_list:
        if n[2] in ner_dict:
            value = ner_dict[n[2]]
            value.append(n[3])
            ner_dict.update({n[2]: value})
        else:
            ner_dict[n[2]] = [n[3]]

    filter = dict()

    for nk in ner_dict:
        if nk == 'MONEY' or nk == 'CARDINAL':
            if len(ner_dict[nk]) == 1:
                if '大於' in words_ws_result[0] or '多於' in words_ws_result[0] or '高於' in words_ws_result[0]:
                    filter['MONEY'] = ['>', ner_dict[nk][0]]
                elif '小於' in words_ws_result[0] or '少於' in words_ws_result[0] or '低於' in words_ws_result[0]:
                    filter['MONEY'] = ['<', ner_dict[nk][0]]
        elif nk == 'QUANTITY':
            if len(ner_dict[nk]) == 1:
                if '大於' in words_ws_result[0] or '多於' in words_ws_result[0] or '高於' in words_ws_result[0]:
                    filter['LAYOUT'] = ['>', ner_dict[nk][0]]
                elif '小於' in words_ws_result[0] or '少於' in words_ws_result[0] or '低於' in words_ws_result[0]:
                    filter['LAYOUT'] = ['<', ner_dict[nk][0]]

    message = {
        'ws': words_ws_result[0],
        'ner': ner_dict,
        'filter': filter
    }
    print(message)

    return message

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
                mtext = event.message.text
                output_dict = model(mtext)
                result_text = output_data(output_dict)
                
                if '看房筆記' in mtext:
                    line_bot_api.reply_message(event.reply_token, house_note())

                elif '租屋小叮嚀' in mtext:
                    line_bot_api.reply_message(event.reply_token, warm_reminder_rent())
                
                elif '買房小叮嚀' in mtext:
                    line_bot_api.reply_message(event.reply_token, warm_reminder_buy())

                elif '小叮嚀' in mtext:
                    line_bot_api.reply_message(event.reply_token, warm_reminder())

                if(type(result_text) == str):
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=result_text)
                    )
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        house(result_text)
                    )
        return HttpResponse()
    else:
        return HttpResponseBadRequest()
