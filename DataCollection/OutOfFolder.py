import os
import shutil
from os import listdir
from os.path import join, isfile
folder = "C:\Users\Mikael Laptop\DataDog\pypi"
dest_folder = "C:\Users\Mikael Laptop\MaliciousPackages"
for item in listdir(folder):
    fullpath = os.path.join(folder, item)
    if os.path.isdir(fullpath):
        for sub_item in os.listdir(fullpath):
            subpath = os.path.join(fullpath, sub_item)
            if os.path.isdir(subpath):
                for sub_sub_item in os.listdir(subpath):
                    zippath = os.path.join(subpath, sub_sub_item)

                    destination = shutil.copy(zippath, dest_folder)
                    print(f"Copied {zippath} to {destination}")
    print(fullpath)