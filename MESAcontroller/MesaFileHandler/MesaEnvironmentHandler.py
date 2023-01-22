import os

from .support import *

class MesaEnvironmentHandler():
    def __init__(self, project, binary, star, mesa_env="MESA_DIR"):
        if binary and star == 'binary':
            self.sections, self.defaultsPath = sections_binary, defaultsPath_binary
        else:
            self.sections, self.defaultsPath = sections_star, defaultsPath_star
        self.mesaDir, self.defaultsDir = self.readMesaDirs(mesa_env)

    def readMesaDirs(self, envVar):
        try:
            mesaDir = os.environ[envVar]
        except KeyError:
            raise EnvironmentError("MESA_DIR is not set in your enviroment. Be sure to set it properly!!")
        defaultsDir = mesaDir + self.defaultsPath

        if not os.path.exists(mesaDir):
            raise FileNotFoundError(f"Mesa dir {mesaDir} does not exist. Be sure that it exists on your machine")

        if not os.path.exists(defaultsDir):
            raise FileNotFoundError(f"Defaults directory {defaultsDir} does not exist.")
        return mesaDir, defaultsDir
