from classes.sendmail import SendMail
from classes.configreader import ConfigReader
from time import sleep
import logging as log
from classes.watchdog import WatchDog



log.basicConfig(filename='logs.txt', format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='/ %d-%m-%Y %H:%M:%S /', level='DEBUG')



class Main:
    log.info('################################################################')
    log.info('#################### Guarding services #########################')
    log.info('################################################################')

    def __init__(self):
        self.config = ConfigReader()
        self.listOfservices = self.config.services_list
        self.watchdog = WatchDog(self.listOfservices)

        self.startAttemptsMax = 3
        self.resetAfter = self.config.restart_after
        self.startWait = 0.1
        self.stopWait = 0.1
        self.forceStopWait = 0.1
        self.timeDelay = self.config.time_delay

        self.startAttemptsCount = 0
        log.info('GUARDING {} SERVICE/S: {}'.format(len(self.listOfservices),self.listOfservices))


    def start_duty(self):
        counter = 0
        while True:
            if counter < self.resetAfter:
                self.guard_list()
                counter += 1
                self.wait(self.timeDelay)

            elif counter >= self.resetAfter:
                self.guard_list(restart=True)
                counter = 0
                self.wait(self.timeDelay)


    def guard(self, service, restart=False):
        status = self.watchdog.check_status(service)
        if status in self.watchdog.running and restart:
            self.status_running(service)

        elif status in self.watchdog.stopped:
            self.status_stopped(service)

        elif status in self.watchdog.paused:
            self.status_paused(service)

        elif status in self.watchdog.hanged:
            self.status_hanged(service)


    def guard_list(self, restart=False):
        for service in self.watchdog.lst_of_srvcs:
            self.guard(service,restart=restart)


    def status_stopped(self, srvc):
        if self.startAttemptsCount < self.startAttemptsMax:
            log.debug("Attempting to start {} from STOPPED..".format(srvc.name()))
            self.watchdog.start_service(srvc)
            self.wait(self.startWait)
            self.startAttemptsCount += 1
            currentStatus = self.watchdog.check_status(srvc)

            if currentStatus not in self.watchdog.running:
                log.error("{} did not start as exptected on attempt {}.".format(srvc.name(), self.startAttemptsCount))
                self.status_hanged(srvc)
            elif currentStatus in self.watchdog.running:
                log.info("{} did start as exptected on attempt {}.".format(srvc.name(), self.startAttemptsCount))
                self.startAttemptsCount = 0
        else:
            subject = 'Service cannot be started'
            msg = 'Service: {} could not be started from {} after {} attempts. Do something, will you?'.format(srvc.name(), srvc.status(), self.startAttemptsCount)
            mail = SendMail(self.config.recipient_address, subject, msg, subject, ['config.cfg', 'logs.txt'])
            mail.send_mail()
            self.startAttemptsCount = 0



    def status_hanged(self,srvc):
        log.debug("Attempting to FORCE STOP {} from {}..".format(srvc.name(),srvc.status()))
        if srvc.name == 'KSPLIsozService':
            self.watchdog.kill_isoz_sess()
        self.watchdog.force_stop_service(srvc)
        self.wait(self.forceStopWait)
        self.guard(srvc)

    def status_paused(self,srvc):
        log.debug("Attempting to resume {} from PAUSED..".format(srvc.name()))
        self.watchdog.resume_service(srvc)
        self.wait(self.startWait)
        if self.watchdog.check_status(srvc) not in self.watchdog.running:
            log.error("{} did not resume".format(srvc.name()))
            self.status_hanged(srvc)

    def status_running(self,srvc):
        log.debug("Attempting to restart {} on TIMER..".format(srvc.name()))
        if srvc.name() == 'KSPLIsozService':
            self.watchdog.force_stop_service(srvc)
            self.watchdog.kill_isoz_sess()
        else:
            self.watchdog.stop_service(srvc)
        self.wait(self.stopWait)
        self.guard(srvc)

    def wait(self,waitTime):
        log.debug("Waiting for {} minutes".format(waitTime))

        sleep(waitTime*60)




if __name__ == "__main__":
    inst = Main()
    inst.start_duty()