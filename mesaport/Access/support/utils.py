import os

class cwd:
    """
    Directory changer. can change the directory using the 'with' context manager, and returns to the previous path
    after leaving intendation. Example:

    with cwd("some/path/to/go"): # changing dir
        foo()
        ...
        bar()
    #back to old dir
    """
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)