# MESA-controller

<!-- <a href="https://zenodo.org/badge/latestdoi/589065195"><img src="https://zenodo.org/badge/589065195.svg" alt="DOI" width=150></a> -->

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

### ***Importing:***
  ```python
  from MESAcontroller import  ProjectOps, MesaAccess, Installer
  ```
  
  
### ***Using the built-in MESA `Installer`:***
  ```python
  ## Installer for Linux and macOS (ARM/M-series and Intel) systems
  
  Installer(version="latest", parentDir='where/to/install', cleanAfter=False )     
  ## CLI is shown for missing arguments.  
  ## version = "latest" will install the latest version available for your system.
  ## Available versions: 
  #     Linux: "22.05.1", "15140" and "12778".
  #     macOS-Intel: "22.05.1", "15140" and "12778".  
  #     macOS-ARM: "22.05.1".
 
  
  ## cleanAfter=False by default to allow re-running installation without removing downloaded files, 
  ## this saves time when debugging a failed MESA build.
  ```
  
### ***Using a `ProjectOps` class object:***
  * Creating a new MESA work directory:
    ```python
    proj = ProjectOps()                          ## This creates a default project directory named 'work'
    proj.create(overwrite=False, clean=False)    ## CLI is shown if no arguments are passed                       
    ```
    For a custom name or to use an existing MESA work directory, pass its name as a string argument.
    ```python
    proj = ProjectOps("my_project")
    ```
  * Load custom MESA input files:
    ```python
    ### Arguments can be a path or the name of a file in my_project directory ###
    
    proj.load_Extras("path/to/custom/run_star_extras_file")          ## Load custom run_star_extras.f90
    proj.load_ProjInlist("/path/to/custom/inlist")                   ## Load custom inlist_pgstar   
    proj.load_PGstarInlist("/path/to/custom/inlist")                 ## Load custom inlist_pgstar
    proj.load_HistoryColumns("path/to/custom/history_columns_file")  ## Load custom history_columns
    proj.load_ProfileColumns("path/to/custom/profile_columns_file")  ## Load custom profile_columns
    ```
    
  * Take control of your project; make, clean, run, resume and delete.
    ```python
    proj.clean()
    proj.make()
    proj.run(silent=False)
    proj.resume("photo_number", silent=False)
    proj.delete()  ## Deletes the project directory
    ```
    
  * Run GYRE:
    ```python
    proj.runGyre("gyre_input.in", silent=False)  
    
    ## "gyre_input.in" can either be a path to your GYRE input file
    ## or it can also be the name of a file in your_project or your_project/LOGS directory
    ```

### ***Using a `MesaAccess` class object:***
  ```python
  access = MesaAccess("your_project")  ## Use MesaAccess() for the default project name 'work'

  ## Write
  access.set(parameters, values)              
  ## Inputs paramets can be a string or a list of strings
  ## Input values can be a single value or a list of values
  
  ## Read
  value = access.get(parameters)   
  ## Inputs paramets can be a string or a list of strings

  ## Delete
  access.delete(parameters)
  ## Inputs paramets can be a string or a list of strings
  ```
