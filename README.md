# MESA-commando  
A Python command framework for MESA

### 🫵 Be the commander! 


* Create, run and share your MESA projects!  
  With Python and MESA installed, anyone can run your MESA model using this module. You only need to share your python project.

* This module also allows you to manipulate parameters in your inlist files. Your inputs will automatically be converted to the right data type and format for fortran. [Courtesy of [Marco Müllner](https://github.com/MarcoMuellner/PyMesaHandler)]

<br>

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
  opsObject.create(overwrite=False, clean=False)
  opsObject.make()
  opsObject.run(silent=False)
  opsObject.rerun("photo_number")
  opsObject.clean()
  opsObject.loadProjInlist("/path/to/inlist")
  opsObject.loadPGstarInlist("/path/to/inlist")
  ```

* Using a `MesaAccess` class object:
  ```python
  accessObject["your_parameter"] = value    ## write
  value = accessObject["your_parameter"]    ## read
  accessObject.delitem("your_parameter")    ## delete
  ```
