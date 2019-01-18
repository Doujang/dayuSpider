# coding=utf-8

import requests
import json
import redis
import time
import hashlib
from datetime import datetime
from threading import Thread
from requests.packages.urllib3.exceptions import InsecureRequestWarning
#禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

'''大鱼号文章内容抓取'''

class Dayu(object):
    def __init__(self):
        self.redis_cli = redis.Redis(host='xxx', port=6379, db=1, password='xxx', charset='utf8', decode_responses=True)

    def get_dayu_article(self,item):
        aid = item['article_id']
        source_url = 'https://ff.dayu.com/contents/origin/{}?biz_id=1002&_fetch_author=1&_fetch_incrs=1'.format(aid)
        headers = {
            'Host': 'ff.dayu.com',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }

        resp = requests.get(source_url,headers=headers,timeout=5,verify=False)
        response = resp.json()['data']

        #文章内容
        content = response['body']['text']
        inner_imgs = response['body']['inner_imgs']
        for i in range(len(inner_imgs)):
            inner_img = inner_imgs[i]
            j = i + 1
            img = '<!--{img:'+ str(j) + '}-->'
            img2 = '<img src={}>'.format(inner_img['url'])
            content = content.replace(img,img2)
        #文章摘要
        describe = response['sub_title']
        #文章图片
        cover = [response['cover_url']]
        img_url = json.dumps(cover)
        #文章标题
        title = response['title']
        #文章URL
        cid = response['content_id']
        url = 'http://a.mp.uc.cn/article.html?uc_param_str=frdnsnpfvecpntnwprdssskt&from=media#!wm_cid={}'.format(cid)
        #文章作者
        author = response['_author']['author_name']
        #作者logo
        avatar = response['_author']['avatar_url']
        #文章的发布时间
        dt = response['published_at']
        x = dt[11:19]
        y = dt[:10]
        t = str(y) + " " + str(x)
        publish_time = datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
        #文章阅读数
        read_count = response['_incrs']['click1'] + response['_incrs']['click2'] + response['_incrs']['click3']
        #文章评论数
        comment_count = response['_incrs']['comment']
        #文章所在平台
        platform = 'dayu'
        #文章频道id
        channel_id = item['channel_id']

        #当前请求Unix时间戳
        mt = int(time.time())
        #API签名字符串
        para = 'xxx' + 'xxx.com' + str(mt)
        sign = hashlib.md5(para.encode(encoding='UTF-8')).hexdigest()
        # 媒体ID(即用户ID)
        mid = 0
        #文章来源
        spider = '淘金阁'
        source = 'UC头条'

        print('content: ', content)
        print('abstract: ', describe)
        print('img_url: ', img_url)
        print('title: ', title)
        print('url: ', url)
        print('author: ', author)
        print('avatar: ', avatar)
        print('publish_time: ', publish_time)
        print('read_count: ', read_count)
        print('comment_count: ', comment_count)
        print('platform: ', platform)
        print('channel_id: ', channel_id)

        items = {
            'mt': mt,
            'sign': sign,
            'mid': mid,
            'channel_id': channel_id,
            'url': url,
            'title': title,
            'img_url': img_url,
            'author': author,
            'author_logo': avatar,
            'spider': spider,
            'source': source,
            'describe': describe,
            'read_count': read_count,
            'comment_count': comment_count,
            'publish_time': publish_time,
            'content': content,
        }

        if len(content) > 10:
            #文章信息存储
            try:
                url = 'http://xxx'
                requests.post(url, data=items)
            except Exception as e:
                print('insert wrong!!!!', e)

    def run(self):
        while True:
            data = self.redis_cli.lpop('spider_tjg_dayu_article')
            print(type(data), data)
            if data == None:
                time.sleep(600)
                continue
            data = eval(data)  # str转成dict
            try:
                self.get_dayu_article(data)
            except Exception as e:
                print('something is wrong!!!',e)


if __name__ == "__main__":
    for i in range(5):
        d = Dayu()
        work_thread = Thread(target=d.run)
        work_thread.start()
