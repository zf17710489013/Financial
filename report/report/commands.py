# -*- coding: utf-8 -*-
import click

from report import app, db
from report.models import Daily, OldDaily, Product, Repayment, Debt
import pymysql
import datetime

today_info = datetime.date.today()
yester_info = today_info - datetime.timedelta(days=1)

today_info = str(today_info)
yester_info = str(yester_info)

a = today_info
c = yester_info

#a = '2022-01-20'
#c = '2022-01-19'

product_sls_code = [{'product': '四平-信用飞', 'code': 'P0000003'}, {'product': '四平-快牛', 'code': 'P0000004'},
                        {'product': '四平-绿信', 'code': 'P0000005'}, {'product': '四平-全民钱包', 'code': 'P0000006'},
                        {'product': '长发展-绿信', 'code': 'P0000009'}, {'product': '长发展-信用飞', 'code': 'P0000010'},
                        {'product': '长发展-全民钱包', 'code': 'P0000011'}, {'product': '齐商-信用飞', 'code': 'P0000007'},
                    {'product': '齐商-我来贷', 'code': 'PW0000001'}, {'product': '蓝海-信用飞', 'code': 'P0000001'},
                    {'product': '威海-信用飞', 'code': 'P0000008'}, {'product': '兰州-信用飞', 'code': 'P0000013'},
                    {'product': '江苏银行-洋钱罐', 'code': 'P0000012'}]

# product_sls_code = [{'product': '江苏银行-洋钱罐', 'code': 'P0000012'}]


@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')


# 产品映射
@app.cli.command()
def mapping():
    db.create_all()

    conn_product = pymysql.connect(host="rm-uf6355lewwkmn1b59.mysql.rds.aliyuncs.com",
                                   port=3306, user="u_slkj", password="Slong@2020&",
                                   database="product_app")

    # # 测试
    # conn_product = pymysql.connect(host="192.168.100.227", port=3306,
    #                                user="u_slong", password="Slkj@2019.", database="product_app")
    cur = conn_product.cursor()

    sql_product = """SELECT id, extra_info, product_remark, product_mapping_code, product_name, 
            lender_code, lender_product_name, signing_mode, signing_prescription, repayment_frequency, 
            repayment_frequency_company FROM `product_mapping` 
            where 1=1"""

    cur.execute(sql_product)

    data_product = cur.fetchall()

    for each_product in data_product:
        each_data = Product(id=each_product[0], extra_info=each_product[1], product_remark=each_product[2],
                            product_mapping_code=each_product[3], product_name=each_product[4],
                            lender_code=each_product[5], lender_product_name=each_product[6],
                            signing_mode=each_product[7], signing_prescription=each_product[8],
                            repayment_frequency=each_product[9], repayment_frequency_company=each_product[10])
        db.session.add(each_data)

    conn_product.close()

    db.session.commit()
    click.echo('Done.')


# 运营日报表
@app.cli.command()
def old_forge():
    """Generate data."""
    db.create_all()

    conn_ams = pymysql.connect(host="rm-uf6355lewwkmn1b59.mysql.rds.aliyuncs.com", port=3306,
                               user="u_slkj", password="Slong@2020&", database="ams_app")

    # # 测试环境
    # conn_ams = pymysql.connect(host="192.168.100.227", port=3306,
    #                            user="u_slong", password="Slkj@2019.", database="ams_app")
    cur_ams = conn_ams.cursor()

    conn_order = pymysql.connect(host="rm-uf6355lewwkmn1b59.mysql.rds.aliyuncs.com", port=3306,
                                 user="u_slkj", password="Slong@2020&", database="order_app")

    # # 测试环境
    # conn_order = pymysql.connect(host="192.168.100.227", port=3306,
    #                              user="u_slong", password="Slkj@2019.", database="order_app")

    cur_order = conn_order.cursor()

    conn_customer = pymysql.connect(host="rm-uf6355lewwkmn1b59.mysql.rds.aliyuncs.com", port=3306,
                                 user="u_slkj", password="Slong@2020&", database="customer_app")
    # # 测试环境
    # conn_customer = pymysql.connect(host="192.168.100.227", port=3306,
    #                              user="u_slong", password="Slkj@2019.", database="customer_app")

    cur_customer = conn_customer.cursor()

    # 四平 P0000003:信用飞   P0000004：快牛   P0000005：绿信   P0000006：全民钱包

    # 兰州-信用飞  P0000013

    # 长发展 P0000009: 绿信   P0000010: 信用飞  P0000011: 全民钱包

    # 齐商 P0000007：信用飞   PW0000001：我来贷

    # 蓝海-信用飞  P0000001

    # 江苏银行-洋钱罐  P0000012

    # 提前结清 还款 放款

    for each in product_sls_code:
        product_code = each['code']

        sql_advance = """
                    select count(1),sum(lend_amount),product_code FROM `ams_account_borrow`
                    where product_code = '%s' and repay_status='8'
                    and update_time<'%s' group by product_code;""" % (product_code, a + ' 23:00:00')

        sql_lend = """SELECT sum(lend_amount), count(1) FROM `ams_account_borrow` WHERE 
        product_code = '%s' AND lend_time LIKE '%s';""" % (product_code, c + '%')

        cur_ams.execute(sql_advance)
        # 提前结清：笔数 金额
        advance_data = cur_ams.fetchone()
        # 放款数据： 当日放款金额 当日放款笔数
        cur_ams.execute(sql_lend)
        lend_data = cur_ams.fetchone()

        # 进件
        sql_entries = """SELECT COUNT(1) FROM `customer_apply_info` WHERE product_mapping_code = '%s' 
                AND create_time LIKE '%s' AND is_delete='0';""" % (product_code, c + '%')
        cur_customer.execute(sql_entries)
        entries_data = cur_customer.fetchone()

        # 成功授信
        sql_credit = """SELECT COUNT(1) FROM `customer_credit` WHERE product_mapping_code = '%s' 
                        AND create_time LIKE '%s' AND is_delete='0' AND approval_status='2';""" \
                     % (product_code, c + '%')
        cur_customer.execute(sql_credit)
        credit_data = cur_customer.fetchone()

        # 申请放款
        sql_apply_info = """SELECT COUNT(1), sum(apply_amount) from order_apply_base_info 
        WHERE product_mapping_code = '%s' AND create_time LIKE '%s' AND is_delete='0';""" \
                         % (product_code, c + '%')
        cur_order.execute(sql_apply_info)
        apply_info_data = cur_order.fetchone()

        # 当日还款
        # 齐商 P0000007：信用飞   PW0000001：我来贷
        if product_code == 'PW0000001' or product_code == 'P0000007':
            sql_order = """
            SELECT
        sum( repay_amt ),
        sum( repay_capital ),
        sum( repay_interest ),
        count(1)
    FROM
        (
        SELECT
            repay_amt,
            repay_capital,
            repay_interest,
            repay_date 
        FROM
            order_repay_file_qis
        WHERE
            repay_result = 'S' 
            AND process_date = "%s" AND product_no = '%s' UNION ALL
        SELECT
            ( pre_repay_principal + pre_repay_interest ),
            pre_repay_principal,
            pre_repay_interest,
            DATE_FORMAT( create_time, '%%Y-%%m-%%d' ) 
        FROM
            order_repay_apply 
        WHERE
            product_mapping_code = '%s' 
        AND create_time LIKE "%s" 
        ) t""" % (a, product_code, product_code, c + '%')
            cur_order.execute(sql_order)
            order_data = cur_order.fetchone()
            # 贷余
            cur_order.execute("""SELECT sum( apply_amount ) FROM order_apply_base_info WHERE 
                        apply_status = '1007' AND product_mapping_code ='%s' AND loanpay_time<'%s';"""
                              % (product_code, a))
            apply_data = cur_order.fetchone()
            if apply_data:
                apply_dt = apply_data[0] if apply_data[0] else 0
            else:
                apply_dt = 0

            cur_order.execute("""select sum(repay_capital) from (SELECT repay_capital FROM 
order_repay_file_qis WHERE repay_result = 'S' AND process_date <= '%s' AND product_no = '%s' 
UNION ALL SELECT pre_repay_principal as repay_capital
        FROM
            order_repay_apply 
        WHERE
            product_mapping_code = '%s' AND create_time<'%s') t;""" % (a, product_code, product_code, a))
            repay_data = cur_order.fetchone()
            if repay_data:
                repay_dt = repay_data[0] if repay_data[0] else 0
            else:
                repay_dt = 0
        # 蓝海-信用飞 P0000001
        elif product_code == 'P0000001':
            sql_lh = """SELECT sum(repay_amt), sum(repay_capital), sum(repay_interest), 
            count(1) FROM order_repay_file_lh WHERE 
            repay_result = 'S' AND repay_date = '%s';""" % c
            cur_order.execute(sql_lh)
            order_data = cur_order.fetchone()
            # 贷余
            cur_order.execute("""SELECT sum( apply_amount ) FROM order_apply_base_info WHERE 
                        apply_status = '1007' AND product_mapping_code ='%s' 
                        AND loanpay_time<'%s';""" % (product_code, a))
            apply_data = cur_order.fetchone()
            if apply_data:
                apply_dt = apply_data[0] if apply_data[0] else 0
            else:
                apply_dt = 0

            cur_order.execute("""SELECT sum( repay_capital ) FROM order_repay_file_lh 
                        WHERE repay_result = 'S' AND repay_date < '%s';""" % a)
            repay_data = cur_order.fetchone()
            if repay_data:
                repay_dt = repay_data[0] if repay_data[0] else 0
            else:
                repay_dt = 0
        # 威海-信用飞
        elif product_code == 'P0000008':
            sql_wh = """SELECT sum(repay_amt) FROM order_repay_file_wh WHERE 
                    repay_result = 'S' AND process_date = '%s';""" % a
            cur_order.execute(sql_wh)
            order_data = cur_order.fetchone()
            # 贷余
            cur_order.execute("""SELECT sum( apply_amount ) FROM order_apply_base_info WHERE 
                        apply_status = '1007' AND product_mapping_code ='%s' 
                        AND loanpay_time<'%s';""" % (product_code, a))
            apply_data = cur_order.fetchone()
            if apply_data:
                apply_dt = apply_data[0] if apply_data[0] else 0
            else:
                apply_dt = 0

            cur_order.execute("""SELECT sum( repay_capital ) FROM order_repay_file_wh 
                        WHERE repay_result = 'S' AND process_date<'%s';""" % a)
            repay_data = cur_order.fetchone()
            if repay_data:
                repay_dt = repay_data[0] if repay_data[0] else 0
            else:
                repay_dt = 0
        # 江苏银行-洋钱罐  P0000012
        elif product_code == 'P0000012':
            sql_js = """SELECT sum(repay_amt), sum(repay_capital), sum(repay_interest), count(1) 
                        FROM order_repay_file_jsu WHERE 
                        repay_result = 'S' AND process_date = '%s' AND product_no = '%s';""" % (a, product_code)
            cur_order.execute(sql_js)
            order_data = cur_order.fetchone()
            # 贷余
            cur_order.execute("""SELECT sum( apply_amount ) FROM order_apply_base_info WHERE 
                        apply_status = '1007' AND product_mapping_code ='%s' AND loanpay_time<'%s';"""
                              % (product_code, a))
            apply_data = cur_order.fetchone()
            if apply_data:
                apply_dt = apply_data[0] if apply_data[0] else 0
            else:
                apply_dt = 0

            cur_order.execute("""SELECT sum( repay_capital ) FROM order_repay_file_jsu 
                        WHERE repay_result = 'S' AND process_date <= '%s' AND product_no ='%s';""" % (a, product_code))
            repay_data = cur_order.fetchone()
            if repay_data:
                repay_dt = repay_data[0] if repay_data[0] else 0
            else:
                repay_dt = 0
        else:
            # 四平 P0000003:信用飞   P0000004：快牛   P0000005：绿信   P0000006：全民钱包
            # 长发展
            # 兰州 P0000013
            sql_sls = """SELECT sum(repay_amt), sum(repay_capital), sum(repay_interest), count(1) 
            FROM order_repay_file_sls WHERE 
            repay_result = 'S' AND process_date = '%s' AND product_no = '%s';""" % (a, product_code)
            cur_order.execute(sql_sls)
            order_data = cur_order.fetchone()
            # 贷余
            cur_order.execute("""SELECT sum( apply_amount ) FROM order_apply_base_info WHERE 
            apply_status = '1007' AND product_mapping_code ='%s' AND loanpay_time<'%s';""" % (product_code, a))
            apply_data = cur_order.fetchone()
            if apply_data:
                apply_dt = apply_data[0] if apply_data[0] else 0
            else:
                apply_dt = 0

            cur_order.execute("""SELECT sum( repay_capital ) FROM order_repay_file_sls 
            WHERE repay_result = 'S' AND process_date <= '%s' AND product_no ='%s';""" % (a, product_code))
            repay_data = cur_order.fetchone()
            if repay_data:
                repay_dt = repay_data[0] if repay_data[0] else 0
            else:
                repay_dt = 0

        try:
            # 还款
            repay_amount = order_data[0] if order_data[0] else 0
            repay_principal = order_data[1] if order_data[1] else 0
            repay_interest = order_data[2] if order_data[2] else 0
            repay_number = order_data[3] if order_data[3] else 0
        except:
            repay_amount = 0
            repay_principal = 0
            repay_interest = 0
            repay_number = 0

        if advance_data:
            # 提前结清笔数
            advance_settlement = advance_data[0] if advance_data[0] else 0
            # 提前结清金额
            advance_amount = advance_data[1] if advance_data[1] else 0
        else:
            advance_settlement = 0
            advance_amount = 0

        if lend_data:
            # 当日放款金额
            lend_amount = lend_data[0] if lend_data[0] else 0
            # 当日放款笔数
            lend_number = lend_data[1] if lend_data[1] else 0
        else:
            lend_amount = 0
            lend_number = 0

        if entries_data:
            entries = entries_data[0] if entries_data[0] else 0
        else:
            entries = 0

        if credit_data:
            credit_number = credit_data[0] if credit_data[0] else 0
        else:
            credit_number = 0

        if apply_info_data:
            apply_lend_number = apply_info_data[0] if apply_info_data[0] else 0
            apply_lend_amount = apply_info_data[1] if apply_info_data[1] else 0
        else:
            apply_lend_number = 0
            apply_lend_amount = 0

        if entries:
            credit_percent = str(round(credit_number*100/entries, 2)) + '%'
            lend_percent = str(round(lend_number*100/entries, 2)) + '%'
        else:
            credit_percent = '-'
            lend_percent = '-'

        daily = OldDaily(date_info=datetime.datetime.strptime(c, '%Y-%m-%d'), product_mapping_code=product_code,
                         repay_amount=repay_amount, repay_principal=repay_principal, repay_interest=repay_interest,
                         repay_number=repay_number, advance_settlement=advance_settlement,
                         advance_amount=advance_amount, lend_amount=lend_amount, lend_number=lend_number,
                         total_loan_balance=apply_dt-repay_dt, entries=entries, credit_number=credit_number,
                         apply_lend_number=apply_lend_number,
                         apply_lend_amount=apply_lend_amount, credit_percent=credit_percent,
                         lend_percent=lend_percent)

        db.session.add(daily)

    conn_ams.close()
    conn_order.close()
    conn_customer.close()

    db.session.commit()
    click.echo('Done.')


# 还款明细
@app.cli.command()
def repay():
    """Generate data."""
    db.create_all()

    conn_order = pymysql.connect(host="rm-uf6355lewwkmn1b59.mysql.rds.aliyuncs.com", port=3306,
                                 user="u_slkj", password="Slong@2020&", database="order_app")

    # # 测试环境
    # conn_order = pymysql.connect(host="192.168.100.227", port=3306,
    #                              user="u_slong", password="Slkj@2019.", database="order_app")

    cur_order = conn_order.cursor()
    # 账务
    conn_ams = pymysql.connect(host="rm-uf6355lewwkmn1b59.mysql.rds.aliyuncs.com", port=3306,
                               user="u_slkj", password="Slong@2020&", database="ams_app")

    # # 测试环境
    # conn_ams = pymysql.connect(host="192.168.100.227", port=3306,
    #                            user="u_slong", password="Slkj@2019.", database="ams_app")
    cur_ams = conn_ams.cursor()

    # 四平 P0000003:信用飞   P0000004：快牛   P0000005：绿信   P0000006：全民钱包

    # 兰州-信用飞  P0000013

    # 长发展 P0000009: 绿信   P0000010: 信用飞  P0000011: 全民钱包

    # 齐商 P0000007：信用飞   PW0000001：我来贷

    # 蓝海-信用飞  P0000001

    for each in product_sls_code:
        product_code = each['code']
        # 还款
        # 齐商 P0000007：信用飞   PW0000001：我来贷
        if product_code == 'PW0000001' or product_code == 'P0000007':
            sql_qis = """SELECT a.product_no, b.name, a.loan_no, a.repay_date, a.repay_type, 
            a.process_date, b.apply_amount, a.repay_capital, a.repay_interest, b.period, 
            a.current_num FROM order_repay_file_qis as a 
            LEFT JOIN order_apply_base_info as b on a.loan_no = b.loan_no WHERE 
            a.repay_result = 'S' AND a.process_date = '%s' AND a.product_no = '%s' 
            ORDER BY a.process_date DESC;""" \
                      % (a, product_code)
            cur_order.execute(sql_qis)
            order_data = cur_order.fetchall()
        # 蓝海-信用飞 P0000001
        elif product_code == 'P0000001':
            sql_lh = """SELECT b.product_mapping_code, b.name, a.loan_no, a.repay_date, a.repay_type, 
                        mid(a.create_time,1,10) as process_date, b.apply_amount, a.repay_capital, a.repay_interest, 
                        b.period, a.current_num FROM order_repay_file_lh as a 
                        LEFT JOIN order_apply_base_info as b on a.loan_no = b.loan_no WHERE 
                        a.repay_result = 'S' AND a.create_time like '%s' AND b.product_mapping_code = '%s';""" \
                      % (a + '%', product_code)
            cur_order.execute(sql_lh)
            order_data = cur_order.fetchall()
        # # 威海-信用飞
        # elif product_code == 'P0000008':
        #     sql_wh = """SELECT a.product_no, b.name, a.loan_no, a.repay_date, a.repay_type,
        #                 a.process_date, b.apply_amount, a.repay_capital, a.repay_interest, b.period,
        #                 a.current_num FROM order_repay_file_wh as a
        #                 LEFT JOIN order_apply_base_info as b on a.loan_no = b.loan_no WHERE
        #                 a.repay_result = 'S' AND a.process_date = '%s' AND a.product_no = '%s'
        #                 ORDER BY a.process_date DESC;""" \
        #               % (a, product_code)
        #     cur_order.execute(sql_wh)
        #     order_data = cur_order.fetchall()
        elif product_code == 'P0000013':
            # 四平 P0000003:信用飞   P0000004：快牛   P0000005：绿信   P0000006：全民钱包
            # 长发展 P0000009: 绿信   P0000010: 信用飞  P0000011: 全民钱包
            # 兰州-信用飞  P0000013
            sql_sls = """SELECT a.product_no, b.name, a.loan_no, a.repay_date, a.repay_type, 
            a.process_date, b.apply_amount, a.repay_capital, a.repay_interest, b.period, 
            a.current_num FROM order_repay_file_sls as a 
            LEFT JOIN order_apply_base_info as b on a.loan_no = b.loan_no WHERE 
            a.repay_result = 'S' AND a.process_date = '%s' AND a.product_no = '%s' 
            ORDER BY a.process_date DESC;""" \
                      % (a, product_code)
            cur_order.execute(sql_sls)
            order_data = cur_order.fetchall()
        elif product_code == 'P0000012':
            # 江苏-洋钱罐  P0000012
            sql_sls = """SELECT a.product_no, b.name, a.loan_no, a.repay_date, a.repay_type, 
            a.process_date, b.apply_amount, a.repay_capital, a.repay_interest, b.period, 
            a.current_num FROM order_repay_file_jsu as a 
            LEFT JOIN order_apply_base_info as b on a.loan_no = b.loan_no WHERE 
            a.repay_result = 'S' AND a.process_date = '%s' AND a.product_no = '%s' 
            ORDER BY a.process_date DESC;""" \
                      % (a, product_code)
            cur_order.execute(sql_sls)
            order_data = cur_order.fetchall()
        else:
            order_data = []
        if order_data:
            for each_order in order_data:
                if type(each_order[5]) == str:
                    date_time_info = datetime.datetime.strptime(each_order[5], '%Y-%m-%d')
                    process_date = date_time_info.date()
                else:
                    process_date = each_order[5]
                cur_ams.execute("SELECT total_amount_left from ams_account_borrow where loan_no='%s'" % each_order[2])
                remain_amt = cur_ams.fetchone()[0]

                repay_order = Repayment(product_mapping_code=each_order[0], name=each_order[1],
                                        loan_no=each_order[2], repay_date=each_order[3],
                                        repay_type=each_order[4], process_date=process_date,
                                        loan_amt=each_order[6], repay_capital=each_order[7],
                                        repay_interest=each_order[8], total_number=each_order[9],
                                        current_number=each_order[10], remain_amt=remain_amt,
                                        repay_method='0')
                db.session.add(repay_order)

    conn_order.close()
    conn_ams.close()
    db.session.commit()
    click.echo('Done.')


# 分期数
@app.cli.command()
def forge1():
    """Generate data."""
    db.create_all()

    conn_ams = pymysql.connect(host="rm-uf6355lewwkmn1b59.mysql.rds.aliyuncs.com", port=3306,
                               user="u_slkj", password="Slong@2020&", database="ams_app")

    # # 测试环境
    # conn_ams = pymysql.connect(host="192.168.100.227", port=3306,
    #                            user="u_slong", password="Slkj@2019.", database="ams_app")
    cur_ams = conn_ams.cursor()

    conn_order = pymysql.connect(host="rm-uf6355lewwkmn1b59.mysql.rds.aliyuncs.com", port=3306,
                                 user="u_slkj", password="Slong@2020&", database="order_app")

    # # 测试环境
    # conn_order = pymysql.connect(host="192.168.100.227", port=3306,
    #                              user="u_slong", password="Slkj@2019.", database="order_app")

    cur_order = conn_order.cursor()

    conn_customer = pymysql.connect(host="rm-uf6355lewwkmn1b59.mysql.rds.aliyuncs.com", port=3306,
                                    user="u_slkj", password="Slong@2020&", database="customer_app")
    # # 测试环境
    # conn_customer = pymysql.connect(host="192.168.100.227", port=3306,
    #                              user="u_slong", password="Slkj@2019.", database="customer_app")

    cur_customer = conn_customer.cursor()

    # 四平 P0000003:信用飞   P0000004：快牛   P0000005：绿信   P0000006：全民钱包

    # 兰州-信用飞  P0000013

    # 长发展 P0000009: 绿信   P0000010: 信用飞  P0000011: 全民钱包

    # 齐商 P0000007：信用飞   PW0000001：我来贷

    # 蓝海-信用飞  P0000001

    # 江苏银行-洋钱罐  P0000012

    # 提前结清 还款 放款

    # 分期 3，6，9，12
    for each_period in [3, 6, 9, 12]:
        for each in product_sls_code:
            product_code = each['code']

            sql_advance = """
                        select count(1),sum(lend_amount),product_code, repay_period FROM `ams_account_borrow`
                        where product_code = '%s' and repay_status='8'
                        and update_time<'%s' and repay_period='%s';""" % (product_code, a + ' 23:00:00', each_period)

            sql_lend = """SELECT sum(lend_amount), count(1), product_code, repay_period  
            FROM `ams_account_borrow` WHERE product_code = '%s' 
            AND lend_time LIKE '%s' and repay_period='%s';""" % (product_code, c + '%', each_period)

            cur_ams.execute(sql_advance)

            # 提前结清：笔数 金额
            advance_data = cur_ams.fetchone()
            # 放款数据： 当日放款金额 当日放款笔数
            cur_ams.execute(sql_lend)
            lend_data = cur_ams.fetchone()

            # 进件
            sql_entries = """SELECT COUNT(1) FROM `customer_apply_info` WHERE product_mapping_code = '%s' 
                            AND create_time LIKE '%s' AND is_delete='0' AND apply_period='%s';""" \
                          % (product_code, c + '%', each_period)
            cur_customer.execute(sql_entries)
            entries_data = cur_customer.fetchone()

            # 成功授信
            sql_credit = """SELECT COUNT(1) from customer_apply_info where customer_id in (SELECT customer_id FROM 
            `customer_credit` a WHERE product_mapping_code = '%s' AND create_time LIKE '%s' AND is_delete = '0' 
            AND approval_status = '2') and is_delete='0' and apply_period='%s';;""" \
                         % (product_code, c + '%', each_period)
            cur_customer.execute(sql_credit)
            credit_data = cur_customer.fetchone()

            # 申请放款
            sql_apply_info = """SELECT COUNT(1), sum(apply_amount) from order_apply_base_info 
            WHERE product_mapping_code = '%s' AND create_time LIKE '%s' AND is_delete='0' AND period='%s';""" \
                             % (product_code, c + '%', each_period)
            cur_order.execute(sql_apply_info)
            apply_info_data = cur_order.fetchone()

            # 当日还款
            # 齐商 P0000007：信用飞   PW0000001：我来贷
            if product_code == 'PW0000001' or product_code == 'P0000007':
                sql_order = """
                SELECT
            sum( repay_amt ),
            sum( repay_capital ),
            sum( repay_interest ),
            count(1),
            period
        FROM
            (
            SELECT
                repay_amt,
                repay_capital,
                repay_interest,
                repay_date,
                loan_no 
            FROM
                order_repay_file_qis
            WHERE
                repay_result = 'S' 
                AND process_date = "%s" AND product_no = '%s' UNION ALL
            SELECT
                ( pre_repay_principal + pre_repay_interest ),
                pre_repay_principal,
                pre_repay_interest,
                DATE_FORMAT( create_time, '%%Y-%%m-%%d' ),
                loan_no 
            FROM
                order_repay_apply 
            WHERE
                product_mapping_code = '%s' 
            AND create_time LIKE "%s" 
            ) t LEFT JOIN order_apply_base_info k ON t.loan_no=k.loan_no WHERE period='%s';""" \
                            % (a, product_code, product_code, c + '%', each_period)
                cur_order.execute(sql_order)
                order_data = cur_order.fetchone()
                # 贷余
                cur_order.execute("""SELECT sum( apply_amount ) FROM order_apply_base_info WHERE 
                                apply_status = '1007' AND product_mapping_code = '%s' AND period = '%s' 
                                AND loanpay_time<'%s';""" % (product_code, each_period, a))
                apply_data = cur_order.fetchone()
                if apply_data:
                    apply_dt = apply_data[0] if apply_data[0] else 0
                else:
                    apply_dt = 0

                cur_order.execute("""select sum(repay_capital) from ((SELECT m.repay_capital as repay_capital FROM 
                order_repay_file_qis m LEFT JOIN order_apply_base_info n ON m.loan_no=n.loan_no 
                WHERE m.repay_result = 'S' AND m.product_no = '%s' AND n.period='%s') 
                UNION ALL (SELECT j.pre_repay_principal as repay_capital
                        FROM
                            order_repay_apply j LEFT JOIN order_apply_base_info k
                        ON j.loan_no=k.loan_no WHERE
                            j.product_mapping_code = '%s' AND j.create_time<'%s' AND k.period='%s')) a;"""
                                  % (product_code, each_period, product_code, a, each_period))
                repay_data = cur_order.fetchone()
                if repay_data:
                    repay_dt = repay_data[0] if repay_data[0] else 0
                else:
                    repay_dt = 0
            # 蓝海-信用飞 P0000001
            elif product_code == 'P0000001':
                sql_lh = """SELECT SUM( repay_capital )+ sum( repay_interest ), 
                SUM( repay_capital ), sum( repay_interest ) , COUNT(1), period FROM ams_repay_fee 
                WHERE product_no = 'P0000001' AND is_delete = '0' AND actual_date = '%s' AND period='%s';""" \
                         % (c, each_period)
                cur_ams.execute(sql_lh)
                order_data = cur_ams.fetchone()
                # 贷余
                cur_order.execute("""SELECT sum( apply_amount ) FROM order_apply_base_info WHERE 
                                apply_status = '1007' AND product_mapping_code = '%s' AND period = '%s' 
                                AND loanpay_time<'%s';""" % (product_code, each_period, a))
                apply_data = cur_order.fetchone()
                if apply_data:
                    apply_dt = apply_data[0] if apply_data[0] else 0
                else:
                    apply_dt = 0

                cur_order.execute("""SELECT sum( repay_capital ) FROM order_repay_file_lh a 
                                LEFT JOIN order_apply_base_info b ON a.loan_no = b.loan_no WHERE a.repay_result = 'S' 
                                AND b.period = '%s' AND a.repay_date<'%s';"""
                                  % (each_period, a))
                repay_data = cur_order.fetchone()
                if repay_data:
                    repay_dt = repay_data[0] if repay_data[0] else 0
                else:
                    repay_dt = 0
            # 威海-信用飞
            elif product_code == 'P0000008':
                sql_wh = """SELECT sum(a.repay_amt), sum(a.repay_capital), sum(a.repay_interest), count(1), b.period 
                FROM order_repay_file_wh a LEFT JOIN order_apply_base_info b ON a.loan_no=b.loan_no WHERE 
                a.repay_result = 'S' AND a.process_date = '%s' AND a.product_no = '%s' AND b.period='%s';""" \
                         % (a, product_code, each_period)
                cur_order.execute(sql_wh)
                order_data = cur_order.fetchone()
                # 贷余
                cur_order.execute("""SELECT sum( apply_amount ) FROM order_apply_base_info WHERE 
                                apply_status = '1007' AND product_mapping_code = '%s' AND period = '%s' 
                                AND loanpay_time<'%s';""" % (product_code, each_period, a))
                apply_data = cur_order.fetchone()
                if apply_data:
                    apply_dt = apply_data[0] if apply_data[0] else 0
                else:
                    apply_dt = 0

                cur_order.execute("""SELECT sum( repay_capital ) FROM order_repay_file_wh a 
                                LEFT JOIN order_apply_base_info b ON a.loan_no = b.loan_no WHERE a.repay_result = 'S' 
                                AND a.product_no = '%s' AND b.period = '%s' AND a.repay_date<'%s';"""
                                  % (product_code, each_period, a))
                repay_data = cur_order.fetchone()
                if repay_data:
                    repay_dt = repay_data[0] if repay_data[0] else 0
                else:
                    repay_dt = 0
            # 江苏银行-洋钱罐  P0000012
            elif product_code == 'P0000012':
                sql_js = """SELECT sum(a.repay_amt), sum(a.repay_capital), sum(a.repay_interest), count(1), b.period 
                                FROM order_repay_file_jsu a LEFT JOIN order_apply_base_info b ON a.loan_no=b.loan_no 
                                WHERE a.repay_result = 'S' AND a.process_date = '%s' AND a.product_no = '%s' 
                                AND b.period='%s';""" % (a, product_code, each_period)
                cur_order.execute(sql_js)
                order_data = cur_order.fetchone()
                # 贷余
                cur_order.execute("""SELECT sum( apply_amount ) FROM order_apply_base_info WHERE 
                                apply_status = '1007' AND product_mapping_code = '%s' AND period = '%s' 
                                AND loanpay_time<'%s';""" % (product_code, each_period, a))
                apply_data = cur_order.fetchone()
                if apply_data:
                    apply_dt = apply_data[0] if apply_data[0] else 0
                else:
                    apply_dt = 0

                cur_order.execute("""SELECT sum( repay_capital ) FROM order_repay_file_jsu a 
                                LEFT JOIN order_apply_base_info b ON a.loan_no = b.loan_no WHERE a.repay_result = 'S' 
                                AND a.product_no = '%s' AND b.period = '%s';""" % (product_code, each_period))
                repay_data = cur_order.fetchone()
                if repay_data:
                    repay_dt = repay_data[0] if repay_data[0] else 0
                else:
                    repay_dt = 0
            else:
                # 四平 P0000003:信用飞   P0000004：快牛   P0000005：绿信   P0000006：全民钱包
                # 兰州-信用飞  P0000013
                # 长发展
                sql_sls = """SELECT sum(a.repay_amt), sum(a.repay_capital), sum(a.repay_interest), count(1), b.period 
                FROM order_repay_file_sls a LEFT JOIN order_apply_base_info b ON a.loan_no=b.loan_no WHERE 
                a.repay_result = 'S' AND a.process_date = '%s' AND a.product_no = '%s' AND b.period='%s';""" \
                          % (a, product_code, each_period)
                cur_order.execute(sql_sls)
                order_data = cur_order.fetchone()
                # 贷余
                cur_order.execute("""SELECT sum( apply_amount ) FROM order_apply_base_info WHERE 
                apply_status = '1007' AND product_mapping_code = '%s' AND period = '%s' AND loanpay_time<'%s';"""
                                  % (product_code, each_period, a))
                apply_data = cur_order.fetchone()
                if apply_data:
                    apply_dt = apply_data[0] if apply_data[0] else 0
                else:
                    apply_dt = 0

                cur_order.execute("""SELECT sum( repay_capital ) FROM order_repay_file_sls a 
                LEFT JOIN order_apply_base_info b ON a.loan_no = b.loan_no WHERE a.repay_result = 'S' 
                AND a.product_no = '%s' AND b.period = '%s';""" % (product_code, each_period))
                repay_data = cur_order.fetchone()
                if repay_data:
                    repay_dt = repay_data[0] if repay_data[0] else 0
                else:
                    repay_dt = 0

            try:
                # 还款
                repay_amount = order_data[0] if order_data[0] else 0
                repay_principal = order_data[1] if order_data[1] else 0
                repay_interest = order_data[2] if order_data[2] else 0
                repay_number = order_data[3] if order_data[3] else 0
            except:
                repay_amount = 0
                repay_principal = 0
                repay_interest = 0
                repay_number = 0

            if advance_data:
                # 提前结清笔数
                advance_settlement = advance_data[0] if advance_data[0] else 0
                # 提前结清金额
                advance_amount = advance_data[1] if advance_data[1] else 0
            else:
                advance_settlement = 0
                advance_amount = 0

            if lend_data:
                # 当日放款金额
                lend_amount = lend_data[0] if lend_data[0] else 0
                # 当日放款笔数
                lend_number = lend_data[1] if lend_data[1] else 0
            else:
                lend_amount = 0
                lend_number = 0

            if entries_data:
                entries = entries_data[0] if entries_data[0] else 0
            else:
                entries = 0
            if credit_data:
                credit_number = credit_data[0] if credit_data[0] else 0
            else:
                credit_number = 0

            if apply_info_data:
                apply_lend_number = apply_info_data[0] if apply_info_data[0] else 0
                apply_lend_amount = apply_info_data[1] if apply_info_data[1] else 0
            else:
                apply_lend_number = 0
                apply_lend_amount = 0

            if entries:
                credit_percent = str(round(credit_number * 100 / entries, 2)) + '%'
                lend_percent = str(round(lend_number * 100 / entries, 2)) + '%'
            else:
                credit_percent = '-'
                lend_percent = '-'

            daily = Daily(date_info=datetime.datetime.strptime(c, '%Y-%m-%d'), product_mapping_code=product_code,
                          repay_amount=repay_amount, repay_principal=repay_principal, repay_interest=repay_interest,
                          repay_number=repay_number, advance_settlement=advance_settlement,
                          advance_amount=advance_amount, lend_amount=lend_amount, lend_number=lend_number,
                          period=each_period, total_loan_balance=apply_dt-repay_dt,
                          entries=entries, credit_number=credit_number, apply_lend_number=apply_lend_number,
                          apply_lend_amount=apply_lend_amount, credit_percent=credit_percent, lend_percent=lend_percent)

            db.session.add(daily)

    conn_ams.close()
    conn_order.close()
    conn_customer.close()

    db.session.commit()
    click.echo('Done.')


# 还款线上
@app.cli.command()
def debt_online():
    """Generate data."""
    db.create_all()

    conn_order = pymysql.connect(host="rm-uf6355lewwkmn1b59.mysql.rds.aliyuncs.com", port=3306,
                                 user="u_slkj", password="Slong@2020&", database="order_app")

    # # 测试环境
    # conn_order = pymysql.connect(host="192.168.100.227", port=3306,
    #                              user="u_slong", password="Slkj@2019.", database="order_app")

    cur_order = conn_order.cursor()
    # # 账务
    # conn_ams = pymysql.connect(host="rm-uf6355lewwkmn1b59.mysql.rds.aliyuncs.com", port=3306,
    #                            user="u_slkj", password="Slong@2020&", database="ams_app")
    #
    # # # 测试环境
    # # conn_ams = pymysql.connect(host="192.168.100.227", port=3306,
    # #                            user="u_slong", password="Slkj@2019.", database="ams_app")
    # cur_ams = conn_ams.cursor()

    # 四平 P0000003:信用飞   P0000004：快牛   P0000005：绿信   P0000006：全民钱包

    # 兰州-信用飞  P0000013

    # 长发展 P0000009: 绿信   P0000010: 信用飞  P0000011: 全民钱包

    # 齐商 P0000007：信用飞   PW0000001：我来贷

    # 蓝海-信用飞  P0000001

    # 江苏银行-洋钱罐  P0000012

    # 齐商 提前结清,其他 提前还款
    repay_info = [{'repay_type_info': '正常还款', 'repay_no_info': '0'},
                  {'repay_type_info': '提前结清', 'repay_no_info': '1'},
                  {'repay_type_info': '当期代偿', 'repay_no_info': '2'},
                  {'repay_type_info': '全额代偿', 'repay_no_info': '3'},
                  {'repay_type_info': '逾期还款', 'repay_no_info': '4'}]

    all_period = ['3', '6', '9', '12']

    for each in product_sls_code:
        for each_repay_info in repay_info:
            for each_period in all_period:
                product_code = each['code']
                # 还款
                # 齐商 P0000007：信用飞   PW0000001：我来贷
                if product_code == 'PW0000001' or product_code == 'P0000007':
                    if each_repay_info['repay_type_info'] == '提前结清':
                        sql_qis = """SELECT sum( a.pre_repay_principal + a.pre_repay_interest ), 
                        sum(a.pre_repay_principal), sum(a.pre_repay_interest), sum(a.pre_repay_overdue_fee), COUNT(1) 
                        FROM order_repay_apply a LEFT JOIN order_apply_base_info b ON a.loan_no=b.loan_no WHERE 
                        a.product_mapping_code = '%s' AND a.create_time LIKE "%s" AND b.period='%s';""" \
                                  % (product_code, c + '%', each_period)
                        cur_order.execute(sql_qis)
                        order_data = cur_order.fetchone()
                        # 累计
                        total_sql_qis = """SELECT sum( a.pre_repay_principal + a.pre_repay_interest ), 
                        sum(a.pre_repay_principal), sum(a.pre_repay_interest), COUNT(1) 
                        FROM order_repay_apply a LEFT JOIN order_apply_base_info b ON a.loan_no=b.loan_no WHERE 
                        a.product_mapping_code = '%s' AND a.create_time < "%s" AND b.period='%s';""" \
                                        % (product_code, a, each_period)
                        cur_order.execute(total_sql_qis)
                        total_order_data = cur_order.fetchone()
                    else:
                        sql_qis = """select sum( repay_amt ), sum( repay_capital ), sum( repay_interest ), 0, count(1) 
                    from (SELECT a.repay_amt, a.repay_capital, a.repay_interest, a.loan_no FROM order_repay_file_qis a 
                    WHERE a.repay_result = 'S' AND a.process_date = '%s' AND product_no = '%s' AND a.repay_type = '%s') t LEFT JOIN 
                    order_apply_base_info k on t.loan_no=k.loan_no where k.period='%s';""" \
                                  % (a, product_code, each_repay_info['repay_no_info'], each_period)
                        cur_order.execute(sql_qis)
                        order_data = cur_order.fetchone()
                        # 累计
                        total_sql_qis = """select sum( repay_amt ), sum( repay_capital ), sum( repay_interest ), count(1) 
                    from (SELECT a.repay_amt, a.repay_capital, a.repay_interest, a.loan_no FROM order_repay_file_qis a 
                    WHERE a.repay_result = 'S' AND a.process_date <= '%s' AND product_no = '%s' AND a.repay_type = '%s') t LEFT JOIN 
                    order_apply_base_info k on t.loan_no=k.loan_no where k.period='%s';""" \
                                  % (a, product_code, each_repay_info['repay_no_info'], each_period)
                        cur_order.execute(total_sql_qis)
                        total_order_data = cur_order.fetchone()
                # 蓝海-信用飞 P0000001
                elif product_code == 'P0000001':
                    sql_lh = """select sum( repay_amt ), sum( repay_capital ), sum( repay_interest ), 0, count(1) 
                    from (SELECT a.repay_amt, a.repay_capital, a.repay_interest, a.loan_no FROM order_repay_file_lh a 
                    WHERE a.repay_result = 'S' AND a.repay_date = '%s' AND a.repay_type = '%s') t LEFT JOIN 
                    order_apply_base_info k on t.loan_no=k.loan_no where k.period='%s';""" \
                             % (c, each_repay_info['repay_no_info'], each_period)

                    cur_order.execute(sql_lh)
                    order_data = cur_order.fetchone()
                    # 累计
                    total_sql_lh = """select sum( repay_amt ), sum( repay_capital ), sum( repay_interest ), count(1) 
                    from (SELECT a.repay_amt, a.repay_capital, a.repay_interest, a.loan_no FROM order_repay_file_lh a 
                    WHERE a.repay_result = 'S' AND a.repay_date <= '%s' AND a.repay_type = '%s') t LEFT JOIN 
                    order_apply_base_info k on t.loan_no=k.loan_no where k.period='%s';""" \
                             % (a, each_repay_info['repay_no_info'], each_period)
                    cur_order.execute(total_sql_lh)
                    total_order_data = cur_order.fetchone()
                # 兰州-信用飞  P0000013
                elif product_code == 'P0000013':
                    sql_sls = """select sum( repay_amt ), sum( repay_capital ), sum( repay_interest ), sum( repay_over_fee ), count(1) 
                                            from ( SELECT repay_amt, repay_capital, repay_interest, repay_over_fee, loan_no FROM order_repay_file_sls
                                             WHERE repay_result = 'S' AND process_date = '%s' AND product_no = '%s' AND repay_type = '%s') 
                                             t LEFT JOIN order_apply_base_info k on t.loan_no=k.loan_no where k.period='%s';""" \
                              % (a, product_code, each_repay_info['repay_no_info'], each_period)
                    cur_order.execute(sql_sls)
                    order_data = cur_order.fetchone()
                    # 累计
                    total_sql_sls = """select sum( repay_amt ), sum( repay_capital ), sum( repay_interest ), count(1) 
                                            from ( SELECT repay_amt, repay_capital, repay_interest, repay_over_fee, loan_no FROM order_repay_file_sls
                                             WHERE repay_result = 'S' AND process_date <= '%s' AND product_no = '%s' AND repay_type = '%s') t 
                                             LEFT JOIN order_apply_base_info k on t.loan_no=k.loan_no where k.period='%s';""" \
                                    % (a, product_code, each_repay_info['repay_no_info'], each_period)
                    cur_order.execute(total_sql_sls)
                    total_order_data = cur_order.fetchone()
                # 江苏银行-洋钱罐   P0000012
                elif product_code == 'P0000012':
                    sql_js = """select sum( repay_amt ), sum( repay_capital ), sum( repay_interest ), sum( repay_over_fee ), count(1) 
                                            from ( SELECT repay_amt, repay_capital, repay_interest, repay_over_fee, loan_no FROM order_repay_file_jsu
                                             WHERE repay_result = 'S' AND process_date = '%s' AND product_no = '%s' AND repay_type = '%s') 
                                             t LEFT JOIN order_apply_base_info k on t.loan_no=k.loan_no where k.period='%s';""" \
                              % (a, product_code, each_repay_info['repay_no_info'], each_period)
                    cur_order.execute(sql_js)
                    order_data = cur_order.fetchone()
                    # 累计
                    total_sql_js = """select sum( repay_amt ), sum( repay_capital ), sum( repay_interest ), count(1) 
                                            from ( SELECT repay_amt, repay_capital, repay_interest, repay_over_fee, loan_no FROM order_repay_file_jsu
                                             WHERE repay_result = 'S' AND process_date <= '%s' AND product_no = '%s' AND repay_type = '%s') t 
                                             LEFT JOIN order_apply_base_info k on t.loan_no=k.loan_no where k.period='%s';""" \
                                    % (a, product_code, each_repay_info['repay_no_info'], each_period)
                    cur_order.execute(total_sql_js)
                    total_order_data = cur_order.fetchone()
                else:
                    # 四平 P0000003:信用飞   P0000004：快牛   P0000005：绿信   P0000006：全民钱包
                    # 长发展 P0000009: 绿信   P0000010: 信用飞  P0000011: 全民钱包

                    # 威海-信用飞 P0000008

                    # ###兰州-信用飞  P0000013
                    order_data = [0.0, 0.0, 0.0, 0.0, 0]
                    # 累计
                    total_order_data = [0.0, 0.0, 0.0, 0]
                if order_data:
                    # 还款
                    repay_amount = order_data[0] if order_data[0] else 0.0
                    repay_principal = order_data[1] if order_data[1] else 0.0
                    repay_interest = order_data[2] if order_data[2] else 0.0
                    repay_type = each_repay_info['repay_type_info']
                    repay_over_fee = order_data[3] if order_data[3] else 0.0
                    repay_number = order_data[4] if order_data[4] else 0
                else:
                    repay_amount = 0.0
                    repay_principal = 0.0
                    repay_interest = 0.0
                    repay_type = each_repay_info['repay_type_info']
                    repay_over_fee = 0.0
                    repay_number = 0

                if total_order_data:
                    total_repay_amount = total_order_data[0] if total_order_data[0] else 0.0
                    total_repay_number = total_order_data[3] if total_order_data[3] else 0
                    total_repay_principal = total_order_data[1] if total_order_data[1] else 0.0
                    total_repay_interest = total_order_data[2] if total_order_data[2] else 0.0
                else:
                    total_repay_amount = 0.0
                    total_repay_number = 0
                    total_repay_principal = 0.0
                    total_repay_interest = 0.0

                repay_order = Debt(date_info=c, bank=(each['product']).split('-')[0],
                                   assets=(each['product']).split('-')[1], product_code=product_code,
                                   product_name=each['product'], repay_type=each_repay_info['repay_no_info'], period=each_period,
                                   repay_number=repay_number, repay_method='0',
                                   repay_amount=repay_amount,
                                   repay_principal=repay_principal, repay_interest=repay_interest,
                                   repay_over_fee=repay_over_fee,
                                   total_repay_number=total_repay_number, total_repay_amount=total_repay_amount,
                                   total_repay_principal=total_repay_principal,
                                   total_repay_interest=total_repay_interest)
                # else:
                #     repay_order = Debt(date_info=c, bank=(each['product']).split('-')[0],
                #                        assets=(each['product']).split('-')[1], product_code=product_code,
                #                        product_name=each['product'], repay_type=each_repay_info['repay_no_info'],
                #                        period=each_period,
                #                        repay_number=0, repay_method='0',
                #                        repay_amount=0.0,
                #                        repay_principal=0.0, repay_interest=0.0,
                #                        repay_over_fee=0.0,
                #                        total_repay_number=0.0, total_repay_amount=0.0,
                #                        total_repay_principal=0.0,
                #                        total_repay_interest=0.0)
                db.session.add(repay_order)

    conn_order.close()
    # conn_ams.close()
    db.session.commit()
    click.echo('Done.')


# 还款线下
@app.cli.command()
def debt_offline():
    """Generate data."""
    db.create_all()

    # conn_order = pymysql.connect(host="rm-uf6355lewwkmn1b59.mysql.rds.aliyuncs.com", port=3306,
    #                              user="u_slkj", password="Slong@2020&", database="order_app")
    #
    # # # 测试环境
    # # conn_order = pymysql.connect(host="192.168.100.227", port=3306,
    # #                              user="u_slong", password="Slkj@2019.", database="order_app")
    #
    # cur_order = conn_order.cursor()
    # # 账务
    # conn_ams = pymysql.connect(host="rm-uf6355lewwkmn1b59.mysql.rds.aliyuncs.com", port=3306,
    #                            user="u_slkj", password="Slong@2020&", database="ams_app")
    #
    # # # 测试环境
    # # conn_ams = pymysql.connect(host="192.168.100.227", port=3306,
    # #                            user="u_slong", password="Slkj@2019.", database="ams_app")
    # cur_ams = conn_ams.cursor()

    # 四平 P0000003:信用飞   P0000004：快牛   P0000005：绿信   P0000006：全民钱包

    # 兰州-信用飞  P0000013

    # 长发展 P0000009: 绿信   P0000010: 信用飞  P0000011: 全民钱包

    # 齐商 P0000007：信用飞   PW0000001：我来贷

    # 蓝海-信用飞  P0000001

    # 齐商 提前结清,其他 提前还款
    repay_info = [{'repay_type_info': '正常还款', 'repay_no_info': '0'},
                  {'repay_type_info': '提前结清', 'repay_no_info': '1'},
                  {'repay_type_info': '当期代偿', 'repay_no_info': '2'},
                  {'repay_type_info': '全额代偿', 'repay_no_info': '3'},
                  {'repay_type_info': '逾期还款', 'repay_no_info': '4'}]

    all_period = ['3', '6', '9', '12']

    for each in product_sls_code:
        for each_repay_info in repay_info:
            for each_period in all_period:
                product_code = each['code']

                repay_amount = 0.0
                repay_principal = 0.0
                repay_interest = 0.0
                repay_type = each_repay_info['repay_type_info']
                repay_over_fee = 0.0
                repay_number = 0

                total_repay_amount = 0.0
                total_repay_number = 0
                total_repay_principal = 0.0
                total_repay_interest = 0.0

                repay_order = Debt(date_info=c, bank=(each['product']).split('-')[0],
                                   assets=(each['product']).split('-')[1], product_code=product_code,
                                   product_name=each['product'], repay_type=each_repay_info['repay_no_info'],
                                   period=each_period,
                                   repay_number=repay_number, repay_method='1', repay_amount=repay_amount,
                                   repay_principal=repay_principal, repay_interest=repay_interest,
                                   repay_over_fee=repay_over_fee,
                                   total_repay_number=total_repay_number, total_repay_amount=total_repay_amount,
                                   total_repay_principal=total_repay_principal,
                                   total_repay_interest=total_repay_interest)
                db.session.add(repay_order)
    # conn_order.close()
    # conn_ams.close()
    db.session.commit()
    click.echo('Done.')


@app.cli.command()
def test():
    """Create user."""
    db.create_all()

    # user = Product.query.all()
    user = Daily.query.filter_by(date_info='2022-01-20').all()
    #user = Daily.query.filter_by(date_info='2021-10-20').all()

    # user = User(username=username, name='矢隆')
    # user.set_password(password)
    # db.session.add(user)

    # db.session.commit()
    # for i in user:
    #     i.date_info = '2021-04-13'
    #     click.echo(i.product_name)

    # user = Sea.query.filter_by(period='12').all()
    for i in user:
        db.session.delete(i)

    # product_chang_code = [{'product': '长发展-绿信', 'code': 'P0000009'}, {'product': '长发展-信用飞', 'code': 'P0000010'},
    #                     {'product': '长发展-全民钱包', 'code': 'P0000011'}]
    #
    # for each in product_chang_code:
    #     daily = Daily(date_info=c, product_name=each['product'], repay_amount=0.0,
    #                   repay_principal=0.0,
    #                   repay_interest=0.0, repay_number=0, advance_settlement=0.0,
    #                   advance_amount=0.0, lend_amount=0.0, lend_number=0.0)
    #
    #     db.session.add(daily)

    # user1 = Sea.query.filter_by(period='9', date_info='2021-05-01').first()
    # db.session.delete(user1)

    db.session.commit()

