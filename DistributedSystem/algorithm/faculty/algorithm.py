from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import json
import urllib.request
from urllib.request import urlopen
from bs4 import BeautifulSoup
from get_data_from_multiple_lists import view_html_structure
import pathlib
from datetime import datetime
import sys
import requests

abs_path = str(pathlib.Path(__file__).parent.absolute())


def find(university, department):
    query = university + ' ' + department
    url = 'https://www.google.com/search?q=' + query.replace(' ', '+').replace('/', "%2F") + '+faculty'
    url = url.replace('&', '%26')
    option = webdriver.ChromeOptions()
    option.add_argument(' — incognito')
    option.add_argument('--no - sandbox')
    option.add_argument('--window - size = 1420, 1080')
    option.add_argument('--headless')
    option.add_argument('--disable - gpu')
    driver = webdriver.Chrome(executable_path=abs_path + '/chromedriver', chrome_options=option)
    driver.get(url)
    elems = driver.find_elements_by_xpath("//a[@href]")
    possibleURLs = []
    words = ['google', 'wiki', 'news', 'instagram', 'twitter', 'linkedin', 'criminal', 'student', 'course', 'facebook']
    n = 0
    for elem in elems:
        t = elem.get_attribute("href")
        flag = True
        for i in words:
            if i in t:
                flag = False
                break
        if flag:
            possibleURLs.append(t)
            n += 1
        if n == 10:
            break
    time.sleep(2)
    driver.quit()

    # html = requests.get(url).content
    # print(html)
    # bsObj = BeautifulSoup(html, 'lxml')

    # links = bsObj.findAll('a')
    # possibleURLs = []
    # for link in links:
    #     possibleURLs.append(link.attrs['href'])

    res_data = {}
    res_url = ''
    res_num = 0
    print(possibleURLs)

    for url in possibleURLs:
        for option in ['urllib', 'urllibs']:
            # print(option, url)
            try:
                r = view_html_structure(url, option)
            except:
                continue

            if len(r) < 6:
                continue
            valid_data = 0
            for i in r:
                for j in i.values():
                    if j != 'Missing':
                        valid_data += 1
            if len(r) >= 7 and valid_data / (5 * len(r)) > 0.56:
                return r, url
            if len(r) > 20 and valid_data / (5 * len(r)) > 0.36 and r[0]['Name'] != 'Missing':
                return r, url
            if valid_data > res_num:
                res_url = url
                res_data = r.copy()
                res_num = valid_data
    return res_data, res_url


# u = 'Gonzaga University'
# a = 'computer science'
# r1, r2 = find(u, a)
# for i in r2:
#     print(i)
# print(r1)

if __name__ == "__main__":
    # args: university name + worker ID
    start = datetime.now()

    name = " ".join(sys.argv[1: -1])
    tmp = name.split('_')
    university = tmp[0]
    department = tmp[1]
    r, url = find(university, department)

    end = datetime.now()
    t = end - start

    res = {}
    res['task'] = 'faculty'
    res['university'] = university
    res['department'] = department
    res['id'] = '_' + end.strftime("%d/%m/%Y-%H:%M:%S")
    res['time_stamp'] = end.strftime("%d/%m/%Y-%H:%M:%S")
    res['execution_time'] = str(t.seconds)
    res['url'] = url
    res['algo_version'] = 1
    res['status'] = 'Success' if r else 'Fail'
    res['data'] = r

    name = name.replace('/', '-slash-')
    f = open('output/' + sys.argv[-1] + '/' + name + '.json', 'w')
    json.dump(res, f, indent=4)
    for i in r:
        print(i)
