import os
import shutil
from . import mesa_access
from .support import *

def load(infile, work_dir, typeof, astero=False, binary=False, target=''):
    """Loads a file into the project directory.

    Args:
        infile (path): Path to the file to be loaded. Can be relative or absolute.
        work_dir (path): Path to the project directory.
        typeof (str): Type of file to be loaded.
                        Can be one of the following:
                            - inlist_project
                            - inlist_pgstar
                            - inlist_astero_search_controls
                            - gyre.in
                            - history_columns
                            - profile_columns
                            - run_star_extras.f90
        binary (bool, optional): True for a binary target system. Defaults to False.
        target (str, optional): Which target to load the file for. Defaults to ''.
                              Can be one of the following:
                                - primary
                                - secondary
                                - binary

    Raises:
        FileNotFoundError: If the file to be loaded does not exist.
        Exception: If the file loading fails.
    """    

    if typeof == "inlist_project":
        if not binary:
            dest = os.path.join(work_dir, "inlist_project")
        elif binary and target == "primary":
            dest = os.path.join(work_dir, "inlist1")
        elif binary and target == "secondary":
            dest = os.path.join(work_dir, "inlist2")
        elif binary and target == "binary":
            dest = os.path.join(work_dir, "inlist_project")

    elif typeof == "inlist_pgstar":
        dest = os.path.join(work_dir, "inlist_pgstar")

    elif typeof == "inlist_astero_search_controls":
        dest = os.path.join(work_dir, "inlist_astero_search_controls")

    elif typeof == "gyre.in":
        if not binary:
            dest = os.path.join(work_dir, "LOGS", "gyre.in")
        elif binary and target == "primary":
            dest = os.path.join(work_dir, "LOGS1", "gyre.in")
        elif binary and target == "secondary":
            dest = os.path.join(work_dir, "LOGS2", "gyre.in")

    elif typeof == "history_columns":
        dest = os.path.join(work_dir, "history_columns.list")
        access = mesa_access.MesaAccess(work_dir, binary=binary, target=target)
        access.set("history_columns_file", dest.split("/")[-1])

    elif typeof == "profile_columns":
        dest = os.path.join(work_dir, "profile_columns.list")
        access = mesa_access.MesaAccess(work_dir)
        access.set("profile_columns_file", infile.split("/")[-1])

    elif typeof == "extras" and binary==False:
        dest = os.path.join(work_dir, "src", "run_star_extras.f90")

    elif typeof == "extras" and binary==True:
        dest = os.path.join(work_dir, "src", "run_binary_extras.f90")

#     with cd(work_dir):
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
