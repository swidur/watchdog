import psutil
import subprocess
import logging as log
from sys import exit
from os import getcwd
import ctypes, os


class WatchDog:
    def __init__(self):
        self.check_admin()

        self.hanged = ['start_pending', 'pause_pending', 'continue_pending', 'stop_pending']
        self.paused = ['paused']
        self.stopped = ['stopped']
        self.running = ['running']


    def check_admin(self):
        if ctypes.windll.shell32.IsUserAnAdmin() == 0:
            log.critical('THIS PROGRAM MUST BE RUN WITH ELEVATED PRIVILEGES! EXITING..')
            exit()
        else:
            log.info("Program running in elevated mode, as it should.")


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
            log.debug('# start_service fired.')
            subprocess.run(['sc', 'start', '{}'.format(srvc.name())], timeout=5, check=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
        except subprocess.TimeoutExpired:
            log.warning('Attempt to start {} timedout.'.format(srvc.name()))
        except Exception:
            log.critical('Unhandled exception occured! {}'.format(srvc.name()))

    def stop_service(self,srvc):
        try:
            log.debug('# stop_service fired.')

            subprocess.run(['sc', 'stop', '{}'.format(srvc.name())], check=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        except Exception:
            log.critical('Unhandled exception occured in stop_service! {}. Psst! There are no handled exceptions..'.format(srvc.name()))


    def force_stop_service(self, srvc):
        try:
            log.debug('# force_stop_service fired.')
            subprocess.run(['taskkill', '/f', '/pid', '{}'.format(srvc.pid())], check=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        except Exception:
            log.critical('Unhandled exception occured in force_stop_service! {}. Psst! There are no handled exceptions..'.format(srvc.name()))



    def resume_service(self,srvc):
        try:
            log.debug('# resume_service fired.')
            subprocess.run(['sc', 'continue', '{}'.format(srvc.name())], check=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
        except Exception:
            log.critical('Unhandled exception occured in resume_service! {}. Psst! There are no handled exceptions..'.format(srvc.name()))



    def kill_isoz_sess(self):
        log.info('Kill bat fired.')
        try:
            subprocess.run(['kill.bat'])
        except FileNotFoundError:
            log.exception('kill_isoz_sessions FILE NOT FOUND')