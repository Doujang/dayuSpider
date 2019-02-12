# coding=utf-8

import requests
import json
import time
import hashlib
from urllib.parse import urlencode

'''
大鱼号文章评论内容抓取
'''

class Comment(object):
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
            para = 'xxx' + 'xxx.com' + str(mt)
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

if __name__ == "__main__":
    c = Comment()
    xss_item_id = 5313168751462901776
    url = 'xxx'
    c.get_dayu_comment(xss_item_id, url)
