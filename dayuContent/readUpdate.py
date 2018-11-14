# -*- coding:utf-8 -*-

import requests
import json
import time
import pymongo
import redis
from threading import Thread

def loadRead(cid):
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
    source_url = 'http://ff.dayu.com/contents/' + str(cid) + '?biz_id=1002&_fetch_author=1&_fetch_incrs=1'
    try:
        body = requests.get(source_url, headers=headers, timeout=5).text
        time.sleep(0.1)
        print(body)
        soup = json.loads(body)
        data = soup['data']
    except:
        save_time = int(time.time())
        items_list = {
            'save_time': save_time,
            'total_read_count': 0,
            'comment_count': 0,
            'impression_count': 0
        }
        return items_list

    # 总阅读数
    try:
        click1 = data['_incrs']['click1']
        click2 = data['_incrs']['click2']
        click3 = data['_incrs']['click3']
        total_read_count = int(click1) + int(click2) + int(click3)
    except:
        total_read_count = 0

    #评论数
    try:
        comment_count = data['_incrs']['comment']
        comment_count = int(comment_count)
    except:
        comment_count = 0

    #推荐数
    try:
        impression_count = data['_incrs']['show']
        impression_count = int(impression_count)
    except:
        impression_count = 0

    # 保存时间
    save_time = int(time.time())

    items_list = {
        'save_time': save_time,
        'total_read_count': total_read_count,
        'comment_count': comment_count,
        'impression_count': impression_count,
    }

    time.sleep(0.1)
    return items_list

def updateMongo(url,item):
    data = {'save_time':item['save_time'],'impression_count': item['impression_count'],
             'comment_count': item['comment_count'],'total_read_count': item['total_read_count']}
    try:
        result = collection.update(
        {"source_url": url},
        {
            "$push": {"date_collection": data},
        })

        print('1', result)
    except Exception as e:
        print('2', e, item['source_ur'])

def loop():
    while True:
        now_time = int(time.time())
        data = redis_cli.lpop('dayuContentId')
        data = eval(data)
        first_time = data['first_time']  # 第一次抓取的时间，保持不变
        save_time = data['save_time']  # 每次抓取的时间，一个小时跟新一次
        cid = data['content_id']
        mid = data['mid']

        with open('cid.txt', 'w') as fr:
            fr.write(str(data) + '\n')

        span_time = now_time - first_time
        if span_time > 259200:  # 三天的时间间隔259200
            continue

        read_time = now_time - save_time
        if read_time < 0:  # 每小时更新一次阅读数
            wait_time = 0 - read_time
            print('===========================广告时间很短，更多精彩内容敬请期待=============================')
            time.sleep(wait_time)

        try:
            item = loadRead(cid)
            source_url = 'http://a.mp.uc.cn/article.html?uc_param_str=frdnsnpfvecpntnwprdssskt&from=media#!wm_cid=' + str(
                cid)
            updateMongo(source_url, item)
            items = {}
            items['first_time'] = first_time
            items['save_time'] = now_time
            items['content_id'] = cid
            items['mid'] = mid
            redis_cli.rpush('dayuContentId', items)
        except:
            redis_cli.rpush('dayuContentId', data)

if __name__ == "__main__":
    mongoUri = 'mongodb://mongouser:zy79117911#@193.112.155.121:3717/admin'
    client = pymongo.MongoClient(mongoUri)
    db = client.Dayu
    collection = db.dayuIncrement

    redis_cli = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)

    for i in range(4):
        print(i)
        t = Thread(target=loop)
        t.start()