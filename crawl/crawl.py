from crawlerutils import CrawlerUtils
import string
from bs4 import BeautifulSoup
import os
import random

def crawl_girl_simple(page):
    print(f"正在爬取第{page}页")
    url = "https://mzt.cx/xinggan/%d/" % page
    response = crwler_utils.get_response(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.find_all("article")
    if not articles:
        print("已经没有了")
    else:
        for article in soup.find_all("article"):
            line = article.find(class_='entry2')
            url = line.find('a')['href']
            print(f"\t{line.text}\t{url}")
            hash_[url] = line.text
        crawl_girl_simple(page + 1)

def carwl_girl_detail():
    for key in hash_:
        set_name = hash_[key]
        crawl_img_url(key, set_name)

def crawl_img_url(url, set_name):
    response = crwler_utils.get_response(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    imgs = soup.findAll(class_='lazyload')
    for img in imgs:
        download_imgs(img['data-original'], set_name)

def get_32_code():
    return  ''.join(random.sample(string.digits + string.ascii_letters[:26], 32)) + '.jpg'

def download_imgs(url, set_name):
    index = 1
    parent_dir = "C:\shy-pictures" if os.name == 'nt' else "/data/shy-pictures"
    response = crwler_utils.get_response(url)
    path = os.path.join(parent_dir, "".join(set_name.split()))
    if not os.path.exists(path):
        os.makedirs(path)
    file_name = os.path.join(path, get_32_code())
    with open(file_name, 'wb') as f:
        print("\t download img " + file_name + " success")
        f.write(response.content)
        f.close()


hash_ = {}
crwler_utils = CrawlerUtils()
if __name__ == '__main__':
    crawl_girl_simple(1)
    carwl_girl_detail()
