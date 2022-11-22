"""tarstall: A package manager for managing archives
    Copyright (C) 2022  hammy3502

    tarstall is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    tarstall is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with tarstall.  If not, see <https://www.gnu.org/licenses/>."""

import sys
import json

###VERSIONS###
from file import get_shell_file, unlock, full, get_db

version = "1.7.0"
prog_internal_version = 130
file_version = 20

#############


def read_config(key):
    """Read config value.

    Gets the value stored in ~/.tarstall/config for the given key

    Returns:
        Any type: The value found at the key supplied

"""
    try:
        return db["options"][key]
    except KeyError:
        if key in ["Verbose", "AutoInstall", "SkipQuestions", "UpdateURLPrograms"]:
            return False
        elif key in ["PressEnterKey", "WarnMissingDeps"]:
            return True
        elif key == "ShellFile":
            return get_shell_file()
        elif key == "Mode":
            return "cli"
        else:
            return "Bad Value"


def change_config(key, mode, value=None):
    """Change Config Value.

    Flips a value in the config between true and false

    Args:
        key (str): Key to change the value of
        mode (str): flip or change. Determines the mode to use for changing the key's value.
        value (any): When using change, this is value to change the key to. Defaults to None.

    Returns:
        Any type: Value the key was changed to

    """
    if mode == 'flip':
        try:
            db["options"][key] = not db["options"][key]
            r = db["options"][key]
        except KeyError:  # All config values are False by default, so this should make them True.
            db["options"][key] = True
            r = True
    elif mode == 'change':
        try:
            db["options"][key] = value
            r = value
        except KeyError:
            db["options"][key] = value
            r = value
    write_db()
    return r


def vcheck():
    """Is Verbose.

    Returns:
        bool: Whether or not we are verbose

    """
    return read_config('Verbose')


def vprint(to_print, end=None):
    """Print a message only if we're verbose"""
    if verbose:
        if mode == "cli":
            print(to_print, end=end)
        elif mode == "gui":
            try:
                if end is not None:
                    output_area.Update(to_print)
                else:
                    output_area.Update(to_print + end.replace("\n", "").replace("\r", ""))
            except AttributeError:
                pass  # GUI hasn't loaded yet


def get_version(version_type):
    """Get Script Version.

    Args:
        version_type (str): prog_internal_version/file_version/version to get the program/file/end-user version

    Returns:
        str/int: Version of the type specified. Int for prog/file and str for version.

    """
    if version_type == 'prog_internal_version':
        return prog_internal_version
    elif version_type == 'file_version':
        return file_version
    elif version_type == 'version':
        return version


def write_db():
    """Write Database.

    Writes the database to file

    """
    try:
        with open(full("~/.tarstall/database"), "w") as dbf:
            json.dump(db, dbf, indent=4)
        vprint("Database written!")
    except FileNotFoundError:
        print(json.dumps(db))
        print("The tarstall database could not be written to! Something is very wrong...")
        print("The database has been dumped to the screen; you should keep a copy of it.")
        print("You may be able to restore tarstall to working order by placing the above" +
              " database dump into a file called \"database\" in ~/.tarstall")
        print("Rest in peace if you're not in a CLI app right now...")
        unlock()
        sys.exit(3)


"""
Database structure

{
    "options" : {
        "Verbose": False,
        "AutoInstall": False,
        "ShellFile": ".bashrc",
        "SkipQuestions": False,
        "UpdateURLPrograms": False,
        "PressEnterKey": True
    }
    "version" : {
        "file_version": file_version,
        "prog_internal_version": prog_internal_version,
        "branch": "master"
    }
    "programs": {
        "package": {
            "install_type": "default",
            "post_upgrade_script": None,
            "desktops": [
                "desktop_file_name"
            ],
            "update_url": None,
            "has_path": False,
            "binlinks": [],
            "update_archive_type": None
        }
    }
}
"""

db = get_db()
verbose = vcheck()
mode = read_config("Mode")

install_bar = None  # Holds a progress bar if we're in a GUI
output_area = None  # Holds a text area if we're in a GUI (for displaying status messages)

if db != {}:
    vprint("Database loaded successfully!")

try:
    branch = db["version"]["branch"]
except KeyError:
    branch = "master"
