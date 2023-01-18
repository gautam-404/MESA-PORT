import os, shutil, sys
import platform
import tarfile
import zipfile
import subprocess 
import cpuinfo
from .mesaurls import *

import requests
from alive_progress import alive_bar
from rich.console import Console

console = Console()

class Installer:
    def __init__(self, version='', parent_directory=''):
        self.directory = self.choose_directory(parent_directory)
        self.ostype = self.whichos()
        self.install(version)
        return



    def whichos(self):
        if "macOS" in platform.platform():
            manufacturer = cpuinfo.get_cpu_info().get('brand_raw')
            arch = 'intel' if 'Intel' in manufacturer.lower() else 'arm'
            return f"macOS-{arch}"
        elif "Linux" in platform.platform():
            return "Linux"
        else:
            raise OSError(f"OS {platform.platform()} not compatible.")



    def choose_directory(self, directory=''):
        while not os.path.exists(directory):
            directory = input("Input path to a directory for installation...    ")
            software_directory = os.path.join(directory, "software")
            if os.path.exists(directory):
                print(f"MESA SDK and MESA will be installed at path: {directory}/software/\n")
                if not os.path.exists( software_directory ):
                    os.mkdir( software_directory )
                return os.path.abspath( software_directory )
            else:
                print("Could not find the specified directory. Please try again.\n")
                directory = ''
        if not os.path.exists():
            os.mkdir(os.path.join(directory, "software"))
        return os.path.abspath(os.path.join(directory, "software"))



    def choose_ver(self, ver=''):
        if self.ostype == "Linux":
            versions = linux_versions
        elif self.ostype == "macOS-intel":
            versions = mac_intel_versions
        elif self.ostype == "macOS-arm":
            versions = mac_arm_versions
        while ver not in versions:
            print("Versions available through this insaller are:")
            print(versions, '\n')
            ver = input("Input the desired version...")
            if ver not in versions:
                print("Not recognised, try again.\n")
        return ver



    def prep_urls(self, ver):
        if self.ostype == "Linux":
            sdk_url = linux_sdk_urls[ver]
            mesa_url = mesa_urls[ver]
        elif self.ostype == "macOS-intel":
            sdk_url = mac_intel_sdk_urls[ver]
            mesa_url = mesa_urls[ver]
        elif self.ostype == "macOS-arm":
            sdk_url = mac_arm_sdk_urls[ver]
            mesa_url = mesa_urls[ver]
        return sdk_url, mesa_url


    def check_n_download(filepath, url):
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
        print("Downloading MESA SDK...")
        sdk_download = os.path.join(self.directory, sdk_url.split('/')[-1])
        self.check_n_download(sdk_download, sdk_url)

        print("Downloading MESA...")
        mesa_zip = os.path.join(self.directory, mesa_url.split('/')[-1])
        self.check_n_download(mesa_zip, mesa_url)
        return sdk_download, mesa_zip



    def install_pre_reqs(self, logfile):
        if self.ostype == "Linux":
            subprocess.call("sudo apt-get update", shell=True, stdout=logfile, stderr=logfile)
            try:
                subprocess.call("sudo apt-get install -yq build-essential wget curl binutils make perl libx11-6 \
                libx11-dev zlib1g zlib1g-dev tcsh", shell=True, stdout=logfile, stderr=logfile)
            except:
                try:
                    subprocess.call("sudo apt-get install -yq binutils make perl libX11 libX11-devel zlib zlib-devel tcsh",\
                     shell=True, stdout=logfile, stderr=logfile)
                except:
                    try:
                        subprocess.call("sudo apt-get install -yq binutils make perl libx11 zlib tcsh glibc",\
                         shell=True, stdout=logfile, stderr=logfile)
                    except:
                        pass           
        if "macOS" in self.ostype:
            subprocess.call("xcode-select --install", shell=True, stdout=logfile, stderr=logfile)
            xquartz = os.path.join(self.directory, url_xquartz.split('/')[-1])
            self.check_n_download(xquartz, url_xquartz)
            subprocess.call(f"sudo installer -pkg {xquartz} -verbose -target /", shell=True, stdout=logfile, stderr=logfile) 
            os.remove(xquartz)


    def print_env_vars(self, mesa_dir):
        source_this=f'''
        export MESASDK_ROOT={self.directory}/mesasdk
        source $MESASDK_ROOT/bin/mesasdk_init.sh
        export MESA_DIR={mesa_dir}
        export OMP_NUM_THREADS=2
        export GYRE_directory=$MESA_DIR/gyre/gyre
        '''
        print("Please add the following to the appropriate shell start-up file (~/.*rc or ~/.*profile):")
        print(source_this)
        


    def extract_mesa(self, sdk_download, mesa_zip, logfile):
        if self.ostype == "Linux":
            with console.status("Extracting MESA SDK...", spinner="moon"):
                with tarfile.open(sdk_download, 'r:gz') as tarball:
                    if os.path.exists( os.path.join(self.directory, 'mesasdk') ):
                        shutil.rmtree( os.path.join(self.directory, 'mesasdk') )
                    tarball.extractall( {self.directory} )
                # os.remove(sdk_download)
            print("MESA SDK extraction complete.\n")
        elif "macOS" in self.ostype:
            with console.status("Installing MESA SDK package...", spinner="moon"):
                subprocess.call(f"sudo installer -pkg {sdk_download} -verbose -target /", 
                                shell=True, stdout=logfile, stderr=logfile) 
                # os.remove(sdk_download)
            print("MESA SDK package installation complete.\n")
        with console.status("Extracting MESA...", spinner="moon"):
            with zipfile.ZipFile(mesa_zip, 'r') as zip_ref:
                zip_ref.extractall( {self.directory} )
            # os.remove(mesa_zip)
        print("MESA extraction complete.\n")



    def install(self, ver=''):
        ver = self.choose_ver(ver)
        sdk_url, mesa_url = self.prep_urls(ver)
        sdk_download, mesa_zip = self.download(self.directory, sdk_url, mesa_url)
        mesa_dir = os.path.join(self.directory, mesa_zip.split('/')[-1][0:-4])

        with open(f"{self.directory}/install_log.txt", "w+") as logfile:
            with console.status("Installing MESA pre-requisites...\n", spinner="moon"):
                self.install_pre_reqs(logfile)
            self.extract_mesa(self.directory, sdk_download, mesa_zip, logfile)

            with console.status("Installing MESA...", spinner="moon"):
                run_shell =f'''
                /bin/bash -c \"
                export MESASDK_ROOT={self.directory}/mesasdk \\
                && export MESA_DIR={mesa_dir} \\
                && export OMP_NUM_THREADS=2 \\
                && export GYRE_directory={mesa_dir}/gyre/gyre \\
                && source {self.directory}/mesasdk/bin/mesasdk_init.sh \\
                && chmod -R +x {mesa_dir} \\
                && cd {mesa_dir} && ./clean  && ./install \\
                && cd {mesa_dir}/gyre/gyre && make\"
                '''
                subprocess.call(run_shell, shell=True, stdout=logfile)
        print("Installation complete.\n")
        self.print_env_vars(self.directory, mesa_dir)

