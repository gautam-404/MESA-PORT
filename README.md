# MESA Python Operational Runtime Toolkit

<!-- <a href="https://zenodo.org/badge/latestdoi/589065195"><img src="https://zenodo.org/badge/589065195.svg" alt="DOI" width=150></a> -->

#### A Python package to control [MESA](https://github.com/MESAHub/mesa) stellar evolution code


### Create, modify, run and share your MESA projects!  

### Features:

  * ***Install MESA*** on ***Linux*** and ***macOS*** (ARM/M-series and Intel) with just this python package!
    <details>
    <summary><b><i>CLI example</b></i></summary>
    <img src="imgs/installer.png">
    </details>

  * With Python and MESA installed, anyone can run your MESA model using this module. You only need to share your python project.
  
  * **Single star** as well as **binary system** evolution supported.

  * This module also allows you to manipulate parameters in your inlist files. Your inputs will automatically be converted to the right data type and format for fortran. 

  * MESA-PORT can also run [GYRE](https://github.com/rhdtownsend/gyre) stellar oscillation code! See Usage.

  * For advanced usage, see the [MESA-tests repository](https://github.com/gautam-404/MESA-tests). 



<br>

## Installation
```
pip install git+https://github.com/gautam-404/MESA-PORT.git
```

## Usage

### ***Importing:***
  ```python
  from mesaport import  ProjectOps, MesaAccess, Installer
  ```
  
  
### ***Using the built-in MESA `Installer`:***
  ```python
  ## Installer for Linux and macOS (ARM/M-series and Intel) systems
  
  Installer(version="latest", parentDir='where/to/install', cleanAfter=False )     
  ## CLI is shown for missing arguments.  
  ## version = "latest" will install the latest version available for your system.
  ## Available versions: 
  #     Linux: "23.05.1", "22.05.1", "15140" and "12778".
  #     macOS-Intel: "23.05.1", "22.05.1", "15140" and "12778".  
  #     macOS-ARM: "23.05.1", "22.05.1".
 
  
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
    proj.run(silent=True, trace=None)                                    ## Run MESA model
    ## Silent=True by default, whch writes MESA output to a run log while the console shows the star's age as it evolves.
    ## Pass a list of MESA parameters as an argument to trace their evolution in terminal along with age. Eg, trace=["log_L", "log_Teff"]
    proj.resume("photo_name", silent=True)
    proj.delete()                                             ## Deletes the project directory
    ```
    
  * Run GYRE:
    ```python
    proj.runGyre("gyre/input")  
    ## "gyre/input" can either be a path to your GYRE input file
    ## or it can also be the name of a file in your_project or your_project/LOGS directory

    ## If you want to run a GYRE input file for all profile FGONG data files in your LOGS directory, 
    ## pass files="all" as an argument.
    proj.runGyre("gyre/input", files="all")

    ## If you want to run GYRE for specific FGONG files, pass file names as an argument.
    proj.runGyre("gyre/input", files=["profile1.data.FGONG", "profile2.data.FGONG"])
    ```
    GYRE can also be run for the primary or the secondary star in a binary system.
    ```python
    proj.runGyre("gyre_input.in", target="primary")  ## Target can be "primary" or "secondary"
    ```

### ***Using a `MesaAccess` class object:***
  ```python
  star = MesaAccess("your_project")

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

  In addition to the above, you can also use the `MesaAccess` class to load your customised pre-prepared input files.
  
  ```python
  ### Path arguments can be a path or the name of a file in 'my_project' directory ###

  star.load_Extras("path/to/custom/run_star_extras_file")          ## Load custom run_star_extras.f90
  star.load_InlistProject("/path/to/custom/inlist")                ## Load custom inlist_project 
  star.load_InlistPG("/path/to/custom/inlist")                     ## Load custom inlist_pgstar    
  star.load_HistoryColumns("path/to/custom/history_columns_file")  ## Load custom history_columns
  star.load_ProfileColumns("path/to/custom/profile_columns_file")  ## Load custom profile_columns
  star.load_InlistAsteroSearch("path/to/inlist")                   ## Load custom inlist_astero_search_controls
  ```
  Use `star = MesaAccess("your_project", astero=True)` when working with an astero project.

  When working with a binary system, you can create multiple `MesaAccess` objects for each star and the binary system.
  ```python
  binary = MesaAccess("your_project", binary=True, target='binary')        ## For the binary system
  primary = MesaAccess("your_project", binary=True, target='primary')      ## For the primary star
  secondary = MesaAccess("your_project", binary=True, target='secondary')  ## For the secondary star
  
  ## Parameters can be accessed using the same methods as above
  ## For example:
  binary.set("binary_mass_ratio", 0.5)
  primary.set("profile_interval", 50)
  secondary.set("history_interval", 1)

  ## Load custom input files 
  primary.load_InlistProject("/path/to/custom/inlist")          ## Load custom 'inlist1'
  secondary.load_InlistProject("/path/to/custom/inlist")        ## Load custom 'inlist2'
  binary.load_InlistProject("/path/to/custom/inlist")           ## Load custom 'inlist_project' for the binary system
  binary.load_Extras("path/to/custom/run_binary_extras_file")   ## Load custom run_binary_extras.f90
  ```
 
