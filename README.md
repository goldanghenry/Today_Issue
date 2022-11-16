# Today_Issue
A website that crawls keywords of articles related to it and displays it in word cloud

# Web-Site url : https://goldanghenry.pythonanywhere.com/
[ project ]
- subject : 오늘의 이슈
- describe : 매일의 이슈를 워드 클라우드와 키워드 수, 기사 리스트를 보여준다
- structure
    - flask 프레임워크를 기반으로 한 웹 어플리케이션
    - DB : SQLite
    - hosting : python anywhere

<작업 노트>
< 현재 작업 >
	- APP 키 암호화 ( git ignore )
	- 서버에서 자동으로 크롤링 실행
    

< 지난 작업 >
1. 부트스트랩 flask 환경에 맞게 적용
    - html은 templates, 나머지는 static
    - flask route로 페이지 연결

2. 로그인, 회원가입 페이지 생성 및 DB에 적용
    - 회원가입시 DB에 개인 북마크 table 생성
    - 북마크 페이지 접근시 sesstion으로 로그인 체크

3. 네이버 기사 크롤링
    - 해당 날짜, 신문사별 많이본 뉴스(1-5위)의 링크 50개 크롤링 -> title, link, date DB 저장
    - 50개 링크를 방문하며 기사 내용 크롤링해서 말뭉치 생성
    - 한국어 정규식, 불용어 등 텍스트 전처리 후 명사 뽑아내기 
    - 상위 30개 단어(rank_tag) 리스트 DB에 저장
    - 50개 link를 다시 방문해 기사 내용을 텍스트 전처리 후 명사 리스트 중 rank_tag에 해당하는 것이 있다면 DB에 해당 기사의 key에 추가(최대 3개)

4. 워드 클라우드
    - DB에 저장된 rank_tag를 가져와 이미지로 저장

5. 메인 페이지 동적 구성
    - index.html : 당일에 해당하는 내용
    - /<int:date> : 선택한 날짜에 해당하는 내용을 DB에서 불러와서 구성
    - 슬라이드 메뉴로 구성

6. 키워드 랭킹
    - js chart -> 동적으로 그 날에 해당하는 랭킹을 DB에서 가져와 출력

7. 북마크 버튼
    - ☆버튼 클릭시, 로그인 체크, 개인 테이블에 기사 추가 후 채워진 ★로 변경
    - 북마크 페이지 그리기

8. 워드 클라우드 페이지
    - 최근 날짜부터 DB에 클롤링된 날까지 출력
    - % 연산자로 날마다 다른 colormap


