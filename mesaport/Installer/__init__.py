"""
This module defines the `Installer` class, which handles MESA installation.

Attributes:
    version (str): Version of MESA to install.
    parentDir (str): Path to a directory to install MESA and MESA SDK.
    cleanAfter (bool): If True, the downloaded MESA SDK and MESA zip files will be deleted after installation. Defaults to False.
    logging (bool): If True, the installation log will be written to a file. Defaults to True.
"""
from .installer import Installer