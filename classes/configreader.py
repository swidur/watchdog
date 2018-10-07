import psutil
import base64
import logging as log
from classes.sendmail import SendMail
from sys import exit
from classes.configcreator import ConfigCreator


class ConfigReader:
    def __init__(self):
        ConfigCreator()

        self.location = "config.cfg"
        self.emailLocation = "email.cfg"
        self.temp_list = []
        self.services_list = []
        self.sender_address = ''
        self.sender_plain_pw = ''
        self.recipient_address = ''
        self.time_delay = None
        self.restart_after = None

        self.def_time_delay = 5
        self.def_restart_after = 3

        self.read_services()
        self.read_email()
        self.validate_services()

    def read_services(self):
        with open(self.location,'r') as file:
            for line in file:

                if line.split('=')[0].strip(' ') == 'servicesList':
                    self.temp_list = line.split('=')[1].strip('\n').strip(' ').split(',')

                elif line.split('=')[0].strip(' ') == 'timeDelay':
                    self.time_delay = line.split('=')[1].strip('\n').strip(' ')
                    try:
                        self.time_delay = float(self.time_delay)
                    except ValueError:
                        log.warning('timeDelay value provided in config is not valid ({}), setting to default: {}'.format(self.time_delay, self.def_time_delay))
                        self.time_delay = self.def_time_delay

                elif line.split('=')[0].strip(' ') == 'restartAfterIterations':
                    self.restart_after = line.split('=')[1].strip('\n').strip(' ')
                    try:
                        self.restart_after = int(self.restart_after)
                    except ValueError:
                        log.warning('restartAfter value provided in config is not valid ({}), setting to default: {}'.format(self.restart_after, self.def_restart_after))
                        self.restart_after = self.def_restart_after


    def validate_services(self):
        for potential in self.temp_list:
            try:
                psutil.win_service_get(potential)
                self.services_list.append(potential)
            except psutil._exceptions.NoSuchProcess:
                log.warning('No such service found: {}, check your spelling in config.'.format(potential))

        if len(self.services_list) == 0:
            msg = 'List of validated services is empty. Nothing to do - aborting.\n' \
                  'Here is list of services from config: {}'. format(self.temp_list)
            subject = 'No valid services to guard!'
            log.critical(msg)
            mail = SendMail(self.recipient_address, subject, msg, subject, ['config.cfg', 'logs.txt'])
            mail.send_mail()
            exit()





    def read_email(self):
        with open(self.emailLocation,'r') as file:
            for line in file:

                if line.split('=')[0].strip(' ') == 'senderAddress':
                    self.sender_address = line.split('=')[1].strip('\n').strip(' ')

                elif line.split('=')[0].strip(' ') == 'recipientAddress':
                    self.recipient_address = line.split('=')[1].strip('\n').strip(' ').split(',')

                elif line.split('=')[0].strip(' ') == 'senderPassword':
                    self.sender_plain_pw = line.split('=')[1].strip('\n').strip(' ')


