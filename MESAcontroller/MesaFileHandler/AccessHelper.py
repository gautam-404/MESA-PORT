import os
import re
from .support import *
from pprint import pprint


def readDefaults(filename, defaultsDir):
    """Reads the defaults files and returns a dictionary with all the parameters and their values.

    Args:
        section (str): The section of the defaults file to be read (e.g. "star_job", "controls", "pgstar")
        defaultsDir (str): The path to the defaults directory
        defaultsFileNames (dict): A dictionary with the names of the defaults files of each section

    Raises:
        FileNotFoundError: If the defaults files do not exist.

    Returns:
        dict: A dictionary with all the parameters and their values.
    """    
    defaultsFile = defaultsDir + filename
    if not os.path.exists(defaultsFile):
        raise FileNotFoundError(f"Defaults file {filename} does not exist.")
    else:
        defaultParameters = {}
        with open(defaultsFile) as file:
            for line in file:
                line = line.strip().replace(" ", "")
                if not line.startswith("!") and not line.startswith("/") and line != "":
                    if "!" in line:
                        line = line.split("!")[0]
                    name, _, var = line.strip().partition("=")
                    defaultParameters[name] = var
    # pprint(defaultParameters)
    return defaultParameters



def matchtoDefaults(parameter, defaultsDict, sections):
    """Returns the section of the defaults file where the parameter is located.

    Args:
        parameter (str): The parameter to be searched for.
        defaultsDict (dict): A dictionary with all the parameters and their values.
        sections (list): A list with the sections of the defaults file.

    Raises:
        KeyError: If the parameter does not exist in the defaults files.

    Returns:
        str: The section of the defaults file where the parameter is located.
    """    
    for section in sections:
        if parameter in defaultsDict[section]:
            return section, toPythonType(defaultsDict[section][parameter]),\
                     type(toPythonType(defaultsDict[section][parameter]))
    else:
        raise KeyError(f"Parameter {parameter} does not exist in the defaults files.")


def toPythonType(data):
    """Returns the 'Python' type of the value.

    Args:
        data (str): The value to be checked.

    Raises:
        AttributeError: If the value cannot be converted to a known type.

    Returns:
        type: The type of the value.
    """
    regex_floatingValue = r"([-\d\.\d]+)[deDE]([\-\d]*)" # regex for floating point values
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


def toFortranType(data):
    """Converts the value to a 'Fortran' type.

    Args:
        data (str): The value to be converted.

    Raises:
        AttributeError: If the value cannot be converted to a known type.

    Returns:
        str: The value converted to a 'Fortran' type.
    """    
    if isinstance(data, bool):
        return "." + ("true" if data else "false") + "."
    elif isinstance(data, str):
        return "'"+data+"'"
    elif isinstance(data, float) or isinstance(data, int):
        return str(data)
    else:
        raise AttributeError(f"Cannot convert type {str(type(data))} to known type")


def matchTypes(inputType, defaultType):
    """Checks if the input type is the same as the default type.

    Args:
        inputType (type): The type of the input value.
        defaultType (type): The type of the default value.

    Raises:
        TypeError: If the input type is not the same as the default type.

    Returns:
        bool: True if the types match, False otherwise.
    """    
    if inputType == defaultType:
        return True
    elif inputType == float and defaultType == int or inputType == int and defaultType == float:
        return True
    else:
        return False


def matchtoFile(parameter, inlistDict, sections, default_section):
    """Returns the section of the inlist file where the parameter is located.

    Args:
        parameter (str): The parameter to be searched for.
        inlistDict (dict): A dictionary with all the parameters and their values.
        sections (list): A list with the sections of the inlist file.

    Returns:
        bool, str: A tuple with a boolean indicating if the parameter exists in the inlist file 
                    and the section of the inlist file where the parameter is located.
    """    
    for section in sections:
        if parameter in inlistDict[section] and section == default_section:
            return True, inlistDict[section][parameter]
    else:
        return False, None



def readFile(inlist, projectDir):
    """Reads the inlist file and returns a dictionary with all the parameters and their values.

    Args:
        inlist (str): The path to the inlist file.

    Raises:
        FileNotFoundError: If the inlist file does not exist.

    Returns:
        dict : A dictionary with all the parameters and their values.
    """    
    with cd(projectDir):
        if not os.path.exists(inlist):
            raise FileNotFoundError(f"Inlist {inlist} does not exist.")
        else:
            inlistParameters = {}
            inlistSections = []
            with open(inlist) as file:
                for line in file:
                    line = line.strip().replace(" ", "")
                    if line.startswith("&"):
                        section = line.split("&")[1].split()[0]
                        inlistParameters[section] = {}
                        inlistSections.append(section)
                    elif not line.startswith("!") and not line.startswith("/") and line != "":
                        line = line.replace(" ", "")
                        if "!" in line:
                            line = line.split("!")[0]
                        name, _, value = line.partition("=")
                        inlistParameters[section][name] = value
        # pprint(inlistParameters)
        return inlistSections, inlistParameters




def writetoFile(projectDir, filename, parameter, value, exists, default_section, delete=False):
    """Writes the parameter and its value to the inlist file.

    Args:
        filename (str): The path to the inlist file.
        parameter (str): The parameter to be written.
        value (str): The value of the parameter to be written.
        inlistDict (dict): A dictionary with all the parameters and their values.
        defaultsDict (dict): A dictionary with all the parameters and their values.
        sections (list): A list with the sections of the inlist file.
    """    
    value = toFortranType(value)
    this_section = False
    with cd(projectDir):
        with open(filename, "r") as file:
            lines = file.readlines()
        with open(filename, "w+") as f:
            indent = "    "
            for line in lines:
                edited = False
                if default_section in line:
                    this_section = True
                if this_section:
                    if exists and parameter in line:
                        if not delete:
                            f.write(line.replace(line.split("=")[1], f" {value}    ! Changed\n"))
                        else:
                            f.write(indent)
                            f.write(f"! {parameter} = {value}    ! Removed\n")
                        edited = True
                        this_section = False
                    elif not exists and line[0] == "/":
                        f.write(indent)
                        f.write(f"{parameter} = {value}    ! Added\n")
                        f.write("/")
                        edited = True
                        this_section = False
                if not edited:
                    f.write(line)
    



