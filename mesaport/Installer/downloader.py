import os

import requests
import time
from rich import print, progress

progress_columns = (progress.DownloadColumn(), 
                    *progress.Progress.get_default_columns(),
                    progress.TimeElapsedColumn())

from . import mesaurls

class Download:
    """Class for downloading the MESA SDK and MESA zip files."""
    def __init__(self, directory, version, ostype):
        """Initialize the Downloader class.

        Args:
            ver (str): Version of MESA to install. 
            directory (str): Path to the directory where the MESA SDK and MESA zip files will be downloaded.
            ostype (str): Operating system type.
        """        
        self.ostype = ostype
        self.directory = directory
        sdk_url, mesa_url = self.prep_urls(version)
        self.sdk_download, self.mesa_zip = self.download(sdk_url, mesa_url)
        # if self.ostype == "macOS-Intel":
        if 'macOS' in self.ostype:
            xquartz = os.path.join(directory, mesaurls.url_xquartz.split('/')[-1])
            self.check_n_download(xquartz, mesaurls.url_xquartz, "[green b]Downloading XQuartz...")


    def prep_urls(self, version):
        """Prepare the URLs for the MESA SDK and MESA zip files.

        Args:
            ver (str): Version of MESA to install. 

        Returns:
            tuple: URLs for the MESA SDK and MESA zip files.
        """      
        if self.ostype == "Linux":
            sdk_url = mesaurls.linux_sdk_urls.get(version)
            mesa_url = mesaurls.mesa_urls.get(version)
        elif self.ostype == "macOS-Intel":
            sdk_url = mesaurls.mac_intel_sdk_urls.get(version)
            mesa_url = mesaurls.mesa_urls.get(version)
        elif self.ostype == "macOS-ARM":
            sdk_url = mesaurls.mac_arm_sdk_urls.get(version)
            mesa_url = mesaurls.mesa_urls.get(version)
        return sdk_url, mesa_url


    def check_n_download(self, filepath, url, text="Downloading..."):
        """Check if a file has already been downloaded, and if not, download it.

        Args:
            filepath (str): Path to the file to be downloaded. 
            url (str): URL of the file to be downloaded.
            text (str, optional): Text to be displayed while downloading the file. Defaults to "Downloading...".
        """    
        headers = {
                        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0",
                    }
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        # total = float(response.headers.get('content-length', 0))    
        total = float(response.headers.get('content-length', 0)) if response.headers.get('content-length') else 0
        if os.path.exists(filepath) and total == os.path.getsize(filepath):
            print(text)
            print("[blue]File already downloaded. Skipping download.[/blue]\n")
        else:
            chunk_size = 1024*1024
            with open(filepath, 'wb') as file, progress.Progress(*progress_columns) as progressbar:
                task = progressbar.add_task(text, total=int(total))
                for chunk in response.raw.stream(chunk_size, decode_content=False):
                    if chunk:
                        size_ = file.write(chunk)
                        progressbar.update(task_id=task, advance=size_)
                time.sleep(5)
                if total == os.path.getsize(filepath):
                    progressbar.update(task, description=text+"[bright_blue b]Done![/bright_blue b]")
                else:
                    progressbar.update(task, description=text+"[red b]Failed![/red b]")
                    raise Exception("Download failed.")
            print("\n", end="")
            

    def download(self, sdk_url, mesa_url):
        """Download the MESA SDK and MESA zip files.

        Args:
            sdk_url (str): URL of the MESA SDK.
            mesa_url (str): URL of the MESA zip file.

        Returns:
            tuple: Paths to the downloaded MESA SDK and MESA zip files.
        """        
        sdk_download = os.path.join(self.directory, sdk_url.split('/')[-1])
        self.check_n_download(sdk_download, sdk_url, "[green b]Downloading MESA SDK...[/green b]")

        mesa_zip = os.path.join(self.directory, mesa_url.split('/')[-1])
        self.check_n_download(mesa_zip, mesa_url, "[green b]Downloading MESA...[/green b]")
        return sdk_download, mesa_zip
