# -*- coding:utf-8 -*-

from pymysql import *
import requests
import urllib3
import json
from datetime import datetime
import time

'''
大鱼号历史文章内容信息抓取，包括文章链接、文章标题、发布时间、文章分类、文章内容、文章作者、标签、阅读数、评论数、转发数、推荐数等信息，并存入MySQL
'''

def loadPage(id,mid):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
        'Host': 'ff.dayu.com',
        'Connection': 'keep-alive',
        'Cache - Control': 'max - age = 0',
        'Upgrade-Insecure-Requests': '1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        #'Cookie':'cna=ssFmE2lTTh8CAXeDsgjtj/mi; isg=BHZ2ncjXMY0PIcVteei_Cq3Qx6y4P7u9nkIVH-Bf7NnQIxW9SCVZ48LSP7_qi7Lp'
        }
    n = 1
    while True:
        url = 'http://ff.dayu.com/contents/author/' + mid + '?biz_id=1002&_size=8&_page=' + str(n)
        try:
            body = requests.get(url,headers=headers,timeout=5,verify=False).text
            time.sleep(0.1)
            urllib3.disable_warnings()
            response = json.loads(body)
            data = response['data']
        except:
            print('something is wrong!!!')
            error_time = int(time.time())
            with open('error_url.txt', 'a') as e:
                e.write(mid + '\n')
                e.write(str(error_time) + '\n')
                e.write(url + '\n')
            return

        if len(data)==0:
            return
        else:
            n += 1

        time.sleep(0.1)
        parsePage(data)

def parsePage(data):
    for i in range(len(data)):
        #文章内容链接
        content_id = data[i]['content_id']
        #origin_id = data[i]['origin_id']
        #shard_id = data[i]['shard_id']
        source_url = 'http://a.mp.uc.cn/article.html?uc_param_str=frdnsnpfvecpntnwprdssskt&from=media#!wm_cid='+ content_id
        content_id = str(content_id)
        biz_id = data[i]['biz_id']
        biz_id = str(biz_id)
        page_url = 'http://ff.dayu.com/contents/' + content_id + '?biz_id=' + biz_id + '&_fetch_author=1&_fetch_incrs=1'

        #文章标题
        title = data[i]['title']
        title = str(title)
        #文章发布时间
        dt = data[i]['published_at']
        y = dt[:10]
        y = str(y)
        x = dt[11:19]
        x = str(x)
        t = y + " " + x
        t = str(t)
        print(t)
        date_time = datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
        time_stamp = datetime.timestamp(date_time)
        time_stamp = int(time_stamp)
        t = 1483200000 #抓取2017年之后的文章内容
        if time_stamp < t:
            return
        else:
            pass

        #文章分类
        try:
            category = data[i]['category']
            category = str(category)
        except:
            category = '[]'
        print(category)

        item_list = loadLink(page_url)
        time.sleep(0.1)

        #文章内容
        try:
            article_content = item_list['article_content']
            print(article_content)
        except:
            article_content = '[]'

        # 文章作者
        try:
            author = item_list['author']
            print(author)
        except:
            author = '[]'

        #关键词
        keywords = '[]'

        #标签
        try:
            label = item_list['label']
        except:
            label = '[]'

        #总阅读数
        try:
            total_read_count = item_list['total_read_count']
            print(total_read_count)
        except:
            total_read_count = 0

        #应用外阅读数
        try:
            external_visit_count = item_list['external_visit_count']
            print(external_visit_count)
        except:
            external_visit_count = 0

        #应用内阅读数
        try:
            internal_visit_count = item_list['internal_visit_count']
            print(internal_visit_count)
        except:
            internal_visit_count = 0

        #评论数
        try:
            comment_count = item_list['comment_count']
            print(comment_count)
        except:
            comment_count = 0

        #转发数
        try:
            share_count = item_list['share_count']
            print(share_count)
        except:
            share_count = 0

        #推荐数
        try:
            impression_count = item_list['impression_count']
            print(impression_count)
        except:
            impression_count = 0

        items = {
            'source_url': source_url,
            'category': category,
            'title': title,
            'author': author,
            'datetime': date_time,
            'keywords': keywords,
            'label': label,
            'total_read_count': total_read_count,
            'internal_visit_count': internal_visit_count,
            'external_visit_count': external_visit_count,
            'comment_count': comment_count,
            'article_content': article_content,
            'share_count': share_count,
            'impression_count': impression_count
        }

        time.sleep(0.1)
        savePage(items)

def savePage(items):
    sql = """insert into dayuPage(source_url,category,title,author,datetime,keywords,label,total_read_count,internal_visit_count,external_visit_count,comment_count,share_count,impression_count,article_content) \
        values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    try:
        cursor.execute(sql, (
            items["source_url"], items['category'], items["title"], items["author"], items["datetime"],
            items["keywords"], items["label"], items["total_read_count"], items["internal_visit_count"],
            items["external_visit_count"], items["comment_count"], items['share_count'], items['impression_count'],
            items["article_content"]))
        db.commit()
        print(items["source_url"] + " is success")
    except:
        db.rollback()

def loadLink(source_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
        'Host': 'ff.dayu.com',
        'Connection': 'keep-alive',
        'Cache - Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        #'Cookie':'cna=ssFmE2lTTh8CAXeDsgjtj/mi; isg=BHZ2ncjXMY0PIcVteei_Cq3Qx6y4P7u9nkIVH-Bf7NnQIxW9SCVZ48LSP7_qi7Lp'
    }
    try:
        body = requests.get(source_url, headers=headers, timeout=5, verify=False).text
        time.sleep(0.1)
        print(body)
        urllib3.disable_warnings()
        soup = json.loads(body)
        data = soup['data']
    except:
        print('something is wrong!!!')
        error_time = int(time.time())
        with open('error_url.txt', 'a') as e:
            e.write(str(error_time) + '\n')
            e.write(source_url + '\n')
        print(source_url)
        return

    # 文章作者
    try:
        author = data['_author']['author_name']
        author = str(author)
    except:
        author = '[]'

    # 文章内容
    try:
        article_content = data['body']['text']
    except:
        article_content = '["视频"]'

    # 总阅读数
    try:
        total_read_count = data['_incrs']['click_total']
        total_read_count = int(total_read_count)
    except:
        total_read_count = 0

    # 应用外阅读数
    try:
        click2 = data['_incrs']['click2']
        click2 = int(click2)
        click3 = data['_incrs']['click3']
        click3 = int(click3)
        external_visit_count = click2 + click3
    except:
        external_visit_count = 0

    #应用内阅读数
    try:
        internal_visit_count = data['_incrs']['click1']
        internal_visit_count = int(internal_visit_count)
    except:
        internal_visit_count = 0

    #评论数
    try:
        comment_count = data['_incrs']['comment']
        comment_count = int(comment_count)
    except:
        comment_count = 0

    #转发数
    try:
        share_count = data['_incrs']['share']
        share_count = int(share_count)
    except:
        share_count = 0

    #推荐数
    try:
        impression_count = data['_incrs']['show']
        impression_count = int(impression_count)
    except:
        impression_count = 0

    #标签数
    try:
        #tags = data['_extra']['customize_tags']
        #tags = str(tags)
        #print('tags='+tags)
        #if tags == '[]':
        item_id = data['_extra']['xss_item_id']
        label = getLabel(item_id)
        #else:
        #    label = tags
    except:
        label = '[]'

    items_list = {
        'author': author,
        'article_content': article_content,
        'total_read_count': total_read_count,
        'internal_visit_count': internal_visit_count,
        'external_visit_count': external_visit_count,
        'comment_count': comment_count,
        'share_count': share_count,
        'impression_count': impression_count,
        'label':label
    }

    time.sleep(0.1)
    return items_list

def getLabel(id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
        'Host': 'm.uczzd.cn',
        'Connection': 'keep-alive',
        'Cache - Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        # 'Cookie':'cna=ssFmE2lTTh8CAXeDsgjtj/mi; isg=BHZ2ncjXMY0PIcVteei_Cq3Qx6y4P7u9nkIVH-Bf7NnQIxW9SCVZ48LSP7_qi7Lp'
    }
    url = 'http://m.uczzd.cn/iflow/api/v1/article?aid=%5B%22' + id + '%22%5D'
    try:
        body = requests.get(url, headers=headers, timeout=5).text
        time.sleep(0.1)
        print(body)
        soup = json.loads(body)
        label = soup['data']['items'][id]['tags']
        label = str(label)
        print(label)
    except:
        label = '[]'

    return label

if __name__ == "__main__":
    db = connect(host="secret", port=3306, db="Spider", user="root", password="secret", charset="utf8")
    cursor = db.cursor()

    try:
        sql = """select id,mid from dayu"""
        cursor.execute(sql)
        data = cursor.fetchall()
        db.commit()
    except:
        db.rollback()

    for i in range(len(data)):
        id = data[i][0]
        id = str(id)
        mid = data[i][1]
        print(id,mid)
        loadPage(id,mid)
        time.sleep(0.1)

    db.close()
