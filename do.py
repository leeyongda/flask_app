#!/usr/bin/env python
# ^*^ coding: utf-8 ^*^


from bson.objectid import ObjectId
from pymongo import MongoClient

client = MongoClient('localhost', 27017)

db = client['data_tui']

collection = db['upload_info']


def find_user(username):

    return db.user.find_one({"name": username})


def insert_user(username, password):

    return db.user.insert({"name": username, "passw": password, "pushtime": "07:00"})


def insert_info(list_info, username):
    return db.upload_info.insert({'info': list_info, "name": username})


def find_one_info(username):

    return db.upload_info.find_one({"name": username})


def update_one_info(username, list_info):

    return db.upload_info.update({"name": username}, {"$push": {"info": list_info}})


def find_info(username):

    return db.upload_info.find_one({"name": username})


def find_push(username):

    return db.upload_info.find_one({"name": username, "state": 0})


def update_push(uid):

    return db.upload_info.update({"_id": ObjectId(uid)}, {"$set": {"state": 1}})

# 传入 用户名,开启状态,时间,任务名字


def create_user_task(username, taks_name, enabled, time):

    return db.creat_user_task.insert({"name": username, "enable": enabled, "cronatab_time": time})