import re
from collections import OrderedDict

from .support import *

class IMesaInterface:

    def __init__(self, project):
        self.projpath = os.path.abspath(os.path.join(os.getcwd(), project))
        self.dataDict = OrderedDict()

    def getParameters(self,text):
        parameters = OrderedDict()
        p = re.compile(regex_read_parameter,flags=re.MULTILINE)

        for matches in p.findall(text):
            if len(matches) != 2:
                raise AttributeError(f"Regex needs to match 2 items here! Found {str(len(matches))}")

            parameters[matches[0]] = self.convertToPythonTypes(matches[1])

        return parameters

    def convertToPythonTypes(self,data):
        if data[0] == "." and data[-1] == ".": # return boolean
            return True if data[1:-1] == "true" else False
        elif data[0] == "'": # return string
            return data[1:-1]
        elif re.compile(regex_floatingValue).match(data) is not None:
            matches = re.compile(regex_floatingValue).findall(data)
            if matches[0][1] == "":
                power = 0
            else:
                power = float(matches[0][1])
            return float(matches[0][0])*pow(10,power)
        elif "." in data:
            return float(data)
        else:
            try:
                return int(data)
            except:
                raise AttributeError(f"Cannot convert {data} to known type!")

    def convertToFortranType(self, data):
        if isinstance(data,bool):
            return "."+("true"if data else "false") + "."
        elif isinstance(data,str):
            return "'"+data+"'"
        elif isinstance(data,float) or isinstance(data,int):
            return str(data)
        else:
            raise AttributeError(f"Cannot convert type {str(type(data))} to known type")

    def readFile(self, fileName):
        with cd(self.projpath):
            with open(fileName) as f:
                return f.read()

    def writeFile(self, fileName, content):
        with cd(self.projpath):
            with open(fileName, 'w') as f:
                f.write(content)

    def items(self):
        return self.dataDict.items()

    def keys(self):
        return self.dataDict.keys()

    def __getitem__(self, item):
        return self.dataDict[item]

    def __setitem__(self, key, value):
        raise NotImplementedError("Please implement the setItem Method!")