from email.mime.text import MIMEText
from email.utils import formataddr
import smtplib
import pandas as pd

def get_seat_info(seatid):
    df = pd.read_excel('zwu_lib.xlsx', index_col = 0 )
    return dict(df[df['id'] == int(seatid)])

def notice(user, dateinfo, seatid):

    seatinfo = get_seat_info(seatid)

    smtp_sever = 'smtp.office365.com'
    from_addr = 'I92.168.50.1@outlook.com'
    password = '改成你的密码'
    to_addr = '收件邮箱'

    message_text =f'''日期:{dateinfo}\n时间：8:00-21:00\n阅览室{seatinfo['room']}\n座位号{seatinfo['title']}\n座位ID为{seatinfo['id']}\n'''

    msg = MIMEText(f'ZWU图书馆助手提醒您：{user}您已成功预约图书馆阅览室，{message_text}','plain','utf-8')
    msg['From'] = formataddr(('ZWU图书馆助手',from_addr))
    msg['To'] = formataddr(('ZWUbot',to_addr))
    msg['Subject'] = f'ZWU图书馆助手_{user}预约成功通知'


    sever = smtplib.SMTP(smtp_sever,587)
    sever.starttls()
    sever.login(from_addr,password)


    sever.sendmail(from_addr,to_addr,msg.as_string())
    sever.quit()


#notice('2023/9/16','12610')
