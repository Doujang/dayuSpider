# -*- coding:utf-8 -*-

from fake_useragent import UserAgent
import requests
import urllib3
from bs4 import BeautifulSoup
import time
import json
from pymysql import *

'''
通过搜索的方式获取大鱼号号主的唯一标识mid
'''

def getMid(iid,user_name):
    #ua = UserAgent()
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
               'Host':'zzd.sm.cn',
               'Connection':'keep-alive',
               'Cache - Control':'max - age = 0',
               'Upgrade-Insecure-Requests':'1',
               'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
               'Accept-Encoding':'gzip, deflate',
               'Accept-Language':'zh-CN,zh;q=0.9',
               #'Cookie':'_uc_pramas=%7B%22fr%22%3A%22android%22%7D; sn=8578984313164124556'
                }

    url = 'http://zzd.sm.cn/webapp/ucnews-search?query=' + user_name
    source_url = 'http://zzd.sm.cn/iflow/api/v1/article/fsearch?q=' + user_name
    requests.get(url,headers=headers,timeout=5,verify=False)
    body = requests.get(source_url,headers=headers,timeout=5,verify=False).text
    urllib3.disable_warnings()

    soup = json.loads(body)
    print(soup)

    try:
        content = soup['data']['wemedias'][0]['wm_id']
        print(content)
    except:
        content = 'None'
        print(content)
        pass

    updateMid(content,iid)
    time.sleep(0.1)

def updateMid(mid,n):

    params = [mid,n]
    db = connect(host="localhost", port=3306, db="spider", user="root", password="secret", charset="utf8")
    conn = db.cursor()

    try:
        sql = """update Newdayu set mid=%s WHERE id=%s"""
        print('ok!!!')
        conn.execute(sql,params)
        db.commit()
    except:
        db.rollback()
    db.close()

if __name__ == "__main__":
    db = connect(host="localhost", port=3306, db="spider", user="root", password="secret", charset="utf8")
    cursor = db.cursor()

    try:
        sql = 'SELECT id,userName FROM Newdayu'
        MainUrl = cursor.execute(sql)
        data = cursor.fetchall()
        db.commit()
    except:
        db.rollback()

    for i in range(len(data)):
        id = data[i][0]
        user_name = data[i][1]
        #mid = data[i][2]
        print(user_name)
        #if mid == 'None':
        getMid(id, user_name)
        time.sleep(0.1)

    db.close()
