import os, shutil, sys
import platform
import tarfile
import zipfile
import subprocess 

import requests
from alive_progress import alive_bar
from rich.console import Console

console = Console()

class Installer:
    def __init__(self, version='', parent_directory=''):
        self.install(version, parent_directory)
        return




    def whichos(self):
        if "macOS" in platform.platform():
            raise OSError("MacOS is not supported by the installer yet!")
        elif "Linux" in platform.platform():
            return "Linux"
        else:
            raise OSError(f"OS {platform.platform()} not compatible.")




    def choose_directory(self, directory=''):
        while not os.path.exists(directory):
            directory = input("Input path to a directory for installation...")
            if os.path.exists(directory):
                print(f"MESA SDK and MESA will be installed at path: {directory}/software/")
                if not os.path.exists(directory+"/software"):
                    os.mkdir(directory+"/software")
                return os.path.abspath(directory+"/software")
            else:
                print("Could not find the specified directory. Please try again.")
                directory = ''
        if not os.path.exists(directory+"/software"):
            os.mkdir(directory+"/software")
        return os.path.abspath(directory+"/software")




    def choose_ver(self, ver=''):
        versions = ["latest", "22.11.1", "22.05.1", "21.12.1", "15140", "12778"]
        while ver not in versions:
            print("Versions available through this insaller are:")
            print(versions)
            ver = input("Input the desired version...")
            if ver not in versions:
                print("Not recognised, try again.")
        return ver



    def prep_urls(self, ver):
        if self.whichos() == "Linux":
            if ver == "latest":
                sdk_url = "http://user.astro.wisc.edu/~townsend/resource/download/mesasdk/mesasdk-x86_64-linux-22.6.1.tar.gz"
                mesa_url = "https://zenodo.org/record/7319739/files/mesa-r22.11.1.zip"
            elif ver == "22.11.1":
                sdk_url = "http://user.astro.wisc.edu/~townsend/resource/download/mesasdk/mesasdk-x86_64-linux-22.6.1.tar.gz"
                mesa_url = "https://zenodo.org/record/7319739/files/mesa-r22.11.1.zip"
            elif ver == "22.05.1":
                sdk_url = "http://user.astro.wisc.edu/~townsend/resource/download/mesasdk/mesasdk-x86_64-linux-22.6.1.tar.gz"
                mesa_url = "https://zenodo.org/record/6547951/files/mesa-r22.05.1.zip"
            elif ver == "21.12.1":
                sdk_url = "http://user.astro.wisc.edu/~townsend/resource/download/mesasdk/mesasdk-x86_64-linux-22.6.1.tar.gz"
                mesa_url = "https://zenodo.org/record/7319739/files/mesa-r22.12.1.zip"
            elif ver == "15140":
                sdk_url = "http://user.astro.wisc.edu/~townsend/resource/download/mesasdk/mesasdk-x86_64-linux-21.4.1.tar.gz"
                mesa_url = "https://zenodo.org/record/7319739/files/mesa-r15140.zip"
            elif ver == "12778":
                sdk_url = "http://user.astro.wisc.edu/~townsend/resource/download/mesasdk/mesasdk-x86_64-linux-20.3.2.tar.gz"
                mesa_url = "https://zenodo.org/record/7319739/files/mesa-r12778.zip"
        return sdk_url, mesa_url



    def download(self, directory, sdk_url, mesa_url):
        def check_n_download(filepath, url):
            if os.path.exists(filepath) and int(requests.head(url, timeout=10).headers['content-length']) == os.path.getsize(filepath):
                print("Skipping download! File already downloaded.")
            else:
                chunk_size = 11*1024*1024
                response = requests.get(url, stream=True, timeout=10)
                total = int(response.headers.get('content-length', 0))
                with open(filepath, 'wb') as file, alive_bar(total, unit='B', scale=True) as progressbar:
                    for chunk in response.raw.stream(chunk_size, decode_content=False):
                        if chunk:
                            size_ = file.write(chunk)
                            progressbar(size_)
                print("Download complete.")
        
        print("Downloading MESA SDK...")
        sdk_tar = directory+"/"+sdk_url.split('/')[-1]
        check_n_download(sdk_tar, sdk_url)

        print("Downloading MESA...")
        mesa_zip = directory+"/"+mesa_url.split('/')[-1]
        check_n_download(mesa_zip, mesa_url)
        return sdk_tar, mesa_zip



    def install_pre_reqs(self, logfile):
        if self.whichos() == "Linux":
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
            



    def print_env_vars(self, directory, mesa_dir):
        source_this=f'''
        export MESASDK_ROOT={directory}/mesasdk
        source $MESASDK_ROOT/bin/mesasdk_init.sh
        export MESA_DIR={mesa_dir}
        export OMP_NUM_THREADS=2
        export GYRE_directory=$MESA_DIR/gyre/gyre
        '''
        print("Please add the following to the appropriate shell start-up file (~/.*rc or ~/.*profile):")
        print(source_this)
        

    def extract_mesa(self, directory, sdk_tar, mesa_zip):
        with console.status("Extracting MESA SDK...", spinner="moon"):
            with tarfile.open(sdk_tar, 'r:gz') as tarball:
                if os.path.exists(f'{directory}/mesasdk'):
                    shutil.rmtree(f'{directory}/mesasdk')
                tarball.extractall(f'{directory}/')
            # os.remove(sdk_tar)
        print("MESA SDK extraction complete.")
        with console.status("Extracting MESA...", spinner="moon"):
            with zipfile.ZipFile(mesa_zip, 'r') as zip_ref:
                zip_ref.extractall(f'{directory}/')
            # os.remove(mesa_zip)
        print("MESA extraction complete.")




    def install(self, ver='', directory=''):
        ver = self.choose_ver(ver)
        directory = self.choose_directory(directory)
        sdk_url, mesa_url = self.prep_urls(ver)
        sdk_tar, mesa_zip = self.download(directory, sdk_url, mesa_url)
        mesa_dir = directory+'/'+mesa_zip.split('/')[-1][0:-4]

        with open(f"{directory}/install_log.txt", "w+") as logfile:
            with console.status("Installing MESA pre-requisites...", spinner="moon"):
                self.install_pre_reqs(logfile)
            # self.extract_mesa(directory, sdk_tar, mesa_zip)

            with console.status("Installing MESA...", spinner="moon"):
                run_shell =f'''
                /bin/bash -c \"
                export MESASDK_ROOT={directory}/mesasdk \\
                && export MESA_DIR={mesa_dir} \\
                && export OMP_NUM_THREADS=2 \\
                && export GYRE_directory={mesa_dir}/gyre/gyre \\
                && source {directory}/mesasdk/bin/mesasdk_init.sh \\
                && chmod -R +x {mesa_dir} \\
                && cd {mesa_dir} && ./clean  && ./install \\
                && cd {mesa_dir}/gyre/gyre && make\"
                '''
                subprocess.call(run_shell, shell=True, stdout=logfile)
        print("Installation complete.")
        self.print_env_vars(directory, mesa_dir)

