import os

###
#   Check if the directory already exists. If not create it.
#   f:  file or folder.
#   returns True if the directory exists at exiting the function.
###
def ensure_dir(f, verbal=False):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)
        if verbal:
            print('Created path:', d)
    return os.path.exists(d)
