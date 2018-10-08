import psutil
import subprocess
import logging as log
from sys import exit
from os import getcwd


class WatchDog:
    def __init__(self, lst_of_srvcs):
        self.check_admin()
        if type(lst_of_srvcs) is list:
            self.lst_of_srvcs = [psutil.win_service_get(x) for x in lst_of_srvcs]
        elif type(lst_of_srvcs) is str:
            self.lst_of_srvcs = [].append(lst_of_srvcs)

        self.hanged = ['start_pending', 'pause_pending', 'continue_pending', 'stop_pending']
        self.paused = ['paused']
        self.stopped = ['stopped']
        self.running = ['running']

        self.subExcepMsg = 'This needs to be run as an ADMIN. Or some other error occured, I dont know.'

    def check_admin(self):
        try:
            subprocess.run(['openfiles'], check=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            log.critical('THIS PROGRAM MUST BE RUN WITH ELEVATED PRIVILEGES! EXITING..')
            exit()

    def check_status(self,srvc):
        status = srvc.status()

        msg = '{} is {}.'.format(srvc.name(), str(status).upper())
        if status in self.running:
            log.info(msg)
        elif status in self.paused:
            log.warning(msg)
        elif status in self.stopped:
            log.error(msg)
        elif status in self.hanged:
            log.warning(msg)
        else:
            log.error(msg+' STATUS NOT RESOLVED')

        return status


    def start_service(self,srvc):

        try:
            subprocess.run(['sc', 'start', '{}'.format(srvc.name())], timeout=5, check=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
        except subprocess.TimeoutExpired:
            log.warning('Attempt to start {} timedout.'.format(srvc.name()))
        except Exception:
            log.critical('Unhandled exception occured! {}'.format(srvc.name()))

    def stop_service(self,srvc):
        try:
            subprocess.run(['sc', 'stop', '{}'.format(srvc.name())], check=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        except Exception:
            log.exception('Caught some exception while trying to stop service.')


    def force_stop_service(self, srvc):
        exe = srvc.binpath().split('/')[0].split('\\')[-1].strip(' ')
        subprocess.run(['taskkill', '/f', '/pid', '{}'.format(exe)], check=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)



    def resume_service(self,srvc):
        subprocess.run(['sc', 'continue', '{}'.format(srvc.name())], check=True, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)


    def kill_isoz_sess(self):
        subprocess.run(['..\\kill.bat'])
