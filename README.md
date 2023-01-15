# MESAcommando
**A Python library to *command and control* [MESA](https://github.com/MESAHub/mesa)**


### Create, modify, run and share your MESA projects!  

* With Python and MESA installed, anyone can run your MESA model using this module. You only need to share your python project.
* This module also allows you to manipulate parameters in your inlist files. Your inputs will automatically be converted to the right data type and format for fortran. [Brainchild of [Marco Müllner](https://github.com/MarcoMuellner/PyMesaHandler)]

<br>

## Installation
```
pip3 install git+https://github.com/gautam-404/MESAcommando.git
```

## Usage

***Import***
```python
from MESAcommando import  ProjectOps, MesaAccess

opsObject = ProjectOps()  ## Use ProjectOps("your_project") for a custom project name
accessObject = MesaAccess()

```

***Commands***

* Using a `ProjectOps` class object:
  ```python
  opsObject.create(overwrite=False, clean=False)    ## CLI is shown if no arguments are passed
  opsObject.clean()
  opsObject.make()
  opsObject.run(silent=False)
  opsObject.rerun("photo_number")                   ## Searches photos folder inside the project dir
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
