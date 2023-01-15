import os, subprocess, shlex
from MESAcommando.MesaFileHandler.MesaEnvironmentHandler import MesaEnvironmentHandler
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
            os.chdir(self.projName)
            self.found = True               ## Proj already present flag
        else:
            self.found = False

    

    def create(self, overwrite=None, clean=None):       ### overwrite and clean are boolean arguments that are intentionally kept empty
        def useExisting():
            if not click.confirm(f"Use the already existing '{self.projName}' project as it is?", default=False):
                raise ValueError("Aborting!!! No project specified.")
                os._exit()

        def cleanCheck():
            if clean == None:
                if click.confirm(f"Clean the existing '{self.projName}' project for re-use?", default=False):
                    self.clean()
                else:
                    useExisting()
            elif clean == True:
                self.clean()
            elif clean == False:
                print(f"Using the already existing '{self.projName}' project as it is.")
            else:
                raise ValueError("Invalid input for argument 'clean'.")
        
        def writeover():
            os.chdir("..")
            pwd = os.getcwd()
            self.oscommand(f"rm -rf {pwd}/{self.projName}")
            self.oscommand(f"cp -r {self.envObject.mesaDir}/star/work {pwd}")
            os.rename("work", self.projName)
            os.chdir(self.projName)

        if self.found == True:
            if overwrite == True:
                writeover()
            elif overwrite == False:
                cleanCheck()
            elif overwrite == None:
                print(f"Mesa project named '{self.projName}' already exists!")
                if not click.confirm(f"Use the already existing '{self.projName}' project as it is?", default=False):
                    if click.confirm("Do you wish to overwrite?", default=False):
                        writeover()
                    else:
                        cleanCheck()
            else:
                raise ValueError("Invalid input for argument 'overwrite'.")
        else:
            pwd = os.getcwd()
            self.oscommand(f"cp -r {self.envObject.mesaDir}/star/work {pwd}/{self.projName}")
            os.chdir(self.projName)

    
    def oscommand(self, command, **args):
        command_split = shlex.split(command)
        return subprocess.check_call(command_split, **args)


    def clean(self):
        pwd = os.getcwd()
        try:
            self.oscommand(f"sh {pwd}/clean")
            print("Done cleaning.\n")
        except subprocess.CalledProcessError:
            print(f"Either the project '{self.projName}' or the file '{self.projName}/clean' does not exists...could not clean!")
            print("Clean terminated!")
            

    def make(self):
        pwd = os.getcwd()
        try:
            with console.status("Making...", spinner="moon"):
                self.oscommand(f"{pwd}/mk", stdout=subprocess.DEVNULL)
            print("Done making.\n")
        except subprocess.CalledProcessError:
            print(f"Either the project '{self.projName}' or the file '{self.projName}/mk' does not exists...could not make!")
            print("Make terminated!")
        
    
    def run(self, silent=False):
        pwd = os.getcwd()
        try:
            if silent == False:
                with console.status("Running...", spinner="moon"):
                    self.oscommand(f"{pwd}/rn")
            elif silent == True:
                with console.status("Running...", spinner="moon"):
                    file = open(f"{pwd}/runlog", "a+") 
                    self.oscommand(f"{pwd}/rn", stdout = file, stderr = file)
                    file.write( "\n\n"+("*"*100)+"\n\n" )
                    file.close()
            else:
                raise ValueError("Invalid input for argument 'silent'")
            print("Done with the run!\n")
        except subprocess.CalledProcessError:
            print(f"Either the project '{self.projName}' or the file '{self.projName}/rn' does not exists...could not run!")
            print("Run terminated! Check runlog.")
            
    
    def rerun(self, photo, silent=False):
        pwd = os.getcwd()
        try:
            if not os.path.isfile(f"{pwd}/photos/{photo}"):
                raise FileNotFoundError("Photo '{photo}' could not be found.")
            else:
                if silent == False:
                    with console.status("Running from photo...", spinner="moon"):
                        self.oscommand(f"{pwd}/re {photo}")
                elif silent == True:
                    with console.status("Running from photo...", spinner="moon"):
                        file = open(f"{pwd}/runlog", "a+")  # append mode
                        self.oscommand(f"{pwd}/re {photo}", stdout = file, stderr = file)
                        file.write( "\n\n"+("*"*100)+"\n\n" )
                        file.close()
                else:
                    raise ValueError("Invalid input for argument 'silent'.")
                print("Done with the run!\n")
        except subprocess.CalledProcessError:
            print(f"Either the project '{self.projName}' or the file '{self.projName}/re' does not exists...could not restart!")
            print("Rerun terminated! Check runlog.")
            
    
    def loadProjInlist(self, inlistPath):
        os.chdir("..")
        pwd = os.getcwd()
        try:
            self.oscommand(f"cp {inlistPath} {pwd}/{self.projName}/inlist_project")
            os.chdir(self.projName)
        except subprocess.CalledProcessError:
            print(f"Either the project '{self.projName}' or the inlist {inlistPath} does not exists...could not load!")
            print("Loading project inlist terminated!")
        
    
    def loadPGstarInlist(self, inlistPath):
        os.chdir("..")
        pwd = os.getcwd()
        try:
            self.oscommand(f"cp {inlistPath} {pwd}/{self.projName}/inlist_pgstar")
            os.chdir(self.projName)
        except subprocess.CalledProcessError:
            print(f"Either the project '{self.projName}' or the inlist '{inlistPath}' does not exists...could not load!")
            print("Loading pgstar inlist terminated!")
            