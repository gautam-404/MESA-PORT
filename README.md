# MESA-controller

<!-- <a href="https://zenodo.org/badge/latestdoi/589065195"><img src="https://zenodo.org/badge/589065195.svg" alt="DOI" width=150></a> -->

#### A Python package to control [MESA](https://github.com/MESAHub/mesa) stellar evolution code


### Create, modify, run and share your MESA projects!  

### Features:

  * ***Install MESA*** on ***Linux*** and ***macOS*** (ARM/M-series and Intel) with just this python package!

  * With Python and MESA installed, anyone can run your MESA model using this module. You only need to share your python project.
  
  * **Single star** as well as **binary system** evolution supported.

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
    proj = ProjectOps(name='work', astero=False, binary=False)   ## Default project name is 'work'. 
                                                     ## Default is single star evolution.

    ## Create a new project
    proj.create(overwrite=False, clean=False)    ## CLI is shown if no arguments are passed                       
    ```
    For a custom name or to use an existing MESA work directory, pass its name as a string argument.
    ```python
    proj = ProjectOps("my_project")
    ```
    
  * Take control of your project; make, clean, run, resume and delete.
    ```python
    proj.clean()
    proj.make()
    proj.run(silent=False)      ## Run MESA. Silent=True will suppress console output and write to a runlog file.
    proj.resume("photo_name", silent=False)
    proj.resume("photo_name", silent=False, target="primary")  ## For binary systems. Can be "primary" or "secondary"
    proj.delete()  ## Deletes the project directory
    ```
    
  * Run GYRE:
    ```python
    proj.runGyre("gyre_input.in", silent=False)  
    ## "gyre_input.in" can either be a path to your GYRE input file
    ## or it can also be the name of a file in your_project or your_project/LOGS directory
    ```
    GYRE can also be run for the primary or the secondary star in a binary system.
    ```python
    proj.runGyre("gyre_input.in", silent=False, target="primary")  ## Target can be "primary" or "secondary"
    ```

### ***Using a `MesaAccess` class object:***
  ```python
  star = MesaAccess("your_project", binary=False)  
  ## Use MesaAccess("your_project", binary=True, target='binary') for the default project name 'work'.
  ## Use target='primary', target='secondary' or target='binary' for binary systems.

  ## Write
  star.set(parameters, values)              
  ## Inputs paramets can be a string or a list of strings
  ## Input values can be a single value or a list of values
  ## If a list of values is passed, the length of the list must be equal to the length of the parameters list.

  ## While using the 'set' method, you can also pass a dictionary.
  star.set({"parameter1":value1, "parameter2":value2, "parameter3":value3})
  
  ## Read
  value = star.get(parameters)   
  ## Inputs paramets can be a string or a list of strings

  ## Delete
  star.delete(parameters)
  ## Inputs paramets can be a string or a list of strings

  ## Set to default
  star.setDefualt(parameters)
  ```

  In addition to the above, you can also use the `MesaAccess` class to load your customised input files.
  
  ```python
  ### Path arguments can be a path or the name of a file in 'my_project' directory ###

  star.load_StarExtras("path/to/custom/run_star_extras_file")      ## Load custom run_star_extras.f90
  star.load_InlistProject("/path/to/custom/inlist")                       ## Load custom inlist_project 
  star.load_InlistPG("/path/to/custom/inlist")                       ## Load custom inlist_pgstar    
  star.load_HistoryColumns("path/to/custom/history_columns_file")  ## Load custom history_columns
  star.load_ProfileColumns("path/to/custom/profile_columns_file")  ## Load custom profile_columns
  ```


  When working with a binary system, you can create multiple `MesaAccess` objects for each star and the binary system.
  ```python
  binary = MesaAccess("your_project", binary=True, target='binary')  ## For the binary system
  primary = MesaAccess("your_project", binary=True, target='primary')  ## For the primary star
  secondary = MesaAccess("your_project", binary=True, target='secondary')  ## For the secondary star
  
  ## Parameters can be accessed using the same methods as above
  ## For example:
  binary.set("binary_mass_ratio", 0.5)
  primary.set("profile_interval", 50)
  secondary.set("history_interval", 1)

  ## Load custom input files 
  primary.load_InlistProject("/path/to/custom/inlist")               ## Load custom 'inlist1'
  secondary.load_InlistProject("/path/to/custom/inlist")             ## Load custom 'inlist2'
  binary.load_InlistProject("/path/to/custom/inlist")                ## Load custom 'inlist_project' for the binary system
  binary.load_BinaryExtras("path/to/custom/run_binary_extras_file")  ## Load custom run_binary_extras.f90
  ```
