from .support import *
from .MesaEnvironmentHandler import MesaEnvironmentHandler
from .AccessHelper import *
from .Loader import *
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
   
    
    
    def setitem(self, key, value, default=False):
        """Sets a value in the full dictionary.

        Args:
            key (str): Key of the value to set.
            value (str): Value to set.

        Raises:
            TypeError: Value is not of default type
        """        
        default_section, default_val, default_type = matchtoDefaults(key, self.defaultsDict, self.sections)
        if default:
            value = default_val
        if not self.binary:
            if default_section in ["star_job", "controls"]:
                filename = "inlist_project"
            elif default_section == "pgstar":
                filename = "inlist_pgstar"
        else:
            filename = self.inlist_filenames[0]
        exists, _ = matchtoFile(key, self.inlistDict[filename], self.inlistSections[filename], default_section)
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



    def set(self, *arg):
        """Sets a value in the full dictionary.

        Args:
            keys (str or list): Key of the value to set.
            values (str or list): Value to set.

        Raises:
            ValueError: Length of keys does not match length of values
            TypeError: Input parameter name(s) must be of type string or list of strings.
        """    
        self.generateDicts() 
        if len(arg) == 1:
            if isinstance(arg[0], dict):
                for key, value in arg[0].items():
                    self.setitem(key, value)
            else:
                raise TypeError("Input parameter name(s) must be of type dict.")
        elif len(arg) == 2:
            keys, values = arg[0], arg[1]  
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
        else:
            raise TypeError("Wrong number of arguments.")

    
    def setDefault(self, keys):
        """Sets all values to default.
        """        
        self.generateDicts()
        if isinstance(keys, list):
            for key in keys:
                self.setitem(key, '', default=True)
        elif isinstance(keys, str):
            self.setitem(keys, '', default=True)
        



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


    def check_exists(self):
        """Checks if the project directory exists.
        """        
        if not os.path.exists(self.projectDir):
            raise FileNotFoundError(f"Project directory {self.projectDir} does not exist.")

    
    def load_InlistProject(self, inlistPath):
        """Loads the inlist file.

        Args:
            inlistPath (str): Path to the inlist file.
            target (str, optional): If the project is a binary system, specify the star 
                                    or binary. Defaults to None.
                                    Input can be 'primary', 'secondary' or 'binary'.

        Raises:
            ValueError: If the input for argument 'typeof' is invalid.
        """        
        self.check_exists()
        if self.target not in [None, 'primary', 'secondary', 'binary']:
            raise ValueError("Invalid input for argument 'typeof'")
        load(inlistPath, self.projectDir, "inlist_project", self.binary, self.target)
            
    
    def load_InlistPG(self, inlistPath):
        """Loads the inlist file.

        Args:
            inlistPath (str): Path to the inlist file.

        Raises:
            ValueError: If the input for argument 'typeof' is invalid.
        """        
        self.check_exists()
        load(inlistPath, self.projectDir, "inlist_pgstar")
        

    def load_HistoryColumns(self, HistoryColumns):
        """Loads the history columns.

        Args:
            HistoryColumns (str): Path to the history columns file.
            target (str, optional): If the project is a binary system, specify the star or binary.
                                    Input 'primary', 'secondary' or 'binary'. Defaults to None.
        """        
        self.check_exists()
        if self.target not in ['primary', 'secondary', 'binary']:
            raise ValueError("Invalid input for argument 'typeof'")
        load(HistoryColumns, self.projectDir, "history_columns", self.binary, self.target)


    def load_ProfileColumns(self, ProfileColumns):
        """Loads the profile columns.

        Args:
            ProfileColumns (str): Path to the profile columns file.
        """  
        self.check_exists()      
        load(ProfileColumns, self.projectDir, "profile_columns")


    def load_GyreInput(self, gyre_in):
        """Loads the GYRE input file.

        Args:
            gyre_in (str): Path to the GYRE input file.
        """ 
        self.check_exists()       
        load(gyre_in, self.projectDir, "gyre.in", self.binary, self.target)


    def load_Extras(self, extras_path):
        """Loads the extras file.

        Args:
            extras_path (str): Path to the extras file.
        """  
        self.check_exists()
        load(extras_path, self.projectDir, "extras", self.binary, self.target)