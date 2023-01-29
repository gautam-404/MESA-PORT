import os
import shlex
import subprocess

from . import Choice, Downloader, Extractor, Prerequisites, Syscheck, mesaurls

from rich import console, print

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
        ostype = Syscheck.whichos()
        directory = Choice.choose_directory(parentDir)
        print(f"\nOS type: [orange3]{ostype}[/orange3]\n")
        version = Choice.choose_ver(ostype, version)
        self.install(version, ostype, directory, cleanAfter)



    
    def install(self, version, ostype, directory, cleanAfter):
        """Install MESA.

        Args:
            version (str):  Version of MESA to install.
            ostype (str):   OS type.
            directory (str): Path to a directory to install MESA and MESA SDK.
            cleanAfter (bool): If True, the downloaded MESA SDK and MESA zip files will be deleted after installation. 
                                Defaults to False.
        """        
        downloaded = Downloader.Download(directory, version, ostype)
        sdk_download, mesa_zip = downloaded.sdk_download, downloaded.mesa_zip
        mesa_dir = os.path.join(directory, mesa_zip.split('/')[-1][0:-4])

        with open(f"install_log.txt", "w+") as logfile:
            ## to get sudo password prompt out of the way
            subprocess.Popen(shlex.split("sudo echo"), stdin=subprocess.PIPE, stdout=logfile, stderr=logfile).wait()    
            with console.Console().status("Installing pre-requisites", spinner="moon"):
                Prerequisites.install_prerequisites(directory, ostype, cleanAfter, logfile)
            Extractor.extract_mesa(directory, ostype, cleanAfter, sdk_download, mesa_zip, logfile)

            with console.Console().status("Installing MESA", spinner="moon"):
                if ostype == "Linux":
                    sdk_dir = os.path.join(directory, 'mesasdk')
                elif "macOS" in ostype:
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

                logfile.write("Build Successful.\n")

        self.write_env_vars(mesa_dir, sdk_dir)
        print("Installation complete.\n")

        


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

        
