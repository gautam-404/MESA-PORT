import os
import shutil
import glob

from .support import *

class MesaEnvironmentHandler():
    def __init__(self, astero=False, binary=False, target='', mesa_env="MESA_DIR"):
        if binary and target == 'binary':
            self.defaultsPath = "binary/defaults/"
        elif astero:
            self.defaultsPath = "astero/defaults/"
        else:
            self.defaultsPath = "star/defaults/"
        self.mesaDir = self.readMesaDirs(mesa_env)
        self.defaultsDir = os.path.join(self.mesaDir, self.defaultsPath)
        if not os.path.exists(self.defaultsDir):
            raise FileNotFoundError(f"Defaults directory {self.defaultsDir} does not exist.")
        if astero:
            for filename in glob.glob(os.path.join(self.mesaDir, "star/defaults","*.defaults")):
                shutil.copy(filename, self.defaultsDir)

    def readMesaDirs(self, envVar):
        try:
            mesaDir = os.environ[envVar]
        except KeyError:
            raise EnvironmentError("MESA_DIR is not set in your enviroment. Be sure to set it properly!!")

        if not os.path.exists(mesaDir):
            raise FileNotFoundError(f"Mesa dir {mesaDir} does not exist. Be sure that it exists on your machine")
        return mesaDir
