#coding = utf-8

from pymysql import *

def new_user():
    db = connect(host="localhost", port=3306, db="spider", user="root", password="123456", charset="utf8")
    conn = db.cursor()
    try:
        sql = 'SELECT mid FROM Newdayu25'
        conn.execute(sql)
        data = conn.fetchall()
        db.commit()
    except:
        db.rollback()
    user_list = []
    for i in range(len(data)):
        mid = data[i][0]
        if mid == '':
            pass
        elif mid == 'None':
            pass
        else:
            user_list.append(mid)
    print(user_list)

    user_set = set(user_list)
    user_list_1 = list(user_set)
    user_list_1.sort(key=user_list.index)
    print(len(user_list_1))
    db.close()

    return user_list_1

def update_user(user_list_1):
    user_lists = new_user()
    user_list2 = user_list_1

    for i in user_lists:
        user_list2.append(i)
    print(len(user_list2))

    new_user_list = list(set(user_list2))
    new_user_list.sort(key=user_list2.index)
    print(len(new_user_list))

    for i in range(418835,len(new_user_list)):
        print(i)
        mid = new_user_list[i]
        sql = """insert into dayu_test(mid) value(%s)"""
        try:
            conn.execute(sql, mid)
            db.commit()
        except:
            db.rollback()


if __name__ == "__main__":
    db = connect(host="localhost", port=3306, db="spider", user="root", password="123456", charset="utf8")
    conn = db.cursor()
    try:
        sql = 'SELECT mid FROM dayu_test'
        MainUrl = conn.execute(sql)
        data = conn.fetchall()
        db.commit()
    except:
        db.rollback()
    user_list = []
    #print(len(data))
    for i in range(len(data)):
        mid = data[i][0]
        user_list.append(mid)
    #print(user_list)

    user_set = set(user_list)
    user_list_1 = list(user_set)
    user_list_1.sort(key=user_list.index)
    print(len(user_list_1))

    update_user(user_list_1)
    db.close()