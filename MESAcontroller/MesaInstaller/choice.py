import os

from rich import print, prompt

from . import mesaurls

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
        directory = prompt.Prompt.ask("\n[bold cyan]Input path to a directory for installation[/bold cyan]")
    software_directory = os.path.join(directory, "software")
    print(f"MESA will be installed at path: [green]{directory}/software/ [/green]\n")
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
            print("[red]Version not recognised, try again.[/red]\n")

    if ostype == "Linux":
        sdk = mesaurls.linux_sdk_urls.get(ver).split('-')[-1][:-7]
        mesa = mesaurls.mesa_urls.get(ver).split('-')[-1][:-4]
    elif ostype == "macOS-Intel":
        sdk = mesaurls.mac_intel_sdk_urls.get(ver).split('-')[-1][:-4]
        mesa = mesaurls.mesa_urls.get(ver).split('-')[-1][:-4]
    elif ostype == "macOS-ARM":
        sdk = mesaurls.mac_arm_sdk_urls.get(ver).split('-')[-1][:-4]
        mesa = mesaurls.mesa_urls.get(ver).split('-')[-1][:-4]
    print("The following will be installed:")
    print(f"MESA SDK version: [green b]{sdk}[/green b]")
    print(f"MESA version: [green b]{mesa}[/green b]\n")
    return ver
