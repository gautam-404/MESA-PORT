import os, sys, subprocess, shutil, shlex
from MESAcontroller.MesaFileHandler.MesaEnvironmentHandler import MesaEnvironmentHandler
from MESAcontroller.MesaFileHandler import MesaAccess
import click
from rich.console import Console
console = Console()

class ProjectOps:
    def __init__(self, name=''):
        self.envObject = MesaEnvironmentHandler()
        if name == '':
            self.projName = "work"
            ### If user input is preferred over a default value, uncomment the line below
            # self.projName = input("No project name supplied! Please provide a project name... \n")
        else:
            self.projName = name
        if os.path.exists(self.projName):
            self.work_dir = os.path.abspath(os.path.join(os.getcwd(), self.projName))
            self.exists = True               ## Proj already present flag
        else:
            self.exists = False
        

    

    def create(self, overwrite=None, clean=None):       ### overwrite and clean are boolean arguments that are intentionally kept empty
        def useExisting():
            if not click.confirm(f"Use the already existing '{self.projName}' project as it is?", default=False):
                raise ValueError("Aborting!!! No project specified.")

        def cleanCheck():
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
            try:
                shutil.rmtree(self.work_dir)
                shutil.copytree(os.path.join(self.envObject.mesaDir, 'star/work'), self.work_dir)
            except shutil.Error:
                raise Exception(f"Could not overwrite the existing '{self.projName}' project!")

        if self.exists is True:
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
                shutil.copytree(os.path.join(self.envObject.mesaDir, 'star/work'), self.projName)
                self.work_dir = os.path.abspath(os.path.join(os.getcwd(), self.projName))
                self.exists = True
            except shutil.Error:
                raise Exception(f"Could not create the project '{self.projName}'!")
    
    def delete(self):
        if self.exists is True:
            shutil.rmtree(self.work_dir)
            print(f"Deleted project '{self.projName}'.")
        else:
            print(f"Project '{self.projName}' does not exist.")

    def check_exists(self):
        if not self.exists:
            raise FileNotFoundError(f"Project '{self.projName}' does not exist. Please create it first.")


    def run_subprocess(self, commands, dir, silent=False, runlog=''):
        with subprocess.Popen(commands, cwd=dir,
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
        self.check_exists()
        ## clean files are missing a shebang (#!/bin/bash) and hence need to be run with bash
        res = self.run_subprocess(shlex.split('/bin/bash ./clean'), self.work_dir, silent=True)
        runlog = os.path.join(self.work_dir, "runlog")
        if os.path.exists(os.path.join(self.work_dir, "runlog")):
            os.remove(runlog)
        if res is False:
            raise Exception("Clean failed!")
        else:
            print("Done cleaning.\n")
            

    def make(self):
        self.check_exists()
        with console.status("Making...", spinner="moon"):
            res = self.run_subprocess('./mk', self.work_dir, silent=True)
        if res is False:
            raise Exception("Make failed!")
        else:    
            print("Done making.\n")


    
    def run(self, silent=False):
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
        

        
    
    def resume(self, photo, silent=False):
        self.check_exists()
        photo_path = os.path.join(self.work_dir, "photos", photo)
        runlog = os.path.join(self.work_dir, "runlog")
        if not os.path.isfile(photo_path):
            raise FileNotFoundError(f"Photo '{photo}' could not be exists.")
        else:
            if silent is False:
                print(f"Resuming run from photo {photo}...")
                res = self.run_subprocess(shlex.split('./re {photo}'), self.work_dir, silent, runlog=runlog)
            elif silent is True:
                with console.status("Resuming run from photo...", spinner="moon"):
                    res = self.run_subprocess(shlex.split(f'./re {photo}'), self.work_dir, silent, runlog=runlog)
            else:
                raise ValueError("Invalid input for argument 'silent'.")
            
            if res is False:
                print("Resume from photo failed! Check runlog.")
            else:
                print("Done with the run!\n")



    def runGyre(self, gyre_in, silent=False):
        self.check_exists()
        self.loadGyreInput(gyre_in)
        gyre_ex = os.path.join(os.environ['GYRE_DIR'], "bin", "gyre")
        runlog = os.path.join(self.work_dir, "runlog")
        if os.environ['GYRE_DIR'] is not None:
            if silent is False:
                print("Running GYRE...")
                res = self.run_subprocess([gyre_ex, 'gyre.in'], os.path.join(self.work_dir, 'LOGS'), silent, runlog=runlog)
            elif silent is True:
                with console.status("Running GYRE...", spinner="moon"):
                    res = self.run_subprocess([gyre_ex, 'gyre.in'], os.path.join(self.work_dir, 'LOGS'), silent, runlog=runlog)
            else:
                raise ValueError("Invalid input for argument 'silent'")   
            
            if res is False:
                    print("GYRE run failed! Check runlog.")
            else:
                print("GYRE run complete!\n") 
        else:
            print("Check if $GYRE_DIR is set in environment variables...could not run!")
            print("Run aborted!")



    def load_ProjInlist(self, inlistPath):
        self.check_exists()
        inlist_project = os.path.join(self.work_dir, "inlist_project")
        try:
            if os.path.exists(inlistPath):
                shutil.copy(inlistPath, inlist_project)
            elif os.path.exists(os.path.join(self.work_dir, inlistPath)):
                inlistPath = os.path.join(self.work_dir, inlistPath)
                shutil.copy(inlistPath, inlist_project)
            else:
                raise Exception(f"Could not find the your specified project inlist file, '{inlistPath}'. Aborting...")
        except shutil.Error:
            raise Exception("Failed loading project inlist!")
        

    
    def load_PGstarInlist(self, inlistPath):
        self.check_exists()
        inlist_pgstar = os.path.join(self.work_dir, "inlist_pgstar")
        try:
            if os.path.exists(inlistPath):
                shutil.copy(inlistPath, inlist_pgstar)
            elif os.path.exists(os.path.join(self.work_dir, inlistPath)):
                inlistPath = os.path.join(self.work_dir, inlistPath)
                shutil.copy(inlistPath, inlist_pgstar)
            else:
                raise Exception(f"Could not find the your specified pgstar inlist file, '{inlistPath}'. Aborting...")
        except shutil.Error:
            raise Exception("Failed loading pgstar inlist!")


    def load_HistoryColumns(self, HistoryColumns):
        self.check_exists()
        access = MesaAccess()
        try:
            if os.path.exists(HistoryColumns):
                shutil.copy(HistoryColumns, self.work_dir)
            elif os.path.exists(os.path.join(self.work_dir, HistoryColumns)):
                pass
            else:
                raise Exception(f"Could not find the your specified history columns file, '{HistoryColumns}'. Aborting...")
            access.set("history_columns_file", HistoryColumns.split("/")[-1])
        except shutil.Error:
            raise Exception("Failed loading history columns file!")


    def load_ProfileColumns(self, ProfileColumns):
        self.check_exists()
        access = MesaAccess()
        try:
            if os.path.exists(ProfileColumns):
                shutil.copy(ProfileColumns, self.work_dir)
            elif os.path.exists(os.path.join(self.work_dir, ProfileColumns)):
                pass
            else:
                raise Exception(f"Could not find the your specified profile columns file, '{ProfileColumns}'. Aborting...")
            access.set("profile_columns_file", ProfileColumns.split("/")[-1])
        except shutil.Error:
            raise Exception("Failed loading profile columns file!")

            
    def load_GyreInput(self, gyre_in):
        self.check_exists()
        gyre_dest = os.path.join(self.work_dir, "LOGS", "gyre.in")
        try:
            if os.path.exists(gyre_in):
                shutil.copy(gyre_in, gyre_dest)
            elif os.path.exists(os.path.join("LOGS", gyre_in)):
                gyre_in = os.path.join("LOGS", gyre_in)
                shutil.copy(gyre_in, gyre_dest)
            elif os.path.exists(os.path.join(self.work_dir, gyre_in)):
                gyre_in = os.path.join(self.work_dir, gyre_in)
                shutil.copy(gyre_in, gyre_dest)
            else:
                raise Exception(f"Could not find your specified GYRE input file, '{gyre_in}'. Aborting...")
        except shutil.Error:
            raise Exception("Failed loading GYRE input file!")
    


    def load_Extras(self, extras_path):
        self.check_exists()
        extras_default = os.path.join(self.work_dir, "src", "run_star_extras.f90")
        try:
            if os.path.exists(extras_path):
                shutil.copy(extras_path, extras_default)
            elif os.path.exists(os.path.join(self.work_dir, extras_path)):
                extras_path = os.path.join(self.work_dir, extras_path)
                shutil.copy(extras_path, extras_default)
            else:
                raise Exception(f"Could not find your customised run_star_extras.f90, '{extras_path}'. Aborting...")
        except shutil.Error:
            raise Exception("Failed loading customised run_star_extras.f90 file!")