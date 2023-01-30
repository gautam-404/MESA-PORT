import os
import shlex
import shutil
import subprocess
import tarfile
import zipfile

from rich import console, print

def extract_mesa(directory, ostype, cleanAfter, sdk_download, mesa_zip, logfile):
    """Extract the MESA SDK and MESA zip files.

    Args:
        sdk_download (path): Path to the downloaded MESA SDK.
        mesa_zip (path): Path to the downloaded MESA zip file.
        logfile (file): File to write the output logs of the installation to.
    """        
    if ostype == "Linux":
        with console.Console().status("[green b]Extracting MESA Linux SDK", spinner="moon"):
            with tarfile.open(sdk_download, 'r:gz') as tarball:
                if os.path.exists( os.path.join(directory, 'mesasdk') ):
                    shutil.rmtree( os.path.join(directory, 'mesasdk') )
                tarball.extractall(directory )
            if cleanAfter:
                os.remove(sdk_download)
        print("[blue b]MESA Linux SDK extraction complete.\n")
    elif "macOS" in ostype:
        with console.Console().status("[green b]Installing MESA SDK package for macOS", spinner="moon"):
            subprocess.Popen(shlex.split(f"sudo installer -pkg {sdk_download} -target /"),
                            stdout=logfile, stderr=logfile).wait()
            if cleanAfter:
                os.remove(sdk_download)
            print("[blue b]MESA SDK package installation complete.\n")

    with console.Console().status("[green b]Extracting MESA", spinner="moon"):
        with zipfile.ZipFile(mesa_zip, 'r') as zip_ref:
            zip_ref.extractall(directory)
        if cleanAfter:
            os.remove(mesa_zip)
    print("[blue b]MESA extraction complete.\n")
    