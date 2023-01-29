import os

from . import mesaurls
from rich import prompt, print

def choose_directory(directory=''):
    """Choose a directory to install MESA.

    Args:
        directory (str, optional):
        Path to a directory to install MESA and MESA SDK. CLI is used to choose directory if not specified.

    Returns:
        str: Path to a directory to install MESA and MESA SDK.
    """   
    directory = prompt.Prompt.ask("\n[bold cyan]Input path to a directory for installation[/bold cyan]")     
    while not os.path.exists(directory):
        print("[red]Directory does not exist. Please try again.[/red]")
        directory = prompt.Prompt.ask("\nInput path to a directory for installation...")
    software_directory = os.path.join(directory, "software")
    print(f"[blue]MESA SDK and MESA will be installed at path: {directory}/software/ [/blue]\n")
    if not os.path.exists(software_directory):
        os.mkdir(software_directory)
    return os.path.abspath( software_directory )


def choose_ver(ostype, ver=''):
    """Choose a version of MESA to install.

    Args:
        ver (str, optional): 
        Version of MESA to install. CLI is used to choose version if not specified.

    Returns:
        str: Version of MESA to install.
    """        
    if ostype == "Linux":
        versions = mesaurls.linux_versions
    elif ostype == "macOS-Intel":
        versions = mesaurls.mac_intel_versions
    elif ostype == "macOS-ARM":
        versions = mesaurls.mac_arm_versions
    while ver not in versions:
        print("Versions available through this insaller are:")
        print(versions, '\n')
        ver = prompt.Prompt.ask("[bold cyan]Input the version of MESA to install[/bold cyan]")
        if ver not in versions:
            print("Version not recognised, try again.\n")
    return ver