from time import sleep
import logging as log
from classes.watchdog import WatchDog


log.basicConfig( format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='/ %d-%m-%Y %H:%M:%S /', level=log.DEBUG)



class Main:
    def __init__(self, listOfservices):
        self.listOfservices = listOfservices
        self.watchdog = WatchDog(self.listOfservices)

        self.startAttemptsMax = 3

        self.startWait = 0.1
        self.stopWait = 0.1
        self.forceStopWait = 0.1

        self.startAttemptsCount = 0


    def start_duty(self, minutes):
        counter = 0
        while True:
            if counter < 3:
                self.guard_list()
                counter += 1
                self.wait(minutes)

            elif counter >= 3:
                self.guard_list(restart=True)
                counter = 0
                self.wait(minutes)



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
        if self.startAttemptsCount <= self.startAttemptsMax:
            log.debug("Attempting to start {} from STOPPED..".format(srvc.name()))
            self.watchdog.start_service(srvc)
            self.wait(self.startWait)
            self.startAttemptsCount += 1

            if self.watchdog.check_status(srvc) not in self.watchdog.running:
                log.error("{} did not start as exptected on attempt {}.".format(srvc.name(), self.startAttemptsCount))
                self.status_hanged(srvc)
            elif self.watchdog.check_status(srvc) in self.watchdog.running:
                log.info("{} did start as exptected on attempt {}.".format(srvc.name(), self.startAttemptsCount))
                self.startAttemptsCount = 0
        else:
            self.startAttemptsCount = 0
            pass


    def status_hanged(self,srvc):
        log.debug("Attempting to FORCE STOP {} from {}..".format(srvc.name(),srvc.status()))
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
        self.watchdog.stop_service(srvc)
        self.wait(self.stopWait)
        self.guard(srvc)

    def wait(self,waitTime):
        log.debug("Waiting for {} minutes".format(waitTime))

        sleep(waitTime*60)




if __name__ == "__main__":
    inst = Main(['KSPLTunelService'])
    inst.start_duty(3)