import os
import shlex
import shutil
import subprocess
import sys

import click
from rich.console import Console

from MESAcontroller.MesaFileHandler import MesaAccess, MesaEnvironmentHandler
from .loader import load

console = Console()

class ProjectOps:
    """This class handles MESA project operations.
    """    
    def __init__(self, name='work', binary = False):
        """Constructor for ProjectOps class.

        Args:
            name (str, optional): Name of the project. Defaults to 'work'.
            binary (bool, optional): True for a binary star system. Defaults to False.
        """        
        self.projName = name
        self.binary = binary
        if os.path.exists(self.projName):
            self.exists = True               ## Proj already present flag
        else:
            self.exists = False
        self.envObject = MesaEnvironmentHandler(self.projName)
        self.access = MesaAccess(self.projName)
    

    def create(self, overwrite=None, clean=None):       ### overwrite and clean are boolean arguments that are intentionally kept empty
        """Creates a new MESA project.

        Args:
            overwrite (bool, optional): Overwrite the existing project. Defaults to None.
            clean (bool, optional): Clean the existing project. Defaults to None.
        """   

        def useExisting():
            """A helper function to use the existing project."""         
            if not click.confirm(f"Use the already existing '{self.projName}' project as it is?", default=False):
                raise ValueError("Aborting!!! No project specified.")

        def cleanCheck():
            """A helper function to check if the user wants to clean the existing project."""
            if clean is None:
                if click.confirm(f"Clean the existing '{self.projName}' project for re-use?", default=False):
                    self.clean()
                else:
                    useExisting()
            elif clean is True:
                self.clean()
            elif clean is False:
                print(f"Using the already existing '{self.projName}' project as it is.")
            else:
                raise ValueError("Invalid input for argument 'clean'.")
        
        def writeover():
            """A helper function to overwrite the existing project."""
            try:
                shutil.rmtree(self.work_dir)
                if not self.binary:
                    shutil.copytree(os.path.join(self.envObject.mesaDir, 'star/work'), self.work_dir)
                else:
                    shutil.copytree(os.path.join(self.envObject.mesaDir, 'binary/work'), self.work_dir)

            except shutil.Error:
                raise Exception(f"Could not overwrite the existing '{self.projName}' project!")

        if self.exists is True:
            self.work_dir = os.path.abspath(os.path.join(os.getcwd(), self.projName))
            if overwrite is True:
                writeover()
            elif overwrite is False:
                cleanCheck()
            elif overwrite is None:
                print(f"Mesa project named '{self.projName}' already exists!")
                if not click.confirm(f"Use the already existing '{self.projName}' project as it is?", default=False):
                    if click.confirm("Do you wish to overwrite?", default=False):
                        writeover()
                    else:
                        cleanCheck()
            else:
                raise ValueError("Invalid input for argument 'overwrite'.") 
        else:
            try:
                if not self.binary:
                    shutil.copytree(os.path.join(self.envObject.mesaDir, 'star/work'), self.work_dir)
                else:
                    shutil.copytree(os.path.join(self.envObject.mesaDir, 'binary/work'), self.work_dir)
                self.work_dir = os.path.abspath(os.path.join(os.getcwd(), self.projName))
                self.exists = True
            except shutil.Error:
                raise Exception(f"Could not create the project '{self.projName}'!")
    
    def delete(self):
        """Deletes the project.
        """        
        if self.exists is True:
            shutil.rmtree(self.work_dir)
            print(f"Deleted project '{self.projName}'.")
        else:
            print(f"Project '{self.projName}' does not exist.")

    def check_exists(self):
        """Checks if the project exists."""
        if not self.exists:
            raise FileNotFoundError(f"Project '{self.projName}' does not exist. Please create it first.")


    def run_subprocess(self, commands, dir, silent=False, runlog=''):
        """Runs a subprocess.

        Args:
            commands (str or list): Command to be run.
            dir (str): Directory in which the command is to be run.
            silent (bool, optional): Run the command silently. Defaults to False.
            runlog (str, optional): Log file to write the output to. Defaults to ''.

        Returns:
            bool: True if the command ran successfully, False otherwise.
        """        
        with subprocess.Popen(shlex.split(commands), cwd=dir,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True) as proc:

            if runlog == '':
                if silent is False:
                    for outline in proc.stdout:
                        sys.stdout.write(outline)
                for errline in proc.stderr:
                    sys.stdout.write(errline)
            elif runlog != '':
                with open(runlog, "a+") as file:
                    for outline in proc.stdout:
                        file.write(outline)
                        if silent is False:
                            sys.stdout.write(outline)
                    for errline in proc.stderr:
                        file.write(errline)
                        sys.stdout.write(outline)
                    file.write( "\n\n"+("*"*100)+"\n\n" )

            _data, error = proc.communicate()
            if proc.returncode or error:
                print('The process raised an error:', proc.returncode, error)
                return False
            else:
                return True


    def clean(self):
        """Cleans the project.

        Raises:
            Exception: If the clean fails.
        """        
        self.check_exists()
        ## clean files are missing a shebang (#!/bin/bash) and hence need to be run with bash
        res = self.run_subprocess('/bin/bash ./clean', self.work_dir, silent=True)
        runlog = os.path.join(self.work_dir, "runlog")
        if os.path.exists(os.path.join(self.work_dir, "runlog")):
            os.remove(runlog)
        if res is False:
            raise Exception("Clean failed!")
        else:
            print("Done cleaning.\n")
            

    def make(self):
        """Makes the project.

        Raises:
            Exception: If the make fails.
        """        
        self.check_exists()
        with console.status("Making...", spinner="moon"):
            res = self.run_subprocess('./mk', self.work_dir, silent=True)
        if res is False:
            raise Exception("Make failed!")
        else:    
            print("Done making.\n")


    
    def run(self, silent=False):
        """Runs the project.

        Args:
            silent (bool, optional): Run the command silently. Defaults to False.

        Raises:
            Exception: If the project is not made yet.
            ValueError: If the input for argument 'silent' is invalid.
            Exception: If the run fails.
        """        
        self.check_exists()
        runlog = os.path.join(self.work_dir, "runlog")
        if not os.path.exists(os.path.join(self.work_dir, "star")):
            raise Exception("The project is not made yet...please make it first!") 
        else:
            if silent is False:
                print("Running...")
                res = self.run_subprocess('./rn', self.work_dir, silent, runlog=runlog)
            elif silent is True:
                with console.status("Running...", spinner="moon"):
                    res = self.run_subprocess('./rn', self.work_dir, silent, runlog=runlog) 
            else:
                raise ValueError("Invalid input for argument 'silent'")

            if res is False:
                raise Exception("Run failed! Check runlog.")
            else:
                print("Done with the run!\n")
        

        
    
    def resume(self, photo, silent=False, star=None):
        """Resumes the run from a given photo.

        Args:
            photo (str): Photo name from which the run is to be resumed.
            silent (bool, optional): Run the command silently. Defaults to False.

        Raises:
            FileNotFoundError: If the photo does not exist.
            ValueError: If the input for argument 'silent' is invalid.
        """
        self.check_exists()
        if self.binary:
            if star == 'primary':
                photo_path = os.path.join(self.work_dir, "photos1", photo)
            elif star == 'secondary':
                photo_path = os.path.join(self.work_dir, "photos2", photo)
            else:
                raise ValueError('''Invalid input for argument 'star'.  
                                Please use 'primary' or 'secondary' or 1 or 2.''')
        else:
            photo_path = os.path.join(self.work_dir, "photos", photo)
        runlog = os.path.join(self.work_dir, "runlog")
        if not os.path.isfile(photo_path):
            raise FileNotFoundError(f"Photo '{photo}' could not be exists.")
        else:
            if silent is False:
                print(f"Resuming run from photo {photo}...")
                res = self.run_subprocess('./re {photo}', self.work_dir, silent, runlog=runlog)
            elif silent is True:
                with console.status("Resuming run from photo...", spinner="moon"):
                    res = self.run_subprocess(f'./re {photo}', self.work_dir, silent, runlog=runlog)
            else:
                raise ValueError("Invalid input for argument 'silent'.")
            
            if res is False:
                print("Resume from photo failed! Check runlog.")
            else:
                print("Done with the run!\n")



    def runGyre(self, gyre_in, silent=False, star=None):
        """Runs GYRE.

        Args:
            gyre_in (str): GYRE input file.
            silent (bool, optional): Run the command silently. Defaults to False.
            star (str, optional): If the project is a binary system, specify the star 
                                    for which GYRE is to be run. Defaults to None.

        Raises:
            ValueError: If the input for argument 'silent' is invalid.
        """        
        self.check_exists()
        self.load_GyreInput(gyre_in)
        gyre_ex = os.path.join(os.environ['GYRE_DIR'], "bin", "gyre")
        if self.binary:
            if star == 'primary':
                LOGS_dir = os.path.join(self.work_dir, "LOGS1")
            elif star == 'secondary':
                LOGS_dir = os.path.join(self.work_dir, "LOGS2")
            else:
                raise ValueError('''Invalid input for argument 'star'.  
                                Please use 'primary' or 'secondary''')
        else:
            LOGS_dir = os.path.join(self.work_dir, "LOGS")
        runlog = os.path.join(self.work_dir, "runlog")
        if os.environ['GYRE_DIR'] is not None:
            if silent is False:
                print("Running GYRE...")
                res = self.run_subprocess(f'{gyre_ex} gyre.in', LOGS_dir, silent, runlog=runlog)
            elif silent is True:
                with console.status("Running GYRE...", spinner="moon"):
                    res = self.run_subprocess(f'{gyre_ex} gyre.in', LOGS_dir, silent, runlog=runlog)
            else:
                raise ValueError("Invalid input for argument 'silent'")   
            
            if res is False:
                    print("GYRE run failed! Check runlog.")
            else:
                print("GYRE run complete!\n") 
        else:
            print("Check if $GYRE_DIR is set in environment variables...could not run!")
            print("Run aborted!")


    def load_InlistProject(self, inlistPath, star=None):
        """Loads the inlist file.

        Args:
            inlistPath (str): Path to the inlist file.
            star (str, optional): If the project is a binary system, specify the star, 
                                    i.e. 'primary' or 'secondary', for which the inlist 
                                    is to be loaded. Defaults to None.
                                    If the project is a single star, this argument is ignored.

        Raises:
            ValueError: If the input for argument 'typeof' is invalid.
        """        
        self.check_exists()
        if self.binary:
            if star == 'primary':
                load(inlistPath, self.work_dir, "inlist_project", binary=True, star='1')
            elif star == 'secondary':
                load(inlistPath, self.work_dir, "inlist_project", binary=True, star='2')
            else:
                raise ValueError("Invalid input for argument 'typeof'")
        else:
            load(inlistPath, self.work_dir, "inlist_project")
            
    
    def load_InlistPG(self, inlistPath):
        """Loads the inlist file.

        Args:
            inlistPath (str): Path to the inlist file.

        Raises:
            ValueError: If the input for argument 'typeof' is invalid.
        """        
        self.check_exists()
        load(inlistPath, self.work_dir, "inlist_pgstar")
        

    def load_HistoryColumns(self, HistoryColumns):
        """Loads the history columns.

        Args:
            HistoryColumns (str): Path to the history columns file.
        """        
        self.check_exists()
        load(HistoryColumns, self.work_dir, "history_columns")


    def load_ProfileColumns(self, ProfileColumns):
        """Loads the profile columns.

        Args:
            ProfileColumns (str): Path to the profile columns file.
        """  
        self.check_exists()      
        load(ProfileColumns, self.work_dir, "profile_columns")


    def load_GyreInput(self, gyre_in):
        """Loads the GYRE input file.

        Args:
            gyre_in (str): Path to the GYRE input file.
        """ 
        self.check_exists()       
        load(gyre_in, self.work_dir, "gyre.in")


    def load_StarExtras(self, extras_path):
        """Loads the extras file.

        Args:
            extras_path (str): Path to the extras file.
        """  
        self.check_exists()
        load(extras_path, self.work_dir, "extras")


    def load_BinaryExtras(self, extras_path):
        """Loads the extras file.

        Args:
            extras_path (str): Path to the extras file.
        """  
        self.check_exists()
        if self.binary:
            load(extras_path, self.work_dir, "extras", binary=True)
        else:
            raise ValueError(f"{self.projName} is not a binary system!")