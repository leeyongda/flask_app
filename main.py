#!/usr/bin/env python
# ^*^ coding: utf-8 ^*^

import re
import flask_login
import requests
from flask import (Flask, jsonify, redirect, render_template, request, session,
                   url_for)
from lxml import etree
from werkzeug import secure_filename
from celery import Celery,task
from celery.schedules import crontab
import do
from datetime import datetime


s = requests.session()

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
cpp= Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
cpp.conf.update(app.config)
app.secret_key = 'adfffjjkjkj54545g54g54g54545'
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
ALLOWED_EXTENSIONS = set(['txt'])

class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(username):
    user = User()
    user.id = username
    return user

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("login.html")


@app.route('/admin', methods=['GET', 'POST'])
def Admin():
    if request.method == 'POST':
        info = ''
        global username
        username = request.form['name']
        password = request.form['passw']
        info = get_login(username, password)

        if info == u'登陆成功！':
            info = u'登陆成功！'
            user = User()
            user.id = username
            flask_login.login_user(user)
            get_name = do.find_user(username)

            if get_name == None:
                do.insert_user(username, password)
            return render_template('index.html', name=username)
        else:
            info = u'登陆失败,学号/密码错误！'

            return render_template('login.html', info=info)
    else:
        return redirect(url_for('index'))


@app.route('/admin/welcome')
@flask_login.login_required
def Admin_welcome():

    return render_template('welcome.html')


def get_login(username, password):
    try:

        url = 'http://bysj.zjtie.edu.cn:8080/Check_Admin.asp?Type=1'

        data = {

            'Cs_Admin_Name': username,

            'Cs_Admin_Pass': password,

            'Cs_Admin_Flag': "2"

        }

        res = s.post(url, data).text

        login_info = re.findall(
            r"<Script>alert(.*?);location.href='Change.asp';</Script>", res)

        if login_info == [u"('\u767b\u9646\u6210\u529f!')"]:

            info = u'登陆成功！'

            return info

        else:

            info = u'登陆失败,学号/密码错误！'

            return info
    except requests.ConnectionError:

        info = u'网络请求失败，请稍后登陆！'

        return info


@app.route('/admin/upload')
@flask_login.login_required
def upload():
    info = do.find_user(username)
    #print info
    if info == None:
        info = ''
    else:
        info = info['name']
    return render_template('upload.html', info = info)


def get_info():
    try:

        url1 = 'http://bysj.zjtie.edu.cn:8080/Journal_ListDo.asp?Type=8&DBFlag=0&Action=1'
        req = s.get(url1)
        tree = etree.HTML(req.text)
        ip_list = tree.xpath('//table[@class="xinxi2"]')
        trs = ip_list[0].xpath('tr')
        # print trs
        pre_item = {}
        count = 0
        dd = []
        for ip in trs[3::]:
            pre_item['time'] = ip.xpath('td[2]//text()')
            pre_item['read'] = ip.xpath('td[3]//text()')
            pre_item['wtime'] = ip.xpath('td[4]//text()')
            pre_item['pass'] = ip.xpath('td[5]//text()')
            pre_item['caozuo'] = ip.xpath('td[6]//text()')

            if pre_item['read'] == []:
                continue
            else:

                aa = {'date_time': pre_item['time'][0].strip(), 'piyue': pre_item['read'][0], 'write_time': pre_item['wtime']
                      [0], 'zhuangtai': pre_item['pass'][0], 'tongguo': pre_item['caozuo'][0]}

                dd.append(aa)

        return dd

    except requests.ConnectionError:
        info = u'网络请求失败，请稍后查询！'
        return info


@app.route('/admin/tuisong')
def tuisong():
    info = do.find_info(username)
    #push_zhouji()
    if info == None:
        info = ''
    else:
        info = info['info']
    return render_template('tuisong.html',items=info)


@app.route('/admin/data_table')
@flask_login.login_required
def table():
    msg = get_info()
    return render_template('data_table.html', items=msg, count=len(msg))


@app.route('/admin/querydate')
@flask_login.login_required
def qdate():

    return render_template('date.html')

import cStringIO
date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
@app.route('/ok', methods=["POST"])
def uploa_ok():
    info = {}
    list_info = []
    a = cStringIO.StringIO()
    try:
        if request.method == "POST":
           uplod_files = request.files.getlist('file')
          # name = request.form.get('username')
           for f in uplod_files:
               if f and allowed_file(f.filename):
                  a = cStringIO.StringIO()
                  # a.seek(0)
                  a.write(f.read())
                  info['date_time'] = date_time
                  info['filename'] = f.filename
                  info['content'] = a.getvalue()
                  info['state'] = 0
                  #print info
                  list_info.append({"filename":info['filename'],"date_time":info['date_time'],"content":info['content'],"state":info['state']})
                  a.close()
               else:
                   return jsonify({"code": 404})
           if do.find_one_info(username) == None:
               do.insert_info(list_info,username)
           else:
               for x in list_info:
                   do.update_one_info(username,x)

           return jsonify({"code":200})

        else:
            return jsonify({"code":200})
    except Exception,e:
        print e
        return jsonify({"code": 400})

#------------------------------------------
#异步推送任务 redis 队列


@cpp.task()
def find_user_push():
    do.findall_user_push()


#@cpp.task()
def push_zhouji():
    info = do.find_push()
    if info == None:
        pass
    else:
        do.update_push(info['_id'])
        post_zj(info['content'])

def post_zj(content):
    try:
        head = {
                # 'Referer': 'http://bysj.zjtie.edu.cn:8080/Journal_List.asp?Type=8&DBFlag=0',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest'
            }

        data = {
                'Journal_Content': content,
                'Jour_Count': '716',
                'DBFlag': '0',
                'Isfill': "1"
            }

        url = 'http://bysj.zjtie.edu.cn:8080/Journal_ListDo.asp?Type=5'
        post_info = s.post(url, headers=head, data=data)
        info = post_info.text
        return info

    except:

        return u'服务器异常！'

@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return redirect(url_for('index'))


# 设置404 页面
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# 未登录认证的，会自动跳转到登录页面
@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.debug = True
    app.run()
