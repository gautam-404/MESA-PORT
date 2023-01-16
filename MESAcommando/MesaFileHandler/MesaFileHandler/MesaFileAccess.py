import re
from collections import OrderedDict

from support import *
from MesaFileInterface import IMesaInterface
from MesaEnvironmentHandler import MesaEnvironmentHandler


class MesaFileAccess(IMesaInterface):

    def __init__(self):
        IMesaInterface.__init__(self)
        self.envObject = MesaEnvironmentHandler()
        self.setupDict()

    def setupDict(self):
        self.dataDict = OrderedDict()

        for section in sections:
            self.dataDict[section]  = OrderedDict()
            self.readSections("inlist",section)

    def readSections(self,filename,section):
        content = self.readFile(filename)

        p = re.compile(regex_sections)

        for matches in p.findall(content):
            if section is not None and section != matches[0]:
                continue

            self.dataDict[section][filename] =self.getParameters(matches[1])

            for externalFile in set(self.dataDict[section][filename].keys()).intersection(external_file_parameters):
                self.readSections(self.dataDict[section][filename][externalFile],section)

    def __setitem__(self, key, value):
        for section in sections:
            for file, parameteDict in self.dataDict[section].items():
                if key in parameteDict.keys():
                    self.dataDict[section][file][key] = value
                    regex = r"(" + key + r".+=)\s* ([\.\w_\d']+)"
                    substring = r"\1 "+self.convertToFortranType(value)
                    self.rewriteFile(file,regex,substring)
                    return

    def rewriteFile(self, file, regex, substring):
        content = self.readFile(file)

        p = re.compile(regex)
        content = p.sub(substring, content)

        self.writeFile(file, content)

    def addValue(self, key, value=None):
        section,parmValue = self.envObject.checkParameter(key, value)

        if section == "":
            raise KeyError(f"The parameter {key} is not available through Mesa. Please add it to the defaults list,"
                                                  "before adding it to the inlist files")

        parmValue = parmValue if value is None else value

        subset = list(set(self.dataDict[section]["inlist"].keys()).intersection(set(external_file_parameters)))

        if len(subset) != 0:
            usedFile = self.dataDict[section]["inlist"][subset[0]]
        else:
            usedFile = "inlist"

        if key in self.dataDict[section][usedFile].keys():
            self.__setitem__(key,parmValue)
        else:
            regex = r"(&" + section + r"[\w_\s\.\'\=\!\(\)\/\>\<\-\,]+)(\/)"
            substring = r"\1\n    " + key + "=" + self.convertToFortranType(value) + r"\n\2"
            self.rewriteFile(usedFile, regex, substring)
            self.dataDict[section][usedFile][key] = parmValue


    def removeValue(self, key):
        section,_ = self.envObject.checkParameter(key)

        if section == "":
            raise KeyError(f"The parameter {key} is not available through Mesa. Please add it to the defaults list,"
                                                  "before adding it to the inlist files")

        if section not in sections:
            raise ValueError(f"Mesa says section for parameter {key} is {section}. This section is not in the "
                                                                                   "Sections read by this code")

        for file, parameteDict in self.dataDict[section].items():
            if key in parameteDict.keys():
                del self.dataDict[section][file][key]
                regex = r"\s"+key+".+"
                substring = ""
                self.rewriteFile(file, regex, substring)







