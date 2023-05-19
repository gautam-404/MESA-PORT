import subprocess
import shlex
import sys, os, glob
import shutil
from rich import print

from ..MesaFileHandler.support import *
from ..MesaFileHandler.access_helper import toFortranType, toPythonType
from ..MesaFileHandler import MesaAccess

def check_exists(exists, projName):
        """Checks if the project exists."""
        if not exists:
            raise FileNotFoundError(f"Project '{projName}' does not exist. Please create it first.")


def run_subprocess(commands, wdir, silent=True, runlog='', status=None, 
                    gyre=False, filename="", data_format="FGONG", parallel=False, 
                    gyre_in="gyre.in", gyre_input_params=None, trace=None):
    """Runs a subprocess.

    Args:
        commands (str or list): Command to be run.
        wdir (str): Directory in which the command is to be run.
        silent (bool, optional): Run the command silently. Defaults to False.
        runlog (str, optional): Log file to write the output to. Defaults to ''.
        status (rich.status.Status, optional): Status to update. Defaults to status.Status("Running...").
        gyre (bool, optional): Whether the command is a gyre command. Defaults to False.
        filename (str, optional): The name of the file to be used by gyre. Defaults to None.
        data_format (str, optional): The format of the data to be used by gyre. Defaults to None.
        parallel (bool, optional): Whether the command is a parallel gyre command. Defaults to False.
        gyre_in (str, optional): The name of the gyre input file. Defaults to "gyre.in".
        gyre_input_params (dict, optional): The parameters to be written to the gyre input file. Defaults to None.
    Returns:
        bool: True if the command ran successfully, False otherwise.
    """      
    if gyre:
        if parallel:
            num = filename.split(".")[0]
            shutil.copy(gyre_in, os.path.join(wdir, f"gyre{num}.in"))
            gyre_in = os.path.join(wdir, f"gyre{num}.in")
            commands = commands.replace("gyre.in", f"gyre{num}.in")
        if gyre_input_params is not None:
            for parameter, value in gyre_input_params.items():
                writetoGyreFile(wdir, parameter, toFortranType(value), gyre_in=gyre_in)
        modify_gyre_params(wdir, filename, data_format, gyre_in=gyre_in) 

    evo_terminated = False
    if trace is not None:
        trace_values = [None for i in range(len(trace))]
    with subprocess.Popen(shlex.split(commands), bufsize=0, cwd=wdir,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True) as proc:
        with open(runlog, "a+") as logfile:
            for outline in proc.stdout:
                logfile.write(outline)
                logfile.flush()
                if silent is False:
                    sys.stdout.write(outline)
                elif not gyre:
                    if "terminated evolution:" in outline:
                        evo_terminated = True
                    age = process_outline(outline)
                    if age is not None:
                        if age < 1/365:
                            age_str = f"[b]Age: [cyan]{age*365*24:.4f}[/cyan] hours"
                        elif 1/365 < age < 1:
                            age_str = f"[b]Age: [cyan]{age*365:.4f}[/cyan] days"
                        elif 1 < age < 1000:
                            age_str = f"[b]Age: [cyan]{age:.3f}[/cyan] years"
                        else:
                            age_str = f"[b]Age: [cyan]{age:.3e}[/cyan] years"
                    if trace is not None:
                        trace_values = process_trace(trace, outline, trace_values)
                        trace_ = [trace[i] for i in range(len(trace)) if trace_values[i] is not None]
                        values = [val for val in trace_values if val is not None]
                        if len(values) > 0 and parallel is False:
                            trace_str = ""
                            for i in range(len(trace_)):
                                trace_str += f"[b]{trace_[i]}[/b]: [cyan]{values[i]:.5f}[/cyan]\n"
                            status.update(status=f"[b i cyan3]Running....[/b i cyan3]\n"+age_str+"\n"+trace_str, spinner="moon")
                        elif parallel is False and age is not None:
                            status.update(status=f"[b i cyan3]Running....[/b i cyan3]\n"+age_str, spinner="moon")
                    elif parallel is False and age is not None:
                        status.update(status=f"[b i cyan3]Running....[/b i cyan3]\n"+age_str, spinner="moon")
            for errline in proc.stderr:
                logfile.write(errline)
                sys.stdout.write(errline)
            logfile.write( "\n\n"+("*"*100)+"\n\n" )

        _data, error = proc.communicate()
    if gyre:
        working_dir = wdir.replace("LOGS", "")
        with open(f'{working_dir}/gyre.log', 'a+') as f:
            f.write(f"Done with {filename}.\n")
        if parallel:
            os.remove(gyre_in)
    if proc.returncode or error:
        print('The process raised an error:', proc.returncode, error)
        return False
    elif evo_terminated:
        return False
    else:
        return True

def process_outline(outline):
    try:
        keyword1 = outline.split()[-1]
        keyword2 = outline.split()[-2] + " " + outline.split()[-1]
        keyword3 = outline.split()[-3] + " " + outline.split()[-2] + " " + outline.split()[-1]
        if keyword1 in dt_limit_values or keyword2 in dt_limit_values or keyword3 in dt_limit_values:
            return float(outline.split()[0])
        else:
            return None
    except:
        return None

def setup_trace(trace, work_dir):
    if isinstance(trace, str):
        trace = [trace]
    elif isinstance(trace, list):
        pass
    else:
        raise TypeError("Trace must be a string or a list of strings.")
    star = MesaAccess(work_dir)
    num_trace_history_values = star.get("num_trace_history_values")
    for tr in trace:
        exists = False
        for i in range(num_trace_history_values+1):
            if tr == star.get(f'trace_history_value_name({i+1})'):
                exists = True
                break
        if not exists:
            num_trace_history_values += 1
            star.set({f'trace_history_value_name({num_trace_history_values})': f'{tr}'})
    star.set({'num_trace_history_values': num_trace_history_values})


def process_trace(trace, outline, values):
    if isinstance(trace, str):
        trace = [trace]
    splitline = outline.split()
    for i in range(len(trace)):
        if trace[i] in splitline:
            try:
                values[i] = float(toPythonType(splitline[1]))
            except:
                pass
    return values
            

def gyreDefaults():
    """Reads the defaults files and returns a dictionary with all the parameters and their values.
    Returns:
        dict: A dictionary with all the parameters and their values.
    """    
    gyre_dir = os.path.abspath(os.environ["GYRE_DIR"])
    gyre_defaults_dir = os.path.join(gyre_dir, "doc/source/ref-guide/input-files/*")
    defaultsFiles = glob.glob(gyre_defaults_dir)
    # sections = ["&"+name.split("/")[-1].split('.')[0].split('-')[0] for name in defaultsFiles]
    # print(sections)
    section_parameters = {}
    for i, file in enumerate(defaultsFiles):
        params = []
        sections = []
        with open(file) as file:
            for line in file:
                if ":nml_g:" in line:
                    splits = line.split(":nml_g:")
                    for s in splits:
                        if "`" in s:
                            sections.append("&"+s.split("`")[1])
                if ":nml_n:" in line:
                    params.append(line.split(":nml_n:")[1].split("`")[1])
        sections = list(set(sections))
        for section in sections:
            section_parameters[section] = params
    return section_parameters


def writetoGyreFile(wdir, parameter, value, default_section=None, gyre_in="gyre.in"):
    """Writes the parameter and its value to the inlist file.

    Args:
        filename (str): The path to the inlist file.
        parameter (str): The parameter to be written.
        value (str): The value of the parameter to be written.
        default_section (str): The section in which the parameter is to be written.
        sections (list): A list with the sections of the inlist file.
    """   
    if default_section is None:
        for section, values in gyreDefaults().items():
            if parameter in values:
                default_section = section
        if default_section is None:
            raise(f"Parameter {parameter} not found in any GYRE input files.")
    this_section = False
    with cd(wdir):
        with open(gyre_in, "r") as file:
            lines = file.readlines()
        with open(gyre_in, "w+") as f:
            indent = "    "
            for line in lines:
                edited = False
                if default_section in line:
                    this_section = True
                if this_section:
                    if parameter in line:
                        if parameter == line.split("=")[0].strip():
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

   

def modify_gyre_params(LOGS_dir, filename, data_format, gyre_in="gyre.in"):
    if data_format == "GYRE":
        file_format = "MESA"
    elif data_format == "FGONG":
        file_format = "FGONG"
    writetoGyreFile(LOGS_dir, parameter="model_type", value="'EVOL'", default_section="&model", gyre_in=gyre_in)
    writetoGyreFile(LOGS_dir, parameter="file_format", value=f"'{file_format}'", default_section="&model", gyre_in=gyre_in)
    writetoGyreFile(LOGS_dir, parameter="file", value=f"'{filename}'", default_section="&model", gyre_in=gyre_in)
    writetoGyreFile(LOGS_dir, parameter="summary_file", value=f"'{filename.split('.')[0]}-freqs.dat'", default_section="&ad_output", gyre_in=gyre_in)
    writetoGyreFile(LOGS_dir, parameter="summary_file", value="'freq_output_nonad.txt'", default_section="&nad_output", gyre_in=gyre_in)


dt_limit_values = ['burn steps', 'Lnuc', 'Lnuc_cat', 'Lnuc_H', 'Lnuc_He', 'lgL_power_phot', 'Lnuc_z', 'bad_X_sum',
                  'dH', 'dH/H', 'dHe', 'dHe/He', 'dHe3', 'dHe3/He3', 'dL/L', 'dX', 'dX/X', 'dX_nuc_drop', 'delta mdot',
                  'delta total J', 'delta_HR', 'delta_mstar', 'diff iters', 'diff steps', 'min_dr_div_cs', 'dt_collapse',
                  'eps_nuc_cntr', 'error rate', 'highT del Ye', 'hold', 'lgL', 'lgP', 'lgP_cntr', 'lgR', 'lgRho', 'lgRho_cntr',
                  'lgT', 'lgT_cntr', 'lgT_max', 'lgT_max_hi_T', 'lgTeff', 'dX_div_X_cntr', 'lg_XC_cntr', 'lg_XH_cntr', 
                  'lg_XHe_cntr', 'lg_XNe_cntr', 'lg_XO_cntr', 'lg_XSi_cntr', 'XC_cntr', 'XH_cntr', 'XHe_cntr', 'XNe_cntr',
                  'XO_cntr', 'XSi_cntr', 'log_eps_nuc', 'max_dt', 'neg_mass_frac', 'adjust_J_q', 'solver iters', 'rel_E_err',
                  'varcontrol', 'max increase', 'max decrease', 'retry', 'b_****']