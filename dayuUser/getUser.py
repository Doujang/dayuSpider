# -*- coding:utf-8 -*-

import json
import requests
from pymysql import *
import time
import random

def user_rearch(style,user_list_1):
    for i in range(2000000):
        headers = {
            'Host':'iflow.uczzd.cn',
            'Content-Type':'application/json',
            'Accept-Encoding':'gzip, deflate, sdch',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Cookie': '__guid=225131074.2726864781373896000.1533184021308.0845; monitor_count=112'

        }
        #url = 'http://iflow.uczzd.cn/iflow/api/v1/channel/100?app=ssrd_an-iflow&uc_param_str=dnnivebichfrmintcpgieiwidsudsvme&dn=20482094026-ef950e83&nn=KvmHLiOdeIT2rexCpkFGm%2BYDW%2FHdqq%2BMYRNYGyimDi09EA%3D%3D&ve=3.7.0.370&bi=35581&ch=ttzd_1&fr=android&mi=EVA-DL00&nt=2&pc=KvmV1x3IdVeVUcW4KYHoQ%2F0%2BGmOVE9RouD3v1kvPjB7rQbAKauXLg2zFyhW6oaEvEGVNaFJSFHi0EY6M5JdJCcon&gp=KvmNWpY1gQobV38QTTsxqU2pIkrcVnfhYSQXhTIprvuETQ%3D%3D&wf=&ut=Kvm7o%2BfVFLKwOCZ%2FjeuC0fZqc%2FHcyY4ym3LNkHxgntJRKQ%3D%3D&ai=Kvn3dN4oRyUmetA5TKb7zmvMQCKsYiR7o3bCzZbPak%2BavA%3D%3D&sv=release&me=Kvm6vhVME0Ql5pLjn3q9dHU1&content_ratio=0&auto=1&recoid=&method=new&ftime=0&_tm=1533189363565&user_tag=bTkwBA6mcd%2BmfoJ0p2M%3D&count=10'
        #requests.get(source_url,headers=headers)
        #time.sleep(0.2)
        tag = random.choice(style)
        print(tag)
        url = 'http://iflow.uczzd.cn/iflow/api/v1/channel/' + tag + '?app=ucnews-iflow&uc_param_str=dnnivebichfrmintcpgieiwidsudsvme&dn=20482094026-ef950e83&nn=KvmHLiOdeIT2rexCpkFGm%2BYDW%2FHdqq%2BMYRNYGyimDi09EA%3D%3D&ve=3.7.0.370&bi=35581&ch=ttzd_1&fr=android&mi=EVA-DL00&nt=2&pc=KvmV1x3IdVeVUcW4KYHoQ%2F0%2BGmOVE9RouD3v1kvPjB7rQbAKauXLg2zFyhW6oaEvEGVNaFJSFHi0EY6M5JdJCcon&gp=KvmNWpY1gQobV38QTTsxqU2pIkrcVnfhYSQXhTIprvuETQ%3D%3D&wf=&ut=Kvm7o%2BfVFLKwOCZ%2FjeuC0fZqc%2FHcyY4ym3LNkHxgntJRKQ%3D%3D&ai=Kvn3dN4oRyUmetA5TKb7zmvMQCKsYiR7o3bCzZbPak%2BavA%3D%3D&sv=release&me=Kvm6vhVME0Ql5pLjn3q9dHU1&no_op=0&content_ratio=0&auto=0&recoid=10234692666428933737&puser=1&method=new&ftime=1533189363191&_tm=1533189363981&user_tag=bTkwBPXdbtDJKYUFyDQ%3D&count=10&ssign=Kvg6qOcrD6Q2QjusjWv8f0TDZhX56xfy%2B1DgIaZpczst3agnR9nMf884ieW5PZtJzxs%3D'
        body = requests.get(url,headers=headers,timeout=5,verify=False).text
        print(body)
        soup = json.loads(body)
        items = soup['data']['items']
        response = soup['data']['articles']
        print(response)

        for i in range(len(items)):
            id = items[i]['id']
            try:
                user = response[id]['source_name']
            except:
                user = 'None'
                pass
            print(user)
            user_list2 = user_list_1
            print(len(user_list2))

            user_list2.append(user)
            print(len(user_list2))
            time.sleep(0.5)

            new_user_list = list(set(user_list2))
            new_user_list.sort(key = user_list2.index)
            print(len(new_user_list))

            if len(new_user_list) == len(user_list_1):
                print('good!')
                userName = new_user_list[-1]
                userName = str(userName)
                print(userName)
                mid = 'None'
                sql = """insert into Newdayu04(userName,mid) value(%s,%s)"""
                try:
                    cursor.execute(sql,(userName,mid))
                    db.commit()
                except:
                    db.rollback()
            else:
                pass

            user_list_1 = new_user_list

        print(str(i)+' is ok')
        time.sleep(5)
        user_list_1 = new_user_list



if __name__ == "__main__":
    db = connect(host="localhost", port=3306, db="spider", user="root", password="123456", charset="utf8")
    cursor = db.cursor()

    try:
        sql = """SELECT userName FROM Newdayu04"""
        MainUrl = cursor.execute(sql)
        data = cursor.fetchall()
        db.commit()
    except:
        db.rollback()

    user_list = []
    for i in range(len(data)):
        userName = data[i][0]
        userName = str(userName)
        user_list.append(userName)
    #print(user_list)

    user_set = set(user_list)
    user_list_1 = list(user_set)
    user_list_1.sort(key=user_list.index)
    print(len(user_list_1))


    style = ['179223212','100','500','1525483516','10308','923258246','26325229','323644874','1105405272','701104723','1911322354','10012','90002',
             '10122','10013','1001932710','696724','90001','242677432','835729','1972619079','1213442674','169476544','472933935','586710362',
             '1404457531635','681723207','10000','408250330','90003','10008','674534','684625112','701538712','66498','90005','10005']
    user_rearch(style,user_list_1)
    db.close()