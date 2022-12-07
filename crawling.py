# import
import requests                 # 서버 접속
from bs4 import BeautifulSoup   # HTML 해석
import pandas as pd
import re
from konlpy.tag import Okt
from collections import Counter
import sqlite3
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
from os import path
from datetime import datetime

ROOT = path.dirname(path.realpath(__file__))

# 당일 상위 50개 뉴스 제목, 링크 크롤링
def Title_List_Crawling(date):
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"}
    url = f'https://news.naver.com/main/ranking/popularDay.naver?date={date}'
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'lxml')

    all_box = soup.find_all("div", attrs={"class":"rankingnews_box"})   # 신문사별 1~5위 데이터
    all_publish = soup.find_all("strong", attrs={"class":"rankingnews_name"})

    pubList =[]
    limit = 0
    for pub in all_publish:
        if limit >= 10: break   # 10개까지 크롤링
        pubList.append(pub.text)
        limit+=1

    list_all_data = []  # 모든 데이터
    count = 0 # 반복 횟수
    for box in all_box: # 각 신문사별 1-5위 데이터 접근
        list_all_rank = box.find_all("li")  # 1-5위 li 모두 가져오기

        for rank in list_all_rank:  # 5번 반복
            list_data = []  # 각 데이터를 담을 리스트
            if rank.a == None:
                continue
            list_data.append(rank.a.text)       # 뉴스 타이틀
            list_data.append(rank.a['href'])    # 뉴스 링크
            list_data.append(date)              # 발행일
            list_data.append(pubList[count])
            list_all_data.append(list_data)

        count+=1
        if count == 10: break

    # csv로 저장
    # df = pd.DataFrame(list_all_data, columns =['title', 'link', 'date'])
    # df.to_csv(f"{date}NaverNews.csv", encoding='utf-8-sig')
    print('[OK] Title_List_Crawling')
    return list_all_data    # [i][0] : title / [i][1] : link / [i][2] : date / [i][3]: publish


# DB에 Title List 추가
def Add_Title_List(dataset, date):
    con = sqlite3.connect(path.join(ROOT, 'Keyword_Statics.db'))
    cur = con.cursor()
    sql = "INSERT INTO ArticleList(title, link, published_date, publish) values(?,?,?,?)"
    for i in range(len(dataset)):
        cur.execute(sql, (dataset[i][0],dataset[i][1],date,dataset[i][3]))
    con.commit()
    print('[OK] Add_Title_List to DB')

# DB에서 해당 날짜의 Link list 가져오기
def Take_Link_List(date):
    con = sqlite3.connect(path.join(ROOT, 'Keyword_Statics.db'))
    cur = con.cursor()
    sql = "SELECT idx, link FROM ArticleList where published_date =?"
    cur.execute(sql, (date,))
    dataset = cur.fetchall()
    print('[OK] Take_Link_List from DB')
    return dataset # 2차원 rows[0][0] : idx / rows[0][1] : link

# 텍스트 전처리, 한글 정규표현식을 이용해 영어, 숫자 제외하고 결과 변수에 저장
def Text_Cleaning(content):
    hangul = re.compile('[^ ㄱ-ㅣ가-힣+]')
    result = hangul.sub('',content)
    return result

# 내용 크롤링
def Content_Crawling(link):
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"}
    url = link
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'lxml')
    table = soup.find("div", attrs={"class":"go_trans _article_content"})
    content = table.getText()
    content = content.replace("\n","")
    content = Text_Cleaning(content)
    return content

# DateFram
def Make_DataFrame(dataset):
    columns = ['idx', 'content']
    df = pd.DataFrame(columns=columns)
    for i in range(len(dataset)):
        row = [dataset[i][0], Content_Crawling(dataset[i][1])]
        series = pd.Series(row, index=df.columns)
        df = df.append(series, ignore_index=True)
    print('[OK] Make_DataFrame')
    return df

# Count Words
def Count_Words(df):
    # 크롤링한 기사 내용으로 말뭉치 만들기
    content_corpus = ''.join(df['content'].tolist())
    # 키워드 추출
    # Open Korea Text -> Pos(문자열, 품사) : 튜플로 변환, nouns 문자열의 명사 리스트로 반환
    nouns_tagger = Okt()
    nouns = nouns_tagger.nouns(content_corpus)
    count = Counter(nouns)

    # 한글자 키워드 제거(의미없는 경우 많음)
    remove_char_counter = Counter({x: count[x] for x in count if len(x) > 1})

    # 불용어 사전을 통해 키워드 제거
    korean_stopwords_path = "korean_stopwords.txt"
    with open(korean_stopwords_path, encoding='utf-8') as f:
        stopwords = f.readlines()
    stopwords = [x.strip() for x in stopwords]

    news_stopwords=['기자', '매경닷컴']
    for stopword in news_stopwords:
        stopwords.append(stopword)

    remove_char_counter = Counter({x: remove_char_counter[x] for x in count if x not in stopwords })
    print('[OK] Count_Words')
    return remove_char_counter

# Add_Ranked_Tags to DB
def Add_Ranked_Tags(ranked_tags,date):
    con = sqlite3.connect(path.join(ROOT, 'Keyword_Statics.db'))
    cur = con.cursor()
    sql = "INSERT INTO Ranked_Tags(dates, r1,n1,r2,n2,r3,n3,r4,n4,r5,n5,r6,n6,r7,n7,r8,n8,r9,n9,r10,n10,r11,n11,r12,n12,r13,n13,r14,n14,r15,n15,r16,n16,r17,n17,r18,n18,r19,n19,r20,n20,r21,n21,r22,n22,r23,n23,r24,n24,r25,n25,r26,n26,r27,n27,r28,n28,r29,n29,r30,n30) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    cur.execute(sql, (date, ranked_tags[0][0],ranked_tags[0][1], ranked_tags[1][0],ranked_tags[1][1], ranked_tags[2][0],ranked_tags[2][1], ranked_tags[3][0],ranked_tags[3][1], ranked_tags[4][0],ranked_tags[4][1], ranked_tags[5][0],ranked_tags[5][1], ranked_tags[6][0],ranked_tags[6][1], ranked_tags[7][0],ranked_tags[7][1], ranked_tags[8][0],ranked_tags[8][1], ranked_tags[9][0],ranked_tags[9][1], ranked_tags[10][0],ranked_tags[10][1], ranked_tags[11][0],ranked_tags[11][1], ranked_tags[12][0],ranked_tags[12][1], ranked_tags[13][0],ranked_tags[13][1], ranked_tags[14][0],ranked_tags[14][1], ranked_tags[15][0],ranked_tags[15][1], ranked_tags[16][0],ranked_tags[16][1], ranked_tags[17][0],ranked_tags[17][1], ranked_tags[18][0],ranked_tags[18][1], ranked_tags[19][0],ranked_tags[19][1], ranked_tags[20][0],ranked_tags[20][1], ranked_tags[21][0],ranked_tags[21][1], ranked_tags[22][0],ranked_tags[22][1], ranked_tags[23][0],ranked_tags[23][1], ranked_tags[24][0],ranked_tags[24][1], ranked_tags[25][0],ranked_tags[25][1], ranked_tags[26][0],ranked_tags[26][1], ranked_tags[27][0],ranked_tags[27][1], ranked_tags[28][0],ranked_tags[28][1], ranked_tags[29][0],ranked_tags[29][1],))
    con.commit()
    print('[OK] Add_Ranked_Tags to DB')

# 기사와 키워드 연결(최대 3개) - dataset : 2차원 rows[0][0] : idx / rows[0][1] : link
# 해당 기사의 토큰 중 ranked_tag에 해당하는 tag가 있으면 해당 기사 DB에 key1,2,3으로 추가
def Connect_Keyword(dataset,ranked):
    ranked_tags =[]
    for tag in ranked:
        ranked_tags.append(tag[0])

    for data in dataset:
        keywords = []
        idx = data[0]
        link = data[1]
        content = Content_Crawling(link)

        # 토큰으로 분리 후 키워드 리스트에 추가
        nouns_tagger = Okt()
        nouns = nouns_tagger.nouns(content)
        check = 0

        for ranked_tag in ranked_tags:
            if ranked_tag in nouns:
                keywords.append(ranked_tag)
                check += 1
                if check >= 3: break
        if   len(keywords) == 2: keywords.append('None')
        elif len(keywords) == 1: keywords.append('None'); keywords.append('None')
        elif len(keywords) == 0: keywords.append('None'); keywords.append('None'); keywords.append('None')

        # DB에 넣기
        con = sqlite3.connect(path.join(ROOT, 'Keyword_Statics.db'))
        cur = con.cursor()
        sql = "UPDATE  ArticleList SET key1=?, key2=?, key3=? WHERE idx=?"
        cur.execute(sql, (keywords[0],keywords[1],keywords[2],idx,))
        con.commit()
    print('[OK] Connect_Keyword to DB')

# Run_Crawling
def Run_Crawling(date):
    dataset = Take_Link_List(date)              # DB에 저장된 결과 가져오기
    df = Make_DataFrame(dataset)                # 말뭉치 만들기
    result = Count_Words(df)                    # 카운트
    ranked_tags = result.most_common(30)        # 가장 출현 빈도수가 높은 30개의 단어 선정
    print(ranked_tags)
    return ranked_tags

def Make_Cloud_Img(tags, date):
    font='NanumGothic.ttf'  # 폰트
    mask = np.array(Image.open('mask.png')) # 구름 모양의 mask

    # Init WordCloud, 날짜마다 다른 디자인으로
    day = int(date)
    if(day%5 == 0):
        word_cloud = WordCloud(font_path=font, background_color='white',mask = mask, width=1600, height=800,max_font_size=150, colormap='autumn')
    elif(day%5 == 1):
        word_cloud = WordCloud(font_path=font, background_color='white',mask = mask, width=1600, height=800,max_font_size=150, colormap='brg')
    elif(day%5 == 2):
        word_cloud = WordCloud(font_path=font, background_color='white',mask = mask, width=1600, height=800,max_font_size=150, colormap='winter')
    elif(day%5 == 3):
        word_cloud = WordCloud(font_path=font, background_color='white',mask = mask, width=1600, height=800,max_font_size=150, colormap='prism')
    else:
        word_cloud = WordCloud(font_path=font, background_color='white',mask = mask, width=1600, height=800,max_font_size=150, colormap='Dark2')

    word_cloud.generate_from_frequencies(dict(tags))
    plt.figure(figsize=(20, 10)) # Drawing WordCloud
    plt.imshow(word_cloud)
    plt.axis("off")
    # Save Image
    plt.savefig("static\img\Word_Cloud/wc_{0}.png".format(date), bbox_inches='tight')
    print('[OK] Make_Cloud_Img')

def Save_Crawling(date):           # 가장 출현 빈도수가 높은 30개의 단어 선정
    dataset = Take_Link_List(date)             # DB에 저장된 결과 가져오기
    df = Make_DataFrame(dataset)                # 말뭉치 만들기
    result = Count_Words(df)                    # 카운트
    ranked_tags = result.most_common(30)        # 가장 출현 빈도수가 높은 30개의 단어 선정
    Add_Ranked_Tags(ranked_tags,date)           # ranked_tags DB에 저장
    Connect_Keyword(dataset,ranked_tags)       # 해당 기사에 ranked_tag key로 연결
    Make_Cloud_Img(ranked_tags,date)

#------------------------------------------Run!!------------------------------------------
# 크롤링할 날짜
#date = datetime.today().strftime("%Y%m%d") # 시작 전 크롤링 실행
date = "20221124"
for i in range(20221204, 20221208):
    # 최초1회->주석
    date = str(i)
    dataset = Title_List_Crawling(date)             # 50개의 기사 크롤링하기
    Add_Title_List(dataset, date)                   # (최초1회->주석) 크롤링 결과 DB에 저장

    # 반복 실행
    #Run_Crawling(date)                              #  불용어 수정

    # 주석->수정후 실행
    Save_Crawling(date)                           #  DB에 결과 저장

#-----------------------------------------------------------------------------------------
