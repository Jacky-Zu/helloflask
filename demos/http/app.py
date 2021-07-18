# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li
    :license: MIT, see LICENSE for more details.
"""
import os

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

from jinja2 import escape
from jinja2.utils import generate_lorem_ipsum
from flask import Flask, make_response, request, redirect, url_for, abort, session, jsonify, g

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'secret string')
# @app.route('/more')
# def load_post():
#     return generate_lorem_ipsum(n=1)
#

#
#
# def is_safe_url(target):
#     ref_url = urlparse(request.host_url)
#     test_url = urlparse(urljoin(request.host_url, target))
#     return test_url.scheme in ('http', 'https') and \
#            ref_url.netloc == test_url.netloc
#


@app.route('/')
@app.route('/hi' ''', methods=['GET', 'POST']''')
def hi():
    # name = request.args.get('name', 'Jacky')  # 直接使用键索引且没有对应的键时，会400即请求无效
    # return '<h1>Hi, %s!<h1>' % name, 201  # 可以指定不同状态码
    name = request.args.get('name')
    if name is None:
        name = request.cookies.get('name', 'Human')
        response = '<h1>Hello, %s!</h1>' % name
        # 根据认证状态返回不同内容
        if 'logged_in' in session:
            response += '[Authenticated]'
        else:
            response += '[Not Authenticated]'
        return response


# redirect
@app.route('/hello')
def hello():
    # return '', 302, {'Location', 'http://localhost:5000/hi'}
    return redirect(url_for('hi'))


@app.route('/goback/<int:year>')
def go_back(year):
    return '<p>Welcome to %d!</p>' % (2021 - year)


# any的用法
# @app.route('/colors/<any(blue,white,red):color>') # any(value1,value2...):变量名
colors = ['blue', 'red', 'green']


@app.route('/colors/<any(%s):color>' % str(colors)[1:-1])
def three_colors(color):
    return '<p>Love is patient and kind. Love is not jealous or boastful or proud or rude.</p>'


# 请求钩子结合g
@app.before_request
def get_name():
    g.name = request.args.get('name')


# 手动返回错误响应
@app.route('/404')
def not_found():
    abort(404)  # 可以手动改状态码


# return error response
@app.route('/brew/<drink>')
def teapot(drink):
    if drink == 'coffee':
        abort(418)
    else:
        return 'A drop of tea.'


# 重定向实战
@app.route('/foo')
def foo():
    # data = {
    #     'name':'Jacky Zu',
    #     'gender':'male'
    # }
    # response = make_response(json.dumps(data))
    # response.mimetype = 'application/json'
    # return jsonify(name='Jacky Zu', gender='male')
    return '<h1>Foo page</h1><a href="%s">Do something and redirect</a>' % url_for('do_something',
                                                                                   next=request.full_path)


@app.route('/bar')
def bar():
    return '<h1>Bar page</h1><a href="%s">Do something and redirect</a>' % url_for('do_something',
                                                                                   next=request.full_path)


@app.route('/do_something_and_redirect')
def do_something():
    return redirect_back()


# 重定向至上个界面
def redirect_back(default='hi', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
        return redirect(url_for(default, **kwargs))


# return response with different formats
@app.route('/note', defaults={'content_type': 'text'})
@app.route('/note/<content_type>')
def note(content_type):
    content_type = content_type.lower()
    if content_type == 'text':
        body = '''Note
to: Peter
from: Jane
heading: Reminder
body: Don't forget the party!
'''
        response = make_response(body)
        response.mimetype = 'text/plain'
    elif content_type == 'html':
        body = '''<!DOCTYPE html>
<html>
<head></head>
<body>
  <h1>Note</h1>
  <p>to: Peter</p>
  <p>from: Jane</p>
  <p>heading: Reminder</p>
  <p>body: <strong>Don't forget the party!</strong></p>
</body>
</html>
'''
        response = make_response(body)
        response.mimetype = 'text/html'
    elif content_type == 'xml':
        body = '''<?xml version="1.0" encoding="UTF-8"?>
<note>
  <to>Peter</to>
  <from>Jane</from>
  <heading>Reminder</heading>
  <body>Don't forget the party!</body>
</note>
'''
        response = make_response(body)
        response.mimetype = 'application/xml'
    elif content_type == 'json':
        body = {"note": {
            "to": "Peter",
            "from": "Jane",
            "heading": "Remider",
            "body": "Don't forget the party!"
        }
        }
        response = jsonify(body)
        # equal to:
        # response = make_response(json.dumps(body))
        # response.mimetype = "application/json"
    else:
        abort(400)
    return response


# set cookie
@app.route('/set/<name>')
def set_cookie(name):
    response = make_response(redirect(url_for('hi')))
    response.set_cookie('name', name)
    return response


# log in
@app.route('/login')
def login():
    session['logged_in'] = True
    return redirect(url_for('hi'))


# log out
@app.route('/logout')
def logout():
    if 'logged_in' in session:
        session.pop('logged_in')
    return redirect(url_for('hi'))


# 管理后台
@app.route('/admin')
def admin():
    if 'logged_in' not in session:
        abort(403)
    return 'Welcome to the admin page'


# 验证url安全性
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

# 使用AJAX以局部刷新网页，异步加载长文章
@app.route('/post')
def show_post():
    post_body = generate_lorem_ipsum(n=2) # 生成两段长文章
    return '''
<h1>A very long post</h1>
<div class="body">%s</div>
<button id="load">Load More</button>
<script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
<script type="text/javascript">
$(function() {  
    $('#load').click(function() {
        $.ajax({
            url: '/more',             
            type: 'get',
            success: function(data){
                $('.body').append(data);
            }
        })
    })
})
</script>''' % post_body


@app.route('/more')
def load_post():
    return generate_lorem_ipsum(n=1)