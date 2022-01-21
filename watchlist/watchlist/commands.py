# -*- coding: utf-8 -*-
import click

from watchlist import app, db
from watchlist.models import User, North, Daily, Sea, Repayment, Fee
import pymysql
import datetime

today_info = datetime.date.today()
yester_info = today_info - datetime.timedelta(days=1)

today_info = str(today_info)
yester_info = str(yester_info)

a = today_info
c = yester_info

#a = '2021-09-25'
#c = '2021-09-24'

lend_date_info = c[:7]

product_sls_code = [{'product': '四平-信用飞', 'code': 'P0000003'}, {'product': '四平-快牛', 'code': 'P0000004'},
                        {'product': '四平-绿信', 'code': 'P0000005'}, {'product': '四平-全民钱包', 'code': 'P0000006'},
                        {'product': '长发展-绿信', 'code': 'P0000009'}, {'product': '长发展-信用飞', 'code': 'P0000010'},
                        {'product': '长发展-全民钱包', 'code': 'P0000011'}, {'product': '蓝海-信用飞', 'code': 'P0000001'},
                        {'product': '威海-信用飞', 'code': 'P0000008'}, {'product': '兰州-信用飞', 'code': 'P0000013'},
                    {'product': '齐商-我来贷', 'code': 'PW0000001'}, {'product': '齐商-信用飞', 'code': 'P0000007'}]
# {'product': '江苏银行-洋钱罐', 'code': 'P0000012'}


@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')


@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create user."""
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)
    else:
        click.echo('Creating user...')
        user = User(username=username, name='矢隆')
        user.set_password(password)
        db.session.add(user)

    db.session.commit()
    click.echo('Done.')


@app.cli.command()
def forge():
    """Generate data."""
    db.create_all()

    conn_ams = pymysql.connect(host="rm-uf6355lewwkmn1b59.mysql.rds.aliyuncs.com", port=3306,
                               user="u_slkj", password="Slong@2020&", database="ams_app")
    cur_ams = conn_ams.cursor()

    conn_order = pymysql.connect(host="rm-uf6355lewwkmn1b59.mysql.rds.aliyuncs.com", port=3306,
                                 user="u_slkj", password="Slong@2020&", database="order_app")
    cur_order = conn_order.cursor()

    # 四平 P0000003:信用飞   P0000004：快牛   P0000005：绿信   P0000006：全民钱包

    # 齐商 P0000007：信用飞   PW0000001：我来贷

    # 蓝海-信用飞  P0000001

    # 7月2号的 提前结清 还款 放款

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
        # 蓝海-信用飞 P0000001
        elif product_code == 'P0000001':
            sql_lh = """SELECT sum(repay_amt), sum(repay_capital), sum(repay_interest), 
                        count(1) FROM order_repay_file_lh WHERE 
                        repay_result = 'S' AND repay_date = '%s';""" % c
            cur_order.execute(sql_lh)
            order_data = cur_order.fetchone()
        # 威海-信用飞
        elif product_code == 'P0000008':
            sql_wh = """SELECT sum(repay_amt), sum(repay_capital), sum(repay_interest), count(1) 
            FROM order_repay_file_wh WHERE repay_result = 'S' AND process_date = '%s';""" % a
            cur_order.execute(sql_wh)
            order_data = cur_order.fetchone()
        else:
            # 四平 P0000003:信用飞   P0000004：快牛   P0000005：绿信   P0000006：全民钱包
            # 兰州-信用飞 P0000013
            # 长发展
            sql_sls = """SELECT sum(repay_amt), sum(repay_capital), sum(repay_interest), count(1) 
            FROM order_repay_file_sls WHERE 
            repay_result = 'S' AND process_date = '%s' AND product_no = '%s';""" % (a, product_code)
            cur_order.execute(sql_sls)
            order_data = cur_order.fetchone()

        if order_data:
            # 还款
            repay_amount = order_data[0] if order_data[0] else 0
            repay_principal = order_data[1] if order_data[1] else 0
            repay_interest = order_data[2] if order_data[2] else 0
            repay_number = order_data[3] if order_data[3] else 0
        else:
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

        daily = Daily(date_info=c, product_name=each['product'], repay_amount=repay_amount, repay_principal=repay_principal,
                      repay_interest=repay_interest, repay_number=repay_number, advance_settlement=advance_settlement,
                      advance_amount=advance_amount, lend_amount=lend_amount, lend_number=lend_number)

        db.session.add(daily)

    conn_ams.close()
    conn_order.close()

    db.session.commit()
    click.echo('Done.')


@app.cli.command()
def sea():
    db.create_all()
    conn = pymysql.connect(host="rm-uf6355lewwkmn1b59.mysql.rds.aliyuncs.com", port=3306,
                               user="u_slkj", password="Slong@2020&", database="order_app")
    cur = conn.cursor()

    # 9期 12期
    for sea_period in ['9', '12']:
        # 前一天的累计放款金额 还款金额
        total_day = str(datetime.datetime.strptime(c, '%Y-%m-%d') - datetime.timedelta(days=1))[:10]
        total_amt = Sea.query.filter_by(date_info=total_day, period=sea_period).first()
        # 放款
        sql = """select * from (SELECT
            date_day,
            period,
            @val := @val + day_amt,
            day_amt,
            con 
        FROM
            (
                (
                SELECT
                    sum( apply_amount ) day_amt,
                    count( 1 ) con,
                    DATE_FORMAT( loanpay_time, '%%Y-%%m-%%d' ) date_day,
                    period 
                FROM
                    order_apply_base_info 
                WHERE
                    apply_status = '1007' 
                    AND product_mapping_code = 'P0000001' 
                    AND period = '%s' 
                GROUP BY
                    DATE_FORMAT( loanpay_time, '%%Y-%%m-%%d' ) 
                ) t,
            ( SELECT @val := 0 ) r 
            )) as st WHERE date_day = '%s';""" % (sea_period, c)

        cur.execute(sql)

        data = cur.fetchone()
        if data:
            # 在贷余额
            lend_amt = data[2] if data[2] else float(total_amt.lend_amt)
            lend_amount = data[3] if data[3] else 0.0
            lend_number = data[4] if data[4] else 0.0
        else:
            # 在贷余额 ?
            lend_amt = float(total_amt.lend_amt)
            lend_amount = 0.0
            lend_number = 0.0

        # 还款
        sql_repay = """select repay_date,period,day_amt,day_cap,inter,day_amt-day_cap-inter, con from 
        ((SELECT  repay_date,
         info.period,
        sum( repay_amt ) day_amt,
         sum( repay_capital ) day_cap,
         sum( repay_interest ) inter,
         count( 1 ) con 
        FROM
         order_apply_base_info info,
         order_repay_file_lh lh 
        WHERE
         info.loan_no = lh.loan_no 
         AND info.period = '%s' 
         AND repay_result = 'S' 
        GROUP BY
         repay_date ) t) WHERE repay_date = '%s';""" % (sea_period, c)

        cur.execute(sql_repay)

        data_repay = cur.fetchone()

        repay_amt = data_repay[2] if data_repay[2] else 0.0
        repay_amount = data_repay[3] if data_repay[3] else 0.0
        repay_interest = data_repay[4] if data_repay[4] else 0.0
        penalty_interest = data_repay[5] if data_repay[5] else 0.0
        repay_number = data_repay[6] if data_repay[6] else 0.0

        bank_data = Sea(date_info=c, product_name='蓝海', period=sea_period, lend_amt=lend_amt,
                        lend_amount=lend_amount, lend_number=lend_number,
                        total_repay_amt=round(float(repay_amount)+total_amt.total_repay_amt, 2),
                        repay_amt=repay_amt, repay_amount=repay_amount, repay_interest=repay_interest,
                        penalty_interest=penalty_interest, repay_number=repay_number)
        db.session.add(bank_data)

    conn.close()

    db.session.commit()
    click.echo('Done.')


@app.cli.command()
def north():
    sls_code = [{'product': '四平-信用飞', 'code': 'P0000003'},
                {'product': '四平-快牛', 'code': 'P0000004'},
                {'product': '四平-绿信', 'code': 'P0000005'},
                {'product': '四平-全民钱包', 'code': 'P0000006'}]
    db.create_all()
    conn_ams = pymysql.connect(host="rm-uf6355lewwkmn1b59.mysql.rds.aliyuncs.com", port=3306,
                               user="u_slkj", password="Slong@2020&", database="ams_app")

    cur_ams = conn_ams.cursor()
    for each in sls_code:
        sql = """SELECT COUNT( 1 ) FROM ams_account_borrow WHERE 
            product_code = '%s' AND repay_status = '6' 
            and update_time like '%s' and is_delete = 0;""" % (each['code'], a + '%')
        cur_ams.execute(sql)
        order_data = cur_ams.fetchone()[0]

        bank_data = North(date_time=c, product_name=each['product'], number=order_data)
        db.session.add(bank_data)

    conn_ams.close()

    db.session.commit()
    click.echo('Done.')


# 还款
@app.cli.command()
def repayment():
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

    # repay_info = [{'repay_type_info': '正常还款', 'repay_no_info': '0'},
    #               {'repay_type_info': '提前结清', 'repay_no_info': '1'},
    #               {'repay_type_info': '当期代偿', 'repay_no_info': '2'},
    #               {'repay_type_info': '全额代偿', 'repay_no_info': '3'}]

    repay_info = [{'repay_type_info': '正常还款', 'repay_no_info': '0'},
                  {'repay_type_info': '当期代偿', 'repay_no_info': '2'},
                  {'repay_type_info': '全额代偿', 'repay_no_info': '3'}]

    for each in product_sls_code:
        for each_repay_info in repay_info:
            product_code = each['code']
            # 还款
            # 齐商 P0000007：信用飞   PW0000001：我来贷
            if product_code == 'PW0000001' or product_code == 'P0000007':
                sql_qis = """SELECT sum(repay_amt), sum(repay_capital), sum(repay_interest), count( 1 )
                FROM order_repay_file_qis WHERE repay_result = 'S' AND process_date = "%s" 
                AND product_no = '%s' AND repay_type='%s';""" \
                          % (a, product_code, each_repay_info['repay_no_info'])
                cur_order.execute(sql_qis)
                order_data = cur_order.fetchone()
                # 累计
                total_sql_qis = """SELECT sum(repay_amt), count( 1 ) FROM order_repay_file_qis 
                WHERE repay_result = 'S' AND product_no = '%s' AND repay_type='%s';""" \
                                % (product_code, each_repay_info['repay_no_info'])
                cur_order.execute(total_sql_qis)
                total_order_data = cur_order.fetchone()
            # 蓝海-信用飞 P0000001
            elif product_code == 'P0000001':
                sql_lh = """SELECT sum( repay_amt ), sum( repay_capital ), sum( repay_interest ), 
                count( 1 ) FROM order_repay_file_lh WHERE repay_result = 'S' AND repay_date = '%s' 
                AND repay_type='%s';""" % (c, each_repay_info['repay_no_info'])
                cur_order.execute(sql_lh)
                order_data = cur_order.fetchone()
                # 累计
                total_sql_lh = """SELECT sum( repay_amt ), count( 1 ) FROM order_repay_file_lh 
                WHERE repay_result = 'S' AND repay_type='%s';""" % (each_repay_info['repay_no_info'])
                cur_order.execute(total_sql_lh)
                total_order_data = cur_order.fetchone()
            # 威海-信用飞
            elif product_code == 'P0000008':
                sql_wh = """SELECT sum( repay_amt ), sum( repay_capital ), sum( repay_interest ), 
                count( 1 ) FROM order_repay_file_wh WHERE repay_result = 'S' AND process_date = '%s' 
                AND product_no = '%s' AND repay_type='%s';""" % (a, product_code, each_repay_info['repay_no_info'])
                cur_order.execute(sql_wh)
                order_data = cur_order.fetchone()
                # 累计
                total_sql_wh = """SELECT sum( repay_amt ), count( 1 ) FROM order_repay_file_wh 
                WHERE repay_result = 'S' AND product_no = '%s' AND repay_type='%s';""" \
                               % (product_code, each_repay_info['repay_no_info'])
                cur_order.execute(total_sql_wh)
                total_order_data = cur_order.fetchone()
            else:
                # 四平 P0000003:信用飞   P0000004：快牛   P0000005：绿信   P0000006：全民钱包
                # 长发展 P0000009: 绿信   P0000010: 信用飞  P0000011: 全民钱包
                # 兰州-信用飞  P0000013
                sql_sls = """SELECT sum( repay_amt ), sum( repay_capital ), sum( repay_interest ), 
                count( 1 ) FROM order_repay_file_sls WHERE repay_result = 'S' AND process_date = '%s' 
                AND product_no = '%s' AND repay_type='%s';""" % (a, product_code, each_repay_info['repay_no_info'])
                cur_order.execute(sql_sls)
                order_data = cur_order.fetchone()
                # 累计
                total_sql_sls = """SELECT sum( repay_amt ), count( 1 ) FROM order_repay_file_sls 
                WHERE repay_result = 'S'  AND product_no = '%s' AND repay_type='%s';""" \
                                % (product_code, each_repay_info['repay_no_info'])
                cur_order.execute(total_sql_sls)
                total_order_data = cur_order.fetchone()
            if order_data:
                # 还款
                repay_amount = order_data[0] if order_data[0] else 0
                repay_principal = order_data[1] if order_data[1] else 0
                repay_interest = order_data[2] if order_data[2] else 0
                repay_type = each_repay_info['repay_type_info']
                repay_number = order_data[3] if order_data[3] else 0
            else:
                repay_amount = 0
                repay_principal = 0
                repay_interest = 0
                repay_type = each_repay_info['repay_type_info']
                repay_number = 0

            if total_order_data:
                total_repay_amount = total_order_data[0] if total_order_data[0] else 0
                total_repay_number = total_order_data[1] if total_order_data[1] else 0
            else:
                total_repay_amount = 0
                total_repay_number = 0

            repay_order = Repayment(date_info=c, bank=(each['product']).split('-')[0],
                                    assets=(each['product']).split('-')[1], product_code=product_code,
                                    product_name=each['product'], repay_type=repay_type, repay_number=repay_number,
                                    repay_amount=repay_amount, repay_principal=repay_principal,
                                    repay_interest=repay_interest, total_repay_amount=total_repay_amount,
                                    total_repay_number=total_repay_number)
            db.session.add(repay_order)

    conn_order.close()
    conn_ams.close()
    db.session.commit()
    click.echo('Done.')


@app.cli.command()
def fee():
    """Generate data."""
    db.create_all()

    conn_ams = pymysql.connect(host="rm-uf6355lewwkmn1b59.mysql.rds.aliyuncs.com", port=3306,
                               user="u_slkj", password="Slong@2020&", database="ams_app")
    cur_ams = conn_ams.cursor()

    period = ['3', '6', '9', '12']

    # 四平 P0000003:信用飞   P0000004：快牛   P0000005：绿信   P0000006：全民钱包

    # 齐商 P0000007：信用飞   PW0000001：我来贷

    # 蓝海-信用飞  P0000001

    for each in product_sls_code:
        product_code = each['code']
        for each_period in period:
            sql_lend = """SELECT sum(lend_amount), count(1) FROM `ams_account_borrow` WHERE 
            product_code = '%s' AND lend_time LIKE '%s' AND repay_period = '%s';""" \
                       % (product_code, lend_date_info + '%', each_period)

            # 放款数据： 当月放款金额 当月放款笔数
            cur_ams.execute(sql_lend)
            lend_data = cur_ams.fetchone()

            if lend_data:
                # 当日放款金额
                lend_amount = lend_data[0] if lend_data[0] else 0
                # 当日放款笔数
                lend_number = lend_data[1] if lend_data[1] else 0
                # 当月服务费
                fee_month = float(lend_amount)*0.036*(int(each_period)+1)/24
            else:
                lend_amount = 0
                lend_number = 0
                fee_month = 0

            sql_lend_total = """SELECT sum(lend_amount), count(1) FROM `ams_account_borrow` WHERE 
                        product_code = '%s' AND repay_period = '%s';""" % (product_code, each_period)
            cur_ams.execute(sql_lend_total)
            lend_data_total = cur_ams.fetchone()
            if lend_data_total:
                # 累计放款金额
                lend_amount_total = lend_data_total[0] if lend_data_total[0] else 0
                # 累计放款笔数
                lend_number_total = lend_data_total[1] if lend_data_total[1] else 0
                # 累计服务费
                fee_total = float(lend_amount_total)*0.036*(int(each_period)+1)/24
            else:
                lend_amount_total = 0
                lend_number_total = 0
                fee_total = 0

            daily = Fee(date_info=c, product_name=each['product'], period=each_period,lend_amount=lend_amount,
                        lend_number=lend_number, fee_month=round(fee_month, 2), lend_amount_total=lend_amount_total,
                        lend_number_total=lend_number_total, fee_total=round(fee_total, 2))

            db.session.add(daily)

    conn_ams.close()

    db.session.commit()
    click.echo('Done.')


@app.cli.command()
def test():
    """Create user."""
    db.create_all()

    # user = Daily.query.order_by(db.desc('repay_principal')).first()

    # user = Daily.query.filter_by(date_info='2021-04-14').all()

    # user = User(username=username, name='矢隆')
    # user.set_password(password)
    # db.session.add(user)

    # db.session.commit()
    # for i in user:
        # i.date_info = '2021-04-13'
        # click.echo(i.product_name)

    user = Daily.query.filter_by(date_info='2021-09-28').all()
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

