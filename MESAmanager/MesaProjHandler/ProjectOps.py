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
            self.work_dir = os.path.abspath(os.path.join(os.getcwd(), self.projName))
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
            subprocess.call(['rm', '-rf', self.work_dir])
            subprocess.call(['cp', '-r', os.path.join(self.envObject.mesaDir, 'star/work'), self.work_dir])

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
            subprocess.call(['cp', '-r', os.path.join(self.envObject.mesaDir, 'star/work'), self.projName])
            self.work_dir = os.path.abspath(os.path.join(os.getcwd(), self.projName))


    def clean(self):
        clean_ex = os.path.join(self.work_dir, "clean")
        try:
            subprocess.call(clean_ex, stdout=subprocess.DEVNULL)
            print("Done cleaning.\n")
        except subprocess.CalledProcessError:
            print(f"Either the project '{self.projName}' or the file '{self.projName}/clean' does not exists...could not clean!")
            print("Clean aborted!")
            

    def make(self):
        make_ex = os.path.join(self.work_dir, "mk")
        try:
            with console.status("Making...", spinner="moon"):
                subprocess.call(make_ex, stdout=subprocess.DEVNULL)
            print("Done making.\n")
        except subprocess.CalledProcessError:
            print(f"Either the project '{self.projName}' or the file '{self.projName}/mk' does not exists...could not make!")
            print("Make aborted!")
        
    
    def run(self, silent=False):
        run_ex = os.path.join(self.work_dir, "rn")
        runlog = os.path.join(self.work_dir, "runlog")
        try:
            if silent is False:
                print("Running...")
                file = open(runlog, "a+") 
                subprocess.call(run_ex)
                file.write( "\n\n"+("*"*100)+"\n\n" )
                file.close()
            elif silent is True:
                with console.status("Running...", spinner="moon"):
                    file = open(runlog, "a+") 
                    subprocess.call(run_ex, stdout = file, stderr = file)
                    file.write( "\n\n"+("*"*100)+"\n\n" )
                    file.close()
            else:
                raise ValueError("Invalid input for argument 'silent'")
            print("Done with the run!\n")
        except subprocess.CalledProcessError:
            print("Run aborted! Check runlog.")
            
    
    def resume(self, photo, silent=False):
        resume_ex = os.path.join(self.work_dir, "re")
        photo_path = os.path.join(self.work_dir, "photos", photo)
        runlog = os.path.join(self.work_dir, "runlog")
        try:
            if not os.path.isfile(photo_path):
                raise FileNotFoundError(f"Photo '{photo}' could not be found.")
            else:
                if silent is False:
                    print(f"Resuming run from photo {photo}...")
                    file = open(runlog, "a+")  # append mode
                    subprocess.call([resume_ex, photo])
                    file.write( "\n\n"+("*"*100)+"\n\n" )
                    file.close()
                elif silent is True:
                    with console.status("Resuming run from photo...", spinner="moon"):
                        file = open(runlog, "a+")  # append mode
                        subprocess.call(f"{resume_ex} {photo}", stdout = file, stderr = file)
                        file.write( "\n\n"+("*"*100)+"\n\n" )
                        file.close()
                else:
                    raise ValueError("Invalid input for argument 'silent'.")
                print("Done with the run!\n")
        except subprocess.CalledProcessError:
            print("Resume aborted! Check runlog.")
            
    
    def loadProjInlist(self, inlistPath):
        inlistPath = os.path.abspath(inlistPath)
        inlist_project = os.path.join(self.work_dir, "inlist_project")
        try:
            subprocess.call(['cp', inlistPath, inlist_project])
        except subprocess.CalledProcessError:
            raise("Failed loading project inlist!")
        

    
    def loadPGstarInlist(self, inlistPath):
        inlistPath = os.path.abspath(inlistPath)
        inlist_pgstar = os.path.join(self.work_dir, "inlist_pgstar")
        try:
            subprocess.call(['cp', inlistPath, inlist_pgstar])
        except subprocess.CalledProcessError:
            raise("Failed loading pgstar inlist!")


            
    def loadGyreInput(self, gyre_in):
        gyre_dest = os.path.join(self.work_dir, "LOGS", "gyre.in")
        if os.path.exists(gyre_in):
            subprocess.call(['cp', gyre_in, gyre_dest])
        elif os.path.exists(os.path.join("LOGS", gyre_in)):
            gyre_in = os.path.join("LOGS", gyre_in)
            subprocess.call(['cp', gyre_in, gyre_dest])
        elif os.path.exists(os.path.join(self.work_dir, gyre_in)):
            gyre_in = os.path.join(self.work_dir, gyre_in)
            subprocess.call(['cp', gyre_in, gyre_dest])
        else:
            raise("Could not find the specified gyre input file. Aborting...")



    def runGyre(self, gyre_in, silent=False):
        self.loadGyreInput(gyre_in)
        gyre_ex = os.path.join("$GYRE_DIR", "bin", "gyre")
        runlog = os.path.join(self.work_dir, "runlog")
        if os.getenv('GYRE_DIR') is not None:
            if silent is False:
                print("Running gyre...")
                file = open(runlog, "a+") 
                try:
                    subprocess.call(f"cd LOGS && {gyre_ex} gyre.in", shell=True)
                    return
                except subprocess.CalledProcessError:
                    print("Gyre run failed! Check runlog.")
                file.write( "\n\n"+("*"*100)+"\n\n" )
                file.close()
            elif silent is True:
                with console.status("Running gyre...", spinner="moon"):
                    file = open(runlog, "a+") 
                    try:
                        subprocess.call("cd LOGS && {gyre_ex} gyre.in", shell=True, stdout = file, stderr = file)
                        return
                    except subprocess.CalledProcessError:
                        print("Gyre run failed! Check runlog.")
                    file.write( "\n\n"+("*"*100)+"\n\n" )
                    file.close()
            else:
                raise ValueError("Invalid input for argument 'silent'")    
        else:
            print("Check if $GYRE_DIR is set in environment variables...could not run!")
            print("Run terminated! Check runlog.")

        