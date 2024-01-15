from mesaport import  ProjectOps, MesaAccess

## Use ProjectOps("your_project") for a custom project name
work = ProjectOps()          


work.create()   ## Use boolean arguments 'overwrite' and 'clean' to work on existing projects
work.load_Extras("path/to/custom/run_star_extras_file")     ## make after loading extras. this allows the compiler to find the extras file
work.make()           

work.load_ProjInlist("/path/to/inlist")
work.load_PGstarInlist("/path/to/inlist")

obj = MesaAccess()
obj.set("initial_mass", 5)


## Use argument silent=True (False by default) for a silent run, terminal output is redirected to runlog
work.run()              

## arg silent is False by default
work.resume("x450", silent=True)      

work.runGyre("path/to/custom/GYRE/input/file", silent=False)