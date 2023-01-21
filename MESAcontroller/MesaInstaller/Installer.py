import os
import platform
import shlex
import shutil
import subprocess
import tarfile
import zipfile

import cpuinfo
import requests
from alive_progress import alive_bar
from rich.console import Console

from .mesaurls import *

console = Console()

class Installer:
    """Class for installing MESA and MESA SDK.
    """    
    def __init__(self, version='', parentDir='', cleanAfter=False):
        """Constructor for Installer class.

        Args:
            version (str, optional): 
            Version of MESA to install. CLI is used to choose version if not specified.

            parentDir (str, optional): 
            Path to a directory to install MESA and MESA SDK. CLI is used to choose directory if not specified.

            cleanAfter (bool, optional): 
            If True, the downloaded MESA SDK and MESA zip files will be deleted after installation. Defaults to False.
        """     
        self.cleanAfter = cleanAfter
        self.directory = self.choose_directory(parentDir)
        self.ostype = self.whichos()
        print(f"OS type: {self.ostype}\n")
        self.install(version)
        return



    def whichos(self):
        """Determine the OS type.

        Raises:
            OSError: If OS is not compatible.

        Returns:
            str: OS type. 
        """
        if "macOS" in platform.platform():
            manufacturer = cpuinfo.get_cpu_info().get('brand_raw')
            arch = 'Intel' if 'intel' in manufacturer.lower() else 'ARM'
            return f"macOS-{arch}"
        elif "Linux" in platform.platform():
            return "Linux"
        else:
            raise OSError(f"OS {platform.platform()} not compatible.")



    def choose_directory(self, directory=''):
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


    def choose_ver(self, ver=''):
        """Choose a version of MESA to install.

        Args:
            ver (str, optional): 
            Version of MESA to install. CLI is used to choose version if not specified.

        Returns:
            str: Version of MESA to install.
        """        
        if self.ostype == "Linux":
            versions = linux_versions
        elif self.ostype == "macOS-Intel":
            versions = mac_intel_versions
        elif self.ostype == "macOS-ARM":
            versions = mac_arm_versions
        while ver not in versions:
            print("Versions available through this insaller are:")
            print(versions, '\n')
            ver = input("Input the desired version...")
            if ver not in versions:
                print("Version not recognised, try again.\n")
        return ver



    def prep_urls(self, ver):
        """Prepare the URLs for the MESA SDK and MESA zip files.

        Args:
            ver (str): Version of MESA to install. 

        Returns:
            tuple: URLs for the MESA SDK and MESA zip files.
        """        
        if self.ostype == "Linux":
            sdk_url = linux_sdk_urls.get(ver)
            mesa_url = mesa_urls.get(ver)
        elif self.ostype == "macOS-Intel":
            sdk_url = mac_intel_sdk_urls.get(ver)
            mesa_url = mesa_urls.get(ver)
        elif self.ostype == "macOS-ARM":
            sdk_url = mac_arm_sdk_urls.get(ver)
            mesa_url = mesa_urls.get(ver)
        return sdk_url, mesa_url


    def check_n_download(self, filepath, url):
        """Check if a file has already been downloaded, and if not, download it.

        Args:
            filepath (str): Path to the file to be downloaded. 
            url (str): URL of the file to be downloaded.
        """        
        if os.path.exists(filepath) and int(requests.head(url, timeout=10).headers['content-length']) == os.path.getsize(filepath):
            print("Skipping download! File already downloaded.\n")
        else:
            chunk_size = 11*1024*1024
            response = requests.get(url, stream=True, timeout=10)
            total = int(response.headers.get('content-length', 0))
            with open(filepath, 'wb') as file, alive_bar(total, unit='B', scale=True) as progressbar:
                for chunk in response.raw.stream(chunk_size, decode_content=False):
                    if chunk:
                        size_ = file.write(chunk)
                        progressbar(size_)
            print("Download complete.\n")

    def download(self, sdk_url, mesa_url):
        """Download the MESA SDK and MESA zip files.

        Args:
            sdk_url (str): URL of the MESA SDK.
            mesa_url (str): URL of the MESA zip file.

        Returns:
            tuple: Paths to the downloaded MESA SDK and MESA zip files.
        """        
        print("Downloading MESA SDK...")
        sdk_download = os.path.join(self.directory, sdk_url.split('/')[-1])
        self.check_n_download(sdk_download, sdk_url)

        print("Downloading MESA...")
        mesa_zip = os.path.join(self.directory, mesa_url.split('/')[-1])
        self.check_n_download(mesa_zip, mesa_url)
        return sdk_download, mesa_zip


    def install_pre_reqs(self, logfile):
        """Install the pre-requisites for MESA.

        Args:
            logfile (file): File to write the output of the installation to.
        """        
        if self.ostype == "Linux":
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
        if "macOS" in self.ostype:
            print("Installing XCode Command Line Tools...")
            subprocess.Popen(shlex.split("sudo xcode-select --install"), stdout=logfile, stderr=logfile).wait()
            
            if not os.path.exists("/Applications/Utilities/XQuartz.app"):
                xquartz = os.path.join(self.directory, url_xquartz.split('/')[-1])
                print("Downloading XQuartz...")
                self.check_n_download(xquartz, url_xquartz)

                print("Installing XQuartz...")
                subprocess.Popen(shlex.split(f"sudo installer -pkg {xquartz} -target /"), stdout=logfile, stderr=logfile).wait()
                if self.cleanAfter:
                    os.remove(xquartz)
        


    def extract_mesa(self, sdk_download, mesa_zip, logfile):
        """Extract the MESA SDK and MESA zip files.

        Args:
            sdk_download (path): Path to the downloaded MESA SDK.
            mesa_zip (path): Path to the downloaded MESA zip file.
            logfile (file): File to write the output logs of the installation to.
        """        
        if self.ostype == "Linux":
            with console.status("Extracting MESA Linux SDK", spinner="moon"):
                with tarfile.open(sdk_download, 'r:gz') as tarball:
                    if os.path.exists( os.path.join(self.directory, 'mesasdk') ):
                        shutil.rmtree( os.path.join(self.directory, 'mesasdk') )
                    tarball.extractall(self.directory )
                if self.cleanAfter:
                    os.remove(sdk_download)
            print("MESA Linux SDK extraction complete.\n")
        elif "macOS" in self.ostype:
            with console.status("Installing MESA SDK package for macOS", spinner="moon"):
                subprocess.Popen(shlex.split(f"sudo installer -pkg {sdk_download} -target /"),
                                stdout=logfile, stderr=logfile).wait()
                if self.cleanAfter:
                    os.remove(sdk_download)
                print("MESA SDK package installation complete.\n")

        with console.status("Extracting MESA", spinner="moon"):
            with zipfile.ZipFile(mesa_zip, 'r') as zip_ref:
                zip_ref.extractall(self.directory)
            if self.cleanAfter:
                os.remove(mesa_zip)
        print("MESA extraction complete.\n")


    def write_env_vars(self, mesa_dir, sdk_dir):
        """Write the environment variables to the shell .rc file.

        Args:
            mesa_dir (path): Path to the MESA directory.
            sdk_dir (path): Path to the MESA SDK directory.
        """        
        source_this=f'''

        ############ MESA environment variables ###############
        export MESASDK_ROOT={sdk_dir}
        source $MESASDK_ROOT/bin/mesasdk_init.sh
        export MESA_DIR={mesa_dir}
        export OMP_NUM_THREADS=2      ## max should be 2 times the cores on your machine
        export GYRE_DIR=$MESA_DIR/gyre/gyre
        #######################################################

        '''

        env_shell = os.environ['SHELL'].split('/')[-1]
        if env_shell == "bash":
            env_file = os.path.join(os.environ['HOME'], ".bashrc")
        elif env_shell == "zsh":
            env_file = os.path.join(os.environ['HOME'], ".zshrc")
        elif env_shell == "csh":
            env_file = os.path.join(os.environ['HOME'], ".cshrc")
        elif env_shell == "tcsh":
            env_file = os.path.join(os.environ['HOME'], ".tcshrc")
        else:
            env_file = os.path.join(os.environ['HOME'], ".profile")
        
        with open(env_file, "a") as f:
            f.write(source_this)

        print(f"The following environment variables have been written to your ~/{env_file} file:")
        print(source_this)
        print("To activate these variables in your current shell, run the following command:\n")
        print(f"source ~/{env_file}\n") 

        




    def install(self, ver):
        """Install MESA.

        Args:
            ver (str): MESA version to install.
        """        
        ver = self.choose_ver(ver)
        sdk_url, mesa_url = self.prep_urls(ver)
        sdk_download, mesa_zip = self.download(sdk_url, mesa_url)
        mesa_dir = os.path.join(self.directory, mesa_zip.split('/')[-1][0:-4])

        with open(f"install_log.txt", "w+") as logfile:
            ## to get sudo password prompt out of the way
            subprocess.Popen(shlex.split("sudo echo"), stdin=subprocess.PIPE, stdout=logfile, stderr=logfile).wait()    
            with console.status("Installing pre-requisites", spinner="moon"):
                self.install_pre_reqs(logfile)
            self.extract_mesa(sdk_download, mesa_zip, logfile)

            with console.status("Installing MESA", spinner="moon"):
                if self.ostype == "Linux":
                    sdk_dir = os.path.join(self.directory, 'mesasdk')
                elif "macOS" in self.ostype:
                    sdk_dir = '/Applications/mesasdk'

                with subprocess.Popen(f"/bin/bash -c \"export MESASDK_ROOT={sdk_dir} && \
                            source $MESASDK_ROOT/bin/mesasdk_init.sh && gfortran --version\"",
                            shell=True, stdout=logfile, stderr=logfile) as proc:
                    proc.wait()
                    if proc.returncode != 0:
                        raise Exception("MESA SDK initialization failed. \
                            Please check the install_log.txt file for details.")

                run_in_shell = f'''
                /bin/bash -c \"
                export MESASDK_ROOT={sdk_dir} \\
                && source $MESASDK_ROOT/bin/mesasdk_init.sh \\
                && export MESA_DIR={mesa_dir} \\
                && export OMP_NUM_THREADS=2 \\
                && chmod -R +x {mesa_dir} \\
                && cd {mesa_dir} && ./clean  && ./install \\
                && export GYRE_DIR={mesa_dir}/gyre/gyre\"
                '''
                with subprocess.Popen(run_in_shell, shell=True, stdout=logfile, stderr=logfile) as proc:
                    proc.wait()
                    if proc.returncode != 0:
                        raise Exception("MESA installation failed. \
                            Please check the install_log.txt file for details.")
                    else:
                        logfile.write("MESA installation complete.\n")

                ## MESA installs GYRE by default now
                # run_in_shell = f"/bin/bash -c \"export GYRE_DIR={mesa_dir}/gyre/gyre && \
                #                 cd {mesa_dir}/gyre/gyre && make\""
                # with subprocess.Popen(run_in_shell,
                #                     shell=True, stdout=logfile, stderr=logfile) as proc:
                #     proc.wait()
                #     if proc.returncode != 0:
                #         raise Exception("GYRE installation failed. \
                #             Please check the install_log.txt file for details.")
                #     else:
                #         logfile.write("GYRE installation complete.\n")

                logfile.write("Build Successful.\n")

        self.write_env_vars(mesa_dir, sdk_dir)
        print("Installation complete.\n")
