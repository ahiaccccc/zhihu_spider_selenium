#################
###ZouJiu-202306
#################
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver import EdgeOptions
import os
from selenium.webdriver.common.by import By
import time
import pickle
import json
from selenium.webdriver.support.wait import WebDriverWait
import requests
from copy import deepcopy
import argparse
from datetime import datetime
# from selenium.webdriver.common import keys
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
# import numpy as np
import shutil
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.print_page_options import PrintOptions
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
import base64
from zipfile import ZipFile
from bs4 import BeautifulSoup
import re
import platform

abspath = os.path.abspath(__file__)
filename = abspath.split(os.sep)[-1]
abspath = abspath.replace(filename, "")

import sys
sys.path.append(abspath)
# wkhtmltopdf_path = os.path.join(abspath, r'wkhtmltopdf\bin\wkhtmltopdf.exe')
# sys.path.append(wkhtmltopdf_path)
from thinkdeal import *

def save_cookie(driverkkk, path):
    #https://stackoverflow.com/questions/45417335/python-use-cookie-to-login-with-selenium
    with open(path, 'wb') as filehandler:
        pickle.dump(driverkkk.get_cookies(), filehandler)

def load_cookie(driverkkk, path):
    #https://stackoverflow.com/questions/45417335/python-use-cookie-to-login-with-selenium
     with open(path, 'rb') as cookiesfile:
         cookies = pickle.load(cookiesfile)
         for cookie in cookies:
             driverkkk.add_cookie(cookie)

def crawlsleep(times):
    time.sleep(times)

def now():
    return time.time()

def nowtime():
    nowtm = datetime.fromtimestamp(time.time()).isoformat().replace(":", "_")
    return nowtm

def edgeopen(driverpath):
    service=Service(executable_path=driverpath)
    edge_options = EdgeOptions()

    #https://stackoverflow.com/questions/53039551/selenium-webdriver-modifying-navigator-webdriver-flag-to-prevent-selenium-detec
    edge_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    edge_options.add_experimental_option('useAutomationExtension', False)
    edge_options.add_argument('lang=zh-CN,zh,zh-TW,en-US,en')
    edge_options.add_argument("disable-blink-features=AutomationControlled")#就是这一行告诉chrome去掉了webdriver痕迹
    
    # #https://stackoverflow.com/questions/56897041/how-to-save-opened-page-as-pdf-in-selenium-python
    # settings = {
    #     "recentDestinations": [{
    #             "id": "Save as PDF",
    #             "origin": "local",
    #             "account": "",
    #         }],
    #         "selectedDestinationId": "Save as PDF",
    #         "version": 2
    #     }
    # #https://www.apiref.com/java11-zh/java.desktop/javax/print/attribute/standard/MediaSize.ISO.html
    # settings = {
    #     "recentDestinations": [{
    #         "id": "Save as PDF",
    #         "origin": "local",
    #         "account": ""
    #     }],
    #     "selectedDestinationId": "Save as PDF",
    #     "version": 2,
    #     "isHeaderFooterEnabled": False,
    #     "mediaSize": {
            
    #         "height_microns": 297000,
    #         "name": "ISO_A4",
    #         "width_microns": 210000,
    #         "custom_display_name": "A4"
    #     },
    #     "customMargins": {"margin": 0},
    #     "marginsType": 3,
    #     # "scaling": 130,
    #     # "scalingType": 3,
    #     # "scalingTypePdf": 3,
    #     "isCssBackgroundEnabled": True
    # }
    # prefs = {
    #     'printing.print_preview_sticky_settings.appState': json.dumps(settings),
    #     'savefile.default_directory': pdfpath,
    #     }
    # edge_options.add_experimental_option('prefs', prefs)
    # edge_options.add_argument('--kiosk-printing')

    # https://www.selenium.dev/documentation/webdriver/drivers/options/#pageloadstrategy  
    # https://stackoverflow.com/questions/44503576/selenium-python-how-to-stop-page-loading-when-certain-element-gets-loaded
    # edge_options.add_argument(page_load_strategy, 'normal')
    # if strategy:
    edge_options.page_load_strategy = 'normal'
    # cap = DesiredCapabilities.EDGE
    # cap['pageLoadStrategy'] = 'none'
    
    driver = webdriver.Edge(options=edge_options, service = service)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
    driver.set_script_timeout(20)
    
    return driver


def login(driver):
    driver.get(r"https://www.zhihu.com/")
    try:
        driver.find_elements(By.CLASS_NAME, "SignFlow-tab")[1].click()
    except:
        pass
    toggle = []
    ti = 1
    while toggle==[] and ti < 600:
        toggle = driver.find_elements(By.ID, 'Popover15-toggle')
        time.sleep(3)
        if ti%10==0:
            print("等待输入账号并点击登录，登录以后请不要执行任何操作，10分钟后自动退出.........")
        ti += 3
    toggle = driver.find_elements(By.ID, 'Popover15-toggle')
    if toggle==[]:
        print("还没有登陆的，还请登录保存cookie.......")
        driver.quit()
        exit(0)
    # driver.find_elements(By.CLASS_NAME, "username-input")[0].send_keys("")
    # driver.find_elements(By.CLASS_NAME, "username-input")[1].send_keys("")
    # driver.find_element(By.CLASS_NAME, "SignFlow-submitButton").click()
    # time.sleep(130)
    # WebDriverWait(driver, timeout=60).until(lambda d:d.find_element(By.CLASS_NAME, "TopstoryTabs-link"))
    return driver

# Function to check if a link already exists in a file
def link_exists(file_path, link):
    if not os.path.exists(file_path):
        return False
    with open(file_path, 'r', encoding='utf-8') as file:
        return link in file.read()

#通过当前网页获取所有该专栏下所有的链接
def getZhuanlanLinks(driver:webdriver):

    #从zhuanlan_links。txt中读取所有的专栏链接
    with open('zhuanlan_links.txt', 'r', encoding='utf-8') as file:
        zhuanlan_links = file.read().splitlines()
    #遍历所有的专栏链接
    for zhuanlan_link in zhuanlan_links:
        driver.get(zhuanlan_link)
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            # 下滑页面到底部
            ActionChains(driver).scroll_by_amount(0, last_height).perform()
            time.sleep(2)  # 等待页面加载

            # 获取新的页面高度
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # 提取文章链接
        article_elements = driver.find_elements(By.CLASS_NAME, 'ContentItem-title')
        article_links = [element.find_element(By.TAG_NAME, 'a').get_attribute('href') for element in article_elements]
        # 提取文章标题
        article_titles = [element.text for element in article_elements]

        # 保存到文件
        for link, title in zip(article_links, article_titles):
            if 'zhuanlan.zhihu.com/p/' in link:
                file_path = 'zhuanlan_article_links.txt'
            elif 'zhihu.com/question/' in link and '/answer/' in link:
                file_path = 'zhuanlan_answer_links.txt'
                #将形如https://www.zhihu.com/question/461799142/answer/1916419052的link的/answer/1916419052去掉
                link = link.split('/answer/')[0]
            elif 'zhihu.com/zvideo/' in link:
                print(f"视频链接: {link}")
                continue  # Skip video links
            else:
                print(f"未知的链接格式: {link}")
                continue  # Skip other unknown formats

            # Check for duplicates
            if link_exists(file_path, link):
                print(f"链接已存在: {link}")
                continue

            # Save the link and title to the appropriate file
            with open(file_path, 'a', encoding='utf-8') as file:
                file.write(f'{link} {title}\n')



def crawl_article_links(driver:webdriver, username:str):
    #crawl articles links
    articles = r'https://www.zhihu.com/people/zoujiu1/posts'
    articles_one = r'https://www.zhihu.com/people/zoujiu1/posts?page='
    article_detail = r'https://zhuanlan.zhihu.com/p/'

    driver.get(articles.replace("zoujiu1", username))
    try:
        WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(By.CLASS_NAME, "Pagination"))
        pages = driver.find_elements(By.CLASS_NAME, 'PaginationButton')[-2]
        assert isinstance(int(pages.text), int)
        maxpages = int(pages.text)
    except:
        pages = driver.find_elements(By.CLASS_NAME, 'PaginationButton')
        if len(pages)==0:
            maxpages = 1
        else:
            pages = pages[-2]
            assert isinstance(int(pages.text), int)
            maxpages = int(pages.text)
    
    all_article_detail = {}
    #how many pages of articles
    for p in range(1, maxpages + 1):
        driver.get(articles_one + str(p))
        WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(By.CLASS_NAME, "ArticleItem"))
        items = driver.find_elements(By.CLASS_NAME, "ArticleItem")
        #crawl article one by one
        for a in range(len(items)):
            introduce = items[a].get_attribute("data-zop")
            itemId = json.loads(introduce)
            links = items[a].find_elements(By.TAG_NAME, 'a')[0].get_attribute('href')
            # id = itemId['itemId']
            title = str(itemId['title']).strip()
            all_article_detail[str(title)] = links #article_detail + str(id)
        crawlsleep(sleeptime)
    with open(os.path.join(articledir, 'article.txt'), 'w', encoding='utf-%d'%(6+2)) as obj:
        for key, val in all_article_detail.items():
            obj.write(val + " " + key + '\n')

def crawl_answers_links(driver:webdriver, username:str):
    #crawl answers links
    answer = r'https://www.zhihu.com/people/zoujiu1/answers'
    answer_one = r'https://www.zhihu.com/people/zoujiu1/answers?page='

    driver.get(answer.replace("zoujiu1", username))
    try:
        WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(By.CLASS_NAME, "Pagination"))
        pages = driver.find_elements(By.CLASS_NAME, 'PaginationButton')[-2]
        assert isinstance(int(pages.text), int)
        maxpages = int(pages.text)
    except:
        pages = driver.find_elements(By.CLASS_NAME, 'PaginationButton')
        if len(pages)==0:
            maxpages = 1
        else:
            pages = pages[-2]
            assert isinstance(int(pages.text), int)
            maxpages = int(pages.text)
    
    all_answer_detail = []
    #how many pages of answers
    for p in range(1, maxpages + 1):
        driver.get(answer_one + str(p))
        WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(By.CLASS_NAME, "Pagination"))
        items = driver.find_elements(By.CLASS_NAME, "AnswerItem")
        #crawl answer one by one
        for i in range(len(items)):
            introduce = items[i].get_attribute("data-zop")
            itemId = json.loads(introduce)
            id = itemId['itemId']
            title = str(itemId['title'])
            links = items[i].find_elements(By.TAG_NAME, 'a')[0].get_attribute('href')
            all_answer_detail.append([links, str(title)])
        crawlsleep(sleeptime)
    with open(os.path.join(answerdir, 'answers.txt'), 'w', encoding='utf-8') as obj:
        for links, title in all_answer_detail:
            obj.write(links + " " + title + '\n')

def crawl_think_links(driver:webdriver, username:str):
    #crawl think links
    think = r'https://www.zhihu.com/people/zoujiu1/pins'
    think_one = r'https://www.zhihu.com/people/zoujiu1/pins?page='

    driver.get(think.replace("zoujiu1", username))
    try:
        WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(By.CLASS_NAME, "Pagination"))
        pages = driver.find_elements(By.CLASS_NAME, 'PaginationButton')[-2]
        assert isinstance(int(pages.text), int)
        maxpages = int(pages.text)
    except:
        pages = driver.find_elements(By.CLASS_NAME, 'PaginationButton')
        if len(pages)==0:
            maxpages = 1
        else:
            pages = pages[-2]
            assert isinstance(int(pages.text), int)
            maxpages = int(pages.text)
    
    # all_think_detail = []
    #how many pages of think
    allbegin = now()
    numberpage = 1e-6        
    for p in range(1, maxpages + 1):
        driver.get(think_one + str(p))
        WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(By.CLASS_NAME, "Pagination"))
        items = driver.find_elements(By.CLASS_NAME, "PinItem")
        #crawl answer one by one
        for i in range(len(items)):
            begin = now()
            RichContent = items[i].find_element(By.CLASS_NAME, 'RichContent-inner')
            clockitem = items[i].find_element(By.CLASS_NAME, 'ContentItem-time')
            try:
                WebDriverWait(items[i], timeout=10).until(lambda d: len(d.text) > 2)
            except:
                driver.get(think_one + str(p))
                WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(By.CLASS_NAME, "Pagination"))
                items = driver.find_elements(By.CLASS_NAME, "PinItem")
                RichContent = items[i].find_element(By.CLASS_NAME, 'RichContent-inner')
                clockitem = items[i].find_element(By.CLASS_NAME, 'ContentItem-time')
                WebDriverWait(items[i], timeout=10).until(lambda d: len(d.text) > 2)
            # clockspan = clockitem.find_element(By.TAG_NAME, 'span')
            clock = clockitem.text
            clock = clock[3 + 1:].replace(":", "_")
            dirthink = os.path.join(thinkdir, clock)
            if os.path.exists(dirthink):
                print(f"{dirthink}已经爬取过了，不再重复爬取")
                continue
            os.makedirs(dirthink, exist_ok=True)
            try:
                RichContent.find_element(By.CLASS_NAME, 'Button').click()
                WebDriverWait(items[i], timeout=10).until(lambda d: d.find_element(By.CLASS_NAME, "RichContent-inner"))
                RichContent = items[i].find_element(By.CLASS_NAME, 'RichContent-inner')
            except:
                pass
            content = RichContent.find_element(By.CLASS_NAME, 'RichText')
            links_col = content.find_elements(By.TAG_NAME, 'a')
            links = []
            for itext in links_col:
                try:
                    links.append(itext.get_attribute("href"))
                except:
                    continue
            text = content.text.strip()
            if len(text)!=0:
                with open(os.path.join(dirthink, clock+".txt"), 'w', encoding='utf-8') as obj:
                    obj.write(text.replace("<br>", '\n').replace("<br data-first-child=\"\">", '\n')+"\n")
                    for itext in links:
                        obj.write(itext + "\n")
                    # all_think_detail.append([text])
            try:
                items[i].find_elements(By.CLASS_NAME, 'Image-PreviewVague')[0].click()
            except:
                continue
            cnt = 0
            while True:
                WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(By.CLASS_NAME, "ImageGallery-Inner"))
                img = driver.find_element(By.CLASS_NAME, 'ImageGallery-Inner').find_element(By.TAG_NAME, 'img')
                imglink = img.get_attribute('data-original')
                if imglink==None:
                    imglink = img.get_attribute("src")
                try:
                    response = requests.get(imglink, timeout=30)
                except:
                    try:
                        response = requests.get(imglink, timeout=30)
                    except:
                        continue
                if response.status_code==200:
                    with open(os.path.join(dirthink, clock + "_" + str(cnt) + '.jpg'), 'wb') as obj:
                        obj.write(response.content)
                    cnt += 1
                    crawlsleep(sleeptime)
                try:
                    disable = driver.find_element(By.CLASS_NAME, 'ImageGallery-arrow-right')
                    if 'disabled' in disable.get_attribute('class'):
                        driver.find_element(By.CLASS_NAME, 'ImageGallery-close').click()
                        break
                    else:
                        disable.click()
                except:
                    break
            crawlsleep(sleeptime)
            end = now()
            print("爬取一篇想法耗时：", clock,  round(end - begin, 3))
            logfp.write("爬取一篇想法耗时：" +clock + " "+ str(round(end - begin, 3)) + "\n")
        numberpage += 1
        # crawlsleep(600)
    allend = now()
    print("平均爬取一篇想法耗时：", round((allend - allbegin) / numberpage, 3))
    logfp.write("平均爬取一篇想法耗时：" + str(round((allend - allbegin) / numberpage, 3)) + "\n")
    
    dealthink(thinkdir)

def cleartxt(kkk):
    while ' 'in kkk:
        kkk = kkk.replace(" ", "")
    while "\n" in kkk:
        kkk = kkk.replace("\n", "")
    return kkk

def parser_beautiful(innerHTML, article, number, dircrea, bk=False):
    if not innerHTML:
        return article, number
    # if bk:
    #     article += "**"
    if isinstance(innerHTML, str):
        article += innerHTML.text
        return article, number

    inname = innerHTML.name
    allchild = [i for i in innerHTML.children]
    for idk, chi in enumerate(innerHTML.children):
        # article, number = parser_beautiful(chi, article, number, dircrea, bk)
        tag_name = chi.name
        if isinstance(chi, str):
            article += chi.text
            continue
        else:
            cll = [c for c in chi.children]
        # if tag_name in ['table', 'tbody', 'tr', 'td', 'u', 'em']:
        if tag_name in ['table', 'tbody', 'tr', 'td', 'u', "article", 'pre', 'ul']:
            article, number = parser_beautiful(chi, article, number, dircrea, bk)
        elif tag_name=="li":
            # article += "\n* "
            art, _ = parser_beautiful(chi, "", 0, dircrea, bk)
            article += "\n* "+art + "\n"
        elif tag_name=="em":
            article += " *" + chi.text + "* "
        elif tag_name=="br":
            article += "\n"
        elif tag_name=="blockquote":
            if len(cll) > 1:
                art, _ = parser_beautiful(chi, "", 0, dircrea, True)
                art = re.sub(r'\n\n+', '\n', art)
                article += '\n>'+art+'\n'
            else:
                article += "\n>" + chi.text + "\n"
        elif tag_name=="br":
            if inname=="p" and tag_name=='br':
                kk = list(innerHTML.children)
                if len(kk) >= 2 and kk[1].name=='a':
                    linksite = None
                    title = None
                    if 'href' in kk[1].attrs.keys():
                        linksite = kk[1].attrs['href']
                    if 'title' in kk[1].attrs.keys():
                        title = kk[1].attrs['title']
                    if linksite and title:
                        article += f'[{title}]({linksite})\n\n'
                    break
            article += "\n"
        elif tag_name=="p":
            article, number = parser_beautiful(chi, article, number, dircrea, bk)
            article += "\n\n"
        # elif tag_name=="br":
        #     article += "<br>\n"
        elif tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            article += '#' * int(tag_name[-1]) + ' '
            article, number = parser_beautiful(chi, article, number, dircrea, bk)
            article += '\n\n'
        elif tag_name=="span":
            datatex = None
            classc = None
            if 'data-tex' in chi.attrs.keys():
                datatex = chi.attrs["data-tex"]
            if 'class' in chi.attrs.keys():
                classc = chi.attrs["class"]
            if datatex and classc and 'ztext-math' in classc:
                content = chi.attrs["data-tex"]
                while len(content) > 0 and ' '==content[0]:
                    content = content[1:]
                while len(content) > 0 and ' '==content[-1]:
                    content = content[:-1]
                if len(content) > 0:
                    if article[-3-1:]=='<br>' or article[-1:]=='\n':
                        article += "\n$" + content + "$"
                    else:
                        article += "$" + content + "$"
            else:
                article, number = parser_beautiful(chi, article, number, dircrea, bk)
                # article += nod.text
        elif tag_name=="u":
            article, number = parser_beautiful(chi, article, number, dircrea, bk)
        elif tag_name=="a":
            linksite = None
            if 'href' in chi.attrs.keys():
                linksite = chi.attrs['href']
            if linksite:
                linksite = linksite.replace("//link.zhihu.com/?target=https%3A", "").replace("//link.zhihu.com/?target=http%3A", "")
                ar, _ = parser_beautiful(chi, "", 0, dircrea, False)
                if len(article) > 0 and article[-1]=='\n':
                    article += "["+ar+"]"+"("+linksite + ")"
                elif len(article) > 0 and article[-1] not in ['\n', ' ']:
                    article += " ["+ar+"]"+"("+linksite + ")"
                else:
                    article += "\n\n["+ar+"]"+"("+linksite + ")"
            if idk!=len(allchild)-1 and allchild[idk+1].name=='a':
                article += '\n\n'
        elif tag_name=='b' or tag_name=='strong':
            if len(cll) > 1:
                art, _ = parser_beautiful(chi, "", 0, dircrea, False)
                article += "**" + art + "**"
            else:
                txt = chi.text
                while len(txt) > 0 and txt[-1] == " ":
                    txt = txt[:-1]
                article += " **" + txt + "** "
        elif tag_name=="figure":
            noscript = chi.find_all('noscript')
            if len(noscript) > 0:
                chi.noscript.extract()
            imgchunk = chi.find_all('img')
            for i in range(len(imgchunk)):
                imglink = None
                if 'data-original' in imgchunk[i].attrs.keys():
                    imglink = imgchunk[i].attrs["data-original"]

                if 'data-actualsrc' in imgchunk[i].attrs.keys():
                    imglink = imgchunk[i].attrs['data-actualsrc']

                if imglink==None:
                    imglink = imgchunk[i].attrs["src"]
                try:
                    response = requests.get(imglink, timeout=30)
                except:
                    try:
                        response = requests.get(imglink, timeout=30)
                    except:
                        continue
                if response.status_code==200:
                    article += ''' <img src="%d.jpg" width="100%%"/> \n\n'''%number
                    # article += '''<img src="%d.jpg"/>'''%number
                    with open(os.path.join(dircrea, str(number) + '.jpg'), 'wb') as obj:
                        obj.write(response.content)
                    number += 1
                    crawlsleep(sleeptime)
        elif tag_name=="div":
            prenode = chi.find_all('code')
            if len(prenode) > 0:
                for i in prenode:
                    language = "text"
                    if 'class' in i.attrs.keys():
                        lan = i.attrs['class']
                        if len(lan)>0:
                            if 'language-' in lan[0]:
                                language = lan[0].split("-")[-1]
                    article += "\n\n```%s []\n"%language + i.text + "\n```\n\n"
            else:
                article, number = parser_beautiful(chi, article, number, dircrea, bk)
                article += "\n\n"
    # if bk:
    #     article += "**"
    article = article.replace("\n\n\n\n\n", "\n\n")
    article = article.replace("\n\n\n\n", "\n\n")
    article = article.replace("\n\n\n", "\n\n")
    return article, number

def recursion(nod, article, number, driver, dircrea, bk=False):
    if isinstance(nod, dict):
        if 'nodeName' in nod.keys() and nod['nodeName']=='#text':
            kkk = cleartxt(nod['textContent'])
            if len(kkk) > 0:
                if bk:
                    article += "**"
                article += nod['textContent']
                if bk:
                    article += "**"
            return article, number
        
    elif isinstance(nod, webdriver.remote.webelement.WebElement):
        tag_name = nod.tag_name
        if tag_name=="br":
            article += "<br>\n"
        elif tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            article += "\n" + '#' * int(tag_name[-1]) + ' '
            try:
                p_childNodes = driver.execute_script("return arguments[0].childNodes;", nod)
                for pnode in p_childNodes:
                    article, number = recursion(pnode, article, number, driver, dircrea, bk)
            except:
                pass
            article += '\n'
        elif tag_name=="span":
            datatex = nod.get_attribute("data-tex")
            classc = nod.get_attribute("class")
            if datatex and classc and 'ztext-math' in classc:
                if article[-3-1:]=='<br>' or article[-1:]=='\n':
                    article += "\n$" + nod.get_attribute("data-tex") + "$"
                else:
                    article += "$" + nod.get_attribute("data-tex") + "$"
            else:
                imgchunk = nod.find_elements(By.TAG_NAME, 'img')
                achunk = nod.find_elements(By.TAG_NAME, 'a')
                if len(imgchunk)==0 and len(achunk)==0:
                    if bk:
                        article += "**"
                    article += nod.text
                    if bk:
                        article += "**"
                else:
                    p_childNodes = driver.execute_script("return arguments[0].childNodes;", nod)
                    for pnode in p_childNodes:
                        article, number = recursion(pnode, article, number, driver, dircrea, bk)
            # else:
            #     formula_span = nod.find_elements(By.CLASS_NAME, "ztext-math")
            #     for jf in range(len(formula_span)):
            #         ele = formula_span[jf]
            #         article += "$" + ele.get_attribute("data-tex") + "$"
        elif tag_name=="a":
            linksite = nod.get_attribute("href")
            if linksite:
                linksite = linksite.replace("//link.zhihu.com/?target=https%3A", "").replace("//link.zhihu.com/?target=http%3A", "")
                if article[-3-1:]=='<br>' or article[-1:]=='\n':
                    article += "\n\n["+nod.text+"]"+"("+linksite + ")"
                else:
                    article += "["+nod.text+"]"+"("+linksite + ")"
        elif tag_name=="b" or tag_name=="strong":
            try:
                p_childNodes = driver.execute_script("return arguments[0].childNodes;", nod)
                for pnode in p_childNodes:
                    article, number = recursion(pnode, article, number, driver, dircrea, True)
            except:
                txt = nod.text
                while len(txt) > 0 and txt[-1] == " ":
                    txt = txt[:-1]
                article += " **" + txt + "** "
        elif tag_name=="em":
            if bk:
                article += "**"
            article += nod.text
            if bk:
                article += "**"
        # elif tag_name=='td':
        #     article += nod.text
        elif tag_name in ['table', 'tbody', 'tr', 'td', 'u']:
            p_childNodes = driver.execute_script("return arguments[0].childNodes;", nod)
            for pnode in p_childNodes:
                article, number = recursion(pnode, article, number, driver, dircrea, bk)
        elif tag_name=='p':
            try:
                p_childNodes = driver.execute_script("return arguments[0].childNodes;", nod)
                for pnode in p_childNodes:
                    article, number = recursion(pnode, article, number, driver, dircrea, bk)
            except:
                article += nod.text
            article += "\n"
        elif tag_name=="div":
            # atags = nod.find_elements(By.TAG_NAME, 'a')
            prenode = nod.find_elements(By.TAG_NAME, 'code')
            if len(prenode) > 0:
                for i in prenode:
                    article += "<br>\n```\n" + i.text + "\n```\n<br>"
            else:
                p_childNodes = driver.execute_script("return arguments[0].childNodes;", nod)
                for pnode in p_childNodes:
                    article, number = recursion(pnode, article, number, driver, dircrea, bk)
        elif tag_name=="figure":
            imgchunk = nod.find_elements(By.TAG_NAME, 'img')
            for i in range(len(imgchunk)):
                imglink = imgchunk[i].get_attribute("data-original")
                if imglink==None:
                    imglink = imgchunk[i].get_attribute("src")
                try:
                    response = requests.get(imglink, timeout=30)
                except:
                    try:
                        response = requests.get(imglink, timeout=30)
                    except:
                        continue
                if response.status_code==200:
                    article += ''' <img src="%d.jpg" width="100%%"/> '''%number
                    # article += '''<img src="%d.jpg"/>'''%number
                    with open(os.path.join(dircrea, str(number) + '.jpg'), 'wb') as obj:
                        obj.write(response.content)
                    number += 1
                    crawlsleep(sleeptime)
    return article, number

def crawl_article_detail(driver:webdriver):
    website_col = {}
    for i in os.listdir(articledir):
        try:
            kk = int(i)
            shutil.rmtree(os.path.join(articledir, i))
        except:
            pass
    with open(os.path.join(articledir, 'article.txt'), 'r', encoding='utf-8') as obj:
        for i in obj.readlines():
            i = i.strip()
            while len(i)>0 and i[0]==' ':
                i = i[1:]
            if i=="":
                continue
            ind = i.index(" ")
            website = i[:ind]
            title   = i[ind+1:].replace("\n", "")
            while len(title)>0 and title[0]==' ':
                title = title[1:]
            while len(title)>0 and title[-1]==' ':
                title = title[:-1]
            if title=="":
                continue
            website_col[website] = title
    allbegin = now()
    numberpage = 1e-6        
    for website, title in website_col.items():
        begin = now()

        # nam = title.replace(":", "_").replace("?", "_问号_"). \
        #             replace("/","_").replace("\\","_").replace("\"", "_").\
        #             replace("*","_").replace("|", "_").replace("？", "_问号_").replace("！", "_感叹号_").\
        #             replace("<", "小于").replace(">", "大于").replace("(", "").\
        #             replace(")", "").replace(",", "_逗号_").replace("，", "_逗号_").replace("   ", "_空格_").\
        #             replace("  ", "_空格_").replace(" ", "_空格_").replace("：", "_冒号_").replace("、", "_顿号_")

        nam = title.replace(":", "_").replace("?", "_问号_"). \
                    replace("/","_").replace("\\","_").replace("\"", "_").\
                    replace("*","_").replace("|", "_").\
                    replace("<", "小于").replace(">", "大于")


        temp_name = nam #str(np.random.randint(999999999)) + str(np.random.randint(999999999))
        if len(temp_name) > 100:
            temp_name = temp_name[:100]
        while temp_name!="" and temp_name[-1]==" ":
            temp_name = temp_name[:-1]
        while temp_name!="" and temp_name[0]==" ":
            temp_name = temp_name[1:]

        dircrea = os.path.join(articledir, 'content')

        # 定义正则表达式模式，匹配形如"2025-03_"的日期部分
        pattern = re.compile(r'^\d{4}-\d{2}_')

        # 获取文件名，忽略日期部分
        def get_filename_without_date(file_path):
            filename = os.path.basename(file_path)
            return pattern.sub('', filename)

        # 检查文件是否存在，忽略日期部分
        file_path = os.path.join(dircrea, nam + "_.txt")
        filename_without_date = get_filename_without_date(file_path)

        # 遍历目录中的文件，检查是否有相同的文件名（忽略日期部分）
        file_exists = any(
            get_filename_without_date(f) == filename_without_date
            for f in os.listdir(dircrea)
        )

        if file_exists:
            print(f"{file_path} 已经爬取过了，不再重复爬取")
            continue

        # dircrea  = os.path.join(articledir)
        os.makedirs(dircrea, exist_ok = True)

        #get article text
        driver.get(website)
        WebDriverWait(driver, timeout=20).until(lambda d: d.find_element(By.CLASS_NAME, "Post-Topics"))
            
        #https://stackoverflow.com/questions/61877719/how-to-get-current-scroll-height-in-selenium-python
        # scrollHeight = driver.execute_script('''return document.documentElement.scrollHeight''')
        # footer = driver.find_element(By.TAG_NAME, "html")
        # scroll_origin = ScrollOrigin.from_element(footer, 0, -60)
        # ActionChains(driver).scroll_from_origin(scroll_origin, 0, -100000).perform()
        # for i in range(18):
        #     try:
        #         ActionChains(driver).scroll_from_origin(scroll_origin, 0, scrollHeight//18).perform()
        #     except:
        #         try:
        #             ActionChains(driver).scroll_from_origin(scroll_origin, 0, -scrollHeight//18).perform()
        #         except:
        #             pass
        #     crawlsleep(0.1)
        # #remove noneed element
        # try:
        #     driver.execute_script('''document.getElementsByClassName("Post-Sub")[0].remove();''')
        # except:
        #     pass
        # try:
        #     driver.execute_script('''document.getElementsByClassName("ColumnPageHeader-Wrapper")[0].remove();''')
        # except:
        #     pass
        # try:
        #     driver.execute_script('''document.getElementsByClassName("RichContent-actions")[0].remove();''')
        # except:
        #     pass
        #
        # if MarkDown_FORMAT:
        #     richtext = driver.find_element(By.CLASS_NAME, "Post-RichText")
        #     titletext = driver.find_element(By.CLASS_NAME, "Post-Title")
        #     # article_childNodes = driver.execute_script("return arguments[0].childNodes;", richtext)
        #     article = ""
        #     number = 0
        #
        #     # for nod in article_childNodes:
        #         # article, number = recursion(nod, article, number, driver, dircrea)
        #
        #     inner = driver.execute_script("return arguments[0].innerHTML;", richtext)
        #     innerHTML = BeautifulSoup(inner, "html.parser")
        #     article, number = parser_beautiful(innerHTML, article, number, dircrea)
        #
        #     article = article.replace("修改\n", "").replace("开启赞赏\n", "开启赞赏, ").replace("添加评论\n", "").replace("分享\n", "").\
        #         replace("收藏\n", "").replace("设置\n", "")
        #     tle = titletext.text
        #     article += "<br>\n\n["+driver.current_url+"](" + driver.current_url + ")<br>\n"
        #     if len(article) > 0:
        #         try:
        #             f=open(os.path.join(dircrea, nam[:3] + "_.md"), 'w', encoding='utf-8')
        #             f.close()
        #         except:
        #             nam = nam[:len(nam)//2]
        #         with open(os.path.join(dircrea, nam[:3] + "_.md"), 'w', encoding='utf-8') as obj:
        #             obj.write("# " + tle+"\n\n")
        #             if len(article) > 0:
        #                 obj.write(article + "\n\n\n")
        #             obj.write("\n\n\n")

        # article to pdf
        clocktxt = driver.find_element(By.CLASS_NAME, "Post-NormalMain").find_element(By.CLASS_NAME, "ContentItem-time")
        clock = clocktxt.text[3 + 1:]
        year_month = clock.split(' ')[0][:7]
        nam = year_month + "_" + nam

        # crawlsleep(1)
        url = driver.current_url
        driver.execute_script("const para = document.createElement(\"h2\"); \
                                const br = document.createElement(\"br\"); \
                                const node = document.createTextNode(\"%s\");\
                                para.appendChild(node);\
                                const currentDiv = document.getElementsByClassName(\"Post-Header\")[0];\
                                currentDiv.appendChild(br); \
                                currentDiv.appendChild(para);"%url \
                            )

        # pagetopdf(driver, dircrea, temp_name, nam, articledir, url, Created=clock)
        # 直接获取Post-RichTextContainer中的文字
        content = get_article_text(driver, "css-ob6uua")
        # 直接以文章标题为文件名保存文章内容
        with open(os.path.join(dircrea, nam + "_.txt"), 'w', encoding='utf-8') as obj:
            obj.write(clock + '\n')
            obj.write(nam + '\n')
            obj.write(content)


        crawlsleep(sleeptime)

        #https://stackoverflow.com/questions/23359083/how-to-convert-webpage-into-pdf-by-using-python
        #https://github.com/JazzCore/python-pdfkit
        # if article_to_jpg_pdf_markdown:
        #     config = pdfkit.configuration(wkhtmltopdf = wkhtmltopdf_path)
        #     pdfkit.from_url(website, os.path.join(dircrea, nam_pinyin+"_.pdf"), configuration = config)
            
        end = now()
        print("爬取一篇article耗时：", title, round(end - begin, 3))
        logfp.write("爬取一篇article耗时：" + title + " " + str(round(end - begin, 3)) + "\n")
        numberpage += 1
        # crawlsleep(600)
    allend = now()
    print("平均爬取一篇article耗时：", round((allend - allbegin) / numberpage, 3))
    logfp.write("平均爬取一篇article耗时：" + str(round((allend - allbegin) / numberpage, 3)) + "\n")


def get_article_text(driver, txt_element_class_name):
    # 直接获取Post-RichTextContainer中的文字
    txt_element = driver.find_element(By.CLASS_NAME, txt_element_class_name)
    inner_html = txt_element.get_attribute('innerHTML')

    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(inner_html, 'html.parser')

    # 删除所有空格实体
    space_entities = ['\u200b', '\u2002', '\u2003', '\u2009', '\u200c', '\u200d', '\xa0']
    for entity in soup.find_all(
            string=lambda text: isinstance(text, str) and any(space in text for space in space_entities)):
        for space in space_entities:
            if entity.parent and entity in entity.parent.contents:
                entity.replace_with(entity.replace(space, ''))

    # 移除所有图片标签和svg标签
    for img in soup.find_all('img'):
        img.decompose()
    for svg in soup.find_all('svg'):
        svg.decompose()

    # 定义块级元素
    block_elements = ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'pre', 'ul']

    # 获取所有文本内容，块级元素添加换行符
    def get_text_with_blocks(element):
        text = ''
        for child in element.children:

            if child.name is not None:
                if 'ztext-empty-paragraph' in child.get('class', []):
                    continue
                elif child.name in block_elements:
                    text += get_text_with_blocks(child) + '\n'
                else:
                    text += get_text_with_blocks(child)
            else:
                text += child
        return text

    # 获取所有文本内容
    article_text = get_text_with_blocks(soup)

    return article_text.strip()

def get_answer_text(driver, item, txt_element_class_name):
    # 直接获取Post-RichTextContainer中的文字
    txt_element = item.find_element(By.CLASS_NAME, txt_element_class_name)
    inner_html = txt_element.get_attribute('innerHTML')

    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(inner_html, 'html.parser')

    # 删除所有空格实体
    space_entities = ['\u200b', '\u2002', '\u2003', '\u2009', '\u200c', '\u200d', '\xa0']
    for entity in soup.find_all(
            string=lambda text: isinstance(text, str) and any(space in text for space in space_entities)):
        for space in space_entities:
            if entity.parent and entity in entity.parent.contents:
                entity.replace_with(entity.replace(space, ''))

    # 移除所有图片标签和svg标签
    for img in soup.find_all('img'):
        img.decompose()
    for svg in soup.find_all('svg'):
        svg.decompose()

    # 定义块级元素
    block_elements = ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'pre', 'ul']

    # 获取所有文本内容，块级元素添加换行符
    def get_text_with_blocks(element):
        text = ''
        for child in element.children:

            if child.name is not None:
                if 'ztext-empty-paragraph' in child.get('class', []):
                    continue
                elif child.name in block_elements:
                    text += get_text_with_blocks(child) + '\n'
                else:
                    text += get_text_with_blocks(child)
            else:
                text += child
        return text

    # 获取所有文本内容
    article_text = get_text_with_blocks(soup)

    return article_text.strip()


def pagetopdf(driver, dircrea, temp_name, nam, destdir, url, Created=""):
    fileexit = os.path.exists(os.path.join(dircrea, temp_name + "_.pdf"))
    if fileexit:
        try:
            os.remove(os.path.join(dircrea, temp_name + "_.pdf"))
        except:
            pass

    printop = PrintOptions()
    printop.shrink_to_fit = True
    # printop.margin_left = 0
    # printop.margin_right = 0
    # printop.margin_top = 0
    # printop.margin_bottom = 0
    # printop.page_height = 29.7
    # printop.page_width = 21
    printop.background = True
    printop.scale = 1.0
    
    try:
        pdf = driver.print_page(print_options=printop)
        with open(os.path.join(dircrea, nam[:3] + "_.pdf"), 'wb') as obj:
            obj.write(base64.b64decode(pdf))
    except:
        with open(os.path.join(dircrea, nam[:3] + "_pdf.txt"), 'w') as obj:
            obj.write("the page is too large, can not save, you should save pdf using \"Ctrl+P or Ctrl+Shift+P\"\n")
    
    # driver.execute_script('window.print();')
    clock = Created    #clocktxt.text[3+1:].replace(":", "_")
    with open(os.path.join(dircrea, clock+".txt"), 'w', encoding='utf-8') as obj:
        obj.write(clock+"\n")
        obj.write(url)
    
    clocktmp = clock.split(".")[0].replace("T", "_")
    clock = clocktmp.split("・")[0].replace(" ", "_")
    address = ""
    try:
        address += clocktmp.split("・")[1].replace(" ", "_")
    except:
        pass
    try:
        os.rename(dircrea, os.path.join(destdir, clock + "_" + nam + "_" + address))
    except Exception as e0:
        crawlsleep(3+addtime)
        try:
            os.rename(dircrea, os.path.join(destdir, clock + "_" + nam + "_" + address))
        except Exception as e1:
            pass

def crawl_answer_detail(driver:webdriver, answer_count:int):
    website_col = {}
    for i in os.listdir(answerdir):
        try:
            kk = int(i)
            shutil.rmtree(os.path.join(answerdir, i))
        except:
            pass
    with open(os.path.join(answerdir, 'answers.txt'), 'r', encoding='utf-8') as obj:
        for i in obj.readlines():
            i = i.strip()
            while len(i)>0 and i[0]==' ':
                i = i[1:]
            if i=="":
                continue
            ind = i.index(" ")
            website = i[:ind]
            title   = i[ind+1:].replace("\n", "")
            while len(title)>0 and title[0]==' ':
                title = title[1:]
            while len(title)>0 and title[-1]==' ':
                title = title[:-1]
            if title=="":
                continue
            website_col[website] = title
    allbegin = now()
    numberpage = 1e-6
    for website, title in website_col.items():
        begin = now()
        nam = title.replace(":", "_").replace("?", "_问号_"). \
            replace("/", "_").replace("\\", "_").replace("\"", "_"). \
            replace("*", "_").replace("|", "_"). \
            replace("<", "小于").replace(">", "大于")

        if len(nam) > 100:
            nam = nam[:100]
        temp_name = nam #str(np.random.randint(999999999)) + str(np.random.randint(999999999))
        while temp_name!="" and temp_name[-1]==" ":
            temp_name = temp_name[:-1]
        while temp_name!="" and temp_name[0]==" ":
            temp_name = temp_name[1:]
        # nam_pinyin = pinyin.get(nam, format='numerical')
        # if '不定积分该用什么方' not in title:
        #     continue
        direxit = False
        fileexit = False
        dirname = ''
        filesize = 0
        # for i in os.listdir(answerdir):
        #     if nam in i and os.path.isdir(os.path.join(answerdir, i)):
        #         direxit = True
        #         dirname = i
        #         fileexit = os.path.exists(os.path.join(answerdir, dirname, nam + "_.pdf"))
        #         if fileexit:
        #             filesize = os.path.getsize(os.path.join(answerdir, dirname, nam + "_.pdf"))
        #         break

        dircrea = os.path.join(answerdir, 'content')
        json_file_path = os.path.join(dircrea, f"{nam}.json")

        if os.path.exists(json_file_path):
            print(f"{json_file_path} 已经爬取过了，不再重复爬取")
            continue
        


        # if direxit and fileexit and filesize > 0:
        #     if '_IP_' in dirname:
        #         filnam = dirname[16+1:].split("_IP_")[0]
        #     else:
        #         filnam = dirname[16+1:][:-1]
        #     if filnam == nam:
        #         continue

        os.makedirs(dircrea, exist_ok = True)
        
        #get article text
        driver.get(website)
        WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(By.CLASS_NAME, "List-item"))

        #https://stackoverflow.com/questions/61877719/how-to-get-current-scroll-height-in-selenium-python
        try:

            # 获取class=QuestionHeader-main元素
            questionHeader_tags = driver.find_element(By.CLASS_NAME, "QuestionHeader-main")

            # 获取class=QuestionHeader-main元素内的class=QuestionHeader-title元素

            # 获取大标题文本
            question_title = get_answer_text(driver, questionHeader_tags,"QuestionHeader-title")
            print('question_title:', question_title)

            if driver.find_elements(By.CLASS_NAME, "QuestionRichText--expandable"):
                if driver.find_elements(By.CLASS_NAME, "QuestionRichText-more"):
                    driver.find_element(By.CLASS_NAME, "QuestionRichText-more").click()
                question_txt = get_article_text(driver, "QuestionRichText--expandable")
                print('question_txt:', question_txt)
                question_title += question_txt

            answers = []
            scrollHeight = driver.execute_script(
                '''return document.getElementsByClassName("QuestionPage")[0].scrollHeight''')
            footer = driver.find_element(By.TAG_NAME, "html")
            scroll_origin = ScrollOrigin.from_element(footer, 0, 0)

            # Scroll to the bottom of the page in increments

            for i in range(18):
                try:
                    ActionChains(driver).scroll_from_origin(scroll_origin, 0, scrollHeight // 18).perform()
                except:
                    try:
                        ActionChains(driver).scroll_from_origin(scroll_origin, 0, -scrollHeight // 18).perform()
                    except:
                        pass
                crawlsleep(0.1)
            #最后一次往上滑1/18的高度，再往下滑1/18的高度
            try:
                ActionChains(driver).scroll_from_origin(scroll_origin, 0, -scrollHeight // 18).perform()
                ActionChains(driver).scroll_from_origin(scroll_origin, 0, -scrollHeight // 18).perform()
                ActionChains(driver).scroll_from_origin(scroll_origin, 0, -scrollHeight // 18).perform()
                crawlsleep(0.5)
                ActionChains(driver).scroll_from_origin(scroll_origin, 0, scrollHeight // 18).perform()
                ActionChains(driver).scroll_from_origin(scroll_origin, 0, scrollHeight // 18).perform()
                ActionChains(driver).scroll_from_origin(scroll_origin, 0, scrollHeight // 18).perform()
            except:
                pass

            crawlsleep(2)
            # Scroll to the top of the page
            # ActionChains(driver).scroll_from_origin(scroll_origin, 0, -100000).perform()

            list_items = driver.find_elements(By.CLASS_NAME, "List-item")
            for item in list_items:
                inner_item = item.find_element(By.CLASS_NAME, "RichContent-inner")
                answer_text = get_answer_text(driver, inner_item, "css-376mun")
                answers.append(answer_text)

            qa_pairs = [{"input": question_title, "output": answer} for answer in answers]

            json_path = os.path.join(dircrea, f"{nam}.json")
            with open(json_path, 'w', encoding='utf-8') as json_file:
                json.dump(qa_pairs, json_file, ensure_ascii=False, indent=4)

        except Exception as e:
            print(f"Error processing {website}: {e}")


        crawlsleep(sleeptime)
        end = now()
        print("爬取一篇回答耗时：", title, round(end - begin, 3))
        logfp.write("爬取一篇回答耗时：" +title+" "+ str(round(end - begin, 3)) + "\n")
        numberpage += 1
        # crawlsleep(600)
    allend = now()
    print("平均爬取一篇回答耗时：", round((allend - allbegin) / numberpage, 3))
    logfp.write("平均爬取一篇回答耗时：" + str(round((allend - allbegin) / numberpage, 3)) + "\n")

def login_loadsavecookie(driver):
    try:
        load_cookie(driver, cookie_path)
        driver.get(r"https://www.zhihu.com/")
        WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(By.ID, 'Popover15-toggle'))
        toggle = driver.find_element(By.ID, 'Popover15-toggle')
    except Exception as e:
        if os.path.exists(cookie_path):
            os.remove(cookie_path)
            print("浏览器cookie失效了，删除了之前的cookie，需要再次登录并保存cookie。")
        else:
            print("需要登陆并保存cookie，下次就不用登录了。")
        driver = login(driver)
        save_cookie(driver, cookie_path)
        print(f"cookie保存好了的放在了：{cookie_path}")
        crawlsleep(3)
        # driver.quit()
        # exit(0)
    try:
        driver.find_element(By.ID, 'Popover15-toggle').click()
        driver.find_element(By.CLASS_NAME, 'Menu-item').click()
    except:
        crawlsleep(6)
        driver.get(r"https://www.zhihu.com/")
        crawlsleep(3)
        driver.find_element(By.ID, 'Popover15-toggle').click()
        driver.find_element(By.CLASS_NAME, 'Menu-item').click()
    url = driver.current_url
    username = url.split("/")[-1]
    return driver, username

def downloaddriver():
    global driverpath
    url = "https://msedgedriver.azureedge.net/116.0.1938.62/edgedriver_win64.zip"
    if not os.path.exists(driverpath):
        ret = requests.get("https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
        if ret.status_code!=200:
            assert ret.status_code!=200
        ret = BeautifulSoup(ret.content, 'html.parser')
        # divall = ret.find_all('div', class_=r'common-card--lightblue')
        ddl = ret.find_all('a')
        name = "msedgedriver.exe"
        for k in ddl:
            key = k.attrs.keys()
            if 'href' not in key:
                continue
            href = k.attrs['href']
            if 'darwin' not in sys.platform:
                if 'href' in key and "win64" in href and ".zip" in href:
                    url = href
                    break
            elif 'darwin' in sys.platform and 'arm' not in platform.processor():
                if 'href' in key and "mac64" in href and "m1" not in href and ".zip" in href:
                    url = href
                    name = "msedgedriver"
                    break
            elif 'darwin' in sys.platform and 'arm' in platform.processor():
                if 'href' in key and "mac64_m1" in href and ".zip" in href:
                    url = href
                    name = "msedgedriver"
                    break
        response = requests.get(url)
        if response.status_code==200:
            with open(os.path.join(abspath, 'msedgedriver/edgedriver.zip'), 'wb') as obj:
                obj.write(response.content)
            with ZipFile(os.path.join(abspath, 'msedgedriver/edgedriver.zip'), "r") as obj:
                obj.extractall(os.path.join(abspath, 'msedgedriver'))
            nth = os.path.join(abspath, 'msedgedriver')
            for r, d, f in os.walk(nth):
                kk = 6
                for i in f:
                    if 'driver' in i and '.zip' not in i:
                        try:
                            shutil.move(os.path.join(r, i), os.path.join(nth, i))
                        except:
                            pass
                        os.rename(os.path.join(nth, i), os.path.join(nth, name))
                        if 'darwin' in sys.platform:
                            print(f"\n\n请执行权限操作再继续执行：\nchmod +x {os.path.join(nth, name)}\n")
                            exit(0)
                        kk = -6
                        break
                if kk < 0:
                    break

def openEdge():
    global driverpath
    website = r"https://www.zhihu.com/signin"
        
    # login and save cookies of zhihu
    driver = edgeopen(driverpath)
    driver.get(website)
    return driver

def zhihu():
    global driverpath
    # #crawl articles links
    try:
        downloaddriver()
        driver = openEdge()
    except Exception as e:
        if os.path.exists(driverpath):
            os.remove(driverpath)
        downloaddriver()
        driver = openEdge()

    driver, username = login_loadsavecookie(driver)
    
    # #crawl think links
    if crawl_think:
        crawl_think_links(driver, username)
        logfp.write(nowtime() + ', 想法爬取已经好了的\n')

    # #crawl articles links
    if crawl_article:
        if not os.path.exists(os.path.join(articledir, 'article.txt')):
            crawl_article_links(driver, username)
            logfp.write(nowtime() + ', article weblink爬取已经好了的\n')
        else:
            if crawl_links_scratch:
                os.rename(os.path.join(articledir, 'article.txt'), os.path.join(articledir, 'article_%s.txt'%nowtime()))
                crawl_article_links(driver, username)
                logfp.write(nowtime() + ', article weblink爬取已经好了的\n')
            else:
                pass
        crawl_article_detail(driver)
        logfp.write(nowtime() + ', article爬取已经好了的\n')
        
    # #crawl answers links
    if crawl_answer:
        if not os.path.exists(os.path.join(answerdir, 'answers.txt')):
            crawl_answers_links(driver, username)
            logfp.write(nowtime() + ', 回答 weblink爬取已经好了的\n')
        else:
            if crawl_links_scratch:
                os.rename(os.path.join(answerdir, 'answers.txt'), os.path.join(answerdir, 'answers_%s.txt'%nowtime()))
                crawl_answers_links(driver, username)
                logfp.write(nowtime() + ', 回答 weblink爬取已经好了的\n')
            else:
                pass
        crawl_answer_detail(driver, 10)
        logfp.write(nowtime() + ', 回答爬取已经好了的\n')

    # #crawl column links
    if crawl_column:
        getZhuanlanLinks(driver)
        # if not os.path.exists(os.path.join(articledir, 'column.txt')):
        #     crawl_column_links(driver, username)
        #     logfp.write(nowtime() + ', 专栏 weblink爬取已经好了的\n')
        # else:
        #     if crawl_links_scratch:
        #         os.rename(os.path.join(articledir, 'column.txt'), os.path.join(articledir, 'column_%s.txt'%nowtime()))
        #         crawl_column_links(driver, username)
        #         logfp.write(nowtime() + ', 专栏 weblink爬取已经好了的\n')
        #     else:
        #         pass
        # crawl_column_detail(driver)
        # logfp.write(nowtime() + ', 专栏爬取已经好了的\n')
            
    driver.quit()

if __name__ == "__main__":
    #version four.one_zero.zero
    if 'darwin' not in sys.platform:
        driverpath = os.path.join(abspath, 'msedgedriver' +os.sep + 'msedgedriver.exe')
    else:
        driverpath = os.path.join(abspath, 'msedgedriver' +os.sep + 'msedgedriver')
    savepath = deepcopy(abspath)
    cookiedir = os.path.join(savepath, 'cookie')
    thinkdir = os.path.join(savepath, 'think')
    answerdir = os.path.join(savepath, 'answer')
    articledir = os.path.join(savepath, 'article')
    logdir = os.path.join(savepath, 'log')
    logfile = os.path.join(logdir, nowtime() + '_log.txt')
    os.makedirs(cookiedir, exist_ok=True)
    os.makedirs(thinkdir,  exist_ok=True)
    os.makedirs(answerdir,    exist_ok=True)
    os.makedirs(articledir,   exist_ok=True)
    os.makedirs(logdir,   exist_ok=True)
    logfp = open(logfile, 'w', encoding='utf-8')
    cookie_path =os.path.join(cookiedir, 'cookie_zhihu.pkl')
    
    parser = argparse.ArgumentParser(description=r'crawler zhihu.com, 爬取知乎的想法, 回答, 文章, 包括数学公式')
    parser.add_argument('--sleep_time', type=float, default = 6, \
                        help=r'crawler sleep time during crawling, 爬取时的睡眠时间, 避免给知乎服务器带来太大压力, \
                        可以日间调试好，然后深夜运行爬取人少, 给其他小伙伴更好的用户体验, 避免知乎顺着网线过来找人, 默认: 6s')
    parser.add_argument('--computer_time_sleep', type=float, default=0, \
                        help=r'computer running sleep time 默认:0, 电脑运行速度的sleep时间, 默认:0')
    parser.add_argument('--think',   action="store_true", help=r'crawl think, 是否爬取知乎的想法, 已经爬取过的想法不会重复爬取, 所以可以多次爬取断了也没关系')
    parser.add_argument('--answer',  action="store_true", help=r'crawl answer, 是否爬取知乎的回答, 保存到pdf、markdown以及相关图片等，已经爬取过的不会重复爬取，\
                    断了再次爬取的话，可以配置到--links_scratch，事先保存好website')
    parser.add_argument('--article', action="store_true", help=r'crawl article, 是否爬取知乎的文章, 保存到pdf、markdown以及相关图片等，已经爬取过的不会重复爬取，\
                    断了再次爬取的话，可以配置到--links_scratch，事先保存好website')
    parser.add_argument('--MarkDown', action="store_true", help=r'save MarkDown')
    parser.add_argument('--links_scratch', action="store_true",
                        help=r'crawl links scratch for answer or article, 是否使用已经保存好的website和title, 否则再次爬取website')
    parser.add_argument('--column', action="store_true", help=r'crawl column, 是否爬取知乎的专栏, 保存到pdf、markdown以及相关图片等，已经爬取过的不会重复爬取，断了再次爬取的话，可以配置到--links_scratch，事先保存好website')

    args = parser.parse_args()
    sleeptime = args.sleep_time
    crawl_think = args.think
    crawl_answer = args.answer
    crawl_article = args.article
    crawl_links_scratch = args.links_scratch
    crawl_column = args.column
    addtime = args.computer_time_sleep
    MarkDown_FORMAT = args.MarkDown
    
    # crawl_think = True
    # crawl_article = True
    # crawl_answer = True
    # crawl_links_scratch = True
    # MarkDown_FORMAT = True
    # python crawler.py --think --MarkDown --links_scratch
    # python crawler.py --article  --MarkDown --links_scratch
    # python crawler.py --answer  --MarkDown --links_scratch
    # python crawler.py --think --answer --article  --MarkDown --links_scratch
    zhihu()
    # for i in range(100):
    #     try:
    #         zhihu()
    #     except:
    #         crawlsleep(60)
    logfp.close()
