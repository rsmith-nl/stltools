#!/usr/bin/env python
# file: setup.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2020 R.F. Smith <rsmith@xs4all.nl>
# SPDX-License-Identifier: MIT
# Created: 2020-10-25T12:18:04+0100
# Last modified: 2022-01-23T18:07:08+0100
"""Install self-contained scripts for the local user."""

import os
import py_compile
import shutil
import sys
import sysconfig
import tempfile
import zipfile as z


# What to install; (installed name, module, script, nt-extension)
SCRIPTS = (
    ("stl2pov", "stltools", "stl2pov.py", ".py"),
    ("stl2ps", "stltools", "stl2ps.py", ".py"),
    ("stl2pdf", "stltools", "stl2pdf.py", ".py"),
    ("stlinfo", "stltools", "stlinfo.py", ".py"),
)


def main():
    """Entry point for the setup script."""
    dirs = dirnames()
    cmd = None
    if len(sys.argv) == 2:
        cmd = sys.argv[1].lower()
    if cmd == "install":
        # Create primary installation directory if it doesn't exist.
        if not os.path.exists(dirs[0]):
            os.makedirs(dirs[0])
            print(f"Created “{dirs[0]}”. Do not forget to add it to your $PATH.")
    elif cmd in ("uninstall", "clean"):
        pass
    else:
        print(f"Usage {sys.argv[0]} [install|uninstall|clean]")
    # Actual (de)installation.
    for installed_name, module, script, nt_ext in SCRIPTS:
        names = destnames(installed_name, nt_ext, dirs)
        if cmd == "install":
            do_install(installed_name, module, script, nt_ext, names)
        elif cmd == "uninstall":
            do_uninstall(names)
        elif cmd == "clean":
            remove(installed_name)
        else:
            print(f"* '{script}' would be installed as '{names[0]}'")
            if names[1]:
                print(f"  or '{names[1]}'")


def dirnames():
    if os.name == "posix":
        destdir = sysconfig.get_path("scripts", "posix_user")
        destdir2 = ""
    elif os.name == "nt":
        destdir = sysconfig.get_path("scripts", os.name)
        destdir2 = sysconfig.get_path("scripts", os.name + "_user")
    else:
        print(f"The system '{os.name}' is not recognized. Exiting")
        sys.exit(1)
    return destdir, destdir2


def destnames(base, nt_ext, dest):
    if os.name == "posix":
        destname = dest[0] + os.sep + base
        destname2 = ""
    elif os.name == "nt":
        destname = dest[0] + os.sep + base + nt_ext
        destname2 = dest[1] + os.sep + base + nt_ext
    return destname, destname2


def do_install(nm, module, main, nt_ext, names):
    # Actual installation.
    remove(nm)
    mkarchive(nm, module, main=main)
    for n in names:
        try:
            shutil.copyfile(nm, n)
            print(f"* installed '{nm}' as '{n}'.")
            os.chmod(n, 0o700)
            break
        except (OSError, PermissionError, FileNotFoundError):
            pass  # Can't write to destination
    else:
        print(f"! installation of '{nm}' has failed.")


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
        with z.PyZipFile(
            tmpf, mode="w", compression=z.ZIP_DEFLATED, optimize=lvl
        ) as zf:
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


def do_uninstall(names):
    for n in names:
        if n and remove(n):
            print(f"The file '{n}' has been removed.")


def remove(path):
    """Remove a file, ignoring directories and nonexistant files."""
    try:
        os.remove(path)
        return True
    except (FileNotFoundError, PermissionError, IsADirectoryError, OSError):
        pass
    return False


if __name__ == "__main__":
    main()
