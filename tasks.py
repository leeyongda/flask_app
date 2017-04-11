#!/usr/bin/env python
# ^*^ coding: utf-8 ^*^

from __future__ import absolute_import
from celery import task
from celery import Celery
from datetime import timedelta
from celery.schedules import crontab
from flask import Flask,request
from do import *
app = Celery('tasks',broker='redis://localhost:6379/0')

app.config_from_object('config')



def create_task(app, task, crontab_time,enable_vlaue):

    crate_user_task()

    pass
