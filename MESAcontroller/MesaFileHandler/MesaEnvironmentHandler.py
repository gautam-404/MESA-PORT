import os

from .support import *
from .MesaFileInterface import IMesaInterface

class MesaEnvironmentHandler(IMesaInterface):
    def __init__(self, project):
        IMesaInterface.__init__(self, project)
        self.mesaDir,self.defaultsDir = self.readMesaDirs(mesa_env)
        for section,file in defaultsFileDict.items():
            fileContent = self.readFile(self.defaultsDir+file)
            self.dataDict[section] = self.getParameters(fileContent)


    def readMesaDirs(self, envVar):
        try:
            mesaDir = os.environ[envVar]
        except KeyError:
            raise EnvironmentError("MESA_DIR is not set in your enviroment. Be sure to set it properly!!")
        defaultsDir = mesaDir + defaultsPath

        if not os.path.exists(mesaDir):
            raise FileNotFoundError(f"Mesa dir {mesaDir} does not exist. Be sure that it exists on your machine")

        if not os.path.exists(defaultsDir):
            raise FileNotFoundError(f"Defaults directory {defaultsDir} does not exist.")

        return mesaDir,defaultsDir

    def checkParameter(self, parameter, value=None):
        for section, paramDict in self.dataDict.items():
            if parameter in paramDict.keys():
                if value is None or type(value) == type(paramDict[parameter]):
                    return section, paramDict[parameter]
                else:
                    raise TypeError(
                        f"Type of value for parameter {parameter} is wrong, expected type {str(type(value))}")


        return "",value