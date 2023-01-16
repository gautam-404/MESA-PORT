from MESAmanager import  ProjectOps, MesaAccess

## Use ProjectOps("your_project") for a custom project name
work = ProjectOps()          

## Use boolean arguments 'overwrite' and 'clean' to work on existing projects
work.create()   
work.make()           

work.loadProjInlist("/path/to/inlist")
# work.loadPGstarInlist("/path/to/inlist")

object = MesaAccess()
object["initial_mass"] = 5

## Use argument silent=True (False by default) for a silent run, terminal output is redirected to runlog
work.run()              

## arg silent is False by default
work.rerun("x450", silent=True)      
 
## Clean the project
work.clean()              
