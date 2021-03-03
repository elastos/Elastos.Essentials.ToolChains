import os
import sys
import distutils.dir_util as dir_util

# Removes a path if it exists, but don't throw an error if it doesn't
def safeRemove(path):
    if not os.path.exists(path):
        return

    if os.path.isdir(path):
        dir_util.remove_tree(path)
    else:
        os.remove(path)

    # Make sure the deletion was really successful (no file system lock):
    if os.path.exists(path):
        print("Error: file/folder could not be totally deleted. Check possible file system lock: "+path)
        sys.exit(1)

# Create a folder if it does not exists, but don't throw an error if it already exists
def safeMkdir(path):
    if os.path.exists(path):
        return
    os.mkdir(path)
