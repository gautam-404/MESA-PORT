# MESA-manager
#### A Python package to control and administer [MESA](https://github.com/MESAHub/mesa) (Modules for Experiments in Stellar Astrophysics)


### Create, modify, run and share your MESA projects!  

### Features:

  * ***Install MESA*** on ***Linux*** and ***macOS*** (ARM/M-series and Intel) with just this python package!

  * With Python and MESA installed, anyone can run your MESA model using this module. You only need to share your python project.

  * This module also allows you to manipulate parameters in your inlist files. Your inputs will automatically be converted to the right data type and format for fortran. [Brainchild of [Marco Müllner](https://github.com/MarcoMuellner/PyMesaHandler)]

  * MESA-manager can also run [GYRE](https://github.com/rhdtownsend/gyre) stellar oscillation code! See Usage.



<br>

## Installation
```
pip install git+https://github.com/gautam-404/MESA-manager.git
```

## Usage

* ***Importing:***
  ```python
  from MESAmanager import  ProjectOps, MesaAccess, Installer
  ```
  
* ***Using the built-in MESA `Installer`:***
  ```python
  from MESAmanager import Installer
  ## Installer for Linux and macOS (ARM/M-series and Intel) systems
  
  Installer(version="latest", parentDir='where/to/install', cleanAfter=False )     
  ## CLI is shown for missing arguments.         
  ## Available versions:
  #     Linux: "22.11.1", "22.05.1", "21.12.1", "15140" and "12778".
  #     macOS-Intel: "22.05.1", "15140" and "12778".  
  #     macOS-ARM: "22.05.1".
  
  ## cleanAfter=False by default to allow re-running installation without removing downloaded files, 
  ## this saves time when debugging a failed MESA build.
  ```
  
* ***Using a `ProjectOps` class object:***
  ```python
  opsObject = ProjectOps()  ## Use ProjectOps("your_project") for a custom/pre-existing project name
                            ## Default name is 'work'
  opsObject.create(overwrite=False, clean=False)    ## CLI is shown if no arguments are passed
  opsObject.clean()
  opsObject.make()
  opsObject.run(silent=False)
  opsObject.resume("photo_number", silent=False)
  opsObject.loadProjInlist("/path/to/inlist")       ## Load custom inlist_project
  opsObject.loadPGstarInlist("/path/to/inlist")     ## Load custom inlist_pgstar

  opsObject.runGyre("gyre_input.in", silent=False)  
  ## "gyre_input.in" can be a path to a GYRE input file
  ## It can also be the name of a file in either your_project or your_project/LOGS directory
  ```

* ***Using a `MesaAccess` class object:***
  ```python
  accessObject = MesaAccess()

  ## Write
  accessObject.set(parameters, values)              
  ## Inputs paramets can be a string or a list of strings
  ## Input values can be a single value or a list of values
  
  ## Read
  value = accessObject.get(parameters)   
  ## Inputs paramets can be a string or a list of strings

  ## Delete
  accessObject.delete(parameters)
  ## Inputs paramets can be a string or a list of strings
  ```
