import time

import pymysql
from lxml import etree
import requests
import json
import sqlite3
from report import app, db
import datetime
import asyncio
from report.models import Daily, OldDaily

# 浏览器窗口很大，内容显示很小
# # Pyppeteer 支持字典 和 关键字传参，Puppeteer 只支持字典传参。
# # 这里使用字典传参
# browser = await launch(
#     {
#         'headless': False,
#         'dumpio': True,
#         'autoClose': False,
#         'args': [
#             '--no-sandbox',
#             '--window-size=1366,850'
#         ]
#     }
# )
# await page.setViewport({'width': 1366, 'height': 768})


# async def main():
#     browser = await launch({'headless': False})
#     # browser = await launch()
#     page = await browser.newPage()
#     await page.goto('http://www.baidu.com')
#     await page.screenshot({'path': 'example.png'})
#     await browser.close()
#
#
# asyncio.get_event_loop().run_until_complete(main())

# html = requests.post('http://192.168.100.34:5000/report/daily/',
#                      data=json.dumps({'productMappingCode': []})).text
#
# # html = requests.post('http://192.168.100.254:5000/report/market/').text
# print(html)

# x = '2021-05-15'
# y = '2021-05-16'
# conn_product = sqlite3.connect(app.config['SQLALCHEMY_DATABASE'])
# sql = """SELECT a.*, b.* FROM `product` AS a
#                 INNER JOIN `daily` AS b ON a.product_mapping_code = b.product_mapping_code
#                 where a.product_mapping_code = 'P0000007' and b.date_info
#                 >= DATE('%s') order by date_info desc;""" % x
#
# cur_product = conn_product.cursor()
# cur_product.execute(sql)
# product_data = cur_product.fetchall()
# conn_product.close()
# for i in product_data:
#     print(i)

# conn_product = sqlite3.connect(app.config['SQLALCHEMY_DATABASE'])
# sql = """SELECT * FROM `repayment` limit 10;"""
#
# cur_product = conn_product.cursor()
# cur_product.execute(sql)
# product_data = cur_product.fetchall()
# conn_product.close()
# for i in product_data:
#     print(i)

# product_mapping_code_list_qs = ['P0000007']
# sql_qs = """SELECT sum( repay_amt ) FROM
#         (
#         SELECT
#             repay_amt
#         FROM
#             order_repay_file_qis
#         WHERE
#             repay_result = 'S'
#             AND (process_date BETWEEN '%s' and '%s') AND product_no IN ('%s') UNION ALL
#         SELECT
#             pre_repay_principal + pre_repay_interest
#         FROM
#             order_repay_apply
#         WHERE
#             product_mapping_code IN ('%s')
#         AND (create_time BETWEEN '%s' AND '%s')
#         ) t;""" % ('2021-05-21', '2021-05-21', "','".join(product_mapping_code_list_qs),
#                    "','".join(product_mapping_code_list_qs), '2021-05-21', '2021-05-21' + ' 23:59:59')
#
# print(sql_qs)

# P0000004
# data = {'pageNum': 1, 'pageSize': 33, 'productCode': 'P0000004'}
# url = 'http://ams.slong-tech.com/ams-app/amsBizProcessInfo/listPage'
# html = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(data)).text
# html = json.loads(html)
# for i in html['data']['items']:
#     print(i['dayRepayBalance'])


# """SELECT
# 	COUNT(1), SUM(apply_amount)
# FROM
# 	order_apply_base_info
# WHERE
# 	id_no in (SELECT DISTINCT id_no FROM customer_app.customer_info where age >=50)
# 	and is_delete = 0
# 	AND apply_status = '1007'
# 	AND ( loanpay_time BETWEEN '2018-01-01' AND '2021-07-31 23:59:59' );"""
#
#
# """SELECT
# CASE
# 	(121 - SUBSTR ( id_no, 9, 2 ))
# 		WHEN 1 THEN
# 		'男'
# 		ELSE '女'
# 	END AS sex,
# 	count( 1 ), sum(apply_amount) AS rank
# FROM
# 	`order_apply_base_info`
# WHERE
# 	is_delete = 0
# 	AND apply_status = '1007'
# 	AND ( loanpay_time BETWEEN '2018-01-01' AND '2021-07-31 23:59:59' )
# GROUP BY
# 	sex
# ORDER BY
# 	rank DESC;"""
#
#
# """SELECT
# 	COUNT( 1 ),
# 	SUM( apply_amount )
# FROM
# 	order_apply_base_info a
# 	LEFT JOIN ( SELECT * FROM customer_app.customer_info WHERE is_delete = 0 GROUP BY customer_app.customer_info.id_no ) AS b ON a.id_no = b.id_no
# WHERE
# 	a.is_delete = 0
# 	AND b.age >= 20
# 	AND b.age < 25
# 	AND a.apply_status = '1007'
# 	AND ( a.loanpay_time BETWEEN '2018-01-01' AND '2021-07-31 23:59:59' );"""
#
#
# """
# """


product_sls_code = [{'product': '四平-信用飞', 'code': 'P0000003'}, {'product': '四平-快牛', 'code': 'P0000004'},
                        {'product': '四平-绿信', 'code': 'P0000005'}, {'product': '四平-全民钱包', 'code': 'P0000006'},
                        {'product': '长发展-绿信', 'code': 'P0000009'}, {'product': '长发展-信用飞', 'code': 'P0000010'},
                        {'product': '长发展-全民钱包', 'code': 'P0000011'}, {'product': '齐商-信用飞', 'code': 'P0000007'},
                    {'product': '齐商-我来贷', 'code': 'PW0000001'}, {'product': '蓝海-信用飞', 'code': 'P0000001'},
                    {'product': '威海-信用飞', 'code': 'P0000008'}]


def old_forge(a, c):
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

    # 四平 P0000003:信用飞   P0000004：快牛   P0000005：绿信   P0000006：全民钱包

    # 长发展 P0000009: 绿信   P0000010: 信用飞  P0000011: 全民钱包

    # 齐商 P0000007：信用飞   PW0000001：我来贷

    # 蓝海-信用飞  P0000001

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
            cur_ams.execute("SELECT sum(total_capital_left) from ams_account_borrow "
                            "WHERE product_code ='%s';" % product_code)
            balance_data = cur_ams.fetchone()
        # 蓝海-信用飞 P0000001
        elif product_code == 'P0000001':
            sql_lh = """SELECT sum(repay_amt), sum(repay_capital), sum(repay_interest), 
            count(1) FROM order_repay_file_lh WHERE 
            repay_result = 'S' AND repay_date = '%s';""" % c
            cur_order.execute(sql_lh)
            order_data = cur_order.fetchone()
            # 贷余
            cur_ams.execute("SELECT sum(total_capital_left) from ams_account_borrow "
                            "WHERE product_code ='%s';" % product_code)
            balance_data = cur_ams.fetchone()
        # 威海-信用飞
        elif product_code == 'P0000008':
            sql_wh = """SELECT sum(repay_amt) FROM order_repay_file_wh WHERE 
                    repay_result = 'S' AND process_date = '%s';""" % a
            cur_order.execute(sql_wh)
            order_data = cur_order.fetchone()
            # 贷余
            cur_ams.execute("SELECT sum(total_capital_left) from ams_account_borrow "
                            "WHERE product_code ='%s';" % product_code)
            balance_data = cur_ams.fetchone()
        else:
            # 四平 P0000003:信用飞   P0000004：快牛   P0000005：绿信   P0000006：全民钱包
            # 长发展
            sql_sls = """SELECT sum(repay_amt), sum(repay_capital), sum(repay_interest), count(1) 
            FROM order_repay_file_sls WHERE 
            repay_result = 'S' AND process_date = '%s' AND product_no = '%s';""" % (a, product_code)
            cur_order.execute(sql_sls)
            order_data = cur_order.fetchone()
            # 贷余
            cur_ams.execute("SELECT sum(total_capital_left) from ams_account_borrow "
                            "WHERE product_code ='%s';" % product_code)
            balance_data = cur_ams.fetchone()
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

        if balance_data:
            balance = balance_data[0] if balance_data[0] else 0
        else:
            balance = 0
        daily = OldDaily(date_info=datetime.datetime.strptime(c, '%Y-%m-%d'), product_mapping_code=product_code,
                         repay_amount=repay_amount, repay_principal=repay_principal, repay_interest=repay_interest,
                         repay_number=repay_number, advance_settlement=advance_settlement, advance_amount=advance_amount,
                         lend_amount=lend_amount, lend_number=lend_number, total_loan_balance=balance)

        db.session.add(daily)

    conn_ams.close()
    conn_order.close()

    db.session.commit()


def forge1(a, c):
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

    # 四平 P0000003:信用飞   P0000004：快牛   P0000005：绿信   P0000006：全民钱包

    # 长发展 P0000009: 绿信   P0000010: 信用飞  P0000011: 全民钱包

    # 齐商 P0000007：信用飞   PW0000001：我来贷

    # 蓝海-信用飞  P0000001

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
                cur_ams.execute("SELECT sum(total_capital_left) from ams_account_borrow "
                                "WHERE product_code ='%s';" % product_code)
                balance_data = cur_ams.fetchone()
            # 蓝海-信用飞 P0000001
            elif product_code == 'P0000001':
                sql_lh = """SELECT SUM( repay_capital )+ sum( repay_interest ), 
                SUM( repay_capital ), sum( repay_interest ) , COUNT(1), period FROM ams_repay_fee 
                WHERE product_no = 'P0000001' AND is_delete = '0' AND actual_date = '%s' AND period='%s';""" \
                         % (c, each_period)
                cur_ams.execute(sql_lh)
                order_data = cur_ams.fetchone()
                # 贷余
                cur_ams.execute("SELECT sum(total_capital_left) from ams_account_borrow "
                                "WHERE product_code ='%s';" % product_code)
                balance_data = cur_ams.fetchone()
            # 威海-信用飞
            elif product_code == 'P0000008':
                sql_wh = """SELECT sum(a.repay_amt), sum(a.repay_capital), sum(a.repay_interest), count(1), b.period 
                FROM order_repay_file_wh a LEFT JOIN order_apply_base_info b ON a.loan_no=b.loan_no WHERE 
                a.repay_result = 'S' AND a.process_date = '%s' AND a.product_no = '%s' AND b.period='%s';""" \
                         % (a, product_code, each_period)
                cur_order.execute(sql_wh)
                order_data = cur_order.fetchone()
                # 贷余
                cur_ams.execute("SELECT sum(total_capital_left) from ams_account_borrow "
                                "WHERE product_code ='%s';" % product_code)
                balance_data = cur_ams.fetchone()
            else:
                # 四平 P0000003:信用飞   P0000004：快牛   P0000005：绿信   P0000006：全民钱包
                # 长发展
                sql_sls = """SELECT sum(a.repay_amt), sum(a.repay_capital), sum(a.repay_interest), count(1), b.period 
                FROM order_repay_file_sls a LEFT JOIN order_apply_base_info b ON a.loan_no=b.loan_no WHERE 
                a.repay_result = 'S' AND a.process_date = '%s' AND a.product_no = '%s' AND b.period='%s';""" \
                          % (a, product_code, each_period)
                cur_order.execute(sql_sls)
                order_data = cur_order.fetchone()
                # 贷余
                cur_ams.execute("SELECT sum(total_capital_left) from ams_account_borrow "
                                "WHERE product_code ='%s';" % product_code)
                balance_data = cur_ams.fetchone()
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

            daily = Daily(date_info=datetime.datetime.strptime(c, '%Y-%m-%d'), product_mapping_code=product_code,
                          repay_amount=repay_amount, repay_principal=repay_principal, repay_interest=repay_interest,
                          repay_number=repay_number, advance_settlement=advance_settlement,
                          advance_amount=advance_amount, lend_amount=lend_amount, lend_number=lend_number,
                          period=each_period, total_loan_balance=balance_data[0])

            db.session.add(daily)

    conn_ams.close()
    conn_order.close()

    db.session.commit()


l = [('2021-07-12', '2021-07-11'), ('2021-07-11', '2021-07-10'),
     ('2021-07-10', '2021-07-09'), ('2021-07-09', '2021-07-08'), ('2021-07-08', '2021-07-07'),
     ('2021-07-07', '2021-07-06'), ('2021-07-06', '2021-07-05'), ('2021-07-05', '2021-07-04'),
     ('2021-07-04', '2021-07-03'), ('2021-07-03', '2021-07-02'), ('2021-07-02', '2021-07-01')]

for i in l:
    old_forge(i[0], i[1])
    forge1(i[0], i[1])