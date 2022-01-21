# -*- coding: utf-8 -*-
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from watchlist import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))


class Daily(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_info = db.Column(db.String(10))
    product_name = db.Column(db.String(10))
    # 当日还款
    repay_amount = db.Column(db.Float(50))
    repay_principal = db.Column(db.Float(50))
    repay_interest = db.Column(db.Float(50))
    repay_number = db.Column(db.Integer())
    # 提前结清笔数
    advance_settlement = db.Column(db.Float(50))
    # 提前结清金额
    advance_amount = db.Column(db.Float(50))
    # 当日放款金额
    lend_amount = db.Column(db.Float(50))
    # 当日放款笔数
    lend_number = db.Column(db.Float(50))


class Sea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_info = db.Column(db.String(10))
    product_name = db.Column(db.String(10))
    period = db.Column(db.String(10))
    # 在贷余额
    lend_amt = db.Column(db.Float(50))
    # 累计还款
    total_repay_amt = db.Column(db.Float(50))
    # 当日放款金额
    lend_amount = db.Column(db.Float(50))
    # 当日放款笔数
    lend_number = db.Column(db.Float(50))
    # 当日还款总额
    repay_amt = db.Column(db.Float(50))
    # 当日还款本金
    repay_amount = db.Column(db.Float(50))
    # 当日还款利息
    repay_interest = db.Column(db.Float(50))
    # 罚息
    penalty_interest = db.Column(db.Float(50))
    # 当日还款笔数
    repay_number = db.Column(db.Float(50))


class North(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.String(20))
    product_name = db.Column(db.String(20))
    # 笔数
    number = db.Column(db.Float(50))


class Repayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_info = db.Column(db.String(20))
    bank = db.Column(db.String(20))
    assets = db.Column(db.String(20))
    product_code = db.Column(db.String(20))
    product_name = db.Column(db.String(20))
    # 还款
    repay_type = db.Column(db.String(20))
    repay_number = db.Column(db.Integer())
    repay_amount = db.Column(db.Float(50))
    repay_principal = db.Column(db.Float(50))
    repay_interest = db.Column(db.Float(50))
    total_repay_amount = db.Column(db.Float(50))
    total_repay_number = db.Column(db.Integer())


class Fee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_info = db.Column(db.String(10))
    product_name = db.Column(db.String(10))
    period = db.Column(db.String(10))
    # 当月放款金额
    lend_amount = db.Column(db.Float(50))
    # 当月放款笔数
    lend_number = db.Column(db.Float(50))
    # 当月服务费
    fee_month = db.Column(db.Float(50))
    # 累计放款金额
    lend_amount_total = db.Column(db.Float(50))
    # 累计放款笔数
    lend_number_total = db.Column(db.Float(50))
    # 累计服务费
    fee_total = db.Column(db.Float(50))