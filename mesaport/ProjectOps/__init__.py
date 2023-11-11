"""
This module defines the `ProjectOps` class, which handles MESA project operations.

Attributes:
    projName (str): Name of the project.
    binary (bool): True for a binary star system.
    astero (bool): True for an asteroseismic project.
    envObject (MesaEnvironmentHandler): MesaEnvironmentHandler object.
    defaultWork (str): Default work directory.
    exists (bool): True if the project already exists.
    work_dir (str): Path to the project directory.

Methods:
    create(overwrite=None, clean=None): Creates a new MESA project.
    delete(): Deletes the project.
    clean(): Cleans the project.
    make(silent=False): Makes the project.
    run(silent=True, logging=True, parallel=False, trace=None, env=os.environ.copy()): Runs the project.
    resume(photo=None, silent=True, target=None, logging=True, parallel=False, trace=None, env=os.environ.copy()): Resumes the run from a given photo.
    runGyre(gyre_in, files='all', wdir=None, data_format="GYRE", silent=True, target=None, logging=True, logfile="gyre.log",
            parallel=False, n_cores=None, gyre_input_params=None, env=os.environ.copy()): Runs GYRE.
"""

from .project_ops import ProjectOps
from . import ops_helper, istarmap
