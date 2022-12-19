from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage

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
stop_word = ["我", "需要", "的", "房子"]

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
    new_vec = dictionary.doc2bow(new_ckip[0])

    nlp = spacy.load("zh_core_web_sm")
    print('load')
    matcher = PhraseMatcher(nlp.vocab)

    phrases = ["動物園", "木柵", "萬芳社區", "萬芳醫院", "辛亥", "麟光", "六張犁", "科技大樓", "大安", "忠孝復興", "南京復興", "中山國中", "松山機場", "大直", "劍南路", "西湖", "港墘", "文德", "內湖", "大湖公園", "葫洲", "東湖", "南港軟體園區",
               "頂埔", "永寧", "土城", "海山", "亞東醫院", "府中", "板橋", "新埔", "江子翠", "龍山寺", "西門", "台北車站", "善導寺", "忠孝新生", "忠孝敦化", "國父紀念館", "市政府", "永春", "後山埤", "昆陽", "南港", "南港展覽館",
               "新店", "新店區公所", "七張", "小碧潭", "大坪林", "景美", "萬隆", "公館", "台電大樓", "古亭", "小南門", "北門", "松江南京", "南京復興", "台北小巨蛋", "南京三民", "松山",
               "南勢角", "景安", "永安市場", "頂溪", "行天宮", "中山國小", "大橋頭", "台北橋", "菜寮",  "三重", "先嗇宮", "頭前庄", "新莊", "輔大", "丹鳳", "迴龍", "三重國小", "三和國中", "徐匯中學", "三民高中", "蘆洲",
               '象山', '台北101/世貿', '信義安和', '大安森林公園', '東門', '中正紀念堂', '台大醫院', '中山', '雙連', '民權西路', '圓山', '劍潭', '士林', '芝山', '明德', '石牌', '唭哩岸', '奇岩', '北投', '新北投', '復興崗', '忠義', '關渡', '竹圍', '紅樹林', '淡水']

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
        ner_dict["SAT"] = n

    # NER
    for m in new_ckip:
        pos_results = pos([m])
        ner_results = ner([m], pos_results)

    for r in ner_results:
        for x in r:
            if x[3] != n:
                ner_dict[x[2]] = x[3]

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
