#!/usr/bin/env python
# file: setup.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2020 R.F. Smith <rsmith@xs4all.nl>
# Created: 2020-10-25T12:18:04+0100
# Last modified: 2020-12-08T20:55:06+0100
"""Script to install scripts for the local user."""

import os
import shutil
import sys
import sysconfig

# What to install
scripts = [
    ("stl2pdf.py", ".py"),
    ("stl2pov.py", ".py"),
    ("stl2ps.py", ".py"),
    ("stlinfo.py", ".py"),
]

# Preparation
if os.name == "posix":
    destdir = sysconfig.get_path("scripts", "posix_user")
    destdir2 = ""
elif os.name == "nt":
    destdir = sysconfig.get_path("scripts", os.name)
    destdir2 = sysconfig.get_path("scripts", os.name + "_user")
else:
    print(f"The system '{os.name}' is not recognized. Exiting")
    sys.exit(1)
install = "install" in [a.lower() for a in sys.argv]
if install:
    if not os.path.exists(destdir):
        os.mkdir(destdir)
else:
    print("(Use the 'install' argument to actually install scripts.)")
# Actual installation.
for script, nt_ext in scripts:
    base = os.path.splitext(script)[0]
    if os.name == "posix":
        destname = destdir + os.sep + base
        destname2 = ""
    elif os.name == "nt":
        destname = destdir + os.sep + base + nt_ext
        destname2 = destdir2 + os.sep + base + nt_ext
    if install:
        for d in (destname, destname2):
            try:
                shutil.copyfile(script, d)
                print(f"* installed '{script}' as '{destname}'.")
                os.chmod(d, 0o700)
                break
            except (OSError, PermissionError, FileNotFoundError):
                pass  # Can't write to destination
        else:
            print(f"! installation of '{script}' has failed.")
    else:
        print(f"* '{script}' would be installed as '{destname}'")
        if destname2:
            print(f"  or '{destname2}'")
