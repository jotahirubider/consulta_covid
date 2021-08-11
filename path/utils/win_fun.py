import os
from subprocess import check_output



class TaskKill:
    def firefox(self):
        """Kills from Windows CMD Firefox and Geckodriver Process"""
        if "firefox.exe" in str(check_output("tasklist")):
            os.system('cmd /c "cd C:/ & taskkill /IM "firefox.exe" /F"')
    def geckodriver(self):
        if "geckodriver.exe" in str(check_output("tasklist")):
            os.system('cmd /c "cd C:/ & taskkill /IM "geckodriver.exe" /F"')
    def ie(self):
        """Kills from Windows CMD IE and IEDriver Process"""
        if "iexplore.exe" in str(check_output("tasklist")):
            os.system('cmd /c "cd C:/ & taskkill /IM "iexplore.exe" /F"')
    def iedriver(self):
        if "IEDriverServer.exe" in str(check_output("tasklist")):
            os.system('cmd /c "cd C:/ & taskkill /IM "IEDriverServer.exe" /F"')

