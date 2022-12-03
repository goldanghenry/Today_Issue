from flask import Flask, url_for, session, render_template, request, redirect, flash
import sqlite3
from dotenv import load_dotenv
from datetime import datetime
import os
from os import path

load_dotenv()       # dotenv()를 사용하기 위해 로드
ROOT = path.dirname(path.realpath(__file__))
app = Flask(__name__)
APP_SECRET_KEY = os.getenv("APP_SECRET_KEY")    # .env에 있는 SECRET_KEY를 가져옴 
app.secret_key = APP_SECRET_KEY                 # flask의 session을 사용하기 위한 secret_key

# 매일 오후 15시에 웹 사이트 업데이트 (스크랩핑은 14:55분에 자동 실행)
# t = datetime.today().strftime("%Y%m%d") 
# day=""
# if datetime.now().hour >= 15:
#     day = t
# else:
#     day = str(int(t)-1)
day = "20221203"

from flask import Flask, url_for, session, render_template, request, redirect, flash
@app.route('/')
def index():
    # 기사 리스트 가져오기
    con = sqlite3.connect(path.join(ROOT, 'Keyword_Statics.db'))
    cur = con.cursor()
    sql = "SELECT * FROM ArticleList"
    cur.execute(sql)
    articleList = cur.fetchall()
    articleList = sorted(articleList, key=lambda x : (x[3], x[4]), reverse=True)

    # 차트를 위해 rank_tags 가져오기
    con = sqlite3.connect(path.join(ROOT, 'Keyword_Statics.db'))
    cur = con.cursor()
    sql = "SELECT * FROM Ranked_Tags WHERE dates=?"
    cur.execute(sql, (day,))
    Ranked_Tags = cur.fetchall()
    Ranked_Tags = Ranked_Tags[0]

    # datelist
    con = sqlite3.connect(path.join(ROOT, 'Keyword_Statics.db'))
    cur = con.cursor()
    sql = "SELECT dates FROM Ranked_Tags"
    cur.execute(sql)
    dateList = cur.fetchall()
    dateList = set(dateList)
    dateList = sorted(dateList, key=lambda x : (x[0]), reverse=True)

    idx = 0
    for d in dateList:
        if d == day:
            break
        idx += 1

    dList = []
    for d in dateList:
        dList.append(d[0][4:8])

    # 스크랩한 기사 표시하기 위해 usertable에서 스크랩 리스트 가져오기
    if 'userName' in session:
        userid = session.get('userId')
        tableName = userid.replace('@','').replace('.','')
        con1 = sqlite3.connect(path.join(ROOT, 'Keyword_Statics.db'))
        cur1 = con1.cursor()
        sql1 = f"SELECT idx FROM {tableName}"
        cur1.execute(sql1)
        list = cur1.fetchall()

        # 2차원 -> 1차원
        scrapList =[]
        for li in list:
            scrapList.append(li[0])
        session['scrapList'] = scrapList

    return render_template('index.html', login=session.get('logFlag'), date=day, articleList=articleList, scrapList=session.get('scrapList'), Ranked_Tags=Ranked_Tags, dateList=dList, idx=0, lightMode = session.get('light'))

@app.route("/goto/<d>")
def indexToDate(d):
    date = "2022"+d
    # 기사 리스트 가져오기
    con = sqlite3.connect(path.join(ROOT, 'Keyword_Statics.db'))
    cur = con.cursor()
    sql = "SELECT * FROM ArticleList"
    cur.execute(sql)
    articleList = cur.fetchall()
    articleList = sorted(articleList, key=lambda x : (x[3], x[4]), reverse=True)

    # 차트를 위해 rank_tags 가져오기
    con = sqlite3.connect(path.join(ROOT, 'Keyword_Statics.db'))
    cur = con.cursor()
    sql = "SELECT * FROM Ranked_Tags WHERE dates=?"
    cur.execute(sql, (date,))
    Ranked_Tags = cur.fetchall()
    Ranked_Tags = Ranked_Tags[0]

    # datelist
    con = sqlite3.connect(path.join(ROOT, 'Keyword_Statics.db'))
    cur = con.cursor()
    sql = "SELECT dates FROM Ranked_Tags"
    cur.execute(sql)
    dateList = cur.fetchall()
    dateList = set(dateList)
    dateList = sorted(dateList, key=lambda x : (x[0]), reverse=True)

    idx = 0
    for d in dateList:
        if d[0] == date:
            break
        idx += 1
    print(idx)

    dList = []
    for d in dateList:
        dList.append(d[0][4:8])

    # 스크랩한 기사 표시하기 위해 usertable에서 스크랩 리스트 가져오기
    if 'userName' in session:
        userid = session.get('userId')
        tableName = userid.replace('@','').replace('.','')
        con1 = sqlite3.connect(path.join(ROOT, 'Keyword_Statics.db'))
        cur1 = con1.cursor()
        sql1 = f"SELECT idx FROM {tableName}"
        cur1.execute(sql1)
        list = cur1.fetchall()

        # 2차원 -> 1차원
        scrapList =[]
        for li in list:
            scrapList.append(li[0])
        session['scrapList'] = scrapList
    return render_template('index.html', login=session.get('logFlag'), date=date, articleList=articleList, scrapList=session.get('scrapList'), Ranked_Tags=Ranked_Tags, dateList=dList, idx=idx, lightMode = session.get('light'))

@app.route("/favorite/<int:idx>")
def favorite(idx):
    # 로그인 체크
    if 'userName' in session:
        #클릭한 뉴스 객체 가져오기
        con = sqlite3.connect(path.join(ROOT, 'Keyword_Statics.db'))
        cur = con.cursor()
        sql = "SELECT * FROM ArticleList WHERE idx=?"
        cur.execute(sql, (idx,))
        selectedN = cur.fetchall()
        selectedN = selectedN[0]

        # 선택한 기사가 이미 user의 스크랩 테이블에 있다면 삭제
        if selectedN[0] in session.get('scrapList'):
            con = sqlite3.connect(path.join(ROOT, 'Keyword_Statics.db'))
            cur = con.cursor()
            userid = session.get('userId')
            tableName = userid.replace('@','').replace('.','')
            sql = f"DELETE FROM {tableName} WHERE idx= ?"
            cur.execute(sql, (selectedN[0],))
            con.commit()
            return redirect(url_for("index"))

        # 없다면 삽입
        else:
            con = sqlite3.connect(path.join(ROOT, 'Keyword_Statics.db'))
            cur = con.cursor()
            userid = session.get('userId')
            tableName = userid.replace('@','').replace('.','')
            sql = f"""
                INSERT INTO {tableName}(idx, title, link, published_date, key1, key2, key3, publish)
                values(?,?,?,?,?,?,?,?)
            """
            cur.execute(sql, (selectedN[0], selectedN[1], selectedN[2], selectedN[3], selectedN[4], selectedN[5], selectedN[6],selectedN[7],))
            con.commit()
            return redirect(url_for("index"))

    # 로그인 되어 있지 않으면 로그인 페이지로 리디렉션
    else:
        flash("스크랩 기능은 로그인을 해야 이용할 수 있습니다.")
        return redirect(url_for("login"))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login_proc', methods=['GET', 'POST'])
def login_proc():
    global loginId
    if request.method == 'POST':
        loginId = request.form['loginId']
        loginPw = request.form['loginPw']

    elif request.method == 'GET':
        loginId = request.args.get('loginId')
        loginPw = request.args.get('loginPw')

    if len(loginId) == 0:
        flash("Please Enter Email")
        return redirect(url_for("login"))
    elif len(loginPw) == 0:
        flash("Please Enter Password")
        return redirect(url_for("login"))

    else:
        con = sqlite3.connect(path.join(ROOT, 'Keyword_Statics.db'))
        cur = con.cursor()
        sql = "SELECT * FROM USERLIST where userId =?"
        cur.execute(sql, (loginId,))
        rows = cur.fetchall()

        for rs in rows:
            if loginId == rs[1] and loginPw == rs[3]:
                session['logFlag'] = True
                session['idx'] = rs[0]
                session['userId'] = rs[1]
                session['userName'] = rs[2]
                return redirect(url_for("index"))
            else:
                flash("Please check your Email or password")
                return redirect(url_for("login"))   # 팝업 추가!

        flash("Please check your Email or password")
        return redirect(url_for("login"))

@app.route('/register', methods=['GET', 'POST'])
def register():
    # form에서 가져오기
    if request.method == 'POST':
        _id_ = request.form['registerId']
        _username_ = request.form['registerUsername']
        _password_ = request.form['registerPw']

    elif request.method =='GET':
        _id_ = request.args.get('registerId')
        _username_ = request.args.get('registerUsername')
        _password_ = request.args.get('registerPw')
    tableName = _id_.replace('@','').replace('.','')

    # 양식 확인
    if len(_id_) == 0:
        flash("Please Enter Email")
        return redirect(url_for("login"))
    if len(_username_) == 0:
        flash("Please Enter User name")
        return redirect(url_for("login"))
    if len(_password_) == 0:
        flash("Please Enter Password")
        return redirect(url_for("login"))

    # 닉네임 중복 확인
    con = sqlite3.connect(path.join(ROOT, 'Keyword_Statics.db'))
    cur = con.cursor()
    sql = "SELECT userId FROM USERLIST where userId =?"
    cur.execute(sql, (_id_,))
    result = cur.fetchall()

    if result:
        flash("User name already in use.\nPlease enter another name.")
        return redirect(url_for("login"))

    else:
        # DB에 회원가입 정보 삽입
        sql = """
            INSERT INTO USERLIST(userId, userName, userPw)
            values(?,?,?)
        """
        cur.execute(sql, (_id_,_username_,_password_,))
        con.commit()

        # DB에 유저 북마크 table 생성
        con = sqlite3.connect(path.join(ROOT, 'Keyword_Statics.db'))
        cur = con.cursor()

        print(tableName)
        sql =f"""
            create table {tableName} (
                idx integer not null,
                title text not null,
                link text not null,
                published_date text not null,
                key1 text not null,
                key2 text not null,
                key3 text not null,
                publish text not null)
        """
        cur.execute(sql)
        flash("Membership successful!\nPlease login")
        return redirect(url_for("login"))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/bookmarks')
def bookmarks():
    # 로그인 검사
    if 'userName' in session:
        # 기사 리스트 가져오기
        userid = session.get('userId')
        tableName = userid.replace('@','').replace('.','')

        con = sqlite3.connect(path.join(ROOT, 'Keyword_Statics.db'))
        cur = con.cursor()
        sql = f"SELECT * FROM {tableName}"
        cur.execute(sql)
        list = cur.fetchall()
        list = sorted(list, key=lambda x : (x[3], x[4]), reverse=True)
        return render_template('bookmarks.html', userName=session.get("userName"), login=session.get('logFlag'), articleList=list, lightMode = session.get('light'))
    # 로그인 하지 않으면 로그인 페이지로 이동
    else:
        flash("북마크 페이지는 로그인을 해야 이용할 수 있습니다.")
        return redirect(url_for("login"))

@app.route("/favorite1/<int:idx>")
def favorite1(idx):
    #클릭한 뉴스 객체 가져오기
    con = sqlite3.connect(path.join(ROOT, 'Keyword_Statics.db'))
    cur = con.cursor()
    sql = "SELECT * FROM ArticleList WHERE idx=?"
    cur.execute(sql, (idx,))
    selectedN = cur.fetchall()
    selectedN = selectedN[0]

    con = sqlite3.connect(path.join(ROOT, 'Keyword_Statics.db'))
    cur = con.cursor()
    userid = session.get('userId')
    tableName = userid.replace('@','').replace('.','')
    sql = f"DELETE FROM {tableName} WHERE idx= ?"
    cur.execute(sql, (selectedN[0],))
    con.commit()
    return redirect(url_for("index"))

@app.route('/charts')
def charts():
    # datelist
    con = sqlite3.connect(path.join(ROOT, 'Keyword_Statics.db'))
    cur = con.cursor()
    sql = "SELECT dates FROM Ranked_Tags"
    cur.execute(sql)
    dateList = cur.fetchall()
    dateList = set(dateList)
    dateList = sorted(dateList, key=lambda x : (x[0]), reverse=True)

    dList = []
    for d in dateList:
        dList.append(d[0][4:8])
    return render_template('charts.html', dateList=dList, lightMode = session.get('light'))

@app.route('/layout-sidenav-light')
def light():
    if 'light' in session:
        if session['light'] == True:
            session['light'] = False
        else:
            session['light'] = True
    else:
        session['light'] = True
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(debug=True)