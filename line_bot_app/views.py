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
    requests = ['車站', '押金', '管理費', '電器', '學校']
    request_patterns = [nlp(text) for text in requests]
    request_matcher.add('RequestList', request_patterns)

    ner_dict = dict()

    # Find Matches
    # sec = ''
    # doc = nlp(words)
    # matches = matcher(doc)
    # for match_id, start, end in matches:
    #     span = doc[start:end]
    #     sec = span.text
    # if sec != '':
    #     ner_dict['SEC'] = sec
    # print(ner_dict)

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
    # for x in words_ws_result:
    #     pos_results = pos([x])
    #     ner_results = ner([x], pos_results)

    # for result in ner_results:
    #     for x in result:
    #         if x[3] != sec:
    #             ner_dict[x[2]] = x[3]

    # print(ner_dict)

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

    # for x in words_ws_result[0]:
    #     if x == '大於':
    #         i = words_ws_result[0].index(x)
    #         if words_ws_result[0][i+2] == '元' or words_ws_result[0][i+2] == '塊':
    #             filter['MONEY'] = ['>', words_ws_result[0][i+1]]
    #         elif words_ws_result[0][i+2] == '坪':
    #             filter['LAYOUT'] = ['>', words_ws_result[0][i+1]]
    #     elif x == '多於':
    #         i = words_ws_result[0].index(x)
    #         if words_ws_result[0][i+2] == '元' or words_ws_result[0][i+2] == '塊':
    #             filter['MONEY'] = ['>', words_ws_result[0][i+1]]
    #         elif words_ws_result[0][i+2] == '坪':
    #             filter['LAYOUT'] = ['>', words_ws_result[0][i+1]]
    #     elif x == '高於':
    #         i = words_ws_result[0].index(x)
    #         if words_ws_result[0][i+2] == '元' or words_ws_result[0][i+2] == '塊':
    #             filter['MONEY'] = ['>', words_ws_result[0][i+1]]
    #         elif words_ws_result[0][i+2] == '坪':
    #             filter['LAYOUT'] = ['>', words_ws_result[0][i+1]]
    #     elif x == '小於':
    #         i = words_ws_result[0].index(x)
    #         if words_ws_result[0][i+2] == '元' or words_ws_result[0][i+2] == '塊':
    #             filter['MONEY'] = ['<', words_ws_result[0][i+1]]
    #         elif words_ws_result[0][i+2] == '坪':
    #             filter['LAYOUT'] = ['<', words_ws_result[0][i+1]]
    #     elif x == '少於':
    #         i = words_ws_result[0].index(x)
    #         if words_ws_result[0][i+2] == '元' or words_ws_result[0][i+2] == '塊':
    #             filter['MONEY'] = ['<', words_ws_result[0][i+1]]
    #         elif words_ws_result[0][i+2] == '坪':
    #             filter['LAYOUT'] = ['<', words_ws_result[0][i+1]]
    #     elif x == '低於':
    #         i = words_ws_result[0].index(x)
    #         if words_ws_result[0][i+2] == '元' or words_ws_result[0][i+2] == '塊':
    #             filter['MONEY'] = ['<', words_ws_result[0][i+1]]
    #         elif words_ws_result[0][i+2] == '坪':
    #             filter['LAYOUT'] = ['<', words_ws_result[0][i+1]]

    # print(filter)

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

    return message


def output_data(output_dict):
    ner_dict = output_dict['ner']
    Ner_key = list(ner_dict.keys())
    Ner_value = list(ner_dict.values())

    rent_df = rent

    ws_list = output_dict['ws']
    for i in range(len(ws_list)):
        if (ws_list[i]):
            # 若使用者輸入房子則 rend_df 移除車位欄位
            rent_df = rent_df.loc[rent_df['kind'] != '車位']

    for i in range(0, len(ner_dict)):
        # 處理 ner 出來的資訊
        if (Ner_key[i] == 'SEC'):  # section（區）
            ner_dict['section'] = Ner_value[i]
            del ner_dict['SEC']

        elif (Ner_key[i] == 'GPE'):  # section（區）
            ner_dict['section'] = Ner_value[i]
            del ner_dict['GPE']

        elif (Ner_key[i] == 'LOC'):  # section（區）
            ner_dict['section'] = Ner_value[i]
            del ner_dict['LOC']

        elif (Ner_key[i] == 'MONEY'):  # 價格
            ner_dict['price'] = Ner_value[i]
            del ner_dict['MONEY']

        elif (Ner_key[i] == 'CARDINAL'):  # 價格
            ner_dict['price'] = Ner_value[i]
            del ner_dict['CARDINAL']

        elif (Ner_key[i] == 'QUANTITY'):  # 坪數
            ner_dict['area (坪)'] = Ner_value[i]
            del ner_dict['QUANTITY']

        # elif(Ner_key[i] == 'REQ'):
        #   if(Ner_value[i] == '管理費'): #管理費
        #     ner_dict['area (坪)'] = Ner_value[i]
        #     del ner_dict['QUANTITY']

        #   if(Ner_value[i] == '車站'): #車站
        #     ner_dict['area (坪)'] = Ner_value[i]
        #     del ner_dict['QUANTITY']

    # 若有 filter 值
    filter_dict = output_dict['filter']
    filter_key = list(filter_dict.keys())
    filter_value = list(filter_dict.values())
    Ner_after = ner_dict

    # 轉中文字至數字
    for i in range(len(filter_dict)):
        try:
            filter_dict[filter_key[i]][1] = chinese_to_arabic(
                filter_dict[filter_key[i]][1])
        except:
            pass

    for n in range(len(output_dict['filter'])):  # 判別 filter

        if (list(output_dict['filter'].keys())[n] == 'LAYOUT'):
            Layout_key = filter_dict['LAYOUT'][0]
            Layout_value = int(
                filter_dict['LAYOUT'][1].split('坪')[0])  # 去除坪數單位
            if (Layout_key == '>'):  # 大於
                c[rent_df['area (坪)'] > Layout_value]
            elif (Layout_key == '<'):  # 小於
                rent_df = rent_df.loc[rent_df['area (坪)'] < Layout_value]
            del Ner_after['area (坪)']

        elif (list(output_dict['filter'].keys())[n] == 'MONEY'):
            MONEY_key = filter_dict['MONEY'][0]
            MONEY_value = int(filter_dict['MONEY'][1].split('元')[0])  # 去除金額單位
            if (MONEY_key == '>'):  # 大於
                rent_df = rent_df.loc[rent_df['price'] > MONEY_value]
            elif (MONEY_key == '<'):  # 小於
                rent_df = rent_df.loc[rent_df['price'] < MONEY_value]
            del Ner_after['price']

    try:
        if (len(ner_dict['area (坪)']) > 1):  # deal with 坪數區間值
            a = chinese_to_arabic(ner_dict['area (坪)'][0].split('坪')[0])
            b = chinese_to_arabic(ner_dict['area (坪)'][1].split('坪')[0])
            min_area = min(a, b)
            max_area = max(a, b)
            rent_df = rent_df.loc[rent_df['area (坪)'] > float(min_area)]
            rent_df = rent_df.loc[rent_df['area (坪)'] < float(max_area)]
            del ner_dict['area (坪)']
    except:
        pass

    try:
        if (len(ner_dict['price']) > 1):  # deal with 價格區間值
            a = chinese_to_arabic(ner_dict['price'][0].split('元')[0])
            b = chinese_to_arabic(ner_dict['price'][1].split('元')[0])
            min_price = min(a, b)
            max_price = max(a, b)
            rent_df = rent_df.loc[rent_df['price'] > float(min_price)]
            rent_df = rent_df.loc[rent_df['price'] < float(max_price)]
            del ner_dict['price']
    except:
        pass

    for i in range(len(Ner_after)):  # 其他的 Ner select
        rent_df = rent_df.loc[rent_df[list(Ner_after.keys())[i]] == list(
            Ner_after.values())[i][0]]

    # 隨機挑選5個數字，作為隨機挑出的5筆資料的index
    sample = []
    for i in range(5):
        sample.append(random.randint(0, len(rent_df) - 1))
    # 將隨機挑出的資料，轉為list
    result = rent_df.iloc[sample, [4, 18]]
    result_title = result['title'].values.tolist()
    result_url = result['url'].values.tolist()

    # 將挑出的資料依序組合成字串
    result_text = ""
    for i in range(5):
        result_text += result_title[i]
        result_text += '\n'
        result_text += result_url[i]
        result_text += '\n'

    return result_text


def chinese_to_arabic(chinese_value):
    zh2digit_table = {'零': 0, '一': 1, '二': 2, '兩': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10, '百': 100, '千': 1000, '〇': 0, '○': 0, '○': 0, '０': 0, '１': 1, '２': 2,
                      '３': 3, '４': 4, '５': 5, '６': 6, '７': 7, '８': 8, '９': 9, '壹': 1, '貳': 2, '參': 3, '肆': 4, '伍': 5, '陆': 6, '柒': 7, '捌': 8, '玖': 9, '拾': 10, '佰': 100, '仟': 1000, '萬': 10000, '億': 100000000}
    digit_num = 0
    result = 0
    tmp = 0
    billion = 0

    while digit_num < len(chinese_value):
        tmp_zh = chinese_value[digit_num]
        tmp_num = zh2digit_table.get(tmp_zh, None)
        if tmp_num == 100000000:
            result = result + tmp
            result = result * tmp_num
            billion = billion * 100000000 + result
            result = 0
            tmp = 0
        elif tmp_num == 10000:
            result = result + tmp
            result = result * tmp_num
            tmp = 0
        elif tmp_num >= 10:
            if tmp == 0:
                tmp = 1
            result = result + tmp_num * tmp
            tmp = 0
        elif tmp_num is not None:
            tmp = tmp * 10 + tmp_num
        digit_num += 1
    result = result + tmp
    result = result + billion
    return result


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
                output_dict = model(event.message.text)
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=output_data(output_dict))
                )
        return HttpResponse()
    else:
        return HttpResponseBadRequest()
