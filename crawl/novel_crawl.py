import requests
import MySQLdb
import MySQLdb.cursors
from bs4 import BeautifulSoup
import re
from urllib.parse import quote

db = None
cursor = None
novel_id = None
novel_url = None
novel_title = None
novel_type = None
novel_type_id = None
search_novel = []

def connect_db():
    global db
    global cursor
    db = MySQLdb.connect('localhost', 'root', 'root', 'read_book', charset = 'utf8', cursorclass = MySQLdb.cursors.DictCursor)
    cursor = db.cursor()

def log(text, level = 'crawl'):
    sql = "INSERT INTO log(`level`, `text`) VALUES ('%s', '%s')" % (level, text)
    cursor.execute(sql)
    db.commit()

def get_soup(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup

# def get_novel_type_id(soup):
#     pattern = re.compile(u"[\u4e00-\u9fa5]+")
#     result = re.findall(pattern, soup.select("div.con_top")[0].get_text())
#     # sql = "SELECT id FROM novel_type where `type` = '%s';" %  result[3][:2]
#     # cursor.execute(sql)
#     # return int(cursor.fetchone()['id'])
#     type_h = {
#         "玄幻": 1,
#         "修真": 2,
#         "都市": 3,
#         "穿越": 4,
#         "网游": 5,
#         "科幻": 6,
#     }
#     return type_h[result[3][:2]]

def get_novel_type_id():
    type_h = {
        "玄幻": 1,
        "修真": 2,
        "都市": 3,
        "穿越": 4,
        "网游": 5,
        "科幻": 6,
    }
    return type_h[novel_type]

def query_by_novel_title():
    sql = "SELECT * from novel WHERE novel_title = '%s'" % novel_title
    cursor.execute(sql)
    return cursor.fetchone()

def insert_novel():
    global novel_id
    # check if it is empty and print error
    record = query_by_novel_title()
    if not record:
        sql = "INSERT into `novel`(`novel_title`, `novel_type_id`, `url`) VALUES ('%s', %d, '%s')" % (novel_title, novel_type_id, novel_url)
        cursor.execute(sql)
        novel_id = db.insert_id()
        db.commit()
        print("Get new one")
    else:
        novel_id = record['id']
        print("It's already in the database")

def insert_novel_detail(novel_detail_title, novel_detail_body):
    sql = "INSERT into `novel_detail`(`novel_id`, `novel_detail_title`, `novel_detail_body`) VALUES (%d, '%s', '%s')" % (novel_id, novel_detail_title, novel_detail_body)
    cursor.execute(sql)
    db.commit()
    print(f"insert {novel_detail_title}")

# capture detail url
# return : Ordered novel_detail URLs
def query_detail_urls(url):
    soup = get_soup(url)
    urls = list(set([i.get('href') for i in soup.select('div#list dd a')]))
    return sorted(urls, key=lambda url:int(re.match('(\d+)', url)[0]))

def save_detail(url):
    soup = get_soup(novel_url + url)
    novel_detail_title = soup.find('h1').get_text()
    detail_body = soup.select("div#content")[0].get_text().replace("\xa0", "\n")
    novel_detail_body = "".join(detail_body.split(" ！")[1:])
    insert_novel_detail(novel_detail_title, novel_detail_body)

def choose_novel():
    global novel_url
    global novel_type
    global novel_type_id
    print("index\tname-author")
    for i, value in enumerate(search_novel):
        print(str(i) + "\t" + value[0])
    index = input("please enter index to choose novel to crawl:")
    novel_url = search_novel[index][1]
    novel_type = search_novel[index][2][:2]
    novel_type_id = get_novel_type_id()

def set_novel_attribute(soup):
    global novel_url
    global novel_type
    global novel_type_id
    novel_url = soup.link.get('href')
    pattern = re.compile(u"[\u4e00-\u9fa5]+")
    novel_type = re.findall(pattern, soup.select("div.con_top")[0].get_text())[3][:2]
    novel_type_id = get_novel_type_id()


def get_search_results():
    url = "https://www.xbiquge.cc/modules/article/search.php?searchkey=" + quote(novel_title.encode("gb2312"))
    soup = get_soup(url)
    if soup.find('div', {'class', 'novelslistss'}):
        for li in soup.select("div.novelslistss > li"):
            """
            e.g.
            (novel_title,author,novel_type)
            (万古最强赘婿,徐小逗,都市小说)
            """
            search_novel.append((li.find('a').text + " - " + li.find('span', {'class': 's4'}).text, li.find('a').get('href'), li.span.text, ))
            choose_novel()
    else:
        set_novel_attribute(soup)
    insert_novel()

def _crawl():
    urls = query_detail_urls(novel_url)
    for url in urls:
        save_detail(url)

def crawl():
    # log(text='start crawl')
    connect_db()
    get_search_results()
    _crawl()

if __name__ == '__main__':
    print("start work")
    novel_title = input("please input keyword to search novel(no errors are allowed):")
    crawl()
    # crawl("https://www.xbiquge.cc/book/4772/")
