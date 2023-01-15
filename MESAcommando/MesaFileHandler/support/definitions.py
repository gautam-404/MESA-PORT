sectionStarJob = "star_job"
sectionControl = "controls"
sectionPgStar = "pgstar"

mesa_env = "MESA_DIR"

sections = [sectionStarJob, sectionControl, sectionPgStar]
external_file_parameters = ["extra_star_job_inlist1_name","extra_controls_inlist1_name","extra_pgstar_inlist1_name"]
defaults_file_names = ["star_job.defaults","controls.defaults","pgstar.defaults"]

defaultsFileDict = dict(zip(sections,defaults_file_names))


defaultsPath="/star/defaults/"