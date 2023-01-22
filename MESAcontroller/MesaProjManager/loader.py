import os
import shutil
from MESAcontroller.MesaFileHandler.MesaAccess import MesaAccess

def load(infile, work_dir, typeof, binary=False, star=''):
    """Loads a file into the project directory.

    Args:
        infile (path): Path to the file to be loaded. Can be relative or absolute.
        work_dir (path): Path to the project directory.
        typeof (str): Type of file to be loaded.
                        Can be one of the following:
                            - inlist_project
                            - inlist_pgstar
                            - gyre.in
                            - history_columns
                            - profile_columns
                            - run_star_extras.f90
        binary (bool, optional): True for a binary star system. Defaults to False.
        starno (str, optional): Star number in a binary star system. Defaults to ''.

    Raises:
        FileNotFoundError: If the file to be loaded does not exist.
        Exception: If the file loading fails.
    """    
    if typeof == "inlist_project":
        if not binary:
            dest = os.path.join(work_dir, "inlist_project")
        else:
            dest = os.path.join(work_dir, "inlist" + star)        
    elif typeof == "inlist_pgstar":
        dest = os.path.join(work_dir, "inlist_pgstar")
    elif typeof == "gyre.in":
        dest = os.path.join(work_dir, "LOGS", "gyre.in")
    elif typeof == "history_columns":
        dest = os.path.join(work_dir, "history_columns.list")
        access = MesaAccess(work_dir)
        access.set("history_columns_file", infile.split("/")[-1])
    elif typeof == "profile_columns":
        dest = os.path.join(work_dir, "profile_columns.list")
        access = MesaAccess(work_dir)
        access.set("profile_columns_file", infile.split("/")[-1])
    elif typeof == "extras" and binary==False:
        dest = os.path.join(work_dir, "src", "run_star_extras.f90")
    elif typeof == "extras" and binary==True:
        dest = os.path.join(work_dir, "src", "run_binary_extras.f90")

    try:
        if os.path.exists(infile):
            shutil.copy(infile, dest)
        elif os.path.exists(os.path.join(work_dir, infile)):
            infile = os.path.join(work_dir, infile)
            shutil.copy(infile, dest)
        elif typeof == "gyre.in" and os.path.exists(os.path.join("LOGS", gyre_in)):
                gyre_in = os.path.join("LOGS", gyre_in)
        else:
            raise FileNotFoundError(f"Could not find the your specified {typeof} file, '{infile}'. Aborting...")
    except shutil.Error:
        raise Exception(f"File loading {typeof} failed!")
