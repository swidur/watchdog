from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders
import smtplib
import os
import logging as log


class SendMail:
    def __init__(self, msg_to, subject, msg_body, cause, files=[], msg_from='watchdogforpython0099@gmail.com'):
        self.msg_from = msg_from
        self.msg_to = msg_to
        self.subject = subject
        self.msg_body = msg_body
        self.cause = cause
        self.files = files

        self.attached = 0

        assert type(self.files) == list

        self.clause = '\n \n This mail was sent to you because someone entered your email address in config file of WatchDog app' \
                      '\n There isn''t much you can do, except maybe blacklist this addres and contact developer at dawid(at)swidurski.pl'

    def send_mail(self):
        log.info('Attempting to send mail to: {}, because: {}. Attaching {} file/s.'.format(self.msg_to, self.cause, len(self.files)))

        msg = MIMEMultipart()
        msg['From'] = self.msg_from
        msg['To'] = COMMASPACE.join(self.msg_to)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = self.subject

        self.msg_body = (self.msg_body+self.clause).encode("utf-8")
        self.msg_body = MIMEText(self.msg_body, 'plain', "utf-8")

        msg.attach(self.msg_body)

        for file in self.files:
            try:
                part = MIMEBase('application', "octet-stream")
                part.set_payload(open(file,"rb").read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename="%s"'
                               % os.path.basename(file))
                msg.attach(part)
                self.attached += 1

            except FileNotFoundError:
                log.exception('SENDMAIL: Exception occured while attaching file {}'.format(file))


        smtp = smtplib.SMTP('smtp.gmail.com', 587, 'watchdogforpython001', timeout=60)
        smtp.starttls()
        smtp.login('watchdogforpython001',"Wach01This0Dog?")

        if self.attached != len(self.files):
            log.warning(' {} out of {} files attached. There should be exception for that somewhere earlier.'.format(self.attached,len(self.files)))

        errors = len(smtp.sendmail(self.msg_from, self.msg_to, msg.as_string()))
        log.info('Email send to {} out of {} recipients. Hopefully someone will read it. BTW, it doesnt mean it was '
                 'delivered..'.format((len(self.msg_to)-errors),len(self.msg_to)))

        smtp.close()
