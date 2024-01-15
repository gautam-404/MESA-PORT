from .support import *
from .envhandler import MesaEnvironmentHandler
from .access_helper import *
from . import loader

"""
This module defines the `MesaAccess` class, which handles MESA project access.

Attributes:
    project (str): Name of the project.
    binary (bool): True for a binary star system.
    astero (bool): True for an asteroseismic project.
    target (str): If the project is a binary system, specify the star or binary.

Methods:
    set(key, value, default=False, force=False): Sets a value in the full dictionary.
    get(key): Gets a value from the full dictionary.
    delete(key): Deletes a value from the full dictionary.
    setDefault(keys): Sets all values to default.
    getDefault(keys): Gets default value from the full dictionary.
    load_InlistProject(inlistPath): Loads the inlist file.
    load_InlistAsteroSearch(inlistPath): Loads the astero_search_controls inlist file.
    load_InlistPG(inlistPath): Loads the inlist file.
    load_HistoryColumns(HistoryColumns): Loads the history columns.
    load_ProfileColumns(ProfileColumns): Loads the profile columns.
    load_Extras(extras_path): Loads the run_star_extras file.
"""

class MesaAccess:
    def __init__(self, project, astero=False, binary=False, target=''):
        """Initializes the MesaAccess class.

        Args:
            project (str): _description_.
            binary (bool, optional): If the project is a binary. Defaults to False.
            target (str, optional): If the project is a binary, which star to access. Defaults to ''.
        """        
        if binary and target not in [None, 'primary', 'secondary', 'binary']:
            raise ValueError("Invalid input for argument 'target'")
        self.project = project
        self.astero = astero
        self.binary = binary
        self.target = target
        if os.path.isabs(project):
            self.projectDir = project
        else:
            self.projectDir = os.path.join(os.getcwd(), project)
        envObj = MesaEnvironmentHandler(astero, binary, target)
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
        elif astero:
            self.mesaDir, self.defaultsDir = envObj.mesaDir, envObj.defaultsDir
            self.sections, self.defaultsFileNames = sections_astero, defaultsFileNames_astero
            self.inlist_filenames = ["inlist_project", "inlist_pgstar", "inlist_astero_search_controls"]
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
        # pprint(self.inlistDict)


    
    def setitem(self, key, value, default=False, force=False):
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
        filename = getFilename(self.astero, self.binary, default_section, self.inlist_filenames)
        exists, _ = matchtoFile(key, self.inlistDict[filename], self.inlistSections[filename], default_section)
        if not force:
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
        filename = getFilename(self.astero, self.binary, default_section, self.inlist_filenames)
        return matchtoFile(item, self.inlistDict[filename], self.inlistSections[filename], default_section)[1]
    


    def delitem(self, key):
        """Deletes a value from the full dictionary.

        Args:
            key (str): Key of the value to delete.

        Raises:
            KeyError: Parameter does not exist in inlist file
        """        
        default_section, default_val, default_type = matchtoDefaults(key, self.defaultsDict, self.sections)
        filename = getFilename(self.astero, self.binary, default_section, self.inlist_filenames)
        exists, _ = matchtoFile(key, self.inlistDict[filename], self.inlistSections[filename], default_section)
        if exists:
            writetoFile(self.projectDir, filename, key, _, exists, default_section, delete=True)
        else:
            raise KeyError(f"Parameter {key} does not exist in {filename}")

    def set(self, *arg, force=False):
        """Sets a value in the full dictionary.

        Args:
            arg (dict or list of dicts): A dict with the keys and values to set or a list of dicts with the keys and values to set.
        Raises:
            ValueError: Length of keys does not match length of values
            TypeError: Input parameter name(s) must be of type string or list of strings.
        """    
        self.generateDicts() 
        if len(arg) == 1:
            if isinstance(arg[0], dict):
                for key, value in arg[0].items():
                    self.setitem(key, value, force=force)
            elif isinstance(arg[0], list):
                for dict_ in arg[0]:
                    for key, value in dict_.items():
                        self.setitem(key, value, force=force)
            else:
                raise TypeError("Input parameter name(s) must be of type dict or list of dicts.")
        elif len(arg) == 2:
            keys, values = arg[0], arg[1]  
            if isinstance(keys, list):
                if len(keys) == len(values):
                    for i in range(len(keys)):
                        self.setitem(keys[i], values[i], force=force)
                else:
                    raise ValueError(f"Length of keys {keys} does not match length of {values}")
            elif isinstance(keys, str):
                self.setitem(keys, values, force=force)
            else:
                raise TypeError("Input parameter name(s) must be of type string or list of strings.")
    
    def setDefault(self, keys):
        """Sets all values to default.
        """        
        self.generateDicts()
        if isinstance(keys, list):
            for key in keys:
                self.setitem(key, '', default=True)
        elif isinstance(keys, str):
            self.setitem(keys, '', default=True)


    def getDefault(self, keys):
        """Gets default value from the full dictionary.

        Args:
            keys (str or list): Key of the value to get.

        Raises:
            TypeError: Input parameter name(s) must be of type string or list of strings.

        Returns:
            str or list: Value or list of values.
        """        
        self.generateDicts()
        if isinstance(keys, list):
            got = []
            for key in keys:
                default_section, default_val, default_type = matchtoDefaults(key, self.defaultsDict, self.sections)
                got.append(default_val)
            return got
        elif isinstance(keys, str):
            default_section, default_val, default_type = matchtoDefaults(keys, self.defaultsDict, self.sections)
            return default_val
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
            ValueError: If the input for argument 'target' is invalid.
        """        
        self.check_exists()
        loader.load(inlistPath, self.projectDir, "inlist_project", binary=self.binary, target=self.target)

    def load_InlistAsteroSearch(self, inlistPath):
        """Loads the astero_search_controls inlist file.

        Args:
            inlistPath (str): Path to the inlist file.
        """        
        self.check_exists()
        loader.load(inlistPath, self.projectDir, "inlist_astero_search_controls")
            
    
    def load_InlistPG(self, inlistPath):
        """Loads the inlist file.

        Args:
            inlistPath (str): Path to the inlist file.

        Raises:
            ValueError: If the input for argument 'typeof' is invalid.
        """        
        self.check_exists()
        loader.load(inlistPath, self.projectDir, "inlist_pgstar")
        

    def load_HistoryColumns(self, HistoryColumns):
        """Loads the history columns.

        Args:
            HistoryColumns (str): Path to the history columns file.
            target (str, optional): If the project is a binary system, specify the star or binary.
                                    Input 'primary', 'secondary' or 'binary'. Defaults to None.
        """        
        self.check_exists()
        loader.load(HistoryColumns, self.projectDir, "history_columns", binary=self.binary, target=self.target)


    def load_ProfileColumns(self, ProfileColumns):
        """Loads the profile columns.

        Args:
            ProfileColumns (str): Path to the profile columns file.
        """  
        self.check_exists()      
        loader.load(ProfileColumns, self.projectDir, "profile_columns")


    def load_Extras(self, extras_path):
        """Loads the extras file.

        Args:
            extras_path (str): Path to the extras file.
        """  
        self.check_exists()
        loader.load(extras_path, self.projectDir, "extras", binary=self.binary, target=self.target)

