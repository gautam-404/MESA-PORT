from MESAcommando.MesaFileHandler import MesaFileAccess
from MESAcommando.MesaFileHandler.support import *

from collections import OrderedDict

class MesaAccess:
    def __init__(self):
        self.mesaFileAccess = MesaFileAccess()

        self._fullDict = self.stripFullDict()

    def stripToDict(self, section):
        retDict = OrderedDict()
        for file, parameterDict in self.mesaFileAccess.dataDict[section].items():
            for key, value in parameterDict.items():
                retDict[key] = value

        return retDict

    def stripFullDict(self):
        retDict = OrderedDict()

        for section in [sectionStarJob,sectionControl,sectionPgStar]:
            retDict.update(self.stripToDict(section))

        return retDict

    def items(self):
        return self._fullDict.items()

    def keys(self):
        return self._fullDict.keys()

    def setitem(self, key, value):
        if key in self._fullDict.keys():
            self.mesaFileAccess[key] = value
        else:
            self.mesaFileAccess.addValue(key,value)
        self._fullDict = self.stripFullDict()


    def set(self, keys, values):
        if type(keys) == list:
            if len(keys) == len(values):
                for i in range(len(keys)):
                    self.setitem(keys[i], values[i])
            else:
                raise ValueError(f"Length of keys {keys} does not match length of {values}")
        elif type(keys) == str:
            self.setitem(keys, values)
        else:
            raise TypeError("Input parameter name(s) must be of type string or list of strings.")

    def get(self, items):
        if type(items) == list:
            got = []
            for item in items:
                got.append(self._fullDict[item])
            return got
        elif type(items) == str:
            return self._fullDict[items]
        else:
            raise TypeError("Input parameter name(s) must be of type string or list of strings.")
        

    
    def delete(self, keys):
        if type(keys) == list:
            for key in keys:
                if key in self._fullDict.keys():
                    self.mesaFileAccess.removeValue(key)
        elif type(keys) == str:
            if keys in self._fullDict.keys():
                    self.mesaFileAccess.removeValue(keys)
        else:
            raise TypeError("Input parameter name(s) must be of type string or list of strings.")
