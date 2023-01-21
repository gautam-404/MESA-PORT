from .MesaFileAccess import *
from .support import *

from collections import OrderedDict

class MesaAccess:
    """Class to access MESA parameters.
    """    
    def __init__(self, project='work'):
        """Constructor for MesaAccess class.

        Args:
            project (str, optional): Project name. Defaults to 'work'.
        """        
        self.mesaFileAccess = MesaFileAccess(project)
        self._fullDict = self.stripFullDict()

    def stripToDict(self, section):
        """Strips a section of the MESA files to a dictionary.

        Args:
            section (str): Section to strip.

        Returns:
            dict: Dictionary of the section.
        """        
        retDict = OrderedDict()
        for file, parameterDict in self.mesaFileAccess.dataDict[section].items():
            for key, value in parameterDict.items():
                retDict[key] = value

        return retDict

    def stripFullDict(self):
        """Strips all sections of the MESA files to a dictionary.

        Returns:
            dict: Dictionary of all sections.
        """        
        retDict = OrderedDict()

        for section in [sectionStarJob,sectionControl,sectionPgStar]:
            retDict.update(self.stripToDict(section))

        return retDict

    def items(self):
        """Returns a list of tuples of the full dictionary.

        Returns:
            list: List of tuples of the full dictionary.
        """        
        return self._fullDict.items()

    def keys(self):
        """Returns a list of keys of the full dictionary.

        Returns:
            list: List of keys of the full dictionary.
        """        
        return self._fullDict.keys()

    def setitem(self, key, value):
        """Sets a value in the full dictionary.

        Args:
            key (str): Key of the value to set.
            value (str): Value to set.
        """        
        if key in self._fullDict.keys():
            self.mesaFileAccess[key] = value
        else:
            self.mesaFileAccess.addValue(key,value)
        self._fullDict = self.stripFullDict()


    def set(self, keys, values):
        """Sets a value in the full dictionary.

        Args:
            keys (str or list): Key of the value to set.
            values (str or list): Value to set.

        Raises:
            ValueError: Length of keys does not match length of values
            TypeError: Input parameter name(s) must be of type string or list of strings.
        """        
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
        """Gets a value from the full dictionary.

        Args:
            items (str or list): Key of the value to get.

        Raises:
            TypeError: Input parameter name(s) must be of type string or list of strings.

        Returns:
            str or list: Value or list of values.
        """        
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
        """Deletes a value from the full dictionary.

        Args:
            keys (str or list): Key of the value to delete.

        Raises:
            TypeError: Input parameter name(s) must be of type string or list of strings.
        """        
        if type(keys) == list:
            for key in keys:
                if key in self._fullDict.keys():
                    self.mesaFileAccess.removeValue(key)
        elif type(keys) == str:
            if keys in self._fullDict.keys():
                    self.mesaFileAccess.removeValue(keys)
        else:
            raise TypeError("Input parameter name(s) must be of type string or list of strings.")
