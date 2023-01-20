# MESA-controller
 <a href="https://zenodo.org/badge/latestdoi/589065195"><img src="https://zenodo.org/badge/589065195.svg" alt="DOI" width=150></a>

#### A Python package to control [MESA](https://github.com/MESAHub/mesa) stellar evolution code


### Create, modify, run and share your MESA projects!  

### Features:

  * ***Install MESA*** on ***Linux*** and ***macOS*** (ARM/M-series and Intel) with just this python package!

  * With Python and MESA installed, anyone can run your MESA model using this module. You only need to share your python project.

  * This module also allows you to manipulate parameters in your inlist files. Your inputs will automatically be converted to the right data type and format for fortran. [Brainchild of [Marco Müllner](https://github.com/MarcoMuellner/PyMesaHandler)]

  * MESA-controller can also run [GYRE](https://github.com/rhdtownsend/gyre) stellar oscillation code! See Usage.



<br>

## Installation
```
pip install git+https://github.com/gautam-404/MESA-controller.git
```

## Usage

* ***Importing:***
  ```python
  from MESAcontroller import  ProjectOps, MesaAccess, Installer
  ```
  
* ***Using the built-in MESA `Installer`:***
  ```python
  ## Installer for Linux and macOS (ARM/M-series and Intel) systems
  
  Installer(version="latest", parentDir='where/to/install', cleanAfter=False )     
  ## CLI is shown for missing arguments.         
  ## Available versions: 
  #     Linux: "22.05.1", "15140" and "12778".
  #     macOS-Intel: "22.05.1", "15140" and "12778".  
  #     macOS-ARM: "22.05.1".
  #    "latest" will install the latest version available for your system.
  
  ## cleanAfter=False by default to allow re-running installation without removing downloaded files, 
  ## this saves time when debugging a failed MESA build.
  ```
  
* ***Using a `ProjectOps` class object:***
  ```python
  opsObject = ProjectOps()  ## Use ProjectOps("your_project") for a custom/pre-existing project name
                            ## Default name is 'work'
  opsObject.create(overwrite=False, clean=False)    ## CLI is shown if no arguments are passed
  opsObject.clean()

  opsObject.loadExtras("path/to/custom/run_star_extras_file")

  opsObject.make()
  opsObject.run(silent=False)
  opsObject.resume("photo_number", silent=False)

  ## Load custom inlist_project, can be a path or a file in your_project directory
  opsObject.loadProjInlist("/path/to/inlist")
  ## Load custom inlist_pgstar, can be a path or a file in your_project directory     
  opsObject.loadPGstarInlist("/path/to/inlist")
  ## Load custom run_star_extras.f90, can be a path or a file in your_project directory

  opsObject.runGyre("gyre_input.in", silent=False)  
  ## "gyre_input.in" can either be a path to your GYRE input file
  ## or it can also be the name of a file in your_project or your_project/LOGS directory
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
