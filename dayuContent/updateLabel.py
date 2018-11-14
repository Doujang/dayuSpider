# coding = utf-8

from pymysql import *
import time
import re
import requests
import json

def getId(id,url):
    pattern = re.compile('wm_cid=[^\s]*')
    soup = re.findall(pattern,url)
    cid = soup[0][7:]
    #print(cid)

    link = 'http://ff.dayu.com/contents/' + str(cid) + '?biz_id=1002&_fetch_author=1&_fetch_incrs=1'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
        'Host': 'ff.dayu.com',
        'Connection': 'keep-alive',
        'Cache - Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        # 'Cookie':'cna=ssFmE2lTTh8CAXeDsgjtj/mi; isg=BHZ2ncjXMY0PIcVteei_Cq3Qx6y4P7u9nkIVH-Bf7NnQIxW9SCVZ48LSP7_qi7Lp'
    }
    try:
        body = requests.get(link, headers=headers, timeout=5).text
        time.sleep(0.1)
        print(body)
        soup = json.loads(body)
        data = soup['data']
    except:
        print('something is wrong!!!')
        return

    # 应用外阅读数
    try:
        click2 = data['_incrs']['click2']
        click2 = int(click2)
        click3 = data['_incrs']['click3']
        click3 = int(click3)
        external_visit_count = click2 + click3
    except:
        external_visit_count = 0

    # 应用内阅读数
    try:
        internal_visit_count = data['_incrs']['click1']
        internal_visit_count = int(internal_visit_count)
    except:
        internal_visit_count = 0

    # 总阅读数
    total_read_count = external_visit_count + internal_visit_count

    # 评论数
    try:
        comment_count = data['_incrs']['comment']
        comment_count = int(comment_count)
    except:
        comment_count = 0

    # 转发数
    try:
        share_count = data['_incrs']['share']
        share_count = int(share_count)
    except:
        share_count = 0

    # 推荐数
    try:
        impression_count = data['_incrs']['show']
        impression_count = int(impression_count)
    except:
        impression_count = 0

    # 标签数
    try:
        item_id = data['_extra']['xss_item_id']
        label = getLabel(item_id)
    except:
        label = '[]'

    items_list = {
        'total_read_count': total_read_count,
        'internal_visit_count': internal_visit_count,
        'external_visit_count': external_visit_count,
        'comment_count': comment_count,
        'share_count': share_count,
        'impression_count': impression_count,
        'label': label
    }

    time.sleep(0.1)

    savePage(id,items_list)

def savePage(id,items):
    sql = """update dayuPage31 set label=%s,total_read_count=%s,internal_visit_count=%s,external_visit_count=%s,comment_count=%s,share_count=%s,impression_count=%s WHERE id=%s"""
    try:
        cursor.execute(sql, (
            items["label"], items["total_read_count"], items["internal_visit_count"],
            items["external_visit_count"], items["comment_count"], items['share_count'], items['impression_count'],id))
        db.commit()
        print(items["source_url"] + " is success")
    except:
        db.rollback()

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
    url = 'http://m.uczzd.cn/iflow/api/v1/article?aid=%5B%22' + str(id) + '%22%5D'
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
    db = connect(host="192.168.1.100", port=3306, db="Spider", user="root", password="zy79117911#", charset="utf8")
    cursor = db.cursor()
    try:
        sql = """select id,source_url from dayuPage31"""
        cursor.execute(sql)
        data = cursor.fetchall()
        db.commit()
    except:
        db.rollback()

    for i in range(95128,len(data)):
        id = data[i][0]
        print(id)
        url = data[i][1]
        getId(id,url)
        time.sleep(0.1)

    db.close()