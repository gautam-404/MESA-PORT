# MESAcommando

### 🫵 Be the commander! 

* Now create, run and share your MESA projects!
  - With Python and MESA installed, anyone can run your MESA model using this module. You only need to share your python project.
* This package also allows you to manipulate parameters in your inlist files. The package will automatically convert these properly to the right data type and format for fortran. [Courtesy of [Marco Müllner](https://github.com/MarcoMuellner/PyMesaHandler)]

<br>

## Usage

***Import***
```python
from MESAcommando import  ProjectOps, MesaAccess

opsObject = ProjectOps()  ## Use ProjectOps("your_project") for a custom project name
accessObject = MesaAccess

```

***Commands***

* ```python
  opsObject.create(overwrite=False, clean=False)
  ```
* ```python
  opsObject.clean()
  ```
* ```python
  opsObject.make()
  ```
* ```python
  opsObject.run(silent=False)
  ```
* ```python
  opsObject.rerun("photo_number")
  ```
* ```python
  opsObject.loadProjInlist("/path/to/inlist")
  ```
* ```python
  opsObject.loadPGstarInlist("/path/to/inlist")
  ```
* ```python
  accessObject["your_parameter"] = value    ## write
  ```
* ```python
  value = accessObject["your_parameter]"   ## read
  ```
* ```python
  accessObject.delitem("your_parameter)"    ## delete
  ```
