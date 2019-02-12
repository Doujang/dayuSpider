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
                
        xss_item_id = response['_extra']['xss_item_id']
        comment_count = int(comment_count)
        if comment_count > 0:
            try:
                self.get_dayu_comment(xss_item_id, url)
            except Exception as e:
                print('get_dayu_comment is wrong!!!',e)

    def get_dayu_comment(self, xss_item_id, url):
        time_stamp = int(time.time() * 1000)
        param_data = {
            'uc_param_str': 'dnnivebichfrmintcpgieiwidsudpf',
            'app': 'ucnews-iflow',
            'sn': 16061024813939719977,
            'count': 100,
            'ts': -1,
            'hotValue': -1,
            'bid': 800,
            'm_ch': 500,
            'client_os': 'webapp',
            'client_version': '3.9.6.400',
            '_': time_stamp,
        }
        source_url = 'http://m.uczzd.cn/iflow/api/v2/cmt/article/{}/comments/byhot?'.format(xss_item_id) + urlencode(param_data)
        headers = {
            'Host': 'm.uczzd.cn',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (Linux; U; Android 4.4.2; zh-CN; OPPO R11 Build/NMF26X) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 UCNewsApp/3.9.6.400  Mobile Safari/534.30 AliApp(TUnionSDK/0.2.2)',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.uc.infoflow',
            'Cookie': 'sn=16061024813939719977; _uc_pramas=%7B%22nt%22%3A%222%22%2C%22dn%22%3A%2224008021916-db0ded79%22%2C%22fr%22%3A%22android%22%2C%22cp%22%3A%22isp%3A%E7%A7%BB%E5%8A%A8%3Bprov%3A%E5%B9%BF%E4%B8%9C%3Bcity%3A%E6%B7%B1%E5%9C%B3%3Bna%3A%E4%B8%AD%E5%9B%BD%3Bcc%3ACN%3Bac%3A%22%2C%22ve%22%3A%223.9.6.400%22%7D'
        }
        resp = requests.get(source_url, headers=headers, timeout=5).json()
        comments = resp['data']['comments']
        comments_map = resp['data']['comments_map']
        for comment in comments:
            data = comments_map[comment]
            # 当前请求Unix时间戳
            mt = int(time.time())
            # API签名字符串
            para = 'b#28ac3c1abc' + 'juejinchain.com' + str(mt)
            sign = hashlib.md5(para.encode(encoding='UTF-8')).hexdigest()
            # 评论用户名称
            user_name = data['user']['nickname']
            # 评论用户头像链接
            user_img_url = data['user']['faceimg']
            # 评论内容text
            text = data['content']
            # 评论时间
            create_time = data['timeShow']
            create_time = int(create_time / 1000)
            # 评论内容点赞数
            digg_count = data['up_cnt']
            # 评论回复数
            reply_comment = data['children']
            reply_count = len(reply_comment)

            # 获取回复comment
            reply_list = []
            if reply_count > 0:
                for reply in reply_comment:
                    reply_data = comments_map[reply]
                    # 评论用户名称
                    reply_user_name = reply_data['user']['nickname']
                    # 评论用户头像链接
                    reply_user_img_url = reply_data['user']['faceimg']
                    # 评论内容text
                    reply_text = reply_data['content']
                    # 评论时间
                    reply_create_time = reply_data['timeShow']
                    reply_create_time = int(reply_create_time / 1000)
                    # 评论内容点赞数
                    reply_digg_count = reply_data['up_cnt']

                    items = {
                        'nickname': reply_user_name,
                        'avatar': reply_user_img_url,
                        'content': reply_text,
                        'fabulous': reply_digg_count,
                        'comment_time': reply_create_time,
                    }
                    reply_list.append(items)

            reply_list = json.dumps(reply_list)
            print('reply_list: ', reply_list)

            items = {
                'mt': mt,
                'sign': sign,
                'arc_url': url,
                'nickname': user_name,
                'avatar': user_img_url,
                'content': text,
                'reply': reply_count,
                'fabulous': digg_count,
                'comment_time': create_time,
                'reply_list': reply_list,
            }
            print(items)

            # 文章评论信息存储
            try:
                comment_test_url = 'http://dev.api.juejinchain.cn/index/spider/toutiao_comment'
                resp = requests.post(comment_test_url, data=items)
                print(resp.text)
                comment_product_url = 'http://api.juejinchain.com/index/spider/toutiao_comment'
                resp2 = requests.post(comment_product_url, data=items)
                print(resp2.text)
            except Exception as e:
                print('insert db wrong!!!!', e)

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
