# MESAcommando

### Be the commander!!

* Now create, run and share your MESA projects!
  - You only need to share your python project. Anyone who has Python and MESA installed, will then be able to run your model using only python code. You can also run MESA solely through this module.
* This package also allows you to manipulate parameters in your inlist files. The package will automatically convert these properly to the right data type and format for fortran. [Courtesy of [Marco Müllner](https://github.com/MarcoMuellner/PyMesaHandler)]

<br>

## Usage

***Import***
```
from MESAcommando import  ProjectOps, MesaAccess
opsObject = ProjectOps()  ## Use ProjectOps("your_project") for a custom project name
accessObject = MesaAccess

```

***Commands***

* `opsObject.create(overwrite=False, clean=False)`
* `opsObject.clean()`
* `opsObject.make()`
* `opsObject.run(silent=False)`
* `opsObject.rerun("photo_number")`
* `opsObject.loadProjInlist("/path/to/inlist")`
* `opsObject.loadPGstarInlist("/path/to/inlist")`
* `accessObject["your_parameter"] = value    ## write`  
* `value = accessObject.["your_parameter]"   ## read`
* `accessObject.delitem("your_parameter)"    ## delete`
