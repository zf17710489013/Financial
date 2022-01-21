# -*- coding: utf-8 -*-

from lxml import etree
import requests
from datetime import datetime
import smtplib
import email.mime.multipart
import email.mime.text


def goods(product_ids):
    all_url = []
    for each in product_ids:
        # 商品编号
        url = "https://m.hndfbg.com/goods/detail?goods_id=" + each

        html = requests.get(url).text
        selector = etree.HTML(html)

        # 查看产品是否已经售罄
        is_sold_out = selector.xpath('//*[@id="bar_want_buy"]/a/text()')[-1]

        if is_sold_out == '立即购买':
            all_url.append(url)

    if all_url:
        return str(all_url)


def send_mail(content):
    msg = email.mime.multipart.MIMEMultipart()

    msg['Subject'] = u'cdf会员购---买买买'
    msg['From'] = u'zf979792021@163.com'
    # 接收方
    msg['To'] = '919086038@qq.com'

    txt = email.mime.text.MIMEText(content, 'plain', 'utf-8')
    msg.attach(txt)

    smtp = smtplib.SMTP()
    smtp.connect('smtp.163.com', '25')
    smtp.login('zf979792021@163.com', 'WPXARTCUIUNCWNLY')
    smtp.sendmail('zf979792021@163.com', ['919086038@qq.com'], msg.as_string())
    smtp.quit()


if __name__ == '__main__':
    # 输入产品编号
    is_sold = goods(['01C048642'])
    # 可以购买就发送邮件
    if is_sold:
        send_mail(is_sold)