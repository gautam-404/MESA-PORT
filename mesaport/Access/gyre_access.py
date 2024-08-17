import glob
import os
# from . import loader
import shutil
from . import access_helper
from .support.utils import cwd

from threading import Lock
file_operation_lock = Lock()

"""
This module defines the `GyreAccess` class, which handles GYRE input file operations.

Attributes:
    path (str): The path to the GYRE input file.
    binary (str): The name of the binary file to be used.
    target (str): The target to be used.

Methods:
    load(gyre_in="gyre.in"): Loads the GYRE input file into the project directory.
    set(arg, gyre_in="gyre.in"): Sets the value of a parameter in the inlist file.
    modify_gyre_params(wdir, filename, data_format, gyre_in="gyre.in", diff_scheme='MAGNUS_GL2'): Modifies the GYRE input file parameters.
"""

class GyreAccess:
    def __init__(self):
        """
        Args:
            path (str): The path to the GYRE input file.
            binary (str): The name of the binary file to be used.
            target (str): The target to be used.
        """
        self.check_env()
        self.default_sections = self.gyreDefaults()

    def check_env(self):
        """
        Checks if GYRE_DIR is set in the environment.
        """
        if "GYRE_DIR" not in os.environ:
            raise EnvironmentError("GYRE_DIR is not set in your enviroment. Be sure to set it properly!!")

    def load(self, gyre_in="gyre.in", dest=None):
        """
        Loads the GYRE input file into the project directory.
        """
        if dest is None:
            dest = os.path.join(self.projectDir, "LOGS", 'gyre.in')
        shutil.copy(gyre_in, os.path.join(dest, 'gyre.in'))
        
    def gyreDefaults(self):
        """Reads the defaults files and returns a dictionary with all the parameters and their values.
        Returns:
            dict: A dictionary with all the parameters and their values.
        """    
        gyre_dir = os.path.abspath(os.environ["GYRE_DIR"])
        gyre_defaults_dir = os.path.join(gyre_dir, "docs/source/ref-guide/input-files")
        if not os.path.exists(gyre_defaults_dir):
            gyre_defaults_dir = os.path.join(gyre_dir, "doc/source/ref-guide/input-files")
        gyre_defaults_dir = os.path.join(gyre_defaults_dir, "*")
        defaultsFiles = glob.glob(gyre_defaults_dir)
        # sections = ["&"+name.split("/")[-1].split('.')[0].split('-')[0] for name in defaultsFiles]
        # print(sections)
        section_parameters = {}
        for i, file in enumerate(defaultsFiles):
            params = []
            sections = []
            with open(file) as file:
                for line in file:
                    if ":nml_g:" in line:
                        splits = line.split(":nml_g:")
                        for s in splits:
                            if "`" in s:
                                sections.append("&"+s.split("`")[1])
                    if ":nml_n:" in line:
                        params.append(line.split(":nml_n:")[1].split("`")[1])
            sections = list(set(sections))
            for section in sections:
                section_parameters[section] = params
        return section_parameters


    def writetoGyreFile(self, wdir, parameter, value, default_section=None, gyre_in="gyre.in"):
        """Writes the parameter and its value to the inlist file.

        Args:
            filename (str): The path to the inlist file.
            parameter (str): The parameter to be written.
            value (str): The value of the parameter to be written.
            default_section (str): The section in which the parameter is to be written.
            sections (list): A list with the sections of the inlist file.
        """   
        if default_section is None:
            for section, values in self.default_sections.items():
                if parameter in values:
                    default_section = section
            if default_section is None:
                raise TypeError(f"Parameter {parameter} not found in any GYRE input files.")
        this_section = False
        with cwd(wdir):
            with file_operation_lock:
                with open(gyre_in, "r") as file:
                    lines = file.readlines()
                with open(gyre_in, "w+") as f:
                    indent = "    "
                    for line in lines:
                        edited = False
                        if default_section in line:
                            this_section = True
                        if this_section:
                            if parameter in line:
                                if parameter == line.split("=")[0].strip():
                                    f.write(line.replace(line.split("=")[1], f" {value}    ! Changed\n"))
                                    edited = True
                                    this_section = False
                            elif line[0] == "/":
                                f.write(indent)
                                f.write(f"{parameter} = {value}    ! Added\n")
                                f.write("/")
                                edited = True
                                this_section = False
                        if not edited:
                            f.write(line)

   

    def modify_gyre_params(self, wdir, filename, data_format, gyre_in="gyre.in", diff_scheme='MAGNUS_GL2'):
        if data_format == "GYRE":
            file_format = "MESA"
        elif data_format == "FGONG":
            file_format = "FGONG"
        else:
            file_format = "GSM"
        self.writetoGyreFile(wdir, parameter="model_type", value="'EVOL'", default_section="&model", gyre_in=gyre_in)
        self.writetoGyreFile(wdir, parameter="file_format", value=f"'{file_format}'", default_section="&model", gyre_in=gyre_in)
        self.writetoGyreFile(wdir, parameter="file", value=f"'{filename}'", default_section="&model", gyre_in=gyre_in)
        self.writetoGyreFile(wdir, parameter="summary_file", value=f"'{filename.split('.')[0]}-freqs.dat'", default_section="&ad_output", gyre_in=gyre_in)
        self.writetoGyreFile(wdir, parameter="summary_file", value=f"'{filename.split('.')[0]}-freqs-nad.dat'", default_section="&nad_output", gyre_in=gyre_in)


    def set(self, arg, wdir, gyre_in="gyre.in"):
        """Sets the value of a parameter in the inlist file.

        Args:
            arg (dict or list of dicts): A dictionary or a list of dictionaries with the parameters to be set.
        """    
        if isinstance(arg, dict):
            for key, value in arg.items():
                self.writetoGyreFile(wdir, key, access_helper.toFortranType(value), gyre_in=gyre_in)
        elif isinstance(arg, list):
            for item in arg:
                for key, value in item.items():
                    self.writetoGyreFile(wdir, key, access_helper.toFortranType(value), gyre_in=gyre_in)
        elif arg is None:
            pass
        else:
            raise TypeError("Argument must be a dictionary or a list of dictionaries.")
        