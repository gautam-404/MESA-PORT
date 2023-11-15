import subprocess
import shlex
import sys, os, glob, time
import shutil
from rich import print

from ..Access.support import *
from ..Access.access_helper import toFortranType, toPythonType
from ..Access import MesaAccess, GyreAccess

def check_exists(exists, projName):
        """Checks if the project exists."""
        if not exists:
            raise FileNotFoundError(f"Project '{projName}' does not exist. Please create it first.")


def run_subprocess(commands, wdir, silent=True, runlog='', status=None, 
                    filename="", data_format="FGONG", parallel=False, 
                    gyre_in=None, gyre_input_params=None, trace=None, env=None):
    
    """
    Runs a subprocess with the given commands.

    Args:
    commands (str): The commands to be run.
    wdir (str): The working directory.
    silent (bool, optional): If True, the output of the subprocess is not printed. Defaults to True.
    runlog (str, optional): The path to the runlog file. Defaults to ''.
    status (rich.status.Status, optional): The status bar. Defaults to None.
    gyre (bool, optional): If True, the subprocess is a GYRE run. Defaults to False.
    filename (str, optional): The name of the file to be used in the GYRE run. Defaults to "".
    data_format (str, optional): The data format of the file to be used in the GYRE run. Defaults to "FGONG".
    parallel (bool, optional): If True, the subprocess is a parallel GYRE run. Defaults to False.
    gyre_in (str, optional): The path to the GYRE input file. Defaults to "gyre.in".
    gyre_input_params (dict, optional): A dictionary with the parameters to be changed in the GYRE input file. Defaults to None.
    trace (str or list, optional): The trace to be followed in the GYRE run. Defaults to None.
    env (dict, optional): The environment variables. Defaults to None. 
                Pass os.environ.copy() to use the current environment. Or pass a dictionary with the environment variables to be used.
    """   
    if gyre_in is not None:
        # if not os.path.exists(os.path.join(wdir, "gyre.in")):
        #     gyre_obj.load(gyre_in=gyre_in, dest=wdir)
        if parallel:
            num = filename.split(".")[0]
            new_gyre_in = os.path.join(wdir, f"gyre{num}.in")
            if os.path.exists(new_gyre_in):
                os.remove(new_gyre_in)
            # shutil.copy2(gyre_in, new_gyre_in)
            shutil.copyfile(gyre_in, new_gyre_in)
            gyre_in = new_gyre_in
            commands = commands.replace("gyre.in", f"gyre{num}.in")
        else:
            # shutil.copy2(gyre_in, os.path.join(wdir, f"gyre.in"))
            shutil.copyfile(gyre_in, os.path.join(wdir, f"gyre.in"))
            gyre_in = os.path.join(wdir, f"gyre.in")
        gyre_obj = GyreAccess(wdir)
        gyre_obj.modify_gyre_params(wdir, filename, data_format, gyre_in=gyre_in)
        gyre_obj.set(arg=gyre_input_params, gyre_in=gyre_in)

    evo_terminated = False
    termination_code = None
    if trace is not None:
        trace_values = [None for i in range(len(trace))]
    with subprocess.Popen(shlex.split(commands), bufsize=0, cwd=wdir, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True) as proc:
        with open(runlog, "a+") as logfile:
            for outline in proc.stdout:
                logfile.write(outline)
                logfile.flush()
                if silent is False:
                    sys.stdout.write(outline)
                elif gyre_in is not None:
                    if "terminated evolution:" in outline or "ERROR" in outline:
                        evo_terminated = True
                        termination_code = outline.split()[-1]
                    if "termination code:" in outline:
                        evo_terminated = True
                        termination_code = outline.split()[-1]
                    if "photo" in outline and "does not exist" in outline:
                        evo_terminated = True
                        termination_code = "photo does not exist"
                    if not parallel:
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
                            elif age is not None:
                                status.update(status=f"[b i cyan3]Running....[/b i cyan3]\n"+age_str, spinner="moon")
                        elif age is not None:
                            status.update(status=f"[b i cyan3]Running....[/b i cyan3]\n"+age_str, spinner="moon")
            for errline in proc.stderr:
                logfile.write(errline)
                sys.stdout.write(errline)
            logfile.write( "\n\n"+("*"*100)+"\n\n" )
        _data, error = proc.communicate()
    if proc.returncode or error:
        print('The process raised an error:', proc.returncode, error)
        return False
    elif evo_terminated and termination_code == None:
        return False
    else:
        if gyre_in is None:
            age = 0
            with open(runlog, "r") as logfile:
                for line in logfile.readlines():
                    age_ = process_outline(line)
                    if age_ is not None:
                        age = age_
            return termination_code, age
        else:
            working_dir = wdir.replace("LOGS", "")
            with open(f'{working_dir}/gyre.log', 'a+') as f:
                f.write(f"Done with {filename}.\n")
            if parallel:
                os.remove(gyre_in)
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
    if num_trace_history_values is None:
        num_trace_history_values = star.getDefault("num_trace_history_values")
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

dt_limit_values = ['burn steps', 'Lnuc', 'Lnuc_cat', 'Lnuc_H', 'Lnuc_He', 'lgL_power_phot', 'Lnuc_z', 'bad_X_sum',
                  'dH', 'dH/H', 'dHe', 'dHe/He', 'dHe3', 'dHe3/He3', 'dL/L', 'dX', 'dX/X', 'dX_nuc_drop', 'delta mdot',
                  'delta total J', 'delta_HR', 'delta_mstar', 'diff iters', 'diff steps', 'min_dr_div_cs', 'dt_collapse',
                  'eps_nuc_cntr', 'error rate', 'highT del Ye', 'hold', 'lgL', 'lgP', 'lgP_cntr', 'lgR', 'lgRho', 'lgRho_cntr',
                  'lgT', 'lgT_cntr', 'lgT_max', 'lgT_max_hi_T', 'lgTeff', 'dX_div_X_cntr', 'lg_XC_cntr', 'lg_XH_cntr', 
                  'lg_XHe_cntr', 'lg_XNe_cntr', 'lg_XO_cntr', 'lg_XSi_cntr', 'XC_cntr', 'XH_cntr', 'XHe_cntr', 'XNe_cntr',
                  'XO_cntr', 'XSi_cntr', 'log_eps_nuc', 'max_dt', 'neg_mass_frac', 'adjust_J_q', 'solver iters', 'rel_E_err',
                  'varcontrol', 'max increase', 'max decrease', 'retry', 'b_****']
