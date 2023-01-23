from .support import *
from .MesaEnvironmentHandler import MesaEnvironmentHandler
from .AccessHelper import *
import ast
from pprint import pprint

class MesaAccess:
    def __init__(self, project, binary=False, target=''):
        """Initializes the MesaAccess class.

        Args:
            project (str): _description_.
            binary (bool, optional): If the project is a binary. Defaults to False.
            target (str, optional): If the project is a binary, which star to access. Defaults to ''.
        """        
        self.project = project
        self.binary = binary
        self.target = target
        self.projectDir = os.path.join(os.getcwd(), project)
        envObj = MesaEnvironmentHandler(binary, target)
        if binary and target == 'binary':
            self.mesaDir, self.defaultsDir = envObj.mesaDir, envObj.defaultsDir
            self.sections, self.defaultsFileNames = sections_binary, defaultsFileNames_binary
            self.inlist_filenames = ["inlist_project"]
        elif binary and target != 'binary':
            self.mesaDir, self.defaultsDir = envObj.mesaDir, envObj.defaultsDir
            self.sections, self.defaultsFileNames = sections_star, defaultsFileNames_star
            if self.target == 'primary':
                self.inlist_filenames = ["inlist1"]
            elif self.target == 'secondary':
                self.inlist_filenames = ["inlist2"]
        else:
            self.mesaDir, self.defaultsDir = envObj.mesaDir, envObj.defaultsDir
            self.sections, self.defaultsFileNames = sections_star, defaultsFileNames_star
            self.inlist_filenames = ["inlist_project", "inlist_pgstar"]
        self.defaultsDict = {}
        for section in self.sections:
            self.defaultsDict[section] = readDefaults(self.defaultsFileNames[section], self.defaultsDir)
        
        
        
    def generateDicts(self):
        """Generates the dictionaries for the inlist files.
        """        
        self.inlistDict = {}
        self.inlistSections = {}
        for filename in self.inlist_filenames:
            self.inlistSections[filename], self.inlistDict[filename] = readFile(filename, self.projectDir)
        # pprint(self.defaultsDict)
   
    
    
    def setitem(self, key, value):
        """Sets a value in the full dictionary.

        Args:
            key (str): Key of the value to set.
            value (str): Value to set.

        Raises:
            TypeError: Value is not of default type
        """        
        default_section, default_val, default_type = matchtoDefaults(key, self.defaultsDict, self.sections)
        if not self.binary:
            if default_section in ["star_job", "controls"]:
                filename = "inlist_project"
            elif default_section == "pgstar":
                filename = "inlist_pgstar"
        else:
            filename = self.inlist_filenames[0]
        exists, _ = matchtoFile(key, self.inlistDict[filename], self.inlistSections[filename], default_section)
        ## type checking the value not implemented yet
        if not matchTypes(type(value), default_type):
            raise TypeError(f"Value {value} is not of default type {default_type}")
        writetoFile(self.projectDir, filename, key, value, exists, default_section, delete=False)
            


    def getitem(self, item):
        """Gets a value from the full dictionary.

        Args:
            item (str): Key of the value to get.

        Returns:
            str: Value of the key
        """        
        default_section, default_val, default_type = matchtoDefaults(item, self.defaultsDict, self.sections)
        if not self.binary:
            if default_section in ["star_job", "controls"]:
                filename = "inlist_project"
            elif default_section == "pgstar":
                filename = "inlist_pgstar"
        else:
            filename = self.inlist_filenames[0]
        return matchtoFile(item, self.inlistDict[filename], self.inlistSections[filename], default_section)[1]
    


    def delitem(self, key):
        """Deletes a value from the full dictionary.

        Args:
            key (str): Key of the value to delete.

        Raises:
            KeyError: Parameter does not exist in inlist file
        """        
        default_section, default_val, default_type = matchtoDefaults(key, self.defaultsDict, self.sections)
        if not self.binary:
            if default_section in ["star_job", "controls"]:
                filename = "inlist_project"
            elif default_section == "pgstar":
                filename = "inlist_pgstar"
        else:
            filename = self.inlist_filenames[0]
        exists, _ = matchtoFile(key, self.inlistDict[filename], self.inlistSections[filename], default_section)
        if exists:
            writetoFile(self.projectDir, filename, key, _, exists, default_section, delete=True)
        else:
            raise KeyError(f"Parameter {key} does not exist in {filename}")



    def set(self, keys, values):
        """Sets a value in the full dictionary.

        Args:
            keys (str or list): Key of the value to set.
            values (str or list): Value to set.

        Raises:
            ValueError: Length of keys does not match length of values
            TypeError: Input parameter name(s) must be of type string or list of strings.
        """    
        self.generateDicts()    
        if isinstance(keys, list):
            if len(keys) == len(values):
                for i in range(len(keys)):
                    self.setitem(keys[i], values[i])
            else:
                raise ValueError(f"Length of keys {keys} does not match length of {values}")
        elif isinstance(keys, str):
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
        self.generateDicts()
        if isinstance(items, list):
            got = []
            for item in items:
                got.append(self.getitem(item))
            return got
        elif isinstance(items, str):
            return self.getitem(items)
        else:
            raise TypeError("Input parameter name(s) must be of type string or list of strings.")
        


    def delete(self, keys):
        """Deletes a value from the full dictionary.

        Args:
            keys (str or list): Key of the value to delete.

        Raises:
            TypeError: Input parameter name(s) must be of type string or list of strings.
        """       
        self.generateDicts() 
        if isinstance(keys, list):
            for key in keys:
                self.delitem(key)
        elif isinstance(keys, str):
            self.delitem(keys)
        else:
            raise TypeError("Input parameter name(s) must be of type string or list of strings.")
    
    