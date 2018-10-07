import logging as log


class ConfigCreator:
    def __init__(self):

        self.main_config_body = 'servicesList=\n' \
                           'timeDelay=\n' \
                           'restartAfterIterations=\n'
        self.email_config_body =  'senderAddress=sender@address.com\n' \
                           'senderPassword=somepassword\n' \
                           'recipientAddress=fake@mail.com'

        self.sql_body = "ALTER TRIGGER GABINET.T_KSPL$SESSIONS_KILLED DISABLE;\n" \
                        "DELETE FROM GABINET.KSPL$SESSIONS WHERE APPNAME='KSPL_ISOZ';\n" \
                        "ALTER TRIGGER GABINET.T_KSPL$SESSIONS_KILLED ENABLE;\n" \
                        "exit;"

        self.bat_body = 'sqlplus "/as sysdba" @..\killsessions.sql'


        self.configs = [('email.cfg',self.email_config_body),('config.cfg',self.main_config_body),
                        ('killsessions.sql', self.sql_body), ('kill.bat', self.bat_body)]

        self.run()

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

    def run(self):
        for cfg in self.configs:
            if not self.exists(cfg[0]):
                self.write_config(cfg[0],cfg[1])
                log.info('File {} not found. So I made one.'.format(cfg[0]))

