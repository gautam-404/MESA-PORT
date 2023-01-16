# MESAmanager
#### A Python library to control and administer [MESA](https://github.com/MESAHub/mesa)


### Create, modify, run and share your MESA projects!  

* ***NEW***: Can now install MESA on Linux! See Usage.  Compatibility with MacOS coming soon...

* With Python and MESA installed, anyone can run your MESA model using this module. You only need to share your python project.

* This module also allows you to manipulate parameters in your inlist files. Your inputs will automatically be converted to the right data type and format for fortran. [Brainchild of [Marco Müllner](https://github.com/MarcoMuellner/PyMesaHandler)]



<br>

## Installation
```
pip install git+https://github.com/gautam-404/MESAmanager.git
```

## Usage

***Import***
```python
from MESAmanager import  ProjectOps, MesaAccess, Installer

opsObject = ProjectOps()  ## Use ProjectOps("your_project") for a custom/pre-existing project name
accessObject = MesaAccess()

## Interactive installer for Linux systems
Installer()               
# Optional arguments: version="ver.si.on" and parent_dir='where/to/install'
# Available versions options are "latest", "22.11.1", "22.05.1", "21.12.1", "15140" and "12778"

```

***Commands***

* Using a `ProjectOps` class object:
  ```python
  opsObject.create(overwrite=False, clean=False)    ## CLI is shown if no arguments are passed
  opsObject.clean()
  opsObject.make()
  opsObject.run(silent=False)
  opsObject.resume("photo_number", silent=False)
  opsObject.loadProjInlist("/path/to/inlist")       ## Load custom inlist_project, reads absolute path
  opsObject.loadPGstarInlist("/path/to/inlist")     ## Load custom inlist_pgstar, reads absolute path
  ```

* Using a `MesaAccess` class object:
  ```python
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
