"""A set of multiuse functions."""
from PyQt5.QtWidgets import QMessageBox
import os
import ctypes


def getEnv(envPath):
    """Return the .env file as a dictionary."""
    # if(not os.path.isfile('.env')):
    #     with open(envPath, 'w') as env:
    #         env.write('SOURCE=\nDEST=\nEXCEL=')
    #         print('Env created')
    with open(envPath, 'r') as env:
        envvars = env.read().split('\n')
        ENV = {}
        for line in envvars:
            if(len(line) == 0):
                break
            ENV[line.split('=', 1)[0]] = line.split('=', 1)[1]
    return ENV


def updateEnv(newEnv, envPath):
    """Update the env file and return it."""
    with open(envPath, 'w+') as env:
        for key in newEnv:
            env.write(key + '=' + newEnv[key] + '\n')
    return getEnv(envPath)


def throwError(eText):
    """Create an error."""
    alert = QMessageBox()
    alert.setText(eText)
    alert.exec_()


def isAdmin():
    """Check if app is running as admin."""
    try:
        is_admin = (os.getuid() == 0)
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin
