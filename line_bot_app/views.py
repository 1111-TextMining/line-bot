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
import datetime
import pytz
from line_bot_app.Flex_msg import *
from line_bot_app.output_data import *
from line_bot_app.models import *

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

        reminder = '請開始書寫您的筆記！'
        notification = '已儲存您的筆記！'

        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            if isinstance(event, MessageEvent):

                time_zone = pytz.timezone('Asia/Taipei')
                now = datetime.datetime.now(time_zone)

                uid = event.source.user_id
                mtext = event.message.text

                messages = User_Message.objects.filter(uid=uid).order_by(
                    '-mdt').values('mtext', 'rtext', 'mdt')
                messages_list = list(messages)

                output_dict = {}
                result_text = ''

                flag = True

                default_text = [reminder, notification,
                                '看房筆記', '查看筆記', '無筆記紀錄', '新增筆記', '小叮嚀']

                if len(messages_list) > 0:
                    if messages_list[0]['rtext'] == reminder:
                        User_Note.objects.create(uid=uid, notes=mtext)
                        line_bot_api.reply_message(
                            event.reply_token, TextSendMessage(text=notification))
                        output_dict = {'ws': [], 'ner': {}, 'filter': {}}
                        result_text = notification
                        flag = False

                if '看房筆記' in event.message.text:
                    line_bot_api.reply_message(event.reply_token, house_note())
                    output_dict = {'ws': [], 'ner': {}, 'filter': {}}
                    result_text = '看房筆記'
                    flag = False

                if '查看筆記' in event.message.text:
                    notes = User_Note.objects.filter(
                        uid=uid).values('notes', 'mdt')
                    notes_list = list(notes)

                    note_message = ''

                    for note in notes_list:
                        note_datetime = note['mdt'].astimezone(
                            time_zone).strftime('%Y-%m-%d %H:%M')
                        content = note['notes']
                        note_message += note_datetime + '\n' + content + '\n'

                    if note_message != '':
                        line_bot_api.reply_message(
                            event.reply_token, TextSendMessage(note_message))
                        result_text = note_message
                    else:
                        line_bot_api.reply_message(
                            event.reply_token, TextSendMessage('無筆記紀錄'))
                        result_text = '無筆記紀錄'

                    output_dict = {'ws': [], 'ner': {}, 'filter': {}}
                    flag = False

                if '新增筆記' in event.message.text:
                    line_bot_api.reply_message(
                        event.reply_token, TextSendMessage(text=reminder))
                    output_dict = {'ws': [], 'ner': {}, 'filter': {}}
                    result_text = reminder
                    flag = False

                if '小叮嚀' in event.message.text:
                    line_bot_api.reply_message(
                        event.reply_token, warm_reminder())
                    output_dict = {'ws': [], 'ner': {}, 'filter': {}}
                    result_text = '小叮嚀'
                    flag = False

                if (flag):
                    memories_list = []
                    for memory in messages_list:
                        time_diff = now - memory['mdt']
                        tsecs = time_diff.total_seconds()
                        if (memory['rtext'] not in default_text and memory['mtext'] not in default_text):
                            if (tsecs <= 600):
                                memories_list.append(memory)

                    for memory in memories_list:
                        mtext += memory['mtext']

                    print('event.message.text', mtext)

                    output_dict = model(mtext)

                    result_text = output_data(output_dict)

                    if (type(result_text) == str):
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text=result_text)
                        )
                    else:
                        line_bot_api.reply_message(
                            event.reply_token,
                            house(result_text)
                        )

                User_Message.objects.create(
                    uid=uid, mtext=mtext, rtext=result_text, ner_result=output_dict)

        return HttpResponse()
    else:
        return HttpResponseBadRequest()
