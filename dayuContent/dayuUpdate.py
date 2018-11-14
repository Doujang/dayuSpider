# -*- coding:utf-8 -*-

import requests
import json
from datetime import datetime
import time
import pymongo
import redis

'''
大鱼号号主文章增量抓取：监控40多万号主的每日增量
利用Redis+MongoDB实现分布式爬取，并实现去重功能
'''

def loadPage(end_time,mid):
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
    flag = True
    while flag:
        url = 'http://ff.dayu.com/contents/author/' + mid + '?biz_id=1002&_size=8&_page=' + str(n)
        print(url)
        try:
            body = requests.get(url,headers=headers,timeout=5).text
            time.sleep(0.1)
            print(body)
            response = json.loads(body)
            data = response['data']
        except:
            print('something is wrong!!!')
            error_time = int(time.time())
            with open('error01_1.txt', 'a') as e:
                e.write(mid + '\n')
                e.write(str(error_time) + '\n')
                e.write(url + '\n')
            print(url)
            return

        if len(data)==0:
            return
        else:
            n += 1

        #time.sleep(0.1)
        flag = parsePage(data,mid,end_time)

    print('================================华丽的分割线======================================')

def parsePage(data,mid,end_time):

    for i in range(len(data)):
        # 文章内容链接
        content_id = data[i]['content_id']
        source_url = 'http://a.mp.uc.cn/article.html?uc_param_str=frdnsnpfvecpntnwprdssskt&from=media#!wm_cid='+ content_id
        content_id = str(content_id)
        biz_id = data[i]['biz_id']
        biz_id = str(biz_id)
        page_url = 'http://ff.dayu.com/contents/' + content_id + '?biz_id=' + biz_id + '&_fetch_author=1&_fetch_incrs=1'
        print(page_url)

        # 文章标题
        title = data[i]['title']
        title = str(title)
        print(title)

        # 文章发布时间
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
        print('time_stamp',time_stamp)
        if time_stamp < end_time:
            return False
        else:
            pass

        # 发布时间转时间戳
        time_array = date_time.timetuple()
        time_stamp = int(time.mktime(time_array))

        # 文章分类
        try:
            category = data[i]['category']
            category = str(category)
        except:
            category = '[]'
        print(category)

        # 文章格式(1001为文本内容，1002为视频)
        format_type = data[i]['format_type']
        format_type = str(format_type)

        if format_type == '1001':
            item_list = loadLink(page_url)
            #time.sleep(0.1)
        else:
            continue

        # 文章内容
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

        # 关键词
        keywords = '[]'

        # 标签
        try:
            label = item_list['label']
        except:
            label = '[]'

        # 总阅读数
        try:
            total_read_count = item_list['total_read_count']
            print(total_read_count)
        except:
            total_read_count = 0

        # 应用外阅读数
        try:
            external_visit_count = item_list['external_visit_count']
            print(external_visit_count)
        except:
            external_visit_count = 0

        # 应用内阅读数
        try:
            internal_visit_count = item_list['internal_visit_count']
            print(internal_visit_count)
        except:
            internal_visit_count = 0

        # 评论数
        try:
            comment_count = item_list['comment_count']
            print(comment_count)
        except:
            comment_count = 0

        # 转发数
        try:
            share_count = item_list['share_count']
            print(share_count)
        except:
            share_count = 0

        # 推荐数
        try:
            impression_count = item_list['impression_count']
            print(impression_count)
        except:
            impression_count = 0

        # 保存时间
        save_time = int(time.time())

        items = {
            'content_id' : content_id,
            'mid':mid,
            'platfrom':'大鱼号',
            'is_cluster':'false',
            'source_url': source_url,
            'category': category,
            'title': title,
            'author': author,
            'datetime': str(date_time),
            'time_stamp':time_stamp,
            'keywords': keywords,
            'label': label,
            'total_read_count': total_read_count,
            'internal_visit_count': internal_visit_count,
            'external_visit_count': external_visit_count,
            'comment_count': comment_count,
            'article_content': article_content,
            'share_count': share_count,
            'impression_count': impression_count,
            'date_collection': [{'save_time':save_time,'impression_count': impression_count,'comment_count': comment_count,'total_read_count': total_read_count}]
        }

        # time.sleep(0.1)
        savePage(items)

    return True

def savePage(items):
    itemId = {}
    itemId['mid'] = items['mid']
    itemId['content_id'] = items['content_id']
    itemId['save_time'] = items['date_collection'][0]['save_time']
    itemId['first_time'] = items['date_collection'][0]['save_time']
    try:
        result = collection.insert(items)
        redis_cli.rpush('dayuContentId', itemId)
        print('1', result)
    except Exception as e:
        print('2', e)

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
        body = requests.get(source_url, headers=headers, timeout=5).text
        time.sleep(0.1)
        print(body)
        soup = json.loads(body)
        data = soup['data']
    except:
        print('something is wrong!!!')
        error_time = int(time.time())
        with open('error01_1.txt', 'a') as e:
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
        article_content = '[]'

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
    try:
        total_read_count = internal_visit_count + external_visit_count
        total_read_count = int(total_read_count)
    except:
        total_read_count = 0

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
        label = str(label)
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

    #time.sleep(0.1)
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
        time.sleep(0.01)
        print(body)
        soup = json.loads(body)
        label = soup['data']['items'][id]['tags']
        label = str(label)
        print(label)
    except:
        label = '[]'

    return label

if __name__ == "__main__":
    mongoUri = 'mongodb://mongouser:zy79117911#@193.112.155.121:3717/admin'
    client = pymongo.MongoClient(mongoUri)
    db = client.Dayu
    collection = db.dayuIncrement

    redis_cli = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)

    while True:
        new_time = int(time.time())
        data = redis_cli.lpop('dayuMid')
        data = eval(data)  # eval() 函数用来执行一个字符串表达式，并返回表达式的值。data里面是一个字符串，字符里面是一个字典
        end_time = data['end_time']
        mid = data['mid']
        print('mid',mid)
        with open('mid.txt', 'w') as fr:
            fr.write(mid + '\n')
            fr.write(str(end_time) + '\n')

        try:
            loadPage(end_time,mid)
            time.sleep(0.05)
            item = {}
            item['end_time'] = new_time
            item['mid'] = mid
            redis_cli.rpush('dayuMid',item)
        except:
            redis_cli.rpush('dayuMid', data)
