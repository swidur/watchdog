import psutil
import base64
import logging as log
from classes.sendmail import SendMail
from sys import exit
from classes.configcreator import ConfigCreator


class ConfigReader:
    def __init__(self):
        self.config_files = ConfigCreator()
        self.config_files.create()

        self.location = "config.cfg"
        self.emailLocation = "email.cfg"

        self.watch_services_to_val = []
        self.restart_services_to_val = []
        self.hard_rest_to_val = []
        self.sender_address = ''
        self.sender_plain_pw = ''
        self.recipient_address = ''
        self.time_delay = None
        self.restart_after = None
        self.start_attempts = None
        self.hard_restart = []


        self.def_time_delay = 5
        self.def_restart_after = 3
        self.def_start_attempts = 5

        self.read_services()
        self.read_email()

        self.watch_services = self.validate_services(self.watch_services_to_val)
        self.restart_services = self.validate_services(self.restart_services_to_val)
        self.hard_restart = self.validate_services(self.hard_rest_to_val)
        self.mail_exit_if_no_services()

    def read_services(self):
        with open(self.location,'r') as file:
            for line in file:
                if line.split('=')[0].strip(' ') == 'watchServices':
                    self.watch_services_to_val = line.split('=')[1].strip('\n').strip(' ').split(',')

                elif line.split('=')[0].strip(' ') == 'restartServices':
                    self.restart_services_to_val = line.split('=')[1].strip('\n').strip(' ').split(',')

                elif line.split('=')[0].strip(' ') == 'hardRestart':
                    self.hard_rest_to_val = line.split('=')[1].strip('\n').strip(' ').split(',')

                elif line.split('=')[0].strip(' ') == 'timeDelay':
                    self.time_delay = line.split('=')[1].strip('\n').strip(' ')
                    try:
                        self.time_delay = float(self.time_delay)
                    except ValueError:
                        log.warning('timeDelay value provided in config is not valid ({}), setting to default: {}'.format(self.time_delay, self.def_time_delay))
                        self.time_delay = self.def_time_delay

                elif line.split('=')[0].strip(' ') == 'startAttempts':
                    self.start_attempts = line.split('=')[1].strip('\n').strip(' ')
                    try:
                        self.start_attempts = int(self.start_attempts)
                    except ValueError:
                        log.warning('startAttempts value provided in config is not valid ({}), setting to default: {}'.format(self.start_attempts, self.start_attempts))
                        self.start_attempts = self.def_start_attempts

                elif line.split('=')[0].strip(' ') == 'restartAfterIterations':
                    self.restart_after = line.split('=')[1].strip('\n').strip(' ')
                    try:
                        self.restart_after = int(self.restart_after)
                    except ValueError:
                        log.warning('restartAfter value provided in config is not valid ({}), setting to default: {}'.format(self.restart_after, self.def_restart_after))
                        self.restart_after = self.def_restart_after

    def validate_services(self, to_validate):
        after_validation = []
        for potential in to_validate:
            if potential != '':
                try:
                    psutil.win_service_get(potential)
                    after_validation.append(potential)
                except psutil._exceptions.NoSuchProcess:
                    log.warning('While validating: {}: No such service found: {}, check your spelling in config.'.format(to_validate,potential))

        return after_validation

    def mail_exit_if_no_services(self):
        if (len(self.watch_services)+len(self.restart_services)) == 0:
            msg = 'No valid services. I can''t work like this.\n' \
                  'Here is list of services from config: {}, and {}'. format(self.watch_services_to_val,self.restart_services_to_val)
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


