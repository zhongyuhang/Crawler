import requests
import MySQLdb
import MySQLdb.cursors
from bs4 import BeautifulSoup
import re

db = None
cursor = None
novel_id = None

def connect_db():
    global db
    global cursor
    db = MySQLdb.connect('localhost', 'root', 'root', 'read_book', charset = 'utf8', cursorclass = MySQLdb.cursors.DictCursor)
    cursor = db.cursor()

def log(text, level = 'crawl'):
    sql = "INSERT INTO log(`level`, `text`) VALUES ('%s', '%s')" % (level, text)
    cursor.execute(sql)
    db.commit()

def get_novel_type_id(soup):
    pattern = re.compile(u"[\u4e00-\u9fa5]+")
    result = re.findall(pattern, soup.select("div.con_top")[0].get_text())
    # sql = "SELECT id FROM novel_type where `type` = '%s';" %  result[3][:2]
    # cursor.execute(sql)
    # return int(cursor.fetchone()['id'])
    type_h = {
        "玄幻": 1,
        "修真": 2,
        "都市": 3,
        "穿越": 4,
        "网游": 5,
        "科幻": 6,
    }
    return type_h[result[3][:2]]

def query_by_novel_title(novel_title):
    sql = "SELECT * from novel WHERE novel_title = '%s'" % novel_title
    cursor.execute(sql)
    return cursor.fetchone()

def insert_novel(soup):
    global novel_id
    novel_type_id = get_novel_type_id(soup)
    novel_title = soup.find('h1').get_text()
        # check if it is empty and print error
    record = query_by_novel_title(novel_title)
    if not record:
        sql = "INSERT into `novel`(`novel_title`, `novel_type_id`) VALUES ('%s', %d)" % (novel_title, novel_type_id)
        cursor.execute(sql)
        novel_id = db.insert_id()
        db.commit()
    else:
        novel_id = record['id']

def insert_novel_detail(novel_detail_title, novel_detail_body):
    sql = "INSERT into `novel_detail`(`novel_id`, `novel_detail_title`, `novel_detail_body`) VALUES (%d, '%s', '%s')" % (novel_id, novel_detail_title, novel_detail_body)
    cursor.execute(sql)
    db.commit()
    print(f"insert {novel_detail_title}")

# capture detail url
# return : Ordered novel_detail URLs
def get_detail_urls(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    insert_novel(soup)
    urls = list(set([i.get('href') for i in soup.select('div#list dd a')]))
    return sorted(urls, key=lambda url:int(re.match('(\d+)', url)[0]))

def save_detail(urls):
    for url in urls:
        r = requests.get("https://www.xbiquge.cc/book/4772/" + url)
        soup = BeautifulSoup(r.content, 'html.parser')
        novel_detail_title = soup.find('h1').get_text()
        detail_body = soup.select("div#content")[0].get_text().replace("\xa0", "\n")
        novel_detail_body = "".join(detail_body.split(" ！")[1:])
        insert_novel_detail(novel_detail_title, novel_detail_body)

def crawl(url):
    # log(text='start crawl')
    connect_db()
    urls = get_detail_urls(url)
    save_detail(urls)

if __name__ == '__main__':
    crawl("https://www.xbiquge.cc/book/4772/")
