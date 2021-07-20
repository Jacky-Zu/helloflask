import os
from flask import Flask, render_template, flash, redirect, url_for, Markup

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'secret string')
app.jinja_env.trim_blocks = True  # 删除语句后第一个空行
app.jinja_env.lstrip_blocks = True  # 删除语句行之前的空格

# Create template
user = {
    'username': 'Jacky Zu',
    'bio': 'A boy who studys BME in SJTU and loves movies and music.',
}
movies = [
    {
        'name': 'The Matrix',
        'Year': 1999
    },
    {
        'name': 'Let the Bullets Fly',
        'Year': 2010
    },
    {
        'name': 'Inception',
        'Year': 2010
    },
]


@app.route('/watchlist')
def watchlist():
    return render_template('watchlist.html', user=user, movies=movies)


@app.route('/')
def index():
    return render_template('index.html')


# 注册模板上下文处理函数
@app.context_processor
def inject_foo():
    foo = 'I am foo.'
    return dict(foo=foo)  # 在模板中直接使用foo变量


# template global function
@app.template_global()
def bar():
    return 'I am bar.'


# 自定义过滤器
@app.template_filter()
def musical(s):
    return s + Markup(' &#9835;')  # 音符的html符号


# 自定义测试器
@app.template_test()
def baz(n):
    if n == 'baz':
        return True
    return False


@app.route('/watchlist2')
def watchlist_with_static():
    return render_template('watchlist_with_static.html',
                           user=user,
                           movies=movies)


# 使用flash()函数实现闪现消息
@app.route('/flash')
def just_flash():
    flash(u'这里是祖伟韬的flask网站')  # 最好加上u
    return redirect(url_for('index'))


# 自定义错误界面
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500