#!/usr/bin/env python
"""Install the MayaEditor module into the Maya modules directory."""
import argparse
import os
import platform
import sys
from pathlib import Path

MayaLocations = {
    "Linux": "/maya/",
    "Darwin": "/Library/Preferences/Autodesk/maya",
    "Windows": "\\Documents\\maya\\",
}


def install_module(location: str, os_name: str) -> None:
    """Write the MayaEditor.mod file into the Maya modules directory.

    Parameters
    ----------
    location : str
        Path to the Maya preferences directory for the current OS.
    os_name : str
        Operating system name (``Windows``, ``Darwin``, ``Linux``).
    """
    print(f"installing to {location}")
    current_dir = Path.cwd()

    if os_name == "Windows":
        module_dir = Path(location + "\\modules")
        module_path = location + "modules\\MayaEditor.mod"
    else:
        module_dir = Path(location + "//modules")
        module_path = location + "//modules/MayaEditor.mod"

    module_dir.mkdir(exist_ok=True)

    if not Path(module_path).is_file():
        print("writing module file")
        with open(module_path, "w") as file:
            file.write(f"+ MayaEditor 1.0 {current_dir}\n")
            file.write("MAYA_PLUG_IN_PATH +:= plug-ins\n")


def check_maya_installed(op_sys: str) -> str:
    """Check that a Maya preferences directory exists for the current OS.

    Parameters
    ----------
    op_sys : str
        The current operating system name.

    Returns
    -------
    str
        The Maya preferences directory path.

    Raises
    ------
    SystemExit
        If the Maya install directory is not found.
    """
    mloc = f"{Path.home()}{MayaLocations.get(op_sys)}"
    if not os.path.isdir(mloc):
        print("Error can't find maya install")
        sys.exit(-1)
    return mloc


if __name__ == "__main__":
    try:
        op_sys = platform.system()
        m_loc = check_maya_installed(op_sys)
    except Exception:
        print("Error can't find maya install")
        sys.exit(-1)
    install_module(m_loc, op_sys)