# -*- coding: utf-8 -*-
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from report import db

# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(20))
#     username = db.Column(db.String(20))
#     password_hash = db.Column(db.String(128))
#
#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password)
#
#     def validate_password(self, password):
#         return check_password_hash(self.password_hash, password)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    extra_info = db.Column(db.String(50))
    product_remark = db.Column(db.String(50))
    product_mapping_code = db.Column(db.String(50))
    product_name = db.Column(db.String(50))
    lender_code = db.Column(db.String(50))
    lender_product_name = db.Column(db.String(50))
    signing_mode = db.Column(db.String(50))
    signing_prescription = db.Column(db.String(50))
    repayment_frequency = db.Column(db.String(50))
    repayment_frequency_company = db.Column(db.String(50))


class Daily(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 日期
    date_info = db.Column(db.Date)
    # product_name = db.Column(db.String(10))
    # # 资金机构
    # lender_code = db.Column(db.String(10))
    # # 资产方
    # extra_info = db.Column(db.String(10))
    # # 融担
    # signing_prescription = db.Column(db.String(50))
    product_mapping_code = db.Column(db.String(50))
    # 当日还款
    repay_amount = db.Column(db.Float(50))
    repay_principal = db.Column(db.Float(50))
    repay_interest = db.Column(db.Float(50))
    repay_number = db.Column(db.Float(50))
    # 提前结清笔数
    advance_settlement = db.Column(db.Float(50))
    # 提前结清金额
    advance_amount = db.Column(db.Float(50))
    # 成功放款金额(当日放款金额)
    lend_amount = db.Column(db.Float(50))
    # 成功放款笔数(当日放款笔数)
    lend_number = db.Column(db.Float(50))
    # 期数
    period = db.Column(db.Float(50))
    # 贷款余额
    total_loan_balance = db.Column(db.Float(50))
    # 进件笔数
    entries = db.Column(db.Float(50))
    # 成功授信笔数
    credit_number = db.Column(db.Float(50))
    # 申请放款笔数
    apply_lend_number = db.Column(db.Float(50))
    # 申请放款金额
    apply_lend_amount = db.Column(db.Float(50))
    # 授信通过率
    credit_percent = db.Column(db.String(10))
    # 放款通过率
    lend_percent = db.Column(db.String(10))


class OldDaily(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 日期
    date_info = db.Column(db.Date)
    # product_name = db.Column(db.String(10))
    # # 资金机构
    # lender_code = db.Column(db.String(10))
    # # 资产方
    # extra_info = db.Column(db.String(10))
    # # 融担
    # signing_prescription = db.Column(db.String(50))
    product_mapping_code = db.Column(db.String(50))
    # 当日还款
    repay_amount = db.Column(db.Float(50))
    repay_principal = db.Column(db.Float(50))
    repay_interest = db.Column(db.Float(50))
    repay_number = db.Column(db.Float(50))
    # 提前结清笔数
    advance_settlement = db.Column(db.Float(50))
    # 提前结清金额
    advance_amount = db.Column(db.Float(50))
    # 成功放款金额(当日放款金额)
    lend_amount = db.Column(db.Float(50))
    # 成功放款笔数(当日放款笔数)
    lend_number = db.Column(db.Float(50))
    # 贷款余额
    total_loan_balance = db.Column(db.Float(50))
    # 进件笔数
    entries = db.Column(db.Float(50))
    # 成功授信笔数
    credit_number = db.Column(db.Float(50))
    # 申请放款笔数
    apply_lend_number = db.Column(db.Float(50))
    # 申请放款金额
    apply_lend_amount = db.Column(db.Float(50))
    # 授信通过率
    credit_percent = db.Column(db.String(10))
    # 放款通过率
    lend_percent = db.Column(db.String(10))


class Repayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # # 产品名称
    # product_name = db.Column(db.String(10))
    # # 资金机构
    # lender_code = db.Column(db.String(10))
    # # 资产方
    # extra_info = db.Column(db.String(10))
    # # 融担
    # signing_prescription = db.Column(db.String(50))
    # 产品映射代码
    product_mapping_code = db.Column(db.String(50))
    # 客户姓名
    name = db.Column(db.String(10))
    # 借据号
    loan_no = db.Column(db.String(50))
    # 应还日期
    repay_date = db.Column(db.Date)
    # 还款类型
    repay_type = db.Column(db.String(10))
    repay_method = db.Column(db.String(10))
    # 银行确认还款日期
    process_date = db.Column(db.Date)
    # 借款总额
    loan_amt = db.Column(db.Float(50))
    # 还款本金
    repay_capital = db.Column(db.Float(50))
    # 还款利息
    repay_interest = db.Column(db.Float(50))
    # 总期次
    total_number = db.Column(db.String(10))
    # 当前期次
    current_number = db.Column(db.String(10))
    # 借款余额
    remain_amt = db.Column(db.Float(50))


class MainCredit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 日期
    date_info = db.Column(db.Date)
    # # 产品名称
    # product_name = db.Column(db.String(10))
    # # 资金机构
    # lender_code = db.Column(db.String(10))
    # # 资产方
    # extra_info = db.Column(db.String(10))
    # # 融担
    # signing_prescription = db.Column(db.String(50))
    # 产品映射代码
    product_mapping_code = db.Column(db.String(50))
    # 当前贷款余额
    total_loan_balance = db.Column(db.Float(50))
    # 今日放款总额
    today_total_lend_amount = db.Column(db.Float(50))
    # 总放款金额
    total_lend_amount = db.Column(db.Float(50))
    # 今日进件笔数
    today_total_entries = db.Column(db.Float(50))
    # 总进件笔数
    total_entries = db.Column(db.Float(50))
    # 今日放款笔数
    today_lend_number = db.Column(db.Float(50))
    # 总放款笔数
    total_lend_number = db.Column(db.Float(50))


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


class Deduction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # # 产品名称
    # product_name = db.Column(db.String(10))
    # # 资金机构
    # lender_code = db.Column(db.String(10))
    # # 资产方
    # extra_info = db.Column(db.String(10))
    # # 融担
    # signing_prescription = db.Column(db.String(50))
    # 产品映射代码
    product_mapping_code = db.Column(db.String(50))
    # 扣款日期
    deduction_date = db.Column(db.Date)
    # 扣款总额
    deduction_amt = db.Column(db.Float(50))
    # 扣款笔数
    total_number = db.Column(db.String(10))


class Debt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_info = db.Column(db.String(20))
    bank = db.Column(db.String(20))
    assets = db.Column(db.String(20))
    product_code = db.Column(db.String(20))
    product_name = db.Column(db.String(20))
    # 还款
    repay_type = db.Column(db.String(20))
    period = db.Column(db.String(20))
    # 还款方式标记
    repay_method = db.Column(db.String(20))
    repay_number = db.Column(db.Integer())
    repay_amount = db.Column(db.Float(50))
    repay_principal = db.Column(db.Float(50))
    repay_interest = db.Column(db.Float(50))
    repay_over_fee = db.Column(db.Float(50))
    # 累计还款
    total_repay_number = db.Column(db.Integer())
    total_repay_amount = db.Column(db.Float(50))
    total_repay_principal = db.Column(db.Float(50))
    total_repay_interest = db.Column(db.Float(50))