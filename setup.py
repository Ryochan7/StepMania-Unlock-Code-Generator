#!/usr/bin/env python

from distutils.core import setup
import sys
import subprocess

# Compile translation files if not making source build
if not "sdist" in sys.argv:
    new_process = subprocess.Popen (["lrelease", "project.pro"])
    new_process.wait ()

arguments = {
    "name": "sucg",
    "version": "0.7",
    "description": """Program to write an Unlocks.dat file for StepMania """
        """3.9 to set song unlock criteria""",
    "author": "Travis Nickles",
    "author_email": "ryoohki7@yahoo.com",
    "license": "GPLv3",
    "url": "https://github.com/Ryochan7/StepMania-Unlock-Code-Generator",
    "packages": ["stepmaniaunlock", "stepmaniaunlock.controllers",
                  "stepmaniaunlock.ui"],
    "package_data": {"stepmaniaunlock": ["translations/*.qm"]},
    "scripts": ["sucg.py"],
}

if sys.platform == "win32":
    import py2exe
    options = {
        "py2exe": {
            "includes": ["sip"],
            "dll_excludes": ["MSVCP90.dll"],
        }
    }
    arguments.update ({"options": options})
    arguments.update ({"windows": ["sucg.py"]})

setup (**arguments)
