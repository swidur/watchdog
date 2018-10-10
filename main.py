from classes.sendmail import SendMail
from classes.configreader import ConfigReader
from time import sleep
import logging as log
from classes.watchdog import WatchDog
import psutil


log.basicConfig( format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='/ %d-%m-%Y %H:%M:%S /', level='DEBUG')



class Main:
    # log.info('################################################################')
    # log.info('#################### Guarding services #########################')
    # log.info('################################################################')

    def __init__(self):
        self.config = ConfigReader()
        self.watch_services = self.config.watch_services
        self.restart_services = self.config.restart_services
        self.combined_services = [psutil.win_service_get(x) for x in set(self.watch_services + self.restart_services)]
        self.watchdog = WatchDog()
        self.hard_restart = self.config.hard_restart

        self.restart_after = self.config.restart_after
        self.time_delay = self.config.time_delay

        self.start_wait = 0.1
        self.stop_wait = 0.1
        self.force_stop_wait = 0.1
        self.start_max_attempts = self.config.start_attempts
        self.start_attempt_counter = 0


        log.info('NOW GUARDING: \n'
                 'List of services to watch: {}\n'
                 'List of services to restart every {} minutes: {}\n'
                 'and those of them should be killed on stopping: {}'.format(self.watch_services,
                                                                             self.time_delay, self.restart_services,
                                                                             self.hard_restart))


    def start_duty(self):
        counter = 0
        if self.restart_after:
            while True:
                if counter >= self.restart_after:
                    counter = 0
                    self.iterate_over_service_obj(restart=True)
                    self.wait(self.time_delay)

                else:
                    counter += 1
                    self.iterate_over_service_obj()
                    self.wait(self.time_delay)


        else:
            while True:
                    self.iterate_over_service_obj()
                    self.wait(self.time_delay)


    def iterate_over_service_obj(self, restart=False):
        for service in self.combined_services:
            self.respond_to_status(service, restart=restart)

    def respond_to_status(self, service, restart=False):
        status = self.watchdog.check_status(service)
        if status in self.watchdog.running and restart:
            self.status_running(service)

        elif status in self.watchdog.stopped:
            self.status_stopped(service)

        elif status in self.watchdog.paused:
            self.status_paused(service)

        elif status in self.watchdog.hanged:
            self.status_hanged(service)

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
        self.respond_to_status(srvc)

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
            if srvc.name() in self.hard_restart:
                self.watchdog.force_stop_service(srvc)
                if srvc.name() is 'KSPLIsozService': #yeah, I know.
                    self.watchdog.kill_isoz_sess()
            else:
                self.watchdog.stop_service(srvc)

            self.wait(self.stop_wait)
            self.respond_to_status(srvc)


    def wait(self,waitTime):
        log.debug("Waiting for {} minutes".format(waitTime))
        sleep(waitTime*60)




if __name__ == "__main__":
    inst = Main()
    inst.start_duty()