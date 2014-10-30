import smtplib
import logging

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_Server = 'owamsq.epam.com'
SMTP_Login = 'dzmitry_rozberh@epam.com'
SMTP_Password = 'RD1802fe$$$'


def Send_Email(before,tbl,after):
    msg = MIMEMultipart('alternative')
    msg['To'] = 'To Me <dzmitry_rozberh@epam.com>'
    msg['From'] = 'From Me <dzmitry_rozberh@epam.com>'
    msg['Subject'] = 'Auto Report'
    ToList = ['dzmitry_rozberh@epam.com']
    table = '<table frame="border" rules="all" border="1">'
    for row in tbl:
        table+='<tr>'
        for col in row:
            table+='<td>'
            table+=str(col)
            table+='</td>'
        table +='</tr>'
    table+='</table>'

    html = """\
                <html>
                  <head></head>
                  <body>
                    <a><b>%s</b></a>
                    %s
                  </body>
                </html>
                """         % (before,table)
    msg.attach(MIMEText(html, 'html'))
    try:
        logging.info( u'Send notification message')
        logging.debug(str(msg.as_string()) )
        s = smtplib.SMTP(SMTP_Server)
        s.login(SMTP_Login, SMTP_Password)
        s.sendmail('dzmitry_rozberh@epam.com',ToList,msg.as_string())
        s.quit()
        logging.info( u'Send notification message...Completed')
    except Exception as e:
        logging.info( u'Send notification message...Failed: ' + str(e.args))