import os
import shutil
import subprocess
import glob

from rich import print, progress, prompt, status
progress_columns = (progress.SpinnerColumn(spinner_name="moon"),
                    progress.MofNCompleteColumn(),
                    *progress.Progress.get_default_columns(),
                    progress.TimeElapsedColumn())
import multiprocessing as mp

from ..MesaFileHandler import MesaAccess, MesaEnvironmentHandler
from . import ops_helper


class ProjectOps:
    """This class handles MESA project operations.
    """    
    def __init__(self, name='work', astero=False, binary=False):
        """Constructor for ProjectOps class.

        Args:
            name (str, optional): Name of the project. Defaults to 'work'.
            binary (bool, optional): True for a binary star system. Defaults to False.
        """        
        self.projName = name
        self.binary = binary
        self.astero = astero
        self.envObject = MesaEnvironmentHandler()
        if self.binary:
            self.defaultWork = os.path.join(self.envObject.mesaDir, 'binary/work')
        elif self.astero:
            self.defaultWork = os.path.join(self.envObject.mesaDir, 'astero/work')
        else:
            self.defaultWork = os.path.join(self.envObject.mesaDir, 'star/work')

        if os.path.exists(self.projName):
            self.exists = True               ## Proj already present flag
            self.work_dir = os.path.abspath(os.path.join(os.getcwd(), self.projName))
        else:
            self.exists = False
        
    

    def create(self, overwrite=None, clean=None): 
        """Creates a new MESA project.

        Args:
            overwrite (bool, optional): Overwrite the existing project. Defaults to None.
            clean (bool, optional): Clean the existing project. Defaults to None.
        """   

        def useExisting():
            """A helper function to use the existing project."""         
            if not prompt.Confirm.ask(f"Use the already existing '{self.projName}' project as it is?", default=False):
                raise ValueError("Aborting!!! No project specified.")

        def cleanCheck():
            """A helper function to check if the user wants to clean the existing project."""
            if clean is None:
                if prompt.Confirm.ask(f"Clean the existing '{self.projName}' project for re-use?", default=False):
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
                shutil.rmtree(self.projName)
                shutil.copytree(self.defaultWork, self.projName)

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
                if not prompt.Confirm.ask(f"Use the already existing '{self.projName}' project as it is?", default=False):
                    if prompt.Confirm.ask("Do you wish to overwrite?", default=False):
                        writeover()
                    else:
                        cleanCheck()
            else:
                raise ValueError("Invalid input for argument 'overwrite'.") 
        else:
            try:
                shutil.copytree(self.defaultWork, self.projName)
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

    def clean(self):
        """Cleans the project.

        Raises:
            Exception: If the clean fails.
        """        
        ops_helper.check_exists(self.exists, self.projName)
        ## clean files are missing a shebang (#!/bin/bash) and hence need to be run with bash
        res = subprocess.call('/bin/bash ./clean', cwd=self.work_dir, shell=True, stderr=subprocess.STDOUT)
        runlog = os.path.join(self.work_dir, "runlog")
        if os.path.exists(runlog):
            os.remove(runlog)
        if res is False:
            raise Exception("Clean failed!")
        else:
            print("Clean successful.\n")
            

    def make(self):
        """Makes the project.

        Raises:
            Exception: If the make fails.
        """        
        ops_helper.check_exists(self.exists, self.projName)
        with status.Status("[b i cyan3]Making...", spinner="moon"):
            res = subprocess.call('./mk', cwd=self.work_dir, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        if res is False:
            raise Exception("Make failed!")
        else:    
            print("Make successful.\n")


    
    def run(self, silent=True, logging=True):
        """Runs the project.

        Args:
            silent (bool, optional): Run the command silently. Defaults to True.

        Raises:
            Exception: If the project is not made yet.
            ValueError: If the input for argument 'silent' is invalid.
            Exception: If the run fails.
        """        
        ops_helper.check_exists(self.exists, self.projName)
        if logging:
            runlog = os.path.join(self.work_dir, "run.log")
        else:
            runlog = os.devnull
        if not os.path.exists(os.path.join(self.work_dir, "star")) and \
            not os.path.exists(os.path.join(self.work_dir, "binary")):
            raise Exception("Aborting! Run 'make()' first.")
        else:
            if silent not in [True, False]:
                raise ValueError("Invalid input for argument 'silent'")
            else:
                with status.Status("[b i cyan3]Running...", spinner="moon") as status_:
                    res = ops_helper.run_subprocess(commands='./rn', dir=self.work_dir, 
                                silent=silent, runlog=runlog, status=status_) 
            if res is False:
                raise Exception("Run failed! Check runlog.")
            else:
                print("Run successful.\n")
        

        
    
    def resume(self, photo=None, silent=True, target=None, logging=True):
        """Resumes the run from a given photo.

        Args:
            photo (str, optional): Photo name from which the run is to be resumed. 
                                If None, the last photo is used. Defaults to None.
            silent (bool, optional): Run the command silently. Defaults to True.

        Raises:
            FileNotFoundError: If the photo does not exist.
            ValueError: If the input for argument 'silent' is invalid.
        """
        ops_helper.check_exists(self.exists, self.projName)
        if logging:
            runlog = os.path.join(self.work_dir, "run.log")
        else:
            runlog = os.devnull
        if photo == None:
            # print(f"[b i  cyan3]Resuming run from the most recent photo.")
            with status.Status("[b i  cyan3]Resumed run from the most recent photo.\nRunning...", spinner="moon") as status_:
                res = ops_helper.run_subprocess(commands=f'./re', dir=self.work_dir, 
                        silent=silent, runlog=runlog, status=status_)
        else:
            if self.binary:
                if target == 'primary':
                    photo_path = os.path.join(self.work_dir, "photos1", photo)
                elif target == 'secondary':
                    photo_path = os.path.join(self.work_dir, "photos2", photo)
                else:
                    raise ValueError('''Invalid input for argument 'target'.  
                                    Please use 'primary' or 'secondary' ''')
            else:
                photo_path = os.path.join(self.work_dir, "photos", photo)
                
            if not os.path.isfile(photo_path):
                raise FileNotFoundError(f"Photo '{photo}' could not be exists.")
            else:
                if silent not in [True, False]:
                    raise ValueError("Invalid input for argument 'silent'.")
                else:
                    # print(f"[b i  cyan3]Resuming run from photo {photo}.")
                    with status.Status(f"[b i  cyan3]Resumed run from photo {photo}.\nRunning...", spinner="moon") as status_:
                        res = ops_helper.run_subprocess(commands=f'./re {photo}', dir=self.work_dir, 
                                silent=silent, runlog=runlog, status=status_)
        if res is False:
            print("Resume from photo failed! Check runlog.")
        else:
            print("Run successful.\n")





    def runGyre(self, gyre_in, files='', data_format="FGONG", silent=True, target=None, logging=True, parallel=False):
        """Runs GYRE.

        Args:
            gyre_in (str): GYRE input file.
            files (str or list of strings, optional): Profile files in the LOGS directory 
                                            to be processed by GYRE. Defaults to 'all'.
            silent (bool, optional): Run the command silently. Defaults to True.
            target (str, optional): Target star. Defaults to None.

        Raises: 
            FileNotFoundError: If the GYRE input file does not exist.
            ValueError: If the input for argument 'silent' is invalid.
            ValueError: If the input for argument 'files' is invalid.
        """        
        ops_helper.check_exists(self.exists, self.projName)
        star = MesaAccess(self.projName, self.astero, self.binary, target)
        star.load_GyreInput(gyre_in)
        gyre_ex = os.path.join(os.environ['GYRE_DIR'], "bin", "gyre")
        if self.binary:
            if target == 'primary':
                LOGS_dir = os.path.join(self.work_dir, "LOGS1")
            elif target == 'secondary':
                LOGS_dir = os.path.join(self.work_dir, "LOGS2")
            else:
                raise ValueError('''Invalid input for argument 'star'.  
                                Please use 'primary' or 'secondary''')
        else:
            LOGS_dir = os.path.join(self.work_dir, "LOGS")

        if logging:
            runlog = os.path.join(self.work_dir, "run.log")
        else:
            runlog = os.devnull


        if os.environ['GYRE_DIR'] is not None:
            if not silent in [True, False]:
                raise ValueError("Invalid input for argument 'silent'")
            ## ALL FILES
            if files == 'all':
                filenames = sorted(glob.glob(os.path.join(LOGS_dir, f"*.{data_format}")), 
                            key=lambda x: int(os.path.basename(x).split('.')[0].split('profile')[1]))
                if len(filenames) == 0:
                    raise ValueError(f"No {data_format} files found in LOGS directory.")
                else:
                    with progress.Progress(*progress_columns) as progressbar:
                        task = progressbar.add_task("[b i cyan3]Running GYRE...", total=len(filenames))
                        filenames = [filename.split('/')[-1] for filename in filenames]
                        if parallel:
                            n_processes = - (-mp.cpu_count()//int(os.environ['OMP_NUM_THREADS']))
                            with mp.Pool(n_processes) as pool:
                                gyre_in = os.path.abspath(gyre_in)
                                args = zip([f'{gyre_ex} {gyre_in}']*len(filenames), [LOGS_dir]*len(filenames),
                                        [silent]*len(filenames), [runlog]*len(filenames), 
                                        [None]*len(filenames), [True]*len(filenames),
                                        filenames, [data_format]*len(filenames))
                                for _ in pool.starmap(ops_helper.run_subprocess, args):
                                    progressbar.advance(task)
                        else:
                            for filename in filenames:
                                res = ops_helper.run_subprocess(f'{gyre_ex} gyre.in', dir=LOGS_dir, 
                                        silent=silent, runlog=runlog, status=None, gyre=True, filename=filename, data_format=data_format)
                                progressbar.advance(task)

            ## SPECIFIC FILES
            elif type(files) == list or type(files) == str:
                if type(files) == str:
                    files = [files]
                if len(files) == 0:
                    raise ValueError("No files provided.")
                else:
                    with progress.Progress(*progress_columns) as progressbar:
                        task = progressbar.add_task("[b i cyan3]Running GYRE...", total=len(filenames))
                        for file in files:
                            if not os.path.isfile(os.path.join(LOGS_dir, file)):
                                raise FileNotFoundError(f"File '{file}' does not exist.")
                        if parallel:
                            n_processes = - (-mp.cpu_count()//int(os.environ['OMP_NUM_THREADS']))
                            with mp.Pool(n_processes) as pool:
                                gyre_in = os.path.abspath(gyre_in)
                                args = zip([f'{gyre_ex} {gyre_in}']*len(filenames), [LOGS_dir]*len(filenames),
                                        [silent]*len(filenames), [runlog]*len(filenames), 
                                        [None]*len(filenames), [True]*len(filenames),
                                        filenames, [data_format]*len(filenames))
                                for _ in pool.starmap(ops_helper.run_subprocess, args):
                                    progressbar.advance(task)
                        else:
                            for file in files:
                                res = ops_helper.run_subprocess(f'{gyre_ex} gyre.in', dir=LOGS_dir, 
                                    silent=silent, runlog=runlog, status=None, gyre=True, filename=file, data_format=data_format)
                                progressbar.advance(task)
            
            ## NO FILES, i.e. file specified in gyre.in
            elif files == '':
                with status.Status("[b i  cyan3]Running GYRE...", spinner="moon") as status_:
                    res = ops_helper.run_subprocess(f'{gyre_ex} gyre.in', dir=LOGS_dir, 
                                    silent=silent, runlog=runlog, status=status_, gyre=True)
            else:
                raise ValueError("Invalid input for argument 'files'")

            if res is False:
                    print("GYRE run failed! Check runlog.")
            else:
                print("GYRE run complete!\n") 
        else:
            print("Check if $GYRE_DIR is set in environment variables...could not run!")
            print("Run aborted!")
