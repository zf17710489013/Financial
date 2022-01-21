# -*- coding: utf-8 -*-
from flask import render_template, request, url_for, \
    redirect, jsonify, session
from report import app, db
import pymysql, sqlite3, os, json
from report.models import Daily
import datetime


def get_conn_ams():
    # 放款 还款
    conn_ams = pymysql.connect(host="rm-uf6355lewwkmn1b59.mysql.rds.aliyuncs.com", port=3306,
                               user="u_slkj", password="Slong@2020&", database="order_app")
    # # 测试
    # conn_ams = pymysql.connect(host="192.168.100.227", port=3306,
    #                              user="u_slong", password="Slkj@2019.", database="order_app")
    return conn_ams


def get_conn_customer():
    # 进件
    conn_customer = pymysql.connect(host="rm-uf6355lewwkmn1b59.mysql.rds.aliyuncs.com", port=3306,
                                    user="u_slkj", password="Slong@2020&", database="customer_app")
    # # 测试
    # conn_customer = pymysql.connect(host="192.168.100.227", port=3306,
    #                                 user="u_slong", password="Slkj@2019.&", database="customer_app")
    return conn_customer


def get_conn_account():
    # 账务
    conn_account = pymysql.connect(host="rm-uf6355lewwkmn1b59.mysql.rds.aliyuncs.com", port=3306,
                                    user="u_slkj", password="Slong@2020&", database="ams_app")
    # # 测试
    # conn_account = pymysql.connect(host="192.168.100.227", port=3306,
    #                                user="u_slong", password="Slkj@2019.&", database="ams_app")
    return conn_account


def get_conn_cus():
    # 客户
    conn_cus = pymysql.connect(host="rm-uf6355lewwkmn1b59.mysql.rds.aliyuncs.com", port=3306,
                                    user="u_slkj", password="Slong@2020&", database="customer_app")
    # # 测试
    # conn_cus = pymysql.connect(host="192.168.100.227", port=3306,
    #                                user="u_slong", password="Slkj@2019.&", database="customer_app")
    return conn_cus


# 获取列表里的的元素的金额
def amt(elem):
    return elem['lendAmount']


def amount(elem):
    return elem['value']


def amounts(elem):
    return elem[15]


# 查询产品信息
def product_mapping(lender_code, product_mapping_code, signing_prescription):
    # 连接sqlite
    conn_product = sqlite3.connect(app.config['SQLALCHEMY_DATABASE'])
    sql_product = """SELECT id, extra_info, product_remark, product_mapping_code, product_name,
            lender_code, lender_product_name, signing_mode, signing_prescription, repayment_frequency, 
            repayment_frequency_company FROM `product` where 1=1"""

    if lender_code:
        sql_product += ' and lender_code = "%s"' % lender_code

    if product_mapping_code:
        sql_product += ' and product_mapping_code in ({})'.format(','.join(["'%s'" % item for
                                                                            item in product_mapping_code]))

    if signing_prescription:
        sql_product += ' and signing_prescription= "%s"' % signing_prescription

    cur_product = conn_product.cursor()
    cur_product.execute(sql_product)
    product_data = cur_product.fetchall()
    conn_product.close()
    return product_data


@app.route('/report/product/', methods=['GET', 'POST'])
def index():
    post_data = json.loads(request.get_data(as_text=True))
    # 资金方代码
    lender_code = post_data.get('lenderCode')
    # 产品代码
    product_mapping_code = post_data.get('productMappingCode')
    # 融担代码
    signing_prescription = post_data.get('signingPrescription')
    product_data = product_mapping(lender_code, product_mapping_code, signing_prescription)
    product_data = [{'id': each[0], 'extraInfo': each[1], 'productRemark': each[2],
                     'productMappingCode': each[3], 'productName': each[4], 'lenderCode': each[5],
                     'lenderProductName': each[6], 'signingMode': each[7], 'signingPrescription': each[8],
                     'repayment_frequency': each[9], 'repayment_frequency_company': each[10]}
                    for each in product_data]

    return jsonify(product_data)


@app.route('/report/daily/', methods=['GET', 'POST'])
def daily():
    post_data = json.loads(request.get_data(as_text=True))
    # 资金方代码
    lender_code = post_data.get('lenderCode')
    # 产品代码
    product_mapping_code = post_data.get('productMappingCode')
    # 融担代码
    signing_prescription = post_data.get('signingPrescription')
    # 期数
    period = post_data.get('period')
    # 页数
    page = post_data.get('page')
    # 条数
    page_number = post_data.get('pageNumber')
    # 日期
    start_day = post_data.get('startDay')
    end_day = post_data.get('endDay')

    if not page:
        page = 1

    if not page_number:
        page_number = 10

    product_data_info = product_mapping(lender_code, product_mapping_code, signing_prescription)

    product_data = [{'extraInfo': each[1], 'productMappingCode': each[3], 'productName': each[4],
                     'lenderCode': each[5], 'signingPrescription': each[8]}
                    for each in product_data_info]
    data = []
    conn_product = sqlite3.connect(app.config['SQLALCHEMY_DATABASE'])
    cur_product = conn_product.cursor()

    product_mapping_code_list = []
    for each in product_data:
        product_mapping_code_list.append(each['productMappingCode'])

    if period:
        if start_day and end_day:
            sql_data = """SELECT a.*, b.* FROM `product` AS a 
                INNER JOIN `daily` AS b ON a.product_mapping_code = b.product_mapping_code 
                where a.product_mapping_code in ('%s') and (b.date_info between DATE('%s') and DATE('%s')) 
                and period = '%s' order by date_info desc;""" \
                       % ("','".join(product_mapping_code_list), start_day, end_day, period)

            cur_product.execute(sql_data)
            each_data = cur_product.fetchall()
            data += each_data
        else:
            if start_day:
                sql_data = """SELECT a.*, b.* FROM `product` AS a 
                    INNER JOIN `daily` AS b ON a.product_mapping_code = b.product_mapping_code 
                    where a.product_mapping_code in ('%s') and b.date_info >= DATE('%s') and period = '%s'
                    order by date_info desc;""" % ("','".join(product_mapping_code_list), start_day, period)

                cur_product.execute(sql_data)
                each_data = cur_product.fetchall()
                data += each_data
            elif end_day:
                sql_data = """SELECT a.*, b.* FROM `product` AS a 
                    INNER JOIN `daily` AS b ON a.product_mapping_code = b.product_mapping_code 
                    where a.product_mapping_code in ('%s') and b.date_info <= DATE('%s') and period = '%s'
                    order by date_info desc;""" % ("','".join(product_mapping_code_list), end_day, period)

                cur_product.execute(sql_data)
                each_data = cur_product.fetchall()
                data += each_data
            else:
                sql_data = """SELECT a.*, b.* FROM `product` AS a 
                    INNER JOIN `daily` AS b ON a.product_mapping_code = b.product_mapping_code 
                    where a.product_mapping_code in ('%s') and period = '%s' order by date_info desc;""" \
                           % ("','".join(product_mapping_code_list), period)

                cur_product.execute(sql_data)
                each_data = cur_product.fetchall()
                data += each_data
    else:
        if start_day and end_day:
            sql_data = """SELECT a.*, b.* FROM `product` AS a 
                INNER JOIN `old_daily` AS b ON a.product_mapping_code = b.product_mapping_code 
                where a.product_mapping_code in ('%s') and (b.date_info between DATE('%s') and DATE('%s')) 
                order by date_info desc;""" \
                       % ("','".join(product_mapping_code_list), start_day, end_day)

            cur_product.execute(sql_data)
            each_data = cur_product.fetchall()
            data += each_data
        else:
            if start_day:
                sql_data = """SELECT a.*, b.* FROM `product` AS a 
                    INNER JOIN `old_daily` AS b ON a.product_mapping_code = b.product_mapping_code 
                    where a.product_mapping_code in ('%s') and b.date_info >= DATE('%s') order by 
                    date_info desc;""" % ("','".join(product_mapping_code_list), start_day)

                cur_product.execute(sql_data)
                each_data = cur_product.fetchall()
                data += each_data
            elif end_day:
                sql_data = """SELECT a.*, b.* FROM `product` AS a 
                    INNER JOIN `old_daily` AS b ON a.product_mapping_code = b.product_mapping_code 
                    where a.product_mapping_code in ('%s') and b.date_info <= DATE('%s') order by 
                    date_info desc;""" % ("','".join(product_mapping_code_list), end_day)

                cur_product.execute(sql_data)
                each_data = cur_product.fetchall()
                data += each_data
            else:
                sql_data = """SELECT a.*, b.* FROM `product` AS a 
                    INNER JOIN `old_daily` AS b ON a.product_mapping_code = b.product_mapping_code 
                    where a.product_mapping_code in ('%s') order by date_info desc;""" \
                           % ("','".join(product_mapping_code_list))

                cur_product.execute(sql_data)
                each_data = cur_product.fetchall()
                data += each_data

        # 总记录
        total = len(data)

        conn_product.close()
        target_data = []

        data = data[(int(page) - 1) * int(page_number):int(page) * int(page_number)]
        for i in data:
            try:
                target_data.append({'extraInfo': i[1], 'productMappingCode': i[3], 'productName': i[4],
                                    'lenderCode': i[5], 'signingPrescription': i[7], 'dateInfo': i[12],
                                    'repayAmount': i[14], 'repayPrincipal': i[15], 'repayInterest': i[16],
                                    'repayNumber': int(i[17]), 'advanceSettlement': int(i[18]), 'advanceAmount': i[19],
                                    'lendAmount': i[20], 'lendNumber': int(i[21]), 'totalLoanBalance': i[22],
                                    'entries':int(i[23]), 'creditNumber':int(i[24]), 'applyLendNumber':int(i[25]), 'applyLendAmount':i[26],
                                'creditPercent':i[27], 'lendPercent':i[28]})
            except:
                target_data.append({'extraInfo': i[1], 'productMappingCode': i[3], 'productName': i[4],
                                    'lenderCode': i[5], 'signingPrescription': i[7], 'dateInfo': i[12],
                                    'repayAmount': i[14], 'repayPrincipal': i[15], 'repayInterest': i[16],
                                    'repayNumber': int(i[17]), 'advanceSettlement': int(i[18]), 'advanceAmount': i[19],
                                    'lendAmount': i[20], 'lendNumber': int(i[21]), 'totalLoanBalance': i[22],
                                    'entries': '', 'creditNumber': '', 'applyLendNumber': '',
                                    'applyLendAmount': i[26],
                                    'creditPercent': i[27], 'lendPercent': i[28]})

        return jsonify({'data': target_data, 'page': page, 'total': total})

    # 总记录
    total = len(data)

    conn_product.close()
    target_data = []

    data = data[(int(page)-1)*int(page_number):int(page)*int(page_number)]
    for i in data:
        try:
            target_data.append({'extraInfo': i[1], 'productMappingCode': i[3], 'productName': i[4],
                                'lenderCode': i[5], 'signingPrescription': i[7], 'dateInfo': i[12],
                                'repayAmount': i[14], 'repayPrincipal': i[15], 'repayInterest': i[16],
                                'repayNumber': int(i[17]), 'advanceSettlement': int(i[18]), 'advanceAmount': i[19],
                                'lendAmount': i[20], 'lendNumber': int(i[21]), 'totalLoanBalance': i[23],
                                'entries':int(i[24]), 'creditNumber':int(i[25]), 'applyLendNumber':int(i[26]), 'applyLendAmount':i[27],
                                'creditPercent':i[28], 'lendPercent':i[29]})
        except:
            target_data.append({'extraInfo': i[1], 'productMappingCode': i[3], 'productName': i[4],
                                'lenderCode': i[5], 'signingPrescription': i[7], 'dateInfo': i[12],
                                'repayAmount': i[14], 'repayPrincipal': i[15], 'repayInterest': i[16],
                                'repayNumber': int(i[17]), 'advanceSettlement': int(i[18]), 'advanceAmount': i[19],
                                'lendAmount': i[20], 'lendNumber': int(i[21]), 'totalLoanBalance': i[23],
                                'entries': '', 'creditNumber': '', 'applyLendNumber': '',
                                'applyLendAmount': i[27],
                                'creditPercent': i[28], 'lendPercent': i[29]})

    return jsonify({'data': target_data, 'page': page, 'total': total})


@app.route('/report/mapping/', methods=['GET', 'POST'])
def mapping():
    assets = request.form.get('comp_select')
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


@app.route('/report/repay/', methods=['GET', 'POST'])
def daily_repay():
    post_data = json.loads(request.get_data(as_text=True))
    # 资金方代码
    lender_code = post_data.get('lenderCode')
    # 产品代码
    product_mapping_code = post_data.get('productMappingCode')
    # 融担代码
    signing_prescription = post_data.get('signingPrescription')
    # 页数
    page = post_data.get('page')
    # 条数
    page_number = post_data.get('pageNumber')
    # 日期
    start_day = post_data.get('startDay')
    end_day = post_data.get('endDay')
    # 还款类型
    repay_types = post_data.get('repayType')
    # 还款标记
    repay_method = post_data.get('repayMethod')
    if repay_method == '1':
        return jsonify(None)
    # 借据号
    loan_no = post_data.get('loanNo')
    # if loan_no and "\'" in loan_no:
    #     return jsonify({'data': '借据号格式错误'})
    if not page:
        page = 1

    if not page_number:
        page_number = 10

    product_data = product_mapping(lender_code, product_mapping_code, signing_prescription)

    product_data = [{'extraInfo': each[1], 'productMappingCode': each[3], 'productName': each[4],
                     'lenderCode': each[5], 'signingPrescription': each[8]}
                    for each in product_data]
    data = []
    conn_product = sqlite3.connect(app.config['SQLALCHEMY_DATABASE'])
    cur_product = conn_product.cursor()

    if repay_types:
        if start_day and end_day:
            for each in product_data:
                if loan_no:
                    sql_data = """SELECT a.*, b.* FROM `product` AS a 
                        INNER JOIN `repayment` AS b ON a.product_mapping_code = b.product_mapping_code 
                        where b.loan_no = '%s' and b.repay_type = '%s' and a.product_mapping_code = '%s' 
                        and (b.process_date between DATE('%s') and DATE('%s')) 
                        order by process_date desc;""" % (loan_no, repay_types,
                                                          each['productMappingCode'], start_day, end_day)
                else:
                    sql_data = """SELECT a.*, b.* FROM `product` AS a INNER JOIN `repayment` AS b ON 
                    a.product_mapping_code = b.product_mapping_code where b.repay_type = '%s' and 
                    a.product_mapping_code = '%s' and (b.process_date between DATE('%s') and DATE('%s')) 
                    order by process_date desc;""" % (repay_types, each['productMappingCode'], start_day, end_day)

                cur_product.execute(sql_data)
                each_data = cur_product.fetchall()
                data += each_data
        else:
            if start_day:
                for each in product_data:
                    if loan_no:
                        sql_data = """SELECT a.*, b.* FROM `product` AS a 
                            INNER JOIN `repayment` AS b ON a.product_mapping_code = b.product_mapping_code 
                            where b.loan_no = '%s' and b.repay_type = '%s' and a.product_mapping_code = '%s' 
                            and b.process_date >= DATE('%s') 
                            order by process_date desc;""" % (loan_no, repay_types, each['productMappingCode'],
                                                              start_day)
                    else:
                        sql_data = """SELECT a.*, b.* FROM `product` AS a 
                        INNER JOIN `repayment` AS b ON a.product_mapping_code = b.product_mapping_code 
                        where b.repay_type = '%s' and a.product_mapping_code = '%s' and b.process_date >= DATE('%s') 
                        order by process_date desc;""" % (repay_types, each['productMappingCode'], start_day)

                    cur_product.execute(sql_data)
                    each_data = cur_product.fetchall()
                    data += each_data
            elif end_day:
                for each in product_data:
                    if loan_no:
                        sql_data = """SELECT a.*, b.* FROM `product` AS a 
                            INNER JOIN `repayment` AS b ON a.product_mapping_code = b.product_mapping_code 
                            where b.loan_no = '%s' and b.repay_type = '%s' and a.product_mapping_code = '%s' 
                            and b.process_date <= DATE('%s') order by process_date desc;""" \
                                   % (loan_no, repay_types, each['productMappingCode'], end_day)
                    else:
                        sql_data = """SELECT a.*, b.* FROM `product` AS a 
                        INNER JOIN `repayment` AS b ON a.product_mapping_code = b.product_mapping_code 
                                                    where b.repay_type = '%s' and a.product_mapping_code = '%s' 
                                                    and b.process_date <= DATE('%s') 
                                                    order by process_date desc;""" \
                                   % (repay_types, each['productMappingCode'], end_day)

                    cur_product.execute(sql_data)
                    each_data = cur_product.fetchall()
                    data += each_data
            else:
                for each in product_data:
                    if loan_no:
                        sql_data = """SELECT a.*, b.* FROM `product` AS a 
                            INNER JOIN `repayment` AS b ON a.product_mapping_code = b.product_mapping_code 
                            where b.loan_no = '%s' and b.repay_type = '%s' and a.product_mapping_code = '%s' 
                            order by process_date desc;""" \
                                   % (loan_no, repay_types, each['productMappingCode'])
                    else:
                        sql_data = """SELECT a.*, b.* FROM `product` AS a INNER JOIN `repayment` AS b 
                        ON a.product_mapping_code = b.product_mapping_code where b.repay_type = '%s' 
                        and a.product_mapping_code = '%s' and b.process_date = '%s' order by repay_date desc;""" \
                                   % (repay_types, each['productMappingCode'], str(datetime.date.today()))

                    cur_product.execute(sql_data)
                    each_data = cur_product.fetchall()
                    data += each_data
    else:
        if start_day and end_day:
            for each in product_data:
                if loan_no:
                    sql_data = """SELECT a.*, b.* FROM `product` AS a 
                        INNER JOIN `repayment` AS b ON a.product_mapping_code = b.product_mapping_code 
                        where b.loan_no = '%s' and a.product_mapping_code = '%s' 
                        and (b.process_date between DATE('%s') and DATE('%s')) 
                        order by process_date desc;""" % (loan_no, each['productMappingCode'], start_day, end_day)
                else:
                    sql_data = """SELECT a.*, b.* FROM `product` AS a 
                                            INNER JOIN `repayment` AS b ON a.product_mapping_code = b.product_mapping_code 
                                            where a.product_mapping_code = '%s' and (b.process_date between DATE('%s') and DATE('%s')) 
                                            order by process_date desc;""" % (
                    each['productMappingCode'], start_day, end_day)

                cur_product.execute(sql_data)
                each_data = cur_product.fetchall()
                data += each_data
        else:
            if start_day:
                for each in product_data:
                    if loan_no:
                        sql_data = """SELECT a.*, b.* FROM `product` AS a 
                            INNER JOIN `repayment` AS b ON a.product_mapping_code = b.product_mapping_code 
                            where b.loan_no = '%s' and a.product_mapping_code = '%s' and b.process_date >= DATE('%s') 
                            order by process_date desc;""" % (loan_no, each['productMappingCode'], start_day)
                    else:
                        sql_data = """SELECT a.*, b.* FROM `product` AS a INNER JOIN `repayment` AS b 
                        ON a.product_mapping_code = b.product_mapping_code where a.product_mapping_code = '%s' 
                        and b.process_date >= DATE('%s') order by process_date desc;""" \
                                   % (each['productMappingCode'], start_day)

                    cur_product.execute(sql_data)
                    each_data = cur_product.fetchall()
                    data += each_data
            elif end_day:
                for each in product_data:
                    if loan_no:
                        sql_data = """SELECT a.*, b.* FROM `product` AS a 
                            INNER JOIN `repayment` AS b ON a.product_mapping_code = b.product_mapping_code 
                            where b.loan_no = '%s' and a.product_mapping_code = '%s' and b.process_date <= DATE('%s') 
                            order by process_date desc;""" % (loan_no, each['productMappingCode'], end_day)
                    else:
                        sql_data = """SELECT a.*, b.* FROM `product` AS a INNER JOIN `repayment` AS b ON 
                        a.product_mapping_code = b.product_mapping_code where a.product_mapping_code = '%s' 
                        and b.process_date <= DATE('%s') order by process_date desc;""" \
                                   % (each['productMappingCode'], end_day)

                    cur_product.execute(sql_data)
                    each_data = cur_product.fetchall()
                    data += each_data
            else:
                for each in product_data:
                    if loan_no:
                        sql_data = """SELECT a.*, b.* FROM `product` AS a 
                            INNER JOIN `repayment` AS b ON a.product_mapping_code = b.product_mapping_code 
                            where b.loan_no = '%s' and a.product_mapping_code = '%s' order by process_date desc;""" \
                                   % (loan_no, each['productMappingCode'])
                    else:
                        sql_data = """SELECT a.*, b.* FROM `product` AS a INNER JOIN `repayment` AS b 
                        ON a.product_mapping_code = b.product_mapping_code where a.product_mapping_code = '%s' 
                        and b.process_date = '%s' order by repay_date desc;""" % (each['productMappingCode'], str(datetime.date.today()))

                    cur_product.execute(sql_data)
                    each_data = cur_product.fetchall()
                    data += each_data

    # 总记录
    total = len(data)

    conn_product.close()
    target_data = []

    data.sort(key=amounts, reverse=True)
    data = data[(int(page)-1)*int(page_number):int(page)*int(page_number)]
    for i in data:
        target_data.append({'extraInfo': i[1], 'productMappingCode': i[3], 'productName': i[4],
                            'lenderCode': i[5], 'signingPrescription': i[8], 'name': i[13],
                            'loanNo': i[14], 'repayDate': i[15], 'repayType': i[16], 'repayMethod': i[17],
                            'processDate': i[18], 'loanAmt': i[19], 'repayCapital': i[20],
                            'repayInterest': i[21], 'totalNumber': i[22], 'currentNumber': i[23], 'remainAmt': i[24]})

    return jsonify({'data': target_data, 'page': page, 'total': total})


# 数据大盘
@app.route('/report/market/', methods=['GET', 'POST'])
def main_credit():
    post_data = json.loads(request.get_data(as_text=True))
    # 资金方代码
    lender_code = post_data.get('lenderCode')
    # 产品代码
    product_mapping_code = post_data.get('productMappingCode')
    # 融担代码
    signing_prescription = post_data.get('signingPrescription')
    # 获取当天日期
    today_info = datetime.date.today()
    today_info = str(today_info)

    product_data = product_mapping(lender_code, product_mapping_code, signing_prescription)

    product_data = [{'extraInfo': each[1], 'productMappingCode': each[3], 'productName': each[4],
                     'lenderCode': each[5], 'signingPrescription': each[8]}
                    for each in product_data]

    conn_ams = get_conn_ams()
    cur_ams = conn_ams.cursor()

    conn_customer = get_conn_customer()
    cur_customer = conn_customer.cursor()

    conn_account = get_conn_account()
    cur_account = conn_account.cursor()

    product_mapping_code_list = []
    for each in product_data:
        product_mapping_code_list.append(each['productMappingCode'])

    # 放款数据： 当日放款金额 当日放款笔数
    sql_lend = """SELECT sum( apply_amount ), count( 1 ) FROM `order_apply_base_info` WHERE 
    apply_status = '1007' AND product_mapping_code in ('%s') AND loanpay_time 
    LIKE '%s';""" % ("','".join(product_mapping_code_list), today_info + '%')

    cur_ams.execute(sql_lend)
    lend_data = cur_ams.fetchone()

    if lend_data:
        # 当日放款金额
        today_total_lend_amount = float(lend_data[0]) if lend_data[0] else 0
        # 当日放款笔数
        today_lend_number = int(lend_data[1]) if lend_data[1] else 0
    else:
        today_total_lend_amount = 0
        today_lend_number = 0

    # 放款数据： 累计放款金额 累计放款笔数
    sql_lend_total = """SELECT sum( apply_amount ), count( 1 ) FROM order_apply_base_info WHERE 
    apply_status = '1007' AND product_mapping_code in ('%s');""" % "','".join(product_mapping_code_list)

    cur_ams.execute(sql_lend_total)
    lend_total_data = cur_ams.fetchone()

    if lend_total_data:
        # 累计放款金额
        total_lend_amount = float(lend_total_data[0]) if lend_total_data[0] else 0
        # 累计放款笔数
        total_lend_number = int(lend_total_data[1]) if lend_total_data[1] else 0
    else:
        total_lend_amount = 0
        total_lend_number = 0

    # 当日进件笔数
    sql_credit = """SELECT COUNT(1) FROM `customer_credit` WHERE product_mapping_code in ('%s') 
            AND create_time LIKE '%s';""" % ("','".join(product_mapping_code_list), today_info + '%')

    cur_customer.execute(sql_credit)
    customer_data = cur_customer.fetchone()

    # 总进件笔数
    sql_total_credit = """SELECT COUNT(1) FROM `customer_credit` WHERE 
            product_mapping_code in ('%s');""" % "','".join(product_mapping_code_list)

    cur_customer.execute(sql_total_credit)
    customer_total_data = cur_customer.fetchone()

    if customer_data:
        all_today_total_entries = int(customer_data[0]) if customer_data[0] else 0
    else:
        all_today_total_entries = 0

    if customer_total_data:
        all_total_entries = int(customer_total_data[0]) if customer_total_data[0] else 0
    else:
        all_total_entries = 0

    sql_account = """SELECT sum(total_capital_left) from ams_account_borrow WHERE 
    product_code in ('%s');""" % "','".join(product_mapping_code_list)
    cur_account.execute(sql_account)
    account_data = cur_account.fetchone()
    if account_data[0]:
        tlb = float(account_data[0])
    else:
        tlb = 0
    conn_ams.close()
    conn_customer.close()
    conn_account.close()
    return jsonify({'dateInfo': today_info, 'totalLoanBalance': tlb,
                    'todayTotalLendAmount': today_total_lend_amount,
                    'totalLendAmount': total_lend_amount, 'todayTotalEntries': all_today_total_entries,
                    'totalEntries': all_total_entries, 'todayLendNumber': today_lend_number,
                    'totalLendNumber': total_lend_number})


# 地区统计
@app.route('/report/area/', methods=['GET', 'POST'])
def main_area():
    post_data = json.loads(request.get_data(as_text=True))
    # 资金方代码
    lender_code = post_data.get('lenderCode')
    # 产品代码
    product_mapping_code = post_data.get('productMappingCode')
    # 融担代码
    signing_prescription = post_data.get('signingPrescription')

    # 页数
    page = post_data.get('page')
    # 条数
    page_number = post_data.get('pageNumber')

    # 获取当天日期
    today_info = datetime.date.today()
    today_info = str(today_info)

    # 日期
    start_day = post_data.get('startDay')
    end_day = post_data.get('endDay')

    if not page:
        page = 1

    if not page_number:
        page_number = 5

    product_data_info = product_mapping(lender_code, product_mapping_code, signing_prescription)

    product_data = [{'extraInfo': each[1], 'productMappingCode': each[3], 'productName': each[4],
                     'lenderCode': each[5], 'signingPrescription': each[8]}
                    for each in product_data_info]

    conn_ams = get_conn_ams()
    cur_ams = conn_ams.cursor()

    product_mapping_code_list = []
    for each in product_data:
        product_mapping_code_list.append(each['productMappingCode'])
    # 放款数据：某个时间段 放款金额 放款笔数
    if start_day and end_day:
        sql_lend = """SELECT CASE LEFT ( id_no, 2 ) WHEN '11' THEN '北京市' WHEN '12' THEN '天津市' 
        WHEN '13' THEN '河北省' WHEN '14' THEN '山西省' WHEN '15' THEN '内蒙古自治区' WHEN '21' THEN 
        '辽宁省' WHEN '22' THEN '吉林省' WHEN '23' THEN '黑龙江省' WHEN '31' THEN '上海市' WHEN '32' THEN 
        '江苏省' WHEN '33' THEN '浙江省' WHEN '34' THEN '安徽省' WHEN '35' THEN '福建省' WHEN '36' THEN 
        '江西省' WHEN '37' THEN '山东省' WHEN '41' THEN '河南省' WHEN '42' THEN '湖北省' WHEN '43' THEN 
        '湖南省' WHEN '44' THEN '广东省' WHEN '45' THEN '广西壮族自治区' WHEN '46' THEN '海南省' WHEN '50' THEN 
        '重庆市' WHEN '51' THEN '四川省' WHEN '52' THEN '贵州省' WHEN '53' THEN '云南省' WHEN '54' THEN '西藏自治区' 
        WHEN '61' THEN '陕西省' WHEN '62' THEN '甘肃省' WHEN '63' THEN '青海省' WHEN '64' THEN '宁夏回族自治区' 
        WHEN '65' THEN '新疆维吾尔自治区' WHEN '71' THEN '台湾' WHEN '81' THEN '香港' WHEN '82' THEN '澳门' ELSE '未知' 
        END AS addrProvince, count( 1 ) as rank FROM `order_apply_base_info` WHERE is_delete = 0 AND 
        apply_status = '1007' AND product_mapping_code in ('%s') AND (loanpay_time BETWEEN '%s' and '%s') 
        GROUP BY addrProvince ORDER BY rank desc;""" \
                   % ("','".join(product_mapping_code_list), start_day, end_day + ' 23:59:59')
    else:
        sql_lend = """SELECT CASE LEFT ( id_no, 2 ) WHEN '11' THEN '北京市' WHEN '12' THEN '天津市' 
                WHEN '13' THEN '河北省' WHEN '14' THEN '山西省' WHEN '15' THEN '内蒙古自治区' WHEN '21' THEN 
                '辽宁省' WHEN '22' THEN '吉林省' WHEN '23' THEN '黑龙江省' WHEN '31' THEN '上海市' WHEN '32' THEN 
                '江苏省' WHEN '33' THEN '浙江省' WHEN '34' THEN '安徽省' WHEN '35' THEN '福建省' WHEN '36' THEN 
                '江西省' WHEN '37' THEN '山东省' WHEN '41' THEN '河南省' WHEN '42' THEN '湖北省' WHEN '43' THEN 
                '湖南省' WHEN '44' THEN '广东省' WHEN '45' THEN '广西壮族自治区' WHEN '46' THEN '海南省' WHEN '50' THEN 
                '重庆市' WHEN '51' THEN '四川省' WHEN '52' THEN '贵州省' WHEN '53' THEN '云南省' WHEN '54' THEN '西藏自治区' 
                WHEN '61' THEN '陕西省' WHEN '62' THEN '甘肃省' WHEN '63' THEN '青海省' WHEN '64' THEN '宁夏回族自治区' 
                WHEN '65' THEN '新疆维吾尔自治区' WHEN '71' THEN '台湾' WHEN '81' THEN '香港' WHEN '82' THEN '澳门' ELSE '未知' 
                END AS addrProvince, count( 1 ) as rank FROM `order_apply_base_info` WHERE is_delete = 0 
                AND apply_status = '1007' AND product_mapping_code in ('%s') AND loanpay_time LIKE '%s' 
                GROUP BY addrProvince ORDER BY rank desc;""" \
        % ("','".join(product_mapping_code_list), today_info + '%')

    cur_ams.execute(sql_lend)
    lend_data = cur_ams.fetchall()
    if lend_data:
        all_data = [{'province': each[0], 'customerNo': int(each[1])} for each in lend_data]
        all_data = all_data[(int(page) - 1) * int(page_number):int(page) * int(page_number)]
    else:
        all_data = [{'province': '', 'customerNo': ''}]

    conn_ams.close()

    return jsonify({'data': all_data, 'page': page, 'total': len(lend_data)})


# 资产方排行
@app.route('/report/assets/', methods=['GET', 'POST'])
def main_assets():
    post_data = json.loads(request.get_data(as_text=True))
    # 资金方代码
    lender_code = post_data.get('lenderCode')
    # 产品代码
    product_mapping_code = post_data.get('productMappingCode')
    # 融担代码
    signing_prescription = post_data.get('signingPrescription')

    # 页数
    page = post_data.get('page')
    # 条数
    page_number = post_data.get('pageNumber')

    # 获取当天日期
    today_info = datetime.date.today()
    today_info = str(today_info)

    # 日期
    start_day = post_data.get('startDay')
    end_day = post_data.get('endDay')

    if not page:
        page = 1

    if not page_number:
        page_number = 5

    product_data_info = product_mapping(lender_code, product_mapping_code, signing_prescription)

    product_data = [{'extraInfo': each[1], 'productMappingCode': each[3], 'productName': each[4],
                     'lenderCode': each[5], 'signingPrescription': each[8]}
                    for each in product_data_info]

    conn_ams = get_conn_ams()
    cur_ams = conn_ams.cursor()

    product_mapping_code_list = []
    for each in product_data:
        product_mapping_code_list.append(each['productMappingCode'])

    # 放款数据：某个时间段 放款金额 放款笔数
    if start_day and end_day:
        sql_lend = """SELECT sum( apply_amount ), count( 1 ), product_mapping_code FROM
            `order_apply_base_info` WHERE apply_status = '1007' AND product_mapping_code in ('%s')
            AND (loanpay_time BETWEEN '%s' and '%s') GROUP BY product_mapping_code;""" \
                   % ("','".join(product_mapping_code_list), start_day, end_day + ' 23:59:59')
    else:
        sql_lend = """SELECT sum( apply_amount ), count( 1 ), product_mapping_code FROM
            `order_apply_base_info` WHERE apply_status = '1007' AND product_mapping_code in ('%s')
            AND loanpay_time LIKE '%s' GROUP BY product_mapping_code;""" \
                   % ("','".join(product_mapping_code_list), today_info + '%')

    cur_ams.execute(sql_lend)
    assets_data = cur_ams.fetchall()
    all_data = []
    if assets_data:
        assets_data = [{'productMappingCode': each[2], 'lendAmount': float(each[0]),
                        'lendNumber': float(each[1])} for each in assets_data]
        for each_data in assets_data:
            for item in product_data_info:
                if item[3] == each_data['productMappingCode']:
                    all_data.append({'asset': item[1], 'lendAmount': each_data['lendAmount'],
                                     'lendNumber': each_data['lendNumber']})

        info_dic = set([each['asset'] for each in all_data])
        new_info = []
        for n in info_dic:
            t = {'asset': n}
            lendAmount = 0
            lendNumber = 0
            for v in all_data:
                if n == v['asset']:
                    lendAmount += v['lendAmount']
                    lendNumber += v['lendNumber']
            t['lendAmount'] = lendAmount
            t['lendNumber'] = int(lendNumber)
            new_info.append(t)
        new_info.sort(key=amt, reverse=True)
        all_data = new_info
        all_data = all_data[(int(page) - 1) * int(page_number):int(page) * int(page_number)]
    else:
        new_info = []
        all_data = [{'asset': '', 'lendNumber': '', 'lendAmount': ''}]

    conn_ams.close()

    return jsonify({'data': all_data, 'page': page, 'total': len(new_info)})


# 资金方排行
@app.route('/report/lender/', methods=['GET', 'POST'])
def main_lender():
    post_data = json.loads(request.get_data(as_text=True))
    # 资金方代码
    lender_code = post_data.get('lenderCode')
    # 产品代码
    product_mapping_code = post_data.get('productMappingCode')
    # 融担代码
    signing_prescription = post_data.get('signingPrescription')

    # 页数
    page = post_data.get('page')
    # 条数
    page_number = post_data.get('pageNumber')

    # 获取当天日期
    today_info = datetime.date.today()
    today_info = str(today_info)

    # 日期
    start_day = post_data.get('startDay')
    end_day = post_data.get('endDay')

    if not page:
        page = 1

    if not page_number:
        page_number = 5

    product_data_info = product_mapping(lender_code, product_mapping_code, signing_prescription)

    product_data = [{'extraInfo': each[1], 'productMappingCode': each[3], 'productName': each[4],
                     'lenderCode': each[5], 'signingPrescription': each[8]}
                    for each in product_data_info]

    conn_ams = get_conn_ams()
    cur_ams = conn_ams.cursor()

    product_mapping_code_list = []
    for each in product_data:
        product_mapping_code_list.append(each['productMappingCode'])

    # 放款数据：某个时间段 放款金额 放款笔数
    if start_day and end_day:
        sql_lend = """SELECT sum( apply_amount ), count( 1 ), product_mapping_code FROM
            `order_apply_base_info` WHERE apply_status = '1007' AND product_mapping_code in ('%s')
            AND (loanpay_time BETWEEN '%s' and '%s') GROUP BY product_mapping_code;""" \
                   % ("','".join(product_mapping_code_list), start_day, end_day + ' 23:59:59')
    else:
        sql_lend = """SELECT sum( apply_amount ), count( 1 ), product_mapping_code FROM
            `order_apply_base_info` WHERE apply_status = '1007' AND product_mapping_code in ('%s')
            AND loanpay_time LIKE '%s' GROUP BY product_mapping_code;""" \
                   % ("','".join(product_mapping_code_list), today_info + '%')

    cur_ams.execute(sql_lend)
    lender_data = cur_ams.fetchall()
    all_data = []
    if lender_data:
        lender_data = [{'productMappingCode': each[2], 'lendAmount': float(each[0]),
                        'lendNumber': float(each[1])} for each in lender_data]
        for each_data in lender_data:
            for item in product_data_info:
                if item[3] == each_data['productMappingCode']:
                    all_data.append({'bank': item[6], 'lendAmount': each_data['lendAmount'],
                                     'lendNumber': each_data['lendNumber']})
        info_dic = set([each['bank'] for each in all_data])
        new_info = []
        for n in info_dic:
            t = {'bank': n}
            lendAmount = 0
            lendNumber = 0
            for v in all_data:
                if n == v['bank']:
                    lendAmount += v['lendAmount']
                    lendNumber += v['lendNumber']
            t['lendAmount'] = lendAmount
            t['lendNumber'] = int(lendNumber)
            new_info.append(t)
        new_info.sort(key=amt, reverse=True)
        all_data = new_info
        all_data = all_data[(int(page) - 1) * int(page_number):int(page) * int(page_number)]
    else:
        new_info = []
        all_data = [{'bank': '', 'lendNumber': '', 'lendAmount': ''}]

    conn_ams.close()

    return jsonify({'data': all_data, 'page': page, 'total': len(new_info)})


# 数据统计
@app.route('/report/statistics/', methods=['GET', 'POST'])
def main_statistics():
    post_data = json.loads(request.get_data(as_text=True))
    # 资金方代码
    lender_code = post_data.get('lenderCode')
    # 产品代码
    product_mapping_code = post_data.get('productMappingCode')
    # 融担代码
    signing_prescription = post_data.get('signingPrescription')
    # 获取当天日期
    today_info = datetime.date.today()
    today_info = str(today_info)

    # 日期
    start_day = post_data.get('startDay')
    end_day = post_data.get('endDay')

    product_data_info = product_mapping(lender_code, product_mapping_code, signing_prescription)

    product_data = [{'extraInfo': each[1], 'productMappingCode': each[3], 'productName': each[4],
                     'lenderCode': each[5], 'signingPrescription': each[8]}
                    for each in product_data_info]

    conn_ams = get_conn_ams()
    cur_ams = conn_ams.cursor()

    product_mapping_code_list = []
    for each in product_data:
        product_mapping_code_list.append(each['productMappingCode'])

    # 放款数据：某个时间段 放款金额 放款笔数
    if start_day and end_day:
        sql_lend = """SELECT sum( apply_amount ), count( 1 ), product_mapping_code FROM 
        `order_apply_base_info` WHERE apply_status = '1007' AND product_mapping_code in ('%s') 
        AND (loanpay_time BETWEEN '%s' and '%s') GROUP BY product_mapping_code;""" \
                   % ("','".join(product_mapping_code_list), start_day, end_day + ' 23:59:59')
    else:
        sql_lend = """SELECT sum( apply_amount ), count( 1 ), product_mapping_code FROM 
        `order_apply_base_info` WHERE apply_status = '1007' AND product_mapping_code in ('%s') 
        AND loanpay_time LIKE '%s' GROUP BY product_mapping_code;""" \
                   % ("','".join(product_mapping_code_list), today_info + '%')

    cur_ams.execute(sql_lend)
    lend_data = cur_ams.fetchall()
    all_data = []
    if lend_data:
        statistics_data = [{'name': each[2], 'value': float(each[0])} for each in lend_data]
        for each_data in statistics_data:
            for item in product_data_info:
                if item[3] == each_data['name']:
                    all_data.append({'name': item[4], 'value': each_data['value']})
        all_data.sort(key=amount, reverse=True)
        all_data = all_data
        # 某个时间段放款金额
        today_total_lend_amount = sum([float(each[0]) for each in lend_data])
        # 某个时间段放款笔数
        today_lend_number = sum([int(each[1]) for each in lend_data])
    else:
        today_total_lend_amount = 0
        today_lend_number = 0

    conn_ams.close()
    return jsonify({'totalLendNumber': today_lend_number, 'totalLendAmount': today_total_lend_amount,
                    'totalStatistics': all_data})


# 产品统计报表
@app.route('/report/limitation/', methods=['GET', 'POST'])
def limitation():
    post_data = json.loads(request.get_data(as_text=True))
    # 资金方代码
    lender_code = post_data.get('lenderCode')
    # 产品代码
    product_mapping_code = post_data.get('productMappingCode')
    # 融担代码
    signing_prescription = post_data.get('signingPrescription')

    # 获取当天日期
    today_info = datetime.date.today()
    today_info = str(today_info)

    # 页数
    page = post_data.get('page')
    # 条数
    page_number = post_data.get('pageNumber')

    if not page:
        page = 1

    if not page_number:
        page_number = 10

    product_data_info = product_mapping(lender_code, product_mapping_code, signing_prescription)

    product_data = [{'extraInfo': each[1], 'productMappingCode': each[3], 'productName': each[4],
                     'lenderCode': each[5], 'signingPrescription': each[8]}
                    for each in product_data_info]

    conn_product = pymysql.connect(host="rm-uf6355lewwkmn1b59.mysql.rds.aliyuncs.com", port=3306,
                                   user="u_slkj", password="Slong@2020&", database="product_app")
    cur_product = conn_product.cursor()

    conn_ams = get_conn_ams()
    cur_ams = conn_ams.cursor()

    conn_account = get_conn_account()
    cur_account = conn_account.cursor()

    product_mapping_code_list = []
    for each in product_data:
        product_mapping_code_list.append(each['productMappingCode'])

    sql_lend = """SELECT b.product_mapping_code, a.product_limitation, 
    a.product_limitation_available, b.`status`, b.product_name FROM 
    product_limitation a right JOIN product_mapping b ON a.product_mapping_code 
    = b.product_mapping_code WHERE b.product_mapping_code in ('%s') 
    ORDER BY product_limitation DESC;""" % "','".join(product_mapping_code_list)

    cur_product.execute(sql_lend)
    lend_data = cur_product.fetchall()
    if lend_data:
        all_data = []
        for each in lend_data:
            each_product_limitation = each[1]
            if each_product_limitation is None:
                each_product_limitation = '/'
            else:
                each_product_limitation = float(each_product_limitation)
            each_product_limitation_left = each[2]
            if each_product_limitation_left is None:
                each_product_limitation_left = '/'
            else:
                each_product_limitation_left = float(each_product_limitation_left)
            if each_product_limitation_left != '/':
                each_left = each_product_limitation - each_product_limitation_left
                each_product_limitation_left = each_left if each_left > 0.0 else 0.0

            # 放款金额 笔数
            sql_lend_base = """SELECT sum( apply_amount ), count( 1 ) FROM order_apply_base_info WHERE 
            apply_status = '1007' AND product_mapping_code = '%s';""" % each[0]
            cur_ams.execute(sql_lend_base)
            lend_base = cur_ams.fetchone()
            # 当前在贷余额
            if each[0] == 'P0000007':
                sql_account = """SELECT sum(total_capital_left) from ams_account_borrow WHERE 
                                    product_code = '%s' and is_delete=0 and create_time not like '%s';""" \
                              % (each[0], today_info + '%')
            else:
                sql_account = """SELECT sum(total_capital_left) from ams_account_borrow WHERE 
                    product_code = '%s' and is_delete=0;""" % each[0]
            cur_account.execute(sql_account)
            account_data = cur_account.fetchone()

            each_lend = {'productName': each[4], 'status': each[3] if each[3] else '0',
                         'productLimitation': each_product_limitation,
                         'productLimitationLeft': each_product_limitation_left,
                         'totalLendNumber': int(lend_base[1]) if lend_base[1] else 0,
                         'totalLendAmount': float(lend_base[0]) if lend_base[0] else 0.0,
                         'totalLoanBalance': float(account_data[0]) if account_data[0] else 0.0}

            all_data.append(each_lend)
    else:
        all_data = []

    all_data = all_data[(int(page) - 1) * int(page_number):int(page) * int(page_number)]

    conn_account.close()
    conn_product.close()
    conn_ams.close()

    return jsonify({'data': all_data, 'page': page, 'total': len(lend_data)})


# 数据统计-还款
@app.route('/report/payback/', methods=['GET', 'POST'])
def main_payback():
    post_data = json.loads(request.get_data(as_text=True))
    # 资金方代码
    lender_code = post_data.get('lenderCode')
    # 产品代码
    product_mapping_code = post_data.get('productMappingCode')
    # 融担代码
    signing_prescription = post_data.get('signingPrescription')
    # 获取当天日期
    today_info = datetime.date.today()
    today_info = str(today_info)

    # 日期
    start_day = post_data.get('startDay')
    end_day = post_data.get('endDay')

    product_data_info = product_mapping(lender_code, product_mapping_code, signing_prescription)

    product_data = [{'extraInfo': each[1], 'productMappingCode': each[3], 'productName': each[4],
                     'lenderCode': each[5], 'signingPrescription': each[8]}
                    for each in product_data_info]

    conn_ams = get_conn_ams()
    cur_ams = conn_ams.cursor()

    product_mapping_code_list = []
    for each in product_data:
        product_mapping_code_list.append(each['productMappingCode'])

    # 还款金额
    product_mapping_code_repay_qs = []
    product_mapping_code_repay_lh = []
    product_mapping_code_repay_wh = []
    product_mapping_code_repay_sls = []
    product_mapping_code_repay_js = []
    for each in product_data:
        # 齐商 P0000007：信用飞   PW0000001：我来贷
        if each['productMappingCode'] == 'P0000007' or each['productMappingCode'] == 'PW0000001':
            product_mapping_code_repay_qs.append(each['productMappingCode'])
        # 蓝海 P0000001：信用飞
        elif each['productMappingCode'] == 'P0000001':
            product_mapping_code_repay_lh.append(each['productMappingCode'])
        # 威海 P0000008：信用飞
        elif each['productMappingCode'] == 'P0000008':
            product_mapping_code_repay_wh.append(each['productMappingCode'])
        # 江苏银行  P0000012：洋钱罐
        elif each['productMappingCode'] == 'P0000012':
            product_mapping_code_repay_js.append(each['productMappingCode'])
        # 四平 P0000003:信用飞   P0000004：快牛   P0000005：绿信   P0000006：全民钱包
        # 长发展 P0000009: 绿信   P0000010: 信用飞  P0000011: 全民钱包
        else:
            product_mapping_code_repay_sls.append(each['productMappingCode'])

    total_repay_amount = 0

    if start_day and end_day:
        new_start_day = str(datetime.datetime.strptime(start_day, "%Y-%m-%d") + datetime.timedelta(days=1))[:10]
        new_end_day = str(datetime.datetime.strptime(end_day, "%Y-%m-%d") + datetime.timedelta(days=1))[:10]
    else:
        new_start_day = str(datetime.datetime.strptime(today_info, "%Y-%m-%d") + datetime.timedelta(days=1))[:10]
        new_end_day = str(datetime.datetime.strptime(today_info, "%Y-%m-%d") + datetime.timedelta(days=1))[:10]
        start_day = today_info
        end_day = today_info
    if product_mapping_code_repay_qs:
        sql_qs = """SELECT sum( repay_amt ) FROM
        (
        SELECT
            repay_amt
        FROM
            order_repay_file_qis
        WHERE
            repay_result = 'S' 
            AND (process_date BETWEEN '%s' and '%s') AND product_no IN ('%s') UNION ALL
        SELECT
            pre_repay_principal + pre_repay_interest
        FROM
            order_repay_apply 
        WHERE
            product_mapping_code IN ('%s') 
        AND (create_time BETWEEN '%s' AND '%s') 
        ) t;""" % (new_start_day, new_end_day, "','".join(product_mapping_code_repay_qs),
                   "','".join(product_mapping_code_repay_qs), start_day, end_day + ' 23:59:59')
        cur_ams.execute(sql_qs)
        qs_data = cur_ams.fetchone()[0]
        if qs_data:
            total_repay_amount += float(qs_data)
        else:
            total_repay_amount += 0
    if product_mapping_code_repay_lh:
        # product_mapping_code_list_lh = str(tuple(product_mapping_code_repay_lh))
        sql_lh = """SELECT sum(repay_amt) FROM order_repay_file_lh WHERE 
        repay_result = 'S' AND (repay_date BETWEEN '%s' and '%s');""" % (start_day, end_day)
        cur_ams.execute(sql_lh)
        lh_data = cur_ams.fetchone()[0]
        if lh_data:
            total_repay_amount += float(lh_data)
        else:
            total_repay_amount += 0
    if product_mapping_code_repay_wh:
        # product_mapping_code_list_wh = str(tuple(product_mapping_code_repay_wh))
        sql_wh = """SELECT sum(repay_amt) FROM order_repay_file_wh WHERE 
        repay_result = 'S' AND (process_date BETWEEN '%s' and '%s');""" \
                  % (new_start_day, new_end_day)
        cur_ams.execute(sql_wh)
        wh_data = cur_ams.fetchone()[0]
        if wh_data:
            total_repay_amount += float(wh_data)
        else:
            total_repay_amount += 0
    if product_mapping_code_repay_js:
        # product_mapping_code_list_js = str(tuple(product_mapping_code_repay_js))
        sql_js = """SELECT sum(repay_amt) FROM order_repay_file_jsu WHERE 
        repay_result = 'S' AND (process_date BETWEEN '%s' and '%s');""" \
                  % (new_start_day, new_end_day)
        cur_ams.execute(sql_js)
        js_data = cur_ams.fetchone()[0]
        if js_data:
            total_repay_amount += float(js_data)
        else:
            total_repay_amount += 0
    # 包括（兰州 P0000013）
    if product_mapping_code_repay_sls:
        sql_sls = """SELECT sum(repay_amt) FROM order_repay_file_sls WHERE 
        repay_result = 'S' AND (process_date BETWEEN '%s' and '%s') AND product_no in ('%s');""" \
                  % (new_start_day, new_end_day, "','".join(product_mapping_code_repay_sls))
        cur_ams.execute(sql_sls)
        sls_data = cur_ams.fetchone()[0]
        if sls_data:
            total_repay_amount += float(sls_data)
        else:
            total_repay_amount += 0
    conn_ams.close()
    return jsonify({'totalRepayAmount': round(total_repay_amount, 2)})


# 扣款数据
@app.route('/report/deduction/', methods=['GET', 'POST'])
def deduction():
    post_data = json.loads(request.get_data(as_text=True))
    # 资金方代码
    lender_code = post_data.get('lenderCode')
    # 产品代码
    product_mapping_code = post_data.get('productMappingCode')
    # 融担代码
    signing_prescription = post_data.get('signingPrescription')
    # 页数
    page = post_data.get('page')
    # 条数
    page_number = post_data.get('pageNumber')
    # 日期
    start_day = post_data.get('startDay')
    end_day = post_data.get('endDay')

    if not page:
        page = 1

    if not page_number:
        page_number = 10

    product_data_info = product_mapping(lender_code, product_mapping_code, signing_prescription)

    product_data = [{'extraInfo': each[1], 'productMappingCode': each[3], 'productName': each[4],
                     'lenderProductName': each[6], 'signingPrescription': each[8],
                     'repaymentFrequencyCompany': each[10]} for each in product_data_info if each[10]]
    data = []

    conn_ams = get_conn_ams()
    cur_ams = conn_ams.cursor()

    product_mapping_code_list = []
    for each in product_data:
        product_mapping_code_list.append(each['productMappingCode'])

    if start_day and end_day:
        sql_data = """SELECT product_mapping_code, DATE_FORMAT(preRepayDate, '%%Y-%%m-%%d') as date_info, 
        sum( total_amt ) as amt, count(1) as number FROM order_repay_apply WHERE product_mapping_code in ('%s') and
        (preRepayDate BETWEEN '%s' AND '%s') and proce_status = '1' GROUP BY 
        DATE_FORMAT(preRepayDate, '%%Y-%%m-%%d'), product_mapping_code order by date_info desc;""" \
                   % ("','".join(product_mapping_code_list), start_day, end_day + ' 23:59:59')

        cur_ams.execute(sql_data)
        each_data = cur_ams.fetchall()
        data += each_data
    else:
        if start_day:
            sql_data = """SELECT product_mapping_code, DATE_FORMAT(preRepayDate, '%%Y-%%m-%%d') as date_info, 
        sum( total_amt ) as amt, count(1) as number FROM order_repay_apply WHERE product_mapping_code in ('%s') and
        preRepayDate >= '%s' and proce_status = '1') GROUP BY 
        DATE_FORMAT(preRepayDate, '%%Y-%%m-%%d'), product_mapping_code order by date_info desc;""" \
                       % ("','".join(product_mapping_code_list), start_day)

            cur_ams.execute(sql_data)
            each_data = cur_ams.fetchall()
            data += each_data
        elif end_day:
            sql_data = """SELECT product_mapping_code, DATE_FORMAT(preRepayDate, '%%Y-%%m-%%d') as date_info, 
        sum( total_amt ) as amt, count(1) as number FROM order_repay_apply WHERE product_mapping_code in ('%s') and
        preRepayDate <= '%s' and proce_status = '1') GROUP BY 
        DATE_FORMAT(preRepayDate, '%%Y-%%m-%%d'), product_mapping_code order by date_info desc;""" \
                       % ("','".join(product_mapping_code_list), end_day + ' 23:59:59')

            cur_ams.execute(sql_data)
            each_data = cur_ams.fetchall()
            data += each_data
        else:
            sql_data = """SELECT product_mapping_code, DATE_FORMAT(preRepayDate, '%%Y-%%m-%%d') as date_info, 
        sum( total_amt ) as amt, count(1) as number FROM order_repay_apply WHERE product_mapping_code in ('%s') 
        and proce_status = '1' GROUP BY DATE_FORMAT(preRepayDate, '%%Y-%%m-%%d'), product_mapping_code 
        order by date_info desc;""" \
                       % "','".join(product_mapping_code_list)

            cur_ams.execute(sql_data)
            each_data = cur_ams.fetchall()
            data += each_data

    # 总记录
    total = len(data)

    target_data = []
    data = data[(int(page)-1)*int(page_number):int(page)*int(page_number)]
    for i in data:
        product_info = []
        for each in product_data:
            if i[0] == each['productMappingCode']:
                product_info.append(each['extraInfo'])
                product_info.append(each['productMappingCode'])
                product_info.append(each['productName'])
                product_info.append(each['lenderProductName'])
                product_info.append(each['repaymentFrequencyCompany'])
        target_data.append({'dateInfo': i[1], 'extraInfo': product_info[0], 'lenderCode': product_info[3],
                            'productMappingCode': product_info[1], 'channel': product_info[4],
                            'productName': product_info[2], 'deductionAmt': float(i[2]), 'totalNumber': int(i[3])})
    conn_ams.close()
    return jsonify({'data': target_data, 'page': page, 'total': total})


# 还款日报
@app.route('/report/debt/', methods=['GET', 'POST'])
def debt():
    sql_data = """SELECT 0, date_info, bank, assets, product_code, product_name, repay_type, period, 
    repay_method, sum(repay_number), sum(repay_amount), sum(repay_principal), sum(repay_interest), 
    sum(repay_over_fee), sum(total_repay_number), sum(total_repay_amount), sum(total_repay_principal), 
    sum(total_repay_interest) FROM `debt` where 1=1"""

    post_data = json.loads(request.get_data(as_text=True))
    # 资金方代码
    lender_code = post_data.get('lenderCode')
    # 产品代码
    product_mapping_code = post_data.get('productMappingCode')
    # 融担代码
    signing_prescription = post_data.get('signingPrescription')
    # 还款类型
    repay_type = post_data.get('repayType')
    if repay_type:
        sql_data += ' and repay_type = "%s"' % repay_type
    # 还款方式
    repay_method = post_data.get('repayMethod')
    if repay_method:
        sql_data += ' and repay_method = "%s"' % repay_method
    # 期数
    period = post_data.get('period')
    if period:
        sql_data += ' and period = "%s"' % period
    # 页数
    page = post_data.get('page')
    # 条数
    page_number = post_data.get('pageNumber')
    # 日期
    start_day = post_data.get('startDay')
    end_day = post_data.get('endDay')

    if not page:
        page = 1

    if not page_number:
        page_number = 10

    product_data_info = product_mapping(lender_code, product_mapping_code, signing_prescription)

    product_data = [{'extraInfo': each[1], 'productMappingCode': each[3], 'productName': each[4],
                     'lenderCode': each[5], 'signingPrescription': each[8]}
                    for each in product_data_info]
    data = []
    conn_product = sqlite3.connect(app.config['SQLALCHEMY_DATABASE'])
    cur_product = conn_product.cursor()

    product_mapping_code_list = []
    for each in product_data:
        product_mapping_code_list.append(each['productMappingCode'])

    if start_day and end_day:
        sql_data += """ and product_code in ('%s') and (date_info between DATE('%s') and DATE('%s')) GROUP BY date_info, product_code 
        order by date_info desc;""" % ("','".join(product_mapping_code_list), start_day, end_day)
    else:
        if start_day:
            sql_data += """ and product_code in ('%s') and date_info >= DATE('%s') GROUP BY date_info, product_code 
            order by date_info desc;""" % ("','".join(product_mapping_code_list), start_day)
        elif end_day:
            sql_data += """ and product_code in ('%s') and date_info <= DATE('%s') GROUP BY date_info, product_code 
            order by date_info desc;""" % ("','".join(product_mapping_code_list), end_day)
        else:
            sql_data += """ and product_code in ('%s') GROUP BY date_info, product_code order by date_info desc;""" \
                        % "','".join(product_mapping_code_list)
    cur_product.execute(sql_data)
    each_data = cur_product.fetchall()
    data += each_data

    # 总记录
    total = len(data)

    conn_product.close()
    target_data = []

    data = data[(int(page)-1)*int(page_number):int(page)*int(page_number)]
    for i in data:
        if repay_type:
            target_data.append({'dateInfo': i[1], 'bank': i[2], 'assets': i[3],
                                'productCode': i[4], 'productName': i[5], 'repayType': i[6], 'period': i[7],
                                'repayMethod': i[8], 'repayNumber': i[9], 'repayAmount': round(i[10], 2),
                                'repayPrincipal': round(i[11], 2), 'repayInterest': round(i[12], 2),
                                'repayOverFee': i[13],
                                'totalRepayNumber': i[14], 'totalRepayAmount': round(i[15], 2),
                                'totalRepayPrincipal': round(i[16], 2),
                                'totalRepayInterest': round(i[17], 2)})
        else:
            target_data.append({'dateInfo': i[1], 'bank': i[2], 'assets': i[3],
                                'productCode': i[4], 'productName': i[5], 'repayType': '00', 'period': i[7],
                                'repayMethod': i[8], 'repayNumber': i[9], 'repayAmount': round(i[10], 2),
                                'repayPrincipal': round(i[11], 2), 'repayInterest': round(i[12], 2),
                                'repayOverFee': i[13],
                                'totalRepayNumber': i[14], 'totalRepayAmount': round(i[15], 2),
                                'totalRepayPrincipal': round(i[16], 2),
                                'totalRepayInterest': round(i[17], 2)})

    return jsonify({'data': target_data, 'page': page, 'total': total})


# 客户进件数据
@app.route('/report/event/', methods=['GET', 'POST'])
def event():
    post_data = json.loads(request.get_data(as_text=True))
    # 资金方代码
    lender_code = post_data.get('lenderCode')
    # 产品代码
    product_mapping_code = post_data.get('productMappingCode')
    # 融担代码
    signing_prescription = post_data.get('signingPrescription')

    # 进件状态
    status = post_data.get('status')
    # 放款状态
    apply_status = post_data.get('applyStatus')

    # 页数
    page = post_data.get('page')
    # 条数
    page_number = post_data.get('pageNumber')

    # 获取当天日期
    today_info = datetime.date.today()
    today_info = str(today_info)

    # 日期
    start_day = post_data.get('startDay')
    end_day = post_data.get('endDay')

    if not page:
        page = 1

    if not page_number:
        page_number = 5

    product_data_info = product_mapping(lender_code, product_mapping_code, signing_prescription)

    product_data = [{'extraInfo': each[1], 'productMappingCode': each[3], 'productName': each[4],
                     'lenderCode': each[5], 'signingPrescription': each[8]}
                    for each in product_data_info]

    conn_ams = get_conn_ams()
    cur_ams = conn_ams.cursor()

    conn_cus = get_conn_cus()
    cur_cus = conn_cus.cursor()

    product_mapping_code_list = []
    for each in product_data:
        product_mapping_code_list.append(each['productMappingCode'])

    # 某个时间段 放款金额 放款笔数
    # 进件状态
    status_no = ''
    if status is not None:
        if int(status) == 0:
            status_no = ['0', '1', '4', '6', '7']
        elif int(status) == 1:
            status_no = ['2']
        elif int(status) == 2:
            status_no = ['3', '5']
        if start_day and end_day:
            sql_lend = """SELECT a.product_mapping_code, a.approval_status, a.credit_total_amount, a.credit_apply_id, 
            a.reason, b.apply_amount, b.apply_period, b.customer_id, a.create_time, a.update_time, c.customer_name 
            FROM customer_credit a LEFT JOIN customer_apply_info b ON a.customer_id = b.customer_id 
            INNER JOIN customer_info c on a.customer_id=c.id WHERE a.product_mapping_code in ('%s') 
            AND a.approval_status in ('%s') AND (a.create_time BETWEEN '%s' and '%s') AND 
            a.is_delete = 0 AND b.is_delete = 0;""" \
                       % ("','".join(product_mapping_code_list), "','".join(status_no), start_day, end_day + ' 23:59:59')
        else:
            sql_lend = """SELECT a.product_mapping_code, a.approval_status, a.credit_total_amount, a.credit_apply_id, 
            a.reason, b.apply_amount, b.apply_period, b.customer_id, a.create_time, a.update_time, c.customer_name 
            FROM customer_credit a LEFT JOIN customer_apply_info b ON a.customer_id = b.customer_id 
            INNER JOIN customer_info c on a.customer_id=c.id WHERE a.product_mapping_code in ('%s') 
            AND a.approval_status in ('%s') AND a.create_time LIKE '%s' AND a.is_delete = 0 AND b.is_delete = 0;""" \
                       % ("','".join(product_mapping_code_list), "','".join(status_no), today_info + '%')
    else:
        if start_day and end_day:
            sql_lend = """SELECT a.product_mapping_code, a.approval_status, a.credit_total_amount, a.credit_apply_id, 
            a.reason, b.apply_amount, b.apply_period, b.customer_id, a.create_time, a.update_time, c.customer_name 
            FROM customer_credit a LEFT JOIN customer_apply_info b ON a.customer_id = b.customer_id 
            INNER JOIN customer_info c on a.customer_id=c.id WHERE a.product_mapping_code in ('%s') 
            AND (a.create_time BETWEEN '%s' and '%s') AND a.is_delete = 0 AND b.is_delete = 0;""" \
                       % ("','".join(product_mapping_code_list), start_day, end_day + ' 23:59:59')
        else:
            sql_lend = """SELECT a.product_mapping_code, a.approval_status, a.credit_total_amount, a.credit_apply_id, 
            a.reason, b.apply_amount, b.apply_period, b.customer_id, a.create_time, a.update_time, c.customer_name 
            FROM customer_credit a LEFT JOIN customer_apply_info b ON a.customer_id = b.customer_id 
            INNER JOIN customer_info c on a.customer_id=c.id WHERE a.product_mapping_code in ('%s') 
            AND a.create_time LIKE '%s' AND a.is_delete = 0 AND b.is_delete = 0;""" \
                       % ("','".join(product_mapping_code_list), today_info + '%')
    # 授信数据
    cur_cus.execute(sql_lend)
    credit_data = cur_cus.fetchall()
    all_data1 = []
    if credit_data:
        credit_data1 = [{'productMappingCode': each[0], 'status': each[1], 'creditAmount': each[2], 'name': each[10],
                        'eventTime': each[8], 'applyAmount': each[5], 'period': each[6], 'successTime': each[9],
                        'feedBack': each[4], 'creditApplyId': each[3]} for each in credit_data]
        for each_data in credit_data1:
            for item in product_data_info:
                if item[3] == each_data['productMappingCode']:
                    len_name = len(each_data['name'])
                    try:
                        cus_name = (each_data['name'])[0] + (len_name-1)*'*'
                    except:
                        cus_name = ''

                    all_data1.append({'bank': item[6], 'productName': item[4],
                                     'productMappingCode': each_data['productMappingCode'],
                                     'status': str(each_data['status']), 'name': cus_name,
                                     'eventTime': str(each_data['eventTime']),
                                     'applyAmount': str(each_data['applyAmount']).split('.')[0],
                                     'creditAmount': str(each_data['creditAmount']).split('.')[0],
                                     'period': each_data['period'], 'successTime': str(each_data['successTime']),
                                     'feedBack': each_data['feedBack'], 'creditApplyId': each_data['creditApplyId']})

        credit_list = [each[3] for each in credit_data]
        sql_credit = """SELECT apply_status, apply_amount, loanpay_time, reason, credit_apply_id, period FROM order_apply_base_info 
        WHERE credit_apply_id in ('%s');""" % "','".join(credit_list)
        cur_ams.execute(sql_credit)
        credit_data2 = cur_ams.fetchall()
        all_data2 = [{'lendTime': str(each[2]) if each[2] else '', 'lendAmount': str(each[1]).split('.')[0], 'applyStatus': each[0],
                      'applyReason': each[3], 'creditApplyId': each[4], 'actualPeriod': str(each[5])} for each in credit_data2]

        new = []
        for i in all_data1:
            for j in all_data2:
                if i['creditApplyId'] == j['creditApplyId'] and set(i.keys()) != set(j.keys()):
                    i.update(j)
                    new.append(i)
        l = all_data1 + new
        all_data = [dict(i) for i in {}.fromkeys([frozenset(j.items()) for j in l])]
        # 放款状态
        # 放款成功 1007,  放款失败 1005 1008, 放款中  else
        new_info = []
        if apply_status is not None:
            if int(apply_status) == 0:
                new_info = [each for each in all_data if 'applyStatus' not in each]
            elif int(apply_status) == 1:
                new_info = [each for each in all_data if 'applyStatus' in each]
                new_info = [each for each in new_info if each['applyStatus'] != '1005'
                            and each['applyStatus'] != '1007' and each['applyStatus'] != '1008']
            elif int(apply_status) == 2:
                new_info = [each for each in all_data if 'applyStatus' in each]
                new_info = [each for each in new_info if each['applyStatus'] == '1007']
            elif int(apply_status) == 3:
                new_info = [each for each in all_data if 'applyStatus' in each]
                new_info = [each for each in new_info if each['applyStatus'] == '1005'
                            or each['applyStatus'] == '1008']
        else:
            new_info = all_data
        all_data = new_info[(int(page) - 1) * int(page_number):int(page) * int(page_number)]
    else:
        new_info = []
        all_data = []

    conn_ams.close()
    cur_cus.close()
    return jsonify({'data': all_data, 'page': page, 'total': len(new_info)})


@app.route('/report/api/')
def test():
    return render_template('api.html')

