# -*- coding: utf-8 -*-
from flask import render_template, request, url_for, redirect, \
    flash, jsonify, session
from flask_login import login_user, login_required, logout_user, current_user

from watchlist import app, db
import flask_excel
from watchlist.models import User, North, Daily, Sea, Repayment, Fee
from jinja2.utils import generate_lorem_ipsum
import pymysql
import datetime

flask_excel.init_excel(app)

category = [{'id': 1, 'bank': '蓝海', 'channel': '信用飞', 'guarantor': '花旗'},
            {'id': 2, 'name': '齐商', 'channel': '我来贷', 'guarantor': '经协'},
            {'id': 3, 'bank': '四平', 'channel': '信用飞', 'guarantor': '花旗'},
            {'id': 4, 'bank': '四平', 'channel': '快牛', 'guarantor': '花旗'},
            {'id': 5, 'bank': '四平', 'channel': '全民钱包', 'guarantor': '大秦'},
            {'id': 6, 'bank': '威海', 'channel': '信用飞', 'guarantor': '花旗'},
            {'id': 7, 'bank': '长发展', 'channel': '绿信', 'guarantor': '大秦'},
            {'id': 8, 'bank': '长发展', 'channel': '极融', 'guarantor': '大秦'}]

banks = ['蓝海', '齐商', '四平', '威海', '长发展']

channels = ['信用飞', '我来贷', '快牛', '全民钱包', '绿信', '极融']

guarantors = ['花旗', '经协', '大秦']


@app.route('/index/', methods=['GET', 'POST'])
@login_required
def index():
    if session.get('name'):
        session.pop('name')
    page = request.args.get('page', 1, type=int)  # 当前页数
    per_page = request.args.get('per_page', 10, type=int)  # 设置每页数量

    # capital = request.form.get('comp_select1')
    # assets = request.form.get('comp_select2')
    # guarantor = request.form.get('comp_select3')

    # 按日期降序
    paginate = Daily.query.order_by(db.desc('date_info')).paginate(page, per_page, error_out=False)
    data = paginate.items
    return render_template('index.html', paginate=paginate, movies=data)


@app.route('/fee/', methods=['GET', 'POST'])
@login_required
def fee():
    if session.get('fee_period'):
        session.pop('fee_period')
    page = request.args.get('page', 1, type=int)  # 当前页数
    per_page = request.args.get('per_page', 10, type=int)  # 设置每页数量

    # 按日期降序
    paginate = Fee.query.order_by(db.desc('date_info')).paginate(page, per_page, error_out=False)
    data = paginate.items
    return render_template('fee.html', paginate=paginate, movies=data)


@app.route('/charge/', methods=['GET', 'POST'])
@login_required
def charge():
    page = request.args.get('page', 1, type=int)  # 当前页数
    per_page = request.args.get('per_page', 10, type=int)  # 设置每页数量
    if session.get('fee_period'):
        # 按日期降序
        paginate = Fee.query.filter_by(repay_type=session.get('repay_type'))\
            .order_by(db.desc('date_info')).paginate(page, per_page, error_out=False)
    else:
        paginate = Fee.query.order_by(db.desc('date_info')).paginate(page, per_page, error_out=False)
    data = paginate.items
    return render_template('charge.html', paginate=paginate, movies=data)


@app.route('/fees/', methods=['GET', 'POST'])
def fees():
    fee_period = request.form.get('fee_period')
    if fee_period:
        session['fee_period'] = fee_period
        page = request.args.get('page', 1, type=int)  # 当前页数
        per_page = request.args.get('per_page', 10, type=int)  # 设置每页数量

        # 按日期降序
        paginate = Fee.query.filter_by(period=fee_period).\
            order_by(db.desc('date_info')).paginate(page, per_page, error_out=False)
        data = paginate.items
        return render_template('charge.html', paginate=paginate, movies=data)
    else:
        return redirect(url_for('charge'))


@app.route('/repayment/', methods=['GET', 'POST'])
@login_required
def repayment():
    if session.get('repay_type'):
        session.pop('repay_type')
    page = request.args.get('page', 1, type=int)  # 当前页数
    per_page = request.args.get('per_page', 10, type=int)  # 设置每页数量

    # 按日期降序
    paginate = Repayment.query.order_by(db.desc('date_info')).paginate(page, per_page, error_out=False)
    data = paginate.items
    return render_template('repayment.html', paginate=paginate, movies=data)


@app.route('/repay/', methods=['GET', 'POST'])
@login_required
def repay():
    page = request.args.get('page', 1, type=int)  # 当前页数
    per_page = request.args.get('per_page', 10, type=int)  # 设置每页数量
    if session.get('repay_type'):
        # 按日期降序
        paginate = Repayment.query.filter_by(repay_type=session.get('repay_type'))\
            .order_by(db.desc('date_info')).paginate(page, per_page, error_out=False)
    else:
        paginate = Repayment.query.order_by(db.desc('date_info')).paginate(page, per_page, error_out=False)
    data = paginate.items
    return render_template('repay.html', paginate=paginate, movies=data)


@app.route('/content/', methods=['GET', 'POST'])
@login_required
def content():
    page = request.args.get('page', 1, type=int)  # 当前页数
    per_page = request.args.get('per_page', 10, type=int)  # 设置每页数量
    if session.get('name'):
        # 按日期降序
        paginate = Daily.query.filter_by(product_name=session.get('name'))\
            .order_by(db.desc('date_info')).paginate(page, per_page, error_out=False)
    else:
        paginate = Daily.query.order_by(db.desc('date_info')).paginate(page, per_page, error_out=False)
    data = paginate.items
    return render_template('content.html', paginate=paginate, movies=data)


@app.route('/blue/', methods=['GET', 'POST'])
@login_required
def blue():
    page = request.args.get('page', 1, type=int)  # 当前页数
    per_page = request.args.get('per_page', 10, type=int)  # 设置每页数量
    if session.get('period'):
        # 按日期降序
        paginate = Sea.query.filter_by(period=session.get('period'))\
            .order_by(db.desc('date_info')).paginate(page, per_page, error_out=False)
    else:
        paginate = Sea.query.order_by(db.desc('date_info')).paginate(page, per_page, error_out=False)
    data = paginate.items
    return render_template('blue.html', paginate=paginate, movies=data)


@app.route('/bank/', methods=['GET', 'POST'])
@login_required
def bank():
    if session.get('period'):
        session.pop('period')
    cates = ['9', '12']
    page = request.args.get('page', 1, type=int)  # 当前页数
    per_page = request.args.get('per_page', 10, type=int)  # 设置每页数量
    # 按日期降序
    paginate = Sea.query.order_by(db.desc('date_info')).paginate(page, per_page, error_out=False)
    data = paginate.items
    return render_template('sea.html', paginate=paginate, movies=data, cates=cates)
    # return render_template('sea.html')


@app.route('/north/', methods=['GET', 'POST'])
@login_required
def north():
    page = request.args.get('page', 1, type=int)  # 当前页数
    per_page = request.args.get('per_page', 10, type=int)  # 设置每页数量
    # 按日期降序
    paginate = North.query.order_by(db.desc('date_time')).paginate(page, per_page, error_out=False)
    data = paginate.items

    return render_template('north.html', paginate=paginate, movies=data)


@app.route('/upload/', methods=['GET', 'POST'])
def upload():
    period = request.form.get('period')
    if period:
        session['period'] = period
        page = request.args.get('page', 1, type=int)  # 当前页数
        per_page = request.args.get('per_page', 10, type=int)  # 设置每页数量

        # 按日期降序
        paginate = Sea.query.filter_by(period=period).\
            order_by(db.desc('date_info')).paginate(page, per_page, error_out=False)
        data = paginate.items
        return render_template('blue.html', paginate=paginate, movies=data)
    else:
        return redirect(url_for('blue'))


@app.route('/pay/', methods=['GET', 'POST'])
def pay():
    repay_type = request.form.get('repay_type')
    if repay_type:
        session['repay_type'] = repay_type
        page = request.args.get('page', 1, type=int)  # 当前页数
        per_page = request.args.get('per_page', 10, type=int)  # 设置每页数量

        # 按日期降序
        paginate = Repayment.query.filter_by(repay_type=repay_type).\
            order_by(db.desc('date_info')).paginate(page, per_page, error_out=False)
        data = paginate.items
        return render_template('repay.html', paginate=paginate, movies=data)
    else:
        return redirect(url_for('repay'))


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('用户名或密码错误')
            return redirect(url_for('login'))

        user = User.query.first()

        if username == user.username and user.validate_password(password):
            login_user(user)
            flash('登录成功')
            return redirect(url_for('index'))

        flash('用户名或密码错误')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/download/')
def download():
    query = db.session.query(Daily.date_info.label('日期'),
                             Daily.product_name.label('合作产品名称'),
                             Daily.repay_amount.label('当日还款总额'),
                             Daily.repay_principal.label('当日还款本金'),
                             Daily.repay_interest.label('当日还款利息'),
                             Daily.repay_number.label('当日还款笔数'),
                             Daily.advance_settlement.label('提前结清笔数'),
                             Daily.advance_amount.label('提前结清金额'),
                             Daily.lend_amount.label('当日放款金额'),
                             Daily.lend_number.label('当日放款笔数')
                             ).order_by(Daily.date_info.desc())
    page = query.all()
    return flask_excel.make_response_from_query_sets(
        page, column_names=['日期', '合作产品名称', '当日还款总额', '当日还款本金',
                            '当日还款利息', '当日还款笔数', '提前结清笔数', '提前结清金额', '当日放款金额',
                            '当日放款笔数'],
        file_type='xlsx', file_name='报表.xlsx')


@app.route('/load/', methods=['GET', 'POST'])
def load():
    # capital = request.form.get('comp_select1')
    assets = request.form.get('comp_select2')
    # guarantor = request.form.get('comp_select3')
    if assets:
        session['name'] = assets
        page = request.args.get('page', 1, type=int)  # 当前页数
        per_page = request.args.get('per_page', 10, type=int)  # 设置每页数量

        # 按日期降序
        paginate = Daily.query.filter_by(product_name=assets).\
            order_by(db.desc('date_info')).paginate(page, per_page, error_out=False)
        data = paginate.items
        return render_template('content.html', paginate=paginate, movies=data)
    else:
        return redirect(url_for('content'))


@app.route('/test/')
def test():
    data = '测试'
    return render_template('test1.html', data=data)


@app.route('/more')
def load_post():
    return generate_lorem_ipsum(n=1)