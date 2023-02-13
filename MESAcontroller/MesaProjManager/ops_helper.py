import subprocess
import shlex
import sys
from rich import status

from ..MesaFileHandler.support import *

def check_exists(exists, projName):
        """Checks if the project exists."""
        if not exists:
            raise FileNotFoundError(f"Project '{projName}' does not exist. Please create it first.")


def run_subprocess(commands, dir, silent=False, runlog='', status=status.Status("Running..."), gyre=False):
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
        step = 1
        with open(runlog, "a+") as file:
            for outline in proc.stdout:
                file.write(outline)
                if silent is False:
                    sys.stdout.write(outline)
                elif not gyre:
                    step, age = process_outline(outline, step)
                    if age is not None:
                        if age < 1/365:
                            status.update(status=f"[b i cyan3]Running....[/b i cyan3]\n[b]Age: [cyan]{age*365*24:.4f}[/cyan] hours")
                        elif 1/365 < age < 1:
                            status.update(status=f"[b i cyan3]Running....[/b i cyan3]\n[b]Age: [cyan]{age*365:.4f}[/cyan] days")
                        elif 1 < age < 1000:
                            status.update(status=f"[b i cyan3]Running....[/b i cyan3]\n[b]Age: [cyan]{age:.3f}[/cyan] years")
                        else:
                            status.update(status=f"[b i cyan3]Running....[/b i cyan3]\n[b]Age: [cyan]{age:.3e}[/cyan] years")
            for errline in proc.stderr:
                file.write(errline)
                sys.stdout.write(errline)
            file.write( "\n\n"+("*"*100)+"\n\n" )

        _data, error = proc.communicate()
        if proc.returncode or error:
            print('The process raised an error:', proc.returncode, error)
            return False
        else:
            return True

def process_outline(outline, step):
    try:
        if "E" in outline and "0" in outline and "." in outline:
            return step, float(outline.split()[0])
        outline = outline.split()
        # print(outline.split())
        if int(outline[0]) == step+1:
            step += 1
        return step, None
    except:
        return step, None


def writetoGyreFile(dir, parameter, value, default_section):
    """Writes the parameter and its value to the inlist file.

    Args:
        filename (str): The path to the inlist file.
        parameter (str): The parameter to be written.
        value (str): The value of the parameter to be written.
        inlistDict (dict): A dictionary with all the parameters and their values.
        defaultsDict (dict): A dictionary with all the parameters and their values.
        sections (list): A list with the sections of the inlist file.
    """    
    filename = "gyre.in"
    this_section = False
    with cd(dir):
        with open(filename, "r") as file:
            lines = file.readlines()
        with open(filename, "w+") as f:
            indent = "    "
            for line in lines:
                edited = False
                if default_section in line:
                    this_section = True
                if this_section:
                    if parameter in line:
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

   

def modify_gyre_params(LOGS_dir, filename, data_format):
    if data_format == "GYRE":
        file_format = "MESA"
    elif data_format == "FGONG":
        file_format = "FGONG"
    writetoGyreFile(LOGS_dir, parameter="model_type", value="'EVOL'", default_section="&model")
    writetoGyreFile(LOGS_dir, parameter="file_format", value=f"'{file_format}'", default_section="&model")
    writetoGyreFile(LOGS_dir, parameter="file", value=f"'{filename}'", default_section="&model")
    writetoGyreFile(LOGS_dir, parameter="summary_file", value=f"'{filename.split('.')[0]}-freqs.dat'", default_section="&ad_output")
    writetoGyreFile(LOGS_dir, parameter="summary_file", value="'freq_output_nonad.txt'", default_section="&nad_output")