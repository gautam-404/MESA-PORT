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

    def __getitem__(self, item):
        return self._fullDict[item]

    def __setitem__(self, key, value):
        if key in self._fullDict.keys():
            self.mesaFileAccess[key] = value
        else:
            self.mesaFileAccess.addValue(key,value)
        self._fullDict = self.stripFullDict()

    def delitem(self, key):
        if key in self._fullDict.keys():
            self.mesaFileAccess.removeValue(key)


    def set_various(self, keys, values):
        if len(keys) == len(values):
            for i in range(len(keys)):
                self.__setitem__(keys[i], values[i])
        else:
            raise ValueError(f"Length of keys {keys} does not match length of {values}")

    def get_various(self, items):
        got = []
        for item in items:
            got.append(self._fullDict[item])
        return got
    
    def del_various(self, keys):
        for key in keys:
            self.delitem(self, key)
