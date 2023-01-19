from MESAcontroller import  ProjectOps, MesaAccess

## Use ProjectOps("your_project") for a custom project name
work = ProjectOps()          

## Use boolean arguments 'overwrite' and 'clean' to work on existing projects
work.create()   
work.make()           

work.loadProjInlist("/path/to/inlist")
# work.loadPGstarInlist("/path/to/inlist")

object = MesaAccess()
object.set("initial_mass", 5)

## Use argument silent=True (False by default) for a silent run, terminal output is redirected to runlog
work.run()              

## arg silent is False by default
work.resume("x450", silent=True)      
 
## Clean the project
work.clean()              

work.make()           
work.loadProjInlist("/path/to/adifferent/inlist")
# work.loadPGstarInlist("/path/to/inlist")


star = ProjectOps("star")
star.create(overwrite=False, clean=True)
star.make()
star.loadProjInlist("inlist_project_solar")
star.run(silent=True)
star.runGyre("gyre_template.in", silent=False)