import os

from .mesaurls import *


def choose_directory(directory=''):
    """Choose a directory to install MESA.

    Args:
        directory (str, optional):
        Path to a directory to install MESA and MESA SDK. CLI is used to choose directory if not specified.

    Returns:
        str: Path to a directory to install MESA and MESA SDK.
    """        
    while not os.path.exists(directory):
        directory = input("\nInput path to a directory for installation...    ")
    software_directory = os.path.join(directory, "software")
    print(f"MESA SDK and MESA will be installed at path: {directory}/software/\n")
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
        versions = linux_versions
    elif ostype == "macOS-Intel":
        versions = mac_intel_versions
    elif ostype == "macOS-ARM":
        versions = mac_arm_versions
    while ver not in versions:
        print("Versions available through this insaller are:")
        print(versions, '\n')
        ver = input("Input the desired version...")
        if ver not in versions:
            print("Version not recognised, try again.\n")
    return ver