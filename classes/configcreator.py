import logging as log


class ConfigCreator:
    def __init__(self):

        self.main_config_body = '#serviceList= comma separated list of services to guard\n' \
                                '#hardRestart= comma separated list of services that need to be FORCED shut instead of ending gracefully\n' \
                                '#timeDelay= time [minutes] between checking up on service\n' \
                                '#restartAfterIterations= number of iterations before restarting service anyway (for those that just pretend to be working)\n' \
                                '#startAttempts= number of attempts on starting service before sending email\n' \
                                '#\n' \
                                'watchServices=\n' \
                                'restartServices=\n' \
                                'hardRestart=\n' \
                                'timeDelay=\n' \
                                'restartAfterIterations=\n' \
                                'startAttempts=\n'
        self.email_config_body =  'senderAddress=sender@address.com\n' \
                           'senderPassword=somepassword\n' \
                           'recipientAddress=fake@mail.com'

        #
        self.sql_body = "ALTER TRIGGER GABINET.T_KSPL$SESSIONS_KILLED DISABLE;\n" \
                        "DELETE FROM GABINET.KSPL$SESSIONS WHERE APPNAME='KSPL_ISOZ';\n" \
                        "ALTER TRIGGER GABINET.T_KSPL$SESSIONS_KILLED ENABLE;\n" \
                        "exit;"

        self.bat_body = 'sqlplus "/as sysdba" @..\killsessions.sql'


        self.configs = [('email.cfg',self.email_config_body),('config.cfg',self.main_config_body),
                        ('killsessions.sql', self.sql_body), ('kill.bat', self.bat_body)]


    def exists(self, path):
        try:
            file = open(path, 'r')
            file.close()
        except FileNotFoundError:
            return False
        return True


    def write_config(self, path, file_body):
        with open(path, 'w') as file:
            file.write(file_body)

    def create(self):
        for cfg in self.configs:
            if not self.exists(cfg[0]):
                self.write_config(cfg[0],cfg[1])
                log.info('File {} not found. So I made one.'.format(cfg[0]))

