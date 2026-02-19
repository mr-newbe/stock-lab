#before using this, you have to install beautiful soup with terminal odering "pip install beautifulsoup4"

from bs4 import BeautifulSoup
import re

class Crawler:
  def __init__(self):
    #div > ul > li 의 구조로 된 html을 크롤링하기 위한 샘플 소스
    self.html_doc = """
      <html>
        <head>
          <title>Home</title>
        </head>
        <body>
          <div class="section">
            <h2>영역 제목</h2>
            <ul>
              <li><a href="/news/news1">기사 제목1</a></li>
              <li><a href="/news/news2">기사 제목2</a></li>
              <li><a href="/news/news3">기사 제목3</a></li>
            </ul>
          </div>
        </body>
    </html>
    """
    #테이블 구조로 된 html을 크롤링하기 위한 구조
    self.html_table"""
    <html>
      <div class="aside_section">
        <table class="tbl">
          <thead>
            <tr>
              <th scope="col">컬럼1</th>
              <th scope="col">컬럼2</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th><a href="/aside1">항목1</a></th>
              <td>항목1값1</td>
              <td>항목1값2</td>
            </tr>
            <tr>
              <th><a href="/aside1">항목2</a></th>
              <td>항목2값1</td>
              <td>항목2값2</td>
            </tr>
          </tbody>
        </table>
      </div>
    </html>
    """
  def get_news_section(self):
    #soup 객체 생성(html_doc 전달, 그리고 이걸 파싱할 때 html.parser 사용 명시)
    soup = BeautifulSoup(self.html_doc, 'html.parser')
    print(soup.prettify())
    #이제 생성된 soup 객체에서 html의 요소에 . 또는 []을 통해서 접근할 수 있습니다.
    print("title", soup.title)
    #<title>Home</title>
    print("title string", soup.title.string)
    #Home
    print("title parent name", soup.title.parent.name)
    #head
    print("div", soup.div)
    """
    <div class="section">
      <h2>영역 제목</h2>
      <ul>
        <li><a href="/news/news1">기사 제목1</a></li>
        <li><a href="/news/news2">기사 제목2</a></li>
        <li><a href="/news/news3">기사 제목3</a></li>
      </ul>
    </div>
    """
    print("div class", soup.div['class'])
    """
    <li><a href="/news/news1">기사 제목1</a></li>
    <li><a href="/news/news2">기사 제목2</a></li>
    <li><a href="/news/news3">기사 제목3</a></li>
    """
    #find_all 메서드는 원하는 태그를 찾기 위한 메서드이며, 그 태그들과 그 내부 요소들을 전부 끌고옵니다. 
    #class_  라고 쓴 이윤 class가 이미 정의되어 있기 때문에...
    print("find class section", soup.find_all(class_="section"))
    """
    [    <div class="section">
            <h2>영역 제목</h2>
            <ul>
              <li><a href="/news/news1">기사 제목1</a></li>
              <li><a href="/news/news2">기사 제목2</a></li>
              <li><a href="/news/news3">기사 제목3</a></li>
            </ul>
          </div>
    ]
    """
    print("find href", soup.find_all(href=re.compile("/news")))
    #앵커 태그만 추출됨
    for news in news_list:
      print(news["href"])
      print(news.string)
    """
    /news/news1
    기사제목1
    ...
    이런 형식으로 기사 제목들이 출력된다.
    """

  def get_side(self):
    soup = BeautifulSoup(self.html_table, 'html.parser')
    print("table", soup.table)
    print("thead th", soupt.thead.find_all(scope=re.compile("col")))
    """
          <thead>
            <tr>
              <th scope="col">컬럼1</th>
              <th scope="col">컬럼2</th>
            </tr>
          </thead>
    """
    col_list = [col.string for col in soup.thead.find_all(scope=re.compile("col"))]
    print(col_list)
    #['컬럼1', '컬럼2']
    tr_list = soup.tbody.find_all("tr")
    print("tr list", tr_list)
    """
            <tr>
              <th><a href="/aside1">항목1</a></th>
              <td>항목1값1</td>
              <td>항목1값2</td>
            </tr>
            <tr>
              <th><a href="/aside1">항목2</a></th>
              <td>항목2값1</td>
              <td>항목2값2</td>
            </tr>
    """
    for tr in tr_list:
      for td in tr.find_all("td"):
        print("tr td", td.string)
    """
    tr td 항목1값1
    tr td 항목1값2
    tr td 항목2값1
    tr td 항목2값2
    """

if __name__ == "__main__":
  crawler = Crawler()
  crawler.get_news_section()
  crawler.get_side()
  
