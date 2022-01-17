#!/usr/bin/env python
# file: setup.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2020 R.F. Smith <rsmith@xs4all.nl>
# SPDX-License-Identifier: MIT
# Created: 2020-10-25T12:18:04+0100
# Last modified: 2022-01-18T00:16:29+0100
"""Script to install self-contained scripts for the local user."""

import os
import py_compile
import shutil
import sys
import sysconfig
import tempfile
import zipfile as z


def main():
    """Entry point for the setup script."""
    # What to install; (name, module, main, nt-extension)
    scripts = [
        ("stl2pov", "stltools", "stl2pov.py", ".py"),
        ("stl2ps", "stltools", "stl2ps.py", ".py"),
        ("stl2pdf", "stltools", "stl2pdf.py", ".py"),
        ("stlinfo", "stltools", "stlinfo.py", ".py"),
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
            os.makedirs(destdir)
    else:
        print("(Use the 'install' argument to actually install scripts.)")
    do_install(install, scripts, destdir, destdir2)


def do_install(install, scripts, destdir, destdir2):
    # Actual installation.
    for nm, module, main, nt_ext in scripts:
        remove(nm)
        mkarchive(nm, module, main=main)
        base = os.path.splitext(nm)[0]
        if os.name == "posix":
            destname = destdir + os.sep + base
            destname2 = ""
        elif os.name == "nt":
            destname = destdir + os.sep + base + nt_ext
            destname2 = destdir2 + os.sep + base + nt_ext
        if install:
            for d in (destname, destname2):
                try:
                    shutil.copyfile(nm, d)
                    print(f"* installed '{nm}' as '{destname}'.")
                    os.chmod(d, 0o700)
                    break
                except (OSError, PermissionError, FileNotFoundError):
                    pass  # Can't write to destination
            else:
                print(f"! installation of '{nm}' has failed.")
        else:
            print(f"* '{nm}' would be installed as '{destname}'")
            if destname2:
                print(f"  or '{destname2}'")


def mkarchive(name, modules, main="__main__.py"):
    """
    Create a runnable archive.

    Arguments:
        name: Name of the archive.
        modules: Module name or iterable of module names to include.
        main: Name of the main file. Defaults to __main__.py
    """
    std = "__main__.py"
    # extract shebang from current script so we can use SHEBANGFIX on FreeBSD.
    with open(sys.argv[0], "rb") as f:
        shebang = f.readline()
    if isinstance(modules, str):
        modules = [modules]
    if main != std:
        remove(std)
        os.link(main, std)
    # Optimization level for compile.
    lvl = 2
    # Forcibly compile __main__.py lest we use an old version!
    py_compile.compile(std, optimize=lvl)
    with tempfile.TemporaryFile() as tmpf:
        with z.PyZipFile(tmpf, mode="w", compression=z.ZIP_DEFLATED, optimize=lvl) as zf:
            zf.writepy(std)
            for m in modules:
                zf.writepy(m)
        if main != std:
            remove(std)
        tmpf.seek(0)
        archive_data = tmpf.read()
    with open(name, "wb") as archive:
        archive.write(shebang)
        archive.write(archive_data)
    os.chmod(name, 0o755)


def remove(path):
    """Remove a file, ignoring directories and nonexistant files."""
    try:
        os.remove(path)
    except (FileNotFoundError, PermissionError, IsADirectoryError, OSError):
        pass


if __name__ == "__main__":
    main()
