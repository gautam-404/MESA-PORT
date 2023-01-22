import os

import requests
from alive_progress import alive_bar

from .mesaurls import *
from .syscheck import whichos


class Download:
    """Class for downloading the MESA SDK and MESA zip files."""
    def __init__(self, directory, version, ostype):
        """Initialize the Downloader class.

        Args:
            ver (str): Version of MESA to install. 
            directory (str): Path to the directory where the MESA SDK and MESA zip files will be downloaded.
        """        
        self.ostype = ostype
        self.directory = directory
        sdk_url, mesa_url = self.prep_urls(version)
        self.sdk_download, self.mesa_zip = self.download(sdk_url, mesa_url)
        if self.ostype == "macOS-Intel":
            xquartz = os.path.join(directory, url_xquartz.split('/')[-1])
            print("Downloading XQuartz...")
            self.check_n_download(xquartz, url_xquartz)


    def prep_urls(self, version):
        """Prepare the URLs for the MESA SDK and MESA zip files.

        Args:
            ver (str): Version of MESA to install. 

        Returns:
            tuple: URLs for the MESA SDK and MESA zip files.
        """      
        if self.ostype == "Linux":
            sdk_url = linux_sdk_urls.get(version)
            mesa_url = mesa_urls.get(version)
        elif self.ostype == "macOS-Intel":
            sdk_url = mac_intel_sdk_urls.get(version)
            mesa_url = mesa_urls.get(version)
        elif self.ostype == "macOS-ARM":
            sdk_url = mac_arm_sdk_urls.get(version)
            mesa_url = mesa_urls.get(version)
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
