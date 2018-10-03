import psutil
import os
import signal
import logging as log


tunel = ['KSPLTunelService', 'WarpJITSvc']


log.basicConfig( format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='/ %d-%m-%Y %H:%M:%S /', level=log.DEBUG)



class WatchDog:
    def __init__(self, lst_of_srvcs, wait_time):
        self.lst_of_srvcs = [psutil.win_service_get(x) for x in lst_of_srvcs]
        self.wait_time = wait_time
        self.hanged = ['start_pending', 'pause_pending', 'continue_pending', 'stop_pending']
        self.paused = ['paused']
        self.stopped = ['stopped']
        self.running = ['running']

    def check_status(self,srvc,comment=''):
        srvc = psutil.win_service_get(srvc)
        status = srvc.status()

        msg = '{} is {}.'.format(srvc.name(),str(status).upper())
        if status in self.running:
            log.info(comment+msg)
        elif status in self.paused:
            log.warning(msg)
        elif status in self.stopped:
            log.error(msg)
        elif status in self.hanged:
            log.error(msg)
        else:
            log.error(msg+' STATUS NOT RESOLVED IN DECISION TREE')

        return status


    def start_service(self,srvc):
        os.system('sc start {}'.format(srvc.name()))

    def stop_service(self,srvc):
        os.system('sc stop {}'.format(srvc.name()))

    def force_stop_service(self, srvc):
        os.system(' taskkill /f /pid {}'.format(srvc.pid()))


new = WatchDog(tunel,60)

print(new.check_status('KSPLTunelService'))
new.stop_service(psutil.win_service_get('KSPLTunelService'))