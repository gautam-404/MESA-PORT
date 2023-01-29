import subprocess
import shlex
import sys
from rich import status

def check_exists(exists, projName):
        """Checks if the project exists."""
        if not exists:
            raise FileNotFoundError(f"Project '{projName}' does not exist. Please create it first.")


def run_subprocess(commands, dir, silent=False, runlog='', status=status.Status("Running...")):
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
                step, age = process_outline(outline, step)
                if silent is False:
                    sys.stdout.write(outline)
                elif age is not None:
                    status.update(status=f"[b i cyan3]Running....[/b i cyan3]\n[b]Current age: [cyan]{age}[/cyan] years")
                    # print(f"Current age: {age} years", end='\r')
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
