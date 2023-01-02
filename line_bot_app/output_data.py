import pandas as pd
from linebot.models import *
import random

def output_data(output_dict):
    rent_df = pd.read_csv('clean_rent.csv')

    ner_dict = output_dict['ner']
    Ner_key = list(ner_dict.keys())
    Ner_value = list(ner_dict.values())

    ws_list = output_dict['ws']
    for i in range(len(ws_list)):
        if (ws_list[i]):
            # 若使用者輸入房子則 rend_df 移除車位欄位
            rent_df = rent_df.loc[rent_df['kind'] != '車位']
    
    Ner_after = ner_dict
    
    try: #get request data
        for i in range(0, len(ner_dict['REQ'])):
            if(ner_dict['REQ'][i] == '公車站'):
                rent_df = rent_df.loc[rent_df['bus'] >= 1]
            
            elif(ner_dict['REQ'][i] == '管理費'):
                rent_df = rent_df.loc[rent_df['priceadd'] == '管理費']

            elif(ner_dict['REQ'][i] == '小學'):
                rent_df = rent_df.loc[rent_df['primary'] >= 1]

            elif(ner_dict['REQ'][i] == '中學' or ner_dict['REQ'][i] == '高中'):
                rent_df = rent_df.loc[rent_df['secondary'] >= 1]

            elif(ner_dict['REQ'][i] == '大學'):
                rent_df = rent_df.loc[rent_df['university'] >= 1]

            elif(ner_dict['REQ'][i] == '餐廳'):
                rent_df = rent_df.loc[rent_df['restaurant'] >= 1]

            elif(ner_dict['REQ'][i] == '地鐵站' or ner_dict['REQ'][i] == '捷運站'):
                rent_df = rent_df.loc[rent_df['subway'] >= 1]
            
            elif(ner_dict['REQ'][i] == '押金'):
                rent_df = rent_df.loc[rent_df['deposit'] == '無']
        del Ner_after['REQ']
            
    except:
        pass
    
    for i in range(0,len(ner_dict)):
        # 處理 ner 出來的資訊
        if(Ner_key[i] == 'SEC'): #section（區）
            ner_dict['section'] = Ner_value[i]                         

        elif(Ner_key[i] == 'GPE'): #section（區）
            ner_dict['section'] = Ner_value[i]                         

        elif(Ner_key[i] == 'LOC'): #section（區）
            ner_dict['section'] = Ner_value[i]                         
                            
        elif(Ner_key[i] == 'MONEY'): #價格 
            ner_dict['price'] = Ner_value[i]

        elif(Ner_key[i] == 'CARDINAL'): #價格
            ner_dict['price'] = Ner_value[i]

        elif(Ner_key[i] == 'QUANTITY'): #坪數
            ner_dict['area (坪)'] = Ner_value[i]
        del ner_dict[Ner_key[i]]
        
    # 若有 filter 值
    filter_dict = output_dict['filter']

    for n in range(len(output_dict['filter'])): #判別 filter

        if(list(output_dict['filter'].keys())[n] == 'LAYOUT' and len(ner_dict['area (坪)']) <= 1):
            Layout_key = filter_dict['LAYOUT'][0]
            Layout_value = filter_dict['LAYOUT'][1].split('坪')[0]
            value = 0
            if(str.isdigit(Layout_value) == True): #代表已經是數值了，不需要轉換中文成數字
                value = int(Layout_value)
            elif(str.isdigit(Layout_value) != True): #代表是中字，需要轉換中文成數字
                value = chinese_to_arabic(Layout_value)
            
            if(Layout_key == '>'): #大於
                rent_df = rent_df.loc[rent_df['area (坪)'] > value]
            elif(Layout_key == '<'): #小於
                rent_df = rent_df.loc[rent_df['area (坪)'] < value]
            del Ner_after['area (坪)']

        elif(list(output_dict['filter'].keys())[n] == 'MONEY' and len(ner_dict['price']) <= 1):
            MONEY_key = filter_dict['MONEY'][0]
            MONEY_value = filter_dict['MONEY'][1].split('元')[0]
            if(str.isdigit(MONEY_value) == True): #代表已經是數值了，不需要轉換中文成數字
                value = int(MONEY_value)
            elif(str.isdigit(MONEY_value) != True): #代表是中字，需要轉換中文成數字
                value = chinese_to_arabic(MONEY_value)

            if(MONEY_key == '>'): #大於
                rent_df = rent_df.loc[rent_df['price'] > value]
            elif(MONEY_key == '<'): #小於
                rent_df = rent_df.loc[rent_df['price'] < value]
            del Ner_after['price']
    
    Ner_key = list(ner_dict.keys())
    Ner_value = list(ner_dict.values())

    if(len(ner_dict) >= 1):
        for i in range(len(ner_dict)):
            if(len(ner_dict[Ner_key[i]])>=1 and (Ner_key[i] == 'price'or Ner_key[i] == 'area (坪)')):
                a_value = 0
                if(Ner_key[i] == 'price'):
                    a = ner_dict['price'][0].split('元')[0]
                elif(Ner_key[i] == 'area (坪)'):
                    a = ner_dict['area (坪)'][0].split('坪')[0]

                if(str.isdigit(a) == True): #代表已經是數值了，不需要轉換中文成數字
                    a_value = int(a)
                elif(str.isdigit(a) != True): #代表是中字，需要轉換中文成數字
                    a_value = chinese_to_arabic(a)
                
                if(len(ner_dict[Ner_key[i]])>1):
                    b_value = 0
                    if(Ner_key[i] == 'price'):
                        b = ner_dict['price'][1].split('元')[0]
                    elif(Ner_key[i] == 'area (坪)'):
                        b = ner_dict['area (坪)'][1].split('坪')[0]
                    
                    if(str.isdigit(b) == True):
                        b_value = int(b)
                    elif(str.isdigit(b) != True):
                        b_value = chinese_to_arabic(b)

                    min_price = min(a_value, b_value)
                    max_price = max(a_value, b_value)
                    rent_df = rent_df.loc[rent_df[Ner_key[i]] > float(min_price)]
                    rent_df = rent_df.loc[rent_df[Ner_key[i]] < float(max_price)]
                    del Ner_after[Ner_key[i]]
            elif(len(ner_dict[Ner_key[i]])==1 and (Ner_key[i] == 'price'or Ner_key[i] == 'area (坪)')):
                rent_df = rent_df.loc[rent_df[Ner_key[i]] == float(a_value)]
                del Ner_after[Ner_key[i]]
        
    if (len(Ner_after) != 0):
        for i in range(len(Ner_after)):  # 其他的 Ner select
            rent_df = rent_df.loc[rent_df[list(Ner_after.keys())[i]] == list(
                Ner_after.values())[i][0]]

    
    if(len(rent_df)>0): #output recommend houses
        if(len(rent_df) >= 5): #higher than five results
            sample = []
            sample = random.sample(range(len(rent_df) - 1), 5)
                
        else: #lower than five results
            sample = [*range(0,len(rent_df),1)]

        # 將隨機挑出的資料，轉為list
        result = rent_df.iloc[sample, [2, 4, 6, 7, 8, 18, 19]]
        result_section = result['section'].values.tolist()
        result_title = result['title'].values.tolist()
        result_price = result['price'].values.tolist()
        result_layout = result['layout'].values.tolist()
        result_area = result['area'].values.tolist()
        result_url = result['url'].values.tolist()
        result_pic = result['pic'].values.tolist()
        # 將挑出的資料依序組合成字串
        # result_text = ""
        result_text = {}
        for i in range(len(result)):
            result_list = []
            result_list.append(result_section[i])
            result_list.append(result_title[i])
            result_list.append(result_price[i])
            result_list.append(result_layout[i])
            result_list.append(result_area[i])
            result_list.append(result_url[i])
            result_list.append(result_pic[i])
            result_text[i] = result_list
    else: #no output value
        result_text = "搜尋不到相關物件，未來將會更新，敬請期待"
    return result_text


def chinese_to_arabic(chinese_value): #convert chinese into number
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