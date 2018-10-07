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
        self.services_list = self.config.services_list
        self.watchdog = WatchDog(self.services_list)

        self.reset_after = self.config.restart_after
        self.start_wait = 0.1
        self.stop_wait = 0.1
        self.force_stop_wait = 0.1
        self.time_delay = self.config.time_delay
        self.start_max_attempts = self.config.start_attempts

        self.start_attempt_counter = 0
        log.info('GUARDING {} SERVICE/S: {}'.format(len(self.services_list), self.services_list))


    def start_duty(self):
        counter = 0
        if self.reset_after:
            while True:
                if counter < self.reset_after:
                    self.guard_list()
                    counter += 1
                    self.wait(self.time_delay)

                elif counter >= self.reset_after:
                    self.guard_list(restart=True)
                    counter = 0
                    self.wait(self.time_delay)
        elif not self.reset_after:
            while True:
                    self.guard_list()
                    self.wait(self.time_delay)

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
        if self.start_attempt_counter < self.start_max_attempts:
            self.start_attempt_counter += 1
            log.debug("Attempting to start {} from STOPPED.. {}".format(srvc.name(), self.start_attempt_counter))
            self.watchdog.start_service(srvc)
            self.wait(self.start_wait)
            currentStatus = self.watchdog.check_status(srvc)

            if currentStatus in self.watchdog.hanged:
                log.error("{} did not start as expected on attempt {}.".format(srvc.name(), self.start_attempt_counter))
                self.status_hanged(srvc)
            elif currentStatus in self.watchdog.running:
                log.info("{} DID start as expected on attempt {}.".format(srvc.name(), self.start_attempt_counter))
                self.start_attempt_counter = 0
            elif currentStatus in self.watchdog.stopped:
                log.error("{} did not start as expected on attempt {}.".format(srvc.name(), self.start_attempt_counter))
                self.status_stopped(srvc)
        else:
            subject = 'Service cannot be started'
            msg = 'Service: {} could not be started from {} after {} attempts. Do something about that, will you?'.format(srvc.name(), srvc.status(), self.start_attempt_counter)
            mail = SendMail(self.config.recipient_address, subject, msg, subject, ['config.cfg', 'logs.txt'])
            mail.send_mail()
            self.start_attempt_counter = 0



    def status_hanged(self,srvc):
        log.debug("Attempting to FORCE STOP {} from {}..".format(srvc.name(),srvc.status()))
        if srvc.name == 'KSPLIsozService':
            self.watchdog.kill_isoz_sess()
        self.watchdog.force_stop_service(srvc)
        self.wait(self.force_stop_wait)
        self.guard(srvc)

    def status_paused(self,srvc):
        log.debug("Attempting to resume {} from PAUSED..".format(srvc.name()))
        self.watchdog.resume_service(srvc)
        self.wait(self.start_wait)
        if self.watchdog.check_status(srvc) not in self.watchdog.running:
            log.error("{} did not resume".format(srvc.name()))
            self.status_hanged(srvc)

    def status_running(self,srvc):
        log.debug("Attempting to restart {} on TIMER..".format(srvc.name()))
        if srvc.status() in self.watchdog.running:
            self.watchdog.stop_service(srvc)
            self.wait(self.stop_wait)
            self.guard(srvc)


    def wait(self,waitTime):
        log.debug("Waiting for {} minutes".format(waitTime))

        sleep(waitTime*60)




if __name__ == "__main__":
    inst = Main()
    inst.start_duty()