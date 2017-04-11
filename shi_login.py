# coding:utf8
import re


import os
import sys


app_root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(app_root, 'requests'))
# sys.path.insert(0, os.path.join(app_root, 'lxml'))
import requests
from lxml import etree

from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
reload(sys)
sys.setdefaultencoding('utf8')
s = requests.session()

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():

    return 'Hello,经院生活帮 api,By Coding!'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        info = get_login(username,password)
        # print info

        if info == u'登陆成功！':
            info = u'登陆成功！'
            return jsonify({"msg": info,"code":200})

        else:
            info = u'登陆失败,学号/密码错误！'
            return jsonify({"msg": info, "code": 404})

    else:

        return u'请登陆！'




def get_login(username, password):
    try:
        url = 'http://bysj.zjtie.edu.cn:8080/Check_Admin.asp?Type=1'

        data = {
            'Cs_Admin_Name': username,
            'Cs_Admin_Pass': password,
            'Cs_Admin_Flag': "2"
        }

        res = s.post(url, data).text
        login_info = re.findall(r"<Script>alert(.*?);location.href='Change.asp';</Script>", res)

        if login_info == [u"('\u767b\u9646\u6210\u529f!')"]:
            info = u'登陆成功！'
           
            return info

        else:
            info = u'登陆失败,学号/密码错误！'
            return info
           

    except requests.ConnectionError:
        info = u'网络请求失败，请稍后登陆！'
        return info

@app.route('/query', methods=['GET', 'POST'])
def get_query():
    if request.method == 'POST':
         username = request.form['username']
         password = request.form['password']
         # return 'hello'
         msg = get_info(username,password)
         # return msg

         if msg == u'登陆失败,学号/密码错误！':
             return jsonify({"code": 404, "msg": "登陆失败,学号/密码错误！"})
         elif msg ==  u'网络请求失败，请稍后查询！':
             return jsonify({"code": 500, "msg": "网络请求失败，请稍后查询！"})
         else:
             return jsonify({"code": 200, "msg": "登陆成功！", "info": msg})

    else:

        return u'请登陆！'


def get_info(username, password):
    try:
        url = 'http://bysj.zjtie.edu.cn:8080/Check_Admin.asp?Type=1'

        data = {
            'Cs_Admin_Name': username,
            'Cs_Admin_Pass': password,
            'Cs_Admin_Flag': "2"
        }

        res = s.post(url, data).text
        login_info = re.findall(r"<Script>alert(.*?);location.href='Change.asp';</Script>", res)

        if login_info == [u"('\u767b\u9646\u6210\u529f!')"]:
            
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
                    
                    aa = {'时间段':pre_item['time'][0].strip(), '批阅状态': pre_item['read'][0], '撰写日期':pre_item['wtime'][0], '状态':pre_item['pass'][0], '是否通过': pre_item['caozuo'][0]}

                    dd.append(aa)

            return dd
    
        else:
            info =  u'登陆失败,学号/密码错误！'
            return info


    except requests.ConnectionError:
        info =  u'网络请求失败，请稍后查询！'
        return info






#提交周记
@app.route('/postzj', methods=['GET', 'POST'])
def postzz():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        content = request.form['content']
        info = get_login(username,password)
        if info == u'登陆成功！':
            msg =Post_zj(content)
            return jsonify({"code":200,"msg":u'登陆成功！',"info":msg})
        elif  info == u'登陆失败,学号/密码错误！':
            return jsonify({"code":400,"msg":u'登陆失败,学号/密码错误！'})
        else:
            return jsonify({"code":404,"msg":u'网络请求失败，请稍后提交！'})
    else:
        return u'请登陆！'

def Post_zj(content):
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



@app.route('/edit', methods=['GET', 'POST'])
def get_edit():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        info = get_login(username,password)
        if info == u'登陆成功！':
            msg = test()

            return jsonify({"code":200,"msg":u'登陆成功！',"info":msg})
        elif  info == u'登陆失败,学号/密码错误！':
            return jsonify({"code":400,"msg":u'登陆失败,学号/密码错误！'})

        else:
            return jsonify({"code":404,"msg":u'网络请求失败，请稍后提交！'})

    else:
        return u'请登陆！'



def test():
    try:
        url1 = 'http://bysj.zjtie.edu.cn:8080/Journal_ListDo.asp?Type=8&DBFlag=0&Action=1'
        req = s.get(url1)
        tree = etree.HTML(req.text)
        ip_list = tree.xpath('//table[@class="xinxi2"]')
        trs = ip_list[0].xpath('tr')

        pre_item = {}
        count = 0
        dd = []
        for ip in trs[3::]:
            pre_item['read'] = ip.xpath('td[3]//text()')
            pre_item['time'] = ip.xpath('td[2]//text()')
            pre_item['cc'] = ip.xpath("td[7]/a/@onclick")

            if pre_item['read'] == []:
                continue
            elif pre_item['read'][0] == u'暂未批阅':
                count += 1
                id = re.findall(r"Journal(\d+)", pre_item['cc'][1], re.S)
                aa = {u'id':id[0], u'时间段': pre_item['time'][0].strip(), u'批阅状态': pre_item['read'][0]}
                dd.append(aa)

                return dd
            else:
                return None

    except:
        return u'服务器出错！'

@app.route('/post_edit', methods=['GET', 'POST'])
def post_edit():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        content = request.form['content']
        idd = request.form['id']
        info = get_login(username, password)
        if info == u'登陆成功！':
            msg = Edit_zj(idd, content)

            return jsonify({"code": 200, "msg": u'登陆成功！', "info": msg})
        elif info == u'登陆失败,学号/密码错误！':
            return jsonify({"code": 400, "msg": u'登陆失败,学号/密码错误！'})

        else:
            return jsonify({"code": 404, "msg": u'网络请求失败，请稍后提交！'})

    else:
        return u'请登陆！'


# 修改当前星期周记，已批阅的周记不能修改
def Edit_zj(idd,content):
    try:
        head = {
                # 'Referer': 'http://bysj.zjtie.edu.cn:8080/Journal_List.asp?Type=8&DBFlag=0',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest'
            }
        data = {
                'Journal_Content': content,
                'Jour_Count': 715,
                'DBFlag': '0',
                'Id': idd

            }
        url = 'http://bysj.zjtie.edu.cn:8080/Journal_ListDo.asp?Type=7'
        post_info = s.post(url, headers=head, data=data)
        return post_info.text
    except Exception,e:
        return e


if __name__ == '__main__':

    app.run(debug=True)

# if __name__ == '__main__':
#     print "---------------------------------------------"
#     print u"   人生苦短，我用Python!           "
#     print u"   基于Python---实习周记小助手         "
#     print u"   BY Coding QQ:963189900(任何问题联系QQ)                     "
#     print u"                      "
#     print u"   提示："
#     print u"   输入q:可查询当前周记批阅情况。"
#     print u"   输入e:可修改当周周记。"
#     print u"   输入w:可上传当周周记。"
#     print u"   输入c:退出程序。"

#     print "---------------------------------------------"
#     name = raw_input(u"请输入指令:".decode('utf-8').encode('gbk'))
#     if name == 'q':
#         username = raw_input(u"请输入学号:".decode('utf-8').encode('gbk'))
#         password = raw_input(u"请输入密码:".decode('utf-8').encode('gbk'))
#         get_info(username, password)
#     elif name == 'e':
#         username = raw_input(u"请输入学号:".decode('utf-8').encode('gbk'))
#         password = raw_input(u"请输入密码:".decode('utf-8').encode('gbk'))
#         get_login(username, password)
#         test()
#         id = raw_input(u"请输入编号:".decode('utf-8').encode('gbk'))
#         file_name = raw_input(u"请输入文件名:".decode('utf-8').encode('gbk'))
#         Edit_zj(id, file_name)
#     elif name == 'w':
#         username = raw_input(u"请输入学号:".decode('utf-8').encode('gbk'))
#         password = raw_input(u"请输入密码:".decode('utf-8').encode('gbk'))
#         get_login(username, password)
#         file_name = raw_input(u"请输入文件名:".decode('utf-8').encode('gbk'))
#         Post_zj(file_name)
#     elif name == 'c':
#         exit(0)

#     else:
#         print u'指令不存在,请输入正确指令！'
#         main()
