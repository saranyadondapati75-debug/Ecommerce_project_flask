import smtplib
import smtplib
from email.message import EmailMessage
def send_mail(to,subject,body):
    server=None
    try:
        server=smtplib.SMTP_SSL('smtp.gmail.com',465)#creating object to gmail server using port number
        server.login('saranyadondapati75@gmail.com','zxun lquy xdia obam')
        msg=EmailMessage()
        msg['FORM']='saranyadondapati75@gmail.com'
        msg['TO']=to
        msg['SUBJECT']=subject
        msg.set_content(body)
        server.send_message(msg)
        print('otp sent')
    except Exception as e:
        print('Error in email automation',str(e))
    finally:
        if server:
            server.close()


