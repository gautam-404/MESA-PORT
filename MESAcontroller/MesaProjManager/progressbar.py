from alive_progress import alive_bar
from ..MesaFileHandler.MesaAccess import MesaAccess
from simpletail import ropen
import os

def get_last_age(work_dir):
    try:
        with ropen(os.path.join(work_dir, "runlog")) as f:
            for line in f:
                if "E" in line and "0" in line and "." in line:
                    return float(line.split()[0])
    except:
        return 0

def total(work_dir, projName, astero, binary):
    star = MesaAccess(projName, binary, astero)
    if star.get("max_age") is None:
        max_age = star.getDefault("max_age")
    else:
        max_age = star.get("max_age")
    last_age = get_last_age(work_dir)
    return int(max_age - last_age)


def process_outline(outline, step, catch=False):
    # print(outline.split())
    try:
        if not catch and outline.split()[0] == step+1:
            return step+1, True, None
        elif catch:
            return step, False, int(outline.split()[0])
        else:
            return step, False, None
    except:
        return step, False, None
    
    # if "E" in outline and "0" in outline and "." in outline:   ##hacky way to get the age of the star
    #     print(outline.split()[0])
    #     age = int(float(outline.split()[0]))
    #     print(age)


# def run_progress(self):
#         star = MesaAccess(self.projName)
#         if star.get("max_age") is not None:
#             max_age = star.get("max_age")
#         else:
#             star.setDefault("max_age")
#             max_age = star.get("max_age") 