import platform, os
import requests

class Installer:
    def __init__(self, ver='', dir=''):
        self.install(ver='', dir='')

    def whichos(self):
        if "macOS" in platform.platform():
            raise OSError("MacOS is not supported by the installer yet!")
        elif "Linux" in platform.platform():
            return "Linux"
        else:
            raise OSError(f"OS {platform.platform()} not compatible.")

    def choose_dir(self, dir=''):
        while not os.path.exists(dir):
            dir = input("Input path to a directory for installation...")
            if os.path.exists(dir):
                print(f"MESA SDK and MESA will be installed at {dir}/software/")
                return dir
            else:
                print(f"Could not find the specified directory. Please try again.")
                dir = ''

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

    def download(self, dir, sdk_url, mesa_url):
        os.mkdir(dir+"/software")

        sdk_tar = dir+"/software/"+sdk_url.split('/')[-1]
        response = requests.get(sdk_url, stream=True)
        try:
            if response.status_code == 200:
                with open(sdk_tar, 'wb') as f:
                    f.write(response.raw.read())
        except Exception as e:
            print("Could not download  {}")

        mesa_tar = dir+"/software/"+mesa_url.split('/')[-1]
        response = requests.get(mesa_url, stream=True)
        if response.status_code == 200:
            with open(mesa_tar, 'wb') as f:
                f.write(response.raw.read())
        return sdk_tar, mesa_tar

    def install(self, ver='', dir=''):
        ver = self.choose_ver(ver)
        dir = self.choose_dir(dir)
        sdk_url, mesa_url = self.prep_urls(ver)
        sdk_tar, mesa_tar = self.download(sdk_url, mesa_url)

        os.system(f"tar xvfz {sdk_tar} -C {dir}/software/")
        os.remove(sdk_tar)
        os.system(f"export MESASDK_ROOT={dir}/software/mesasdk")
        os.system(f"source $MESASDK_ROOT/bin/mesasdk_init.sh")

        os.system(f"unzip {mesa_tar} -d {dir}/software/")
        os.remove(mesa_tar)
        os.system(f"export MESA_DIR={dir}/software/{mesa_url.split('/')[-1]}")
        os.system(f"export OMP_NUM_THREADS=2")

        print("Please add the following to the appropriate shell start-up file (~/.*rc or ~/.*profile):")
        source_this=f'''
        export MESASDK_ROOT={dir}/software/mesasdk
        source $MESASDK_ROOT/bin/mesasdk_init.sh
        export MESA_DIR={dir}/software/{mesa_url.split('/')[-1]}
        export OMP_NUM_THREADS=2
        '''
        print(source_this)

        print("Installation complete!")



        







