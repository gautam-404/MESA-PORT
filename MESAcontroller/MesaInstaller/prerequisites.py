import os
import shlex
import subprocess

from .mesaurls import *


def install_prerequisites(directory, ostype, cleanAfter, logfile):
        """Install the pre-requisites for MESA.

        Args:
            logfile (file): File to write the output of the installation to.
        """        
        if ostype == "Linux":
            subprocess.Popen(shlex.split("sudo apt-get update"), stdout=logfile, stderr=logfile).wait()
            try:
                subprocess.Popen(shlex.split("sudo apt-get install -yq build-essential wget curl binutils make perl libx11-6 \
                    libx11-dev zlib1g zlib1g-dev tcsh"), stdout=logfile, stderr=logfile).wait()
            except:
                try:
                    subprocess.Popen(shlex.split("sudo apt-get install -yq binutils make perl libx11-6 libx11-dev zlib1g zlib1g-dev tcsh"),
                                stdout=logfile, stderr=logfile).wait()
                except:
                    try:
                        subprocess.Popen(shlex.split("sudo apt-get install -yq binutils make perl libx11 zlib tcsh glibc"),
                                    stdout=logfile, stderr=logfile).wait()
                    except:
                        pass           
        if "macOS" in ostype:
            print("Installing XCode Command Line Tools...")
            subprocess.Popen(shlex.split("sudo xcode-select --install"), stdout=logfile, stderr=logfile).wait()
            
            if not os.path.exists("/Applications/Utilities/XQuartz.app"):
                xquartz = os.path.join(directory, url_xquartz.split('/')[-1])   

                print("Installing XQuartz...")
                subprocess.Popen(shlex.split(f"sudo installer -pkg {xquartz} -target /"), stdout=logfile, stderr=logfile).wait()
                if cleanAfter:
                    os.remove(xquartz)