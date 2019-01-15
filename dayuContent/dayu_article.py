# coding=utf-8

import requests
import json
import redis
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
#禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class Dayu(object):
    def __init__(self):
        self.redis_cli = redis.Redis(host='xxx', port=6379, db=1, password='xxx', charset='utf8', decode_responses=True)

    def get_dayu_article(self,aid):
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
        abstract = response['sub_title']
        #文章图片
        cover = [response['cover_url']]
        img_list = json.dumps(cover)
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
        channel_id = '777'

        print('url: ', url)
        print('author: ', author)
        print('avatar: ', avatar)
        print('publish_time: ', publish_time)
        print('read_count: ', read_count)
        print('comment_count: ', comment_count)
        print('platform: ', platform)
        print('channel_id: ', channel_id)

if __name__ == "__main__":
    d = Dayu()
    aid = '3cdeb1fb412f467383c0bc530b570261'
    d.get_dayu_article(aid)
