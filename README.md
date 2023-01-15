# MESAcommando  
A Python module to command and control [MESA](https://github.com/MESAHub/mesa)

### 🫵 Be the commander! 


* Create, run and share your MESA projects!  
  With Python and MESA installed, anyone can run your MESA model using this module. You only need to share your python project.

* This module also allows you to manipulate parameters in your inlist files. Your inputs will automatically be converted to the right data type and format for fortran. [Courtesy of [Marco Müllner](https://github.com/MarcoMuellner/PyMesaHandler)]

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
  opsObject.create(overwrite=False, clean=False)
  opsObject.make()
  opsObject.run(silent=False)
  opsObject.rerun("photo_number")                   ## Searches photos folder inside the project dir
  opsObject.clean()
  opsObject.loadProjInlist("/path/to/inlist")       ## Load custom inlist_project, reads absolute path
  opsObject.loadPGstarInlist("/path/to/inlist")     ## Load custom inlist_pgstar, reads absolute path
  ```

* Using a `MesaAccess` class object:
  ```python
  ## Write
  accessObject["some_parameter"] = value    
  # or
  accessObject.set_various( ["some_parameter1", "some_parameter2"], [value1, value2])
  
  ## Read
  value = accessObject["some_parameter"]    
  # or
  values_list = accessObject.get_various( ["some_parameter1", "some_parameter2"] )

  ## Delete
  accessObject.delitem("some_parameter")
  # or
  accessObject.del_various_( ["some_parameter1", "some_parameter2"] )
  ```
