import platform, subprocess, os
import requests
from rich.console import Console
console = Console()

class Installer:
    def __init__(self, version='', parent_directory=''):
        self.install(version, parent_directory)

    def whichos(self):
        if "macOS" in platform.platform():
            raise OSError("MacOS is not supported by the installer yet!")
        elif "Linux" in platform.platform():
            return "Linux"
        else:
            raise OSError(f"OS {platform.platform()} not compatible.")

    def choose_directory(self, directory=''):
        while not os.path.exists(directory):
            directory = input("Input path to a directoryectory for installation...")
            try:
                if os.path.exists(directory):
                    print(f"MESA SDK and MESA will be installed at {directory}/software/")
                    return directory
            except:
                print("Could not find the specified directory. Please try again.")
                directory = ''

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
        if os.path.exists(directory):
            if not os.path.exists(directory+"/software"):
                os.mkdir(directory+"/software")
            else:
                print("Software directory already exists. Continuing...")
                
        with console.status("Downloading MESA SDK...", spinner="moon"):
            sdk_tar = directory+"/software/"+sdk_url.split('/')[-1]
            response = requests.get(sdk_url, stream=True, timeout=10)
            try:
                if response.status_code == 200:
                    with open(sdk_tar, 'wb') as file:
                        file.write(response.raw.read())
            except Exception:
                print("Could not download MESA SDK. Please try again later.")
        print("MESA SDK download complete.")

        with console.status("Downloading MESA...", spinner="moon"):
            mesa_tar = directory+"/software/"+mesa_url.split('/')[-1]
            response = requests.get(mesa_url, stream=True, timeout=10)
            try:
                if response.status_code == 200:
                    with open(mesa_tar, 'wb') as file:
                        file.write(response.raw.read())
            except Exception:
                print("Could not download MESA. Please try again later.")
        print("MESA download complete.")
        return sdk_tar, mesa_tar

    def install(self, ver='', directory=''):
        ver = self.choose_ver(ver)
        directory = self.choose_directory(directory)
        sdk_url, mesa_url = self.prep_urls(ver)
        sdk_tar, mesa_tar = self.download(directory, sdk_url, mesa_url)


        with console.status("Installing MESA SDK...", spinner="moon"):
            subprocess.call(f"tar xvfz {sdk_tar} -C {directory}/software/")
            os.remove(sdk_tar)
            subprocess.call(f"export MESASDK_ROOT={directory}/software/mesasdk")
            subprocess.call("source $MESASDK_ROOT/bin/mesasdk_init.sh")
        print("MESA SDK installation complete.")

        with console.status("Installing MESA...", spinner="moon"):
            subprocess.call(f"unzip {mesa_tar} -d {directory}/software/")
            os.remove(mesa_tar)
            subprocess.call(f"export MESA_directory={directory}/software/{mesa_url.split('/')[-1]}")
            subprocess.call("export OMP_NUM_THREADS=2")
        print("MESA installation complete.")

        with console.status("Installing GYRE...", spinner="moon"):
            subprocess.call("export GYRE_directory=$MESA_directory/gyre/gyre")
            subprocess.call("cd $GYRE_directory; make")
        print("GYRE installation complete.")
        

        print("Please add the following to the appropriate shell start-up file (~/.*rc or ~/.*profile):")
        source_this=f'''
        export MESASDK_ROOT={directory}/software/mesasdk
        source $MESASDK_ROOT/bin/mesasdk_init.sh
        export MESA_directory={directory}/software/{mesa_url.split('/')[-1]}
        export OMP_NUM_THREADS=2
        export GYRE_directory=$MESA_directory/gyre/gyre
        '''
        print(source_this)

        print("Installation complete!")

