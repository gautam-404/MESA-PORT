import os, subprocess, shlex
from MESAmanager.MesaFileHandler.MesaEnvironmentHandler import MesaEnvironmentHandler
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
            os.chdir("..")
            pwd = os.getcwd()
            subprocess.call(f"rm -rf {pwd}/{self.projName}", shell=True)
            subprocess.call(f"cp -r {self.envObject.mesaDir}/star/work {pwd}", shell=True)
            os.rename("work", self.projName)
            os.chdir(self.projName)

        if self.found is True:
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
            pwd = os.getcwd()
            subprocess.call(f"cp -r {self.envObject.mesaDir}/star/work {pwd}/{self.projName}", shell=True)
            os.chdir(self.projName)


    def clean(self):
        pwd = os.getcwd()
        try:
            subprocess.call(f"sh {pwd}/clean", shell=True, stdout=subprocess.DEVNULL)
            print("Done cleaning.\n")
        except subprocess.CalledProcessError:
            print(f"Either the project '{self.projName}' or the file '{self.projName}/clean' does not exists...could not clean!")
            print("Clean aborted!")
            

    def make(self):
        pwd = os.getcwd()
        try:
            with console.status("Making...", spinner="moon"):
                subprocess.call(f"{pwd}/mk", shell=True, stdout=subprocess.DEVNULL)
            print("Done making.\n")
        except subprocess.CalledProcessError:
            print(f"Either the project '{self.projName}' or the file '{self.projName}/mk' does not exists...could not make!")
            print("Make aborted!")
        
    
    def run(self, silent=False):
        pwd = os.getcwd()
        try:
            if silent is False:
                print("Running...")
                subprocess.call(f"{pwd}/rn", shell=True)
            elif silent is True:
                with console.status("Running...", spinner="moon"):
                    file = open(f"{pwd}/runlog", "a+") 
                    subprocess.call(f"{pwd}/rn", shell=True, stdout = file, stderr = file)
                    file.write( "\n\n"+("*"*100)+"\n\n" )
                    file.close()
            else:
                raise ValueError("Invalid input for argument 'silent'")
            print("Done with the run!\n")
        except subprocess.CalledProcessError:
            print("Run aborted! Check runlog.")
            
    
    def resume(self, photo, silent=False):
        pwd = os.getcwd()
        try:
            if not os.path.isfile(f"{pwd}/photos/{photo}"):
                raise FileNotFoundError(f"Photo '{photo}' could not be found.")
            else:
                if silent is False:
                    print(f"Resuming run from photo {photo}...")
                    subprocess.call(f"{pwd}/re {photo}", shell=True)
                elif silent is True:
                    with console.status("Resuming run from photo...", spinner="moon"):
                        file = open(f"{pwd}/runlog", "a+")  # append mode
                        subprocess.call(f"{pwd}/re {photo}", shell=True, stdout = file, stderr = file)
                        file.write( "\n\n"+("*"*100)+"\n\n" )
                        file.close()
                else:
                    raise ValueError("Invalid input for argument 'silent'.")
                print("Done with the run!\n")
        except subprocess.CalledProcessError:
            print("Resume aborted! Check runlog.")
            
    
    def loadProjInlist(self, inlistPath):
        inlistPath = os.path.abspath("../"+inlistPath)
        try:
            subprocess.call(f"cp {inlistPath} inlist_project", shell=True)
        except subprocess.CalledProcessError:
            print("Failed loading project inlist!")
        
    
    def loadPGstarInlist(self, inlistPath):
        inlistPath = os.path.abspath("../"+inlistPath)
        try:
            subprocess.call(f"cp {inlistPath} inlist_pgstar", shell=True)
        except subprocess.CalledProcessError:
            print("Failed loading pgstar inlist!")
            
    def loadGyreInput(self, gyre_in):
        gyre_in = os.path.abspath("../"+gyre_in)
        try:
            subprocess.call(f"cp {gyre_in} LOGS/gyre.in", shell=True)
        except subprocess.CalledProcessError:
            print("Failed loading gyre_in!")


    def runGyre(self, gyre_in='', silent=False):
        pwd = os.getcwd()
        self.loadGyreInput(gyre_in)
        try:
            if silent is False:
                print("Running gyre...")
                subprocess.call(f"cd LOGS && $GYRE_DIR/bin/gyre gyre.in", shell=True)
            elif silent is True:
                with console.status("Running gyre...", spinner="moon"):
                    file = open(f"{pwd}/runlog", "a+") 
                    subprocess.call(f"cd LOGS && $GYRE_DIR/bin/gyre gyre.in", shell=True, stdout = file, stderr = file)
                    file.write( "\n\n"+("*"*100)+"\n\n" )
                    file.close()
            else:
                raise ValueError("Invalid input for argument 'silent'")
            print("Done with the run!\n")
        except subprocess.CalledProcessError:
            try:
                subprocess.call(f"cd $MESA_DIR/gyre/gyre && make", shell=True, stdout=subprocess.DEVNULL)
                print('''Add $GYRE_DIR to your preferred shell's rc file (e.g. ~/.bashrc or ~/.zshrc):
                echo "export GYRE_DIR=$MESA_DIR/gyre/gyre" >> ~/.zshrc
                source ~/.zshrc
                Then try again.
                ''')
            except:    
                print(f"Check if $MESA_DIR is set in environment variables...could not run!")
                print("Run terminated! Check runlog.")