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

import os
from shutil import rmtree, move, which
from subprocess import call, run, PIPE
import re

import file
from generic_manage import wget_with_progress, git_clone_with_progress

import config
import generic

from generic_manage import c_out
from config import verbose


def add_upgrade_url(program, url, type_in=None):
    """Adds an Upgrade URL to a Program.

    Args:
        program (str): The program that will be upgraded
        url (str): The URL containing the archive to upgrade from. THIS MUST BE A VALID URL!!!!!
        type_in (str): File extension for updating. If None, tarstall tries to determine it.
    
    Returns:
        str: Success on success, Need Type if tarstall needs the archive type supplied to it, or
        Bad Type if the supplied type is invalid.

    """
    supported_types = [".tar.gz", ".tar.xz", ".zip", ".7z", ".rar"]
    has_type = type_in is not None
    if not has_type:
        for typ in supported_types:
            if url.endswith(typ):
                has_type = True
                type_in = typ
                break
        if not has_type:
            return "Need Type"
    elif type_in not in supported_types:
        return "Bad Type"
    config.db["programs"][program]["update_url"] = url
    config.db["programs"][program]["update_archive_type"] = type_in
    config.write_db()


def remove_update_url(program):
    """Removes Upgrade URL for Program.

    Args:
        program (str): Program to remove URL of.

    """
    config.db["programs"][program]["update_url"] = None
    config.write_db()


def wget_program(program, show_progress=False, progress_modifier=1):
    """Wget an Archive and Overwrite Program.

    Args:
        program (str): Program that has an update_url to update
        show_progress (bool): Whether to display a progress bar. Defaults to False.
        progress_modifier (int): The number to divide the total progress by. Defaults to 1.

    Returns:
        str: "No wget", "Wget error", "Install error" if install() fails, "Success" on success.

    """
    if not file.check_bin("wget"):
        return "No wget"
    else:
        config.vprint("Creating second temp folder for archive.")
        try:
            rmtree(file.full("/tmp/tarstall-temp2"))
        except FileNotFoundError:
            pass
        os.mkdir("/tmp/tarstall-temp2")
        os.chdir("/tmp/tarstall-temp2")
        generic.progress(10 / progress_modifier, show_progress)
        config.vprint("Downloading archive...")
        url = config.db["programs"][program]["update_url"]
        extension = config.db["programs"][program]["update_archive_type"]
        err = wget_with_progress(url, 10 / progress_modifier, 65 / progress_modifier, show_progress=show_progress)
        if err != 0:
            return "Wget error"
        generic.progress(65 / progress_modifier, show_progress)
        files = os.listdir()
        config.vprint("Renaming archive")
        os.rename("/tmp/tarstall-temp2/{}".format(files[0]), "/tmp/tarstall-temp2/{}".format(program + extension))
        os.chdir("/tmp/")
        generic.progress(70 / progress_modifier, show_progress)
        config.vprint("Using install to install the program.")
        inst_status = install("/tmp/tarstall-temp2/{}".format(program + extension), True, show_progress=False)[0]
        generic.progress(95 / progress_modifier, show_progress)
        try:
            rmtree(file.full("/tmp/tarstall-temp2"))
        except FileNotFoundError:
            pass
        generic.progress(100 / progress_modifier, show_progress)
        if inst_status != "Installed":
            return "Install error"
        else:
            return "Success"


def update_program(program, show_progress=False):
    """Update Program.

    Args:
        program (str): Name of program to update

    Returns:
        str: "No script" if script doesn't exist, "Script error" if script
        failed to execute, or "Success" on a success. Can also be something
        from update_git_program if the program supplied is a
        git installed program. Can also return "OSError" if the supplied
        script doesn't specify the shell to be used. Can also return
        something from wget_program().

    """
    progs = 0
    if config.db["programs"][program]["install_type"] == "git" or config.db["programs"][program]["update_url"] is not None:
        progs += 1
    if config.db["programs"][program]["post_upgrade_script"] is not None:
        if not file.exists(config.db["programs"][program]["post_upgrade_script"]):
            config.db["programs"][program]["post_upgrade_script"] = None
            config.write_db()
            return "No script"
        else:
            progs += 1
    if config.db["programs"][program]["install_type"] == "git":
        status = update_git_program(program, show_progress, progs)
        if status != "Success" and status != "No update":
            return status
        elif config.db["programs"][program]["post_upgrade_script"] is None:
            return status
        elif status == "No update":
            generic.progress(100, show_progress)
            return status
    elif config.db["programs"][program]["update_url"] is not None:
        status = wget_program(program, show_progress, progs)
        if status != "Success":
            return status
        elif config.db["programs"][program]["post_upgrade_script"] is None:
            return status
    if config.db["programs"][program]["post_upgrade_script"] is not None:
        try:
            generic.progress(50 * (progs - 1), show_progress)
            err = call(config.db["programs"][program]["post_upgrade_script"],
                       cwd=file.full("~/.tarstall/bin/{}".format(program)), stdout=c_out)
            generic.progress(100, show_progress)
            if err != 0:
                return "Script error"
            else:
                return "Success"
        except OSError:
            return "OSError"
    return "Does not update"


def update_script(program, script_path):
    """Set Update Script.

    Set a script to run when a program is updated.

    Args:
        program (str): Program to set an update script for
        script_path (str): Path to script to run as an/after update.

    Returns:
        str: "Bad path" if the path doesn't exist, "Success" on success, and "Wiped" on clear.

    """
    if script_path == "":
        config.db["programs"][program]["post_upgrade_script"] = None
        return "Wiped"
    if not file.exists(file.full(script_path)):
        return "Bad path"
    config.db["programs"][program]["post_upgrade_script"] = file.full(script_path)
    config.write_db()
    return "Success"


def update_git_program(program, show_progress=False, progress_modifier=1):
    """Update Git Program.

    Args:
        program (str): Name of program to update
        show_progress (bool): Whether to display a progress bar. Defaults to False.
        progress_modifier (int): The number to divide the total progress by. Defaults to 1.

    Returns:
        str: "No git" if git isn't found, "Error updating" on a generic failure, "Success" on a successful update, and
        "No update" if the program is already up-to-date.

    """
    if not file.check_bin("git"):
        config.vprint("git isn't installed!")
        return "No git"
    generic.progress(5 / progress_modifier, show_progress)
    outp = run(["git", "pull"], cwd=file.full("~/.tarstall/bin/{}".format(program)), stdout=PIPE, stderr=PIPE)
    generic.progress(95 / progress_modifier, show_progress)
    err = outp.returncode
    output = str(outp.stdout) + "\n\n\n" + str(outp.stderr)
    if err != 0:
        config.vprint("Failed updating: {}".format(program))
        generic.progress(100 / progress_modifier, show_progress)
        return "Error updating"
    else:
        if "Already up to date." in output:
            config.vprint("{} is already up to date!".format(program))
            generic.progress(100 / progress_modifier, show_progress)
            return "No update"
        else:
            config.vprint("Successfully updated: {}".format(program))
            generic.progress(100 / progress_modifier, show_progress)
            return "Success"


def update_programs():
    """Update Programs Installed through Git or Ones with Upgrade Scripts.

    Returns:
        str/dict: "No git" if git isn't installed, or a dict containing program names and results from update_git_program()
        It can also return "No programs" if no programs are installed.

    """
    if len(config.db["programs"].keys()) == 0:
        return "No programs"
    if not file.check_bin("git"):
        return "No git"
    increment = int(100 / len(config.db["programs"].keys()))
    progress = 0
    statuses = {}
    generic.progress(progress)
    for p in config.db["programs"].keys():
        if not config.db["programs"][p]["update_url"] and (config.db["programs"][p]["install_type"] == "git" or config.db["programs"][p]["post_upgrade_script"]):
            statuses[p] = update_program(p, False)
        elif (config.db["programs"][p]["update_url"] and config.read_config("UpdateURLPrograms")):
            statuses[p] = update_program(p, False)
        else:
            statuses[p] = "Does not update"
        progress += increment
        generic.progress(progress)
    if progress < 100:
        generic.progress(100)
    return statuses


def change_git_branch(program, branch):
    """Change Git Program's Branch.

    Args:
        program (str): Program to change the git branch of
        branch (str): Branch to change to

    Returns:
        str: "No git", "Error changing", or "Success"

    """
    if not file.check_bin("git"):
        return "No git"
    err = call(["git", "checkout", "-f", branch], cwd=file.full("~/.tarstall/bin/{}".format(program)), stdout=c_out)
    if err != 0:
        return "Error changing"
    else:
        return "Success"


def install(path, overwrite=None, show_progress=True, override_name=None):
    """Install a Program.

    Allows installing an archive, a directory, a single file, or a link to a git repo.

    Args:
        path (str): The path to the file or the URL.
        overwrite (bool/None): See above
        show_progress: Whether to show installation progress or not.
        override_name (str): The name for the program if using a wget install

    Returns:
        (str, str): A status from the installation method and the program's internal name.
    """
    is_url = path.startswith("http://") or path.startswith("https://")
    prog_type = None
    if is_url:
        if path.endswith(".git"):
            prog_type = "git"
        for typ in ["7z", "rar", "zip", "tar.gz", "tar.xz"]:
            if path.endswith(typ):
                prog_type = "wget"
                break
        if prog_type is None:
            return "Bad URL", None
    else:
        if not file.exists(path):
            return "Bad file", None

        if os.path.isdir(path):
            prog_type = "dir"
            if not path.endswith("/"):
                path += "/"
        else:
            file_extension = file.extension(path)
            if file_extension in [".7z", ".rar", ".zip", ".tar.gz", ".tar.xz"]:
                prog_type = "archive"
            else:
                prog_type = "single"
    if override_name is not None:
        program_internal_name = override_name
    elif prog_type == "dir":
        program_internal_name = file.dirname(path)
    else:
        program_internal_name = file.name(path)
    if prog_type == "wget" and override_name is None:
        return "Needs name", None
    if program_internal_name in config.db["programs"]:
        if overwrite is None:
            return "Application exists", None
        else:
            if not overwrite:
                uninstall(program_internal_name, show_progress=False)
                return (_install(path, prog_type, program_internal_name, False, True, show_progress),
                        program_internal_name)
            elif overwrite:
                return (_install(path, prog_type, program_internal_name, True, True, show_progress),
                        program_internal_name)
    else:
        return (_install(path, prog_type, program_internal_name, False, False, show_progress),
                program_internal_name)


def _install(program, program_type, program_internal_name, overwrite=False, reinstall=False, show_progress=True):
    if program_type == "git":
        return _git_install(program, program_internal_name, overwrite=overwrite, reinstall=reinstall)
    elif program_type == "single":
        return _single_install(program, program_internal_name, reinstall=reinstall)
    elif program_type == "dir":
        return _dir_install(program, program_internal_name, overwrite=overwrite, reinstall=reinstall)
    elif program_type == "archive":
        return _archive_install(program, program_internal_name=program_internal_name, overwrite=overwrite, reinstall=reinstall, show_progress=show_progress)
    elif program_type == "wget":
        return _wget_install(program, program_internal_name, overwrite=overwrite, reinstall=reinstall)

def remove_desktop(program, desktop):
    """Remove .desktop

    Removes a .desktop file assosciated with a program and its corresponding entry in the database
    This process is walked through with the end-user

    Args:
        program (str): Program to remove
        desktop (str): Name of .desktop to remove

    """
    try:
        os.remove(file.full("~/.local/share/applications/tarstall/{}.desktop".format(desktop)))
    except FileNotFoundError:
        pass
    config.db["programs"][program]["desktops"].remove(desktop)
    config.write_db()


def remove_paths_and_binlinks(program):
    """Remove PATHs and binlinks for "program"

    Args:
        program (str): Program to remove PATHs and binlinks of

    Returns:
        str: "Complete" or "None exist"

    """
    if not config.db["programs"][program]["has_path"] and config.db["programs"][program]["binlinks"] == []:
        return "None exist"
    file.remove_line(program, "~/.tarstall/.bashrc", 'poundword')
    file.remove_line(program, "~/.tarstall/.fishrc", 'poundword')
    config.db["programs"][program]["has_path"] = False
    config.db["programs"][program]["binlinks"] = []
    config.write_db()
    return "Complete"


def rename(program, new_name):
    """Rename Program.

    Args:
        program (str): Name of program to rename

    Returns:
        str/None: New program name or None if program already exists

    """
    is_single = config.db["programs"][program]["install_type"] == "single"
    config.vprint("Checking that program name isn't already in use")
    if new_name in config.db["programs"]:
        return None
    config.vprint("Updating .desktop files")
    for d in config.db["programs"][program]["desktops"]:
        file.replace_in_file("/.tarstall/bin/{}".format(program), "/.tarstall/bin/{}".format(new_name),
        "~/.local/share/applications/tarstall/{}.desktop".format(d))
        if is_single:
            file.replace_in_file("/.tarstall/bin/{}/{}".format(new_name, program), "/.tarstall/bin/{}/{}".format(new_name, new_name),
        "~/.local/share/applications/tarstall/{}.desktop".format(d))
            move(file.full("~/.local/share/applications/tarstall/{p}-{p}.desktop".format(p=program)),
                 file.full("~/.local/share/applications/tarstall/{p}-{p}.desktop".format(p=new_name)))
    generic.progress(25)
    config.vprint("Replacing PATHs")
    config.db["programs"][new_name] = config.db["programs"].pop(program)
    file.replace_in_file("export PATH=$PATH:~/.tarstall/bin/" + program,
    "export PATH=$PATH:~/.tarstall/bin/" + new_name, "~/.tarstall/.bashrc")
    file.replace_in_file("set PATH $PATH ~/.tarstall/bin/" + program + ' # ' + program,
    "set PATH $PATH ~/.tarstall/bin/" + new_name + ' # ' + new_name, "~/.tarstall/.fishrc")
    generic.progress(50)
    config.vprint("Replacing binlinks")
    file.replace_in_file("'cd " + file.full('~/.tarstall/bin/' + program),
    "'cd " + file.full('~/.tarstall/bin/' + new_name), "~/.tarstall/.bashrc")
    file.replace_in_file(";cd " + file.full("~/.tarstall/bin/" + program) + "/;./",
    ";cd " + file.full("~/.tarstall/bin/" + new_name) + "/;./", "~/.tarstall/.fishrc")
    if is_single:
        file.replace_in_file("./" + program, "./" + new_name, "~/.tarstall/.bashrc")
        file.replace_in_file("alias " + program, "alias " + new_name, "~/.tarstall/.bashrc")
        file.replace_in_file("./" + program, "./" + new_name, "~/.tarstall/.fishrc")
        file.replace_in_file("function " + program, "function " + new_name, "~/.tarstall/.fishrc")
    generic.progress(75)
    config.vprint("Replacing program recognisers")
    file.replace_in_file("# " + program, "# " + new_name, "~/.tarstall/.bashrc")
    file.replace_in_file("# " + program, "# " + new_name, "~/.tarstall/.fishrc")
    move(file.full("~/.tarstall/bin/" + program), file.full("~/.tarstall/bin/" + new_name))
    config.write_db()
    generic.progress(90)
    if is_single:
        config.vprint("Renaming single-file")
        move(file.full("~/.tarstall/bin/{}/{}".format(new_name, program)), file.full("~/.tarstall/bin/{}/{}".format(new_name, new_name)))
    generic.progress(100)
    return new_name


def finish_install(program_internal_name, install_type="default",
                   show_progress=True):
    """End of Install.

    Ran after every program install.

    Args:
        program_internal_name (str): Name of program as stored in the database
        install_type (str): Type of install. Should be 'default', 'git', or 'single'. Defaults to "default"

    Returns:
        str: "Installed".

    """
    generic.progress(90, show_progress)
    config.vprint("Removing temporary install directory (if it exists)")
    try:
        rmtree("/tmp/tarstall-temp")
    except FileNotFoundError:
        pass
    config.vprint("Adding program to tarstall list of programs")
    generic.progress(95, show_progress)
    config.db["programs"].update({program_internal_name: {"install_type": install_type, "desktops": [],
    "post_upgrade_script": None, "update_url": None, "has_path": False, "binlinks": []}})
    config.write_db()
    generic.progress(100, show_progress)
    return "Installed"


def create_desktop(program_internal_name, name, program_file, comment="", should_terminal="", cats=[], icon="", path=""):
    """Create Desktop.

    Create a desktop file for a program installed through tarstall.

    Args:
        program_internal_name (str/None): Name of program or None if not a tarstall program.
        name (str): The name as will be used in the .desktop file
        program_file (str): The file in the program directory to point the .desktop to, or the path to it if program_internal_name is None
        comment (str): The comment as to be displayed in the .desktop file
        should_terminal (str): "True" or "False" as to whether or not a terminal should be shown on program run
        cats (str[]): List of categories to put in .desktop file
        icon (str): The path to a valid icon or a specified icon as would be put in a .desktop file
        path (str): The path to where the .desktop should be run. Only used when program_internal_name is None.

    Returns:
        str: "Already exists" if the .desktop file already exists or "Created" if the desktop file was
        successfully created.

    """
    if program_internal_name is not None:
        exec_path = file.full("~/.tarstall/bin/{}/{}".format(program_internal_name, program_file))
        path = file.full("~/.tarstall/bin/{}/".format(program_internal_name))
        file_name = program_file
        if "/" in file_name:
            file_name += ".tar.gz"
            file_name = file.name(file_name)
        desktop_name = "{}-{}".format(file_name, program_internal_name)
    else:
        exec_path = file.full(program_file)
        desktop_name = name
        path = file.full(path)
    if file.exists("~/.local/share/applications/tarstall/{}.desktop".format(desktop_name)):
        config.vprint("Desktop file already exists!")
        return "Already exists"
    if "Video" in cats or "Audio" in cats and "AudioVideo" not in cats:
        cats.append("AudioVideo")
    if not cats:
        cats = ["Utility"]
    cats = ";".join(cats) + ";"  # Get categories for the .desktop
    if comment != "":
        comment = "Comment=" + comment
    if icon != "":
        icon = "Icon=" + icon
    to_write = """
[Desktop Entry]
Name={name}
{comment}
Path={path}
Exec={exec_path}
{icon}
Terminal={should_terminal}
Type=Application
Categories={categories}
""".format(name=name, comment=comment, exec_path=exec_path,
           should_terminal=should_terminal, categories=cats,
           icon=icon, path=path)
    os.chdir(file.full("~/.local/share/applications/tarstall"))
    file.create("./{}.desktop".format(desktop_name))
    with open(file.full("./{}.desktop".format(desktop_name)), 'w') as f:
        f.write(to_write)
    if program_internal_name is not None:
        config.db["programs"][program_internal_name]["desktops"].append(desktop_name)
        config.write_db()
    return "Created"


def _git_install(git_url, program_internal_name, overwrite=False, reinstall=False):
    """Git Install.

    Installs a program from a URL to a Git repository

    Args:
        git_url (str): URL to Git repository
        program_internal_name (str): Name of program to use
        overwrite (bool): Whether or not to assume the program is already installed and to overwite it

    Returns:
       str: A string from finish_install(), "No rsync", "Installed", or "Error"

    """
    if not file.check_bin("rsync") and overwrite:
        return "No rsync"
    config.vprint("Downloading git repository")
    if overwrite:
        try:
            rmtree(file.full("/tmp/tarstall-temp"))  # Removes temp directory (used during installs)
        except FileNotFoundError:
            pass
        os.mkdir("/tmp/tarstall-temp")
        os.chdir("/tmp/tarstall-temp")
    else:
        os.chdir(file.full("~/.tarstall/bin"))
    generic.progress(5)
    err = git_clone_with_progress(git_url, 5, 65)
    if err != 0:
        return "Error"
    generic.progress(65)
    if overwrite:
        call(["rsync", "-a", "/tmp/tarstall-temp/{}/".format(program_internal_name), file.full("~/.tarstall/bin/{}".format(program_internal_name))], stdout=c_out)
    if not overwrite:
        return finish_install(program_internal_name, "git")
    else:
        generic.progress(100)
        return "Installed"


def add_binlink(file_chosen, program_internal_name):
    """Add Binlink.

    Args:
        file_chosen (str): File to add
        program_internal_name (str): Name of program to binlink

    Returns:
        str: "Added" or "Already there"

    """
    name = file_chosen
    if "/" in name:
        name += ".tar.gz"
        name = file.name(name)
    if name in config.db["programs"][program_internal_name]["binlinks"]:
        return "Already there"
    line_to_add = '\nalias ' + name + "='cd " + file.full('~/.tarstall/bin/' + program_internal_name) + \
    '/ && ./' + file_chosen + "' # " + program_internal_name
    config.vprint("Adding alias to bashrc and fishrc")
    file.add_line(line_to_add, "~/.tarstall/.bashrc")
    line_to_add = "\nfunction " + name + ";cd " + file.full("~/.tarstall/bin/" + program_internal_name) + "/;./" + file_chosen + ";end # " + program_internal_name
    file.add_line(line_to_add, "~/.tarstall/.fishrc")
    config.db["programs"][program_internal_name]["binlinks"].append(name)
    config.write_db()
    return "Added"


def pathify(program_internal_name):
    """Add Program to Path.

    Adds a program to PATH through ~/.tarstall/.bashrc and ~/.tarstall/.fishrc

    Args:
        program_internal_name (str): Name of program to add to PATH

    Returns:
        "Complete" or "Already there"

    """
    if config.db["programs"][program_internal_name]["has_path"]:
        return "Already there"
    config.vprint('Adding program to PATH')
    line_to_write = "\nexport PATH=$PATH:~/.tarstall/bin/" + program_internal_name + ' # ' + program_internal_name
    file.add_line(line_to_write, "~/.tarstall/.bashrc")
    line_to_write = "\nset PATH $PATH ~/.tarstall/bin/" + program_internal_name + ' # ' + program_internal_name
    file.add_line(line_to_write, "~/.tarstall/.fishrc")
    config.db["programs"][program_internal_name]["has_path"] = True
    config.write_db()
    return "Complete"


def create_command(file_extension, program):
    """Create Extraction Command.

    Args:
        file_extension (str): File extension of program (including .)
        program (str): Program name
        overwrite_files (bool): Whether or not the command should overwrite files. Defaults to False.

    Returns:
        str: Command to run, "Bad Filetype", or "No bin_that_is_needed"

    """
    if config.vcheck():  # Creates the command to run to extract the archive
        if file_extension == '.tar.gz' or file_extension == '.tar.xz':
            vflag = 'v'
        elif file_extension == '.zip':
            vflag = ''
        elif file_extension == '.7z':
            vflag = ''
        elif file_extension == '.rar':
            vflag = ''
    else:
        if file_extension == '.tar.gz' or file_extension == '.tar.xz':
            vflag = ''
        elif file_extension == '.zip':
            vflag = '-qq'
        elif file_extension == '.7z':
            vflag = '-bb0 -bso0 -bd '
        elif file_extension == '.rar':
            vflag = '-idcdpq '
    if file_extension == '.tar.gz' or file_extension == '.tar.xz':
        command_to_go = "tar " + vflag + "xf " + program + " -C /tmp/tarstall-temp/"
        if which("tar") is None:
            config.vprint("tar not installed!")
            return "No tar"
    elif file_extension == '.zip':
        command_to_go = 'unzip ' + vflag + ' ' + program + ' -d /tmp/tarstall-temp/'
        if which("unzip") is None:
            config.vprint("unzip not installed!")
            return "No unzip"
    elif file_extension == '.7z':
        command_to_go = '7z x ' + vflag + program + ' -o/tmp/tarstall-temp/'
        if which("7z") is None:
            config.vprint("7z not installed!")
            return "No 7z"
    elif file_extension == '.rar':
        command_to_go = 'unrar x ' + vflag + program + ' /tmp/tarstall-temp/'
        if which("unrar") is None:
            config.vprint("unrar not installed!")
            return "No unrar"
    else:
        config.vprint("Filetype {} not supported!".format(file_extension))
        return "Bad Filetype"
    config.vprint("Running command: " + command_to_go)
    return command_to_go


def _wget_install(url, program_internal_name, reinstall=False, overwrite=False):
    if not file.check_bin("wget"):
        return "No wget"
    if reinstall:
        try:
            config.vprint("Removing old copy of program to reinstall (if it exists!)")
            rmtree("~/.tarstall/bin/{}".format(program_internal_name))
        except FileNotFoundError:
            pass
    config.vprint("Creating temporary folder")
    try:
        rmtree(file.full("/tmp/tarstall-temp2"))
    except FileNotFoundError:
        pass
    os.mkdir("/tmp/tarstall-temp2")
    os.chdir("/tmp/tarstall-temp2")
    generic.progress(10)
    config.vprint("Downloading archive...")

    extension = None
    for typ in ["7z", "rar", "zip", "tar.gz", "tar.xz"]:
        if url.endswith(typ):
            extension = "." + typ
            break
    if extension is None:
        return "Bad URL", None

    err = wget_with_progress(url, 10, 65, show_progress=True)
    if err != 0:
        return "Wget error"

    config.vprint("Renaming archive")
    files = os.listdir()
    os.rename("/tmp/tarstall-temp2/{}".format(files[0]), "/tmp/tarstall-temp2/{}".format(program_internal_name + extension))
    os.chdir("/tmp/")
    generic.progress(70)

    config.vprint("Re-running installer with archive to finish installation")

    inst_status = install("/tmp/tarstall-temp2/{}".format(program_internal_name + extension), overwrite=overwrite, show_progress=False)[0]
    generic.progress(95)
    try:
        rmtree(file.full("/tmp/tarstall-temp2"))
    except FileNotFoundError:
        pass
    generic.progress(100)
    if inst_status != "Installed":
        return "Error"
    else:
        config.vprint("Automatically adding update URL to be install URL")
        add_upgrade_url(program_internal_name, url, extension)
        return "Installed"


def _archive_install(program, program_internal_name, overwrite=False, reinstall=False, show_progress=True):
    """Install Archive.

    Takes an archive and installs it.

    Args:
        program (str): Path to archive to install
        overwrite (bool): Whether or not to assume the program is already installed and to overwite it

    Returns:
       str: A string from finish_install() a string from create_command(), "No rsync", "Bad name", "Installed", or "Error".

    """
    if not file.check_bin("rsync") and overwrite:
        return "No rsync"
    if file.char_check(program_internal_name):
        return "Bad name"
    config.vprint("Removing old temp directory (if it exists!)")
    try:
        rmtree(file.full("/tmp/tarstall-temp"))  # Removes temp directory (used during installs)
    except FileNotFoundError:
        pass
    generic.progress(10, show_progress)
    config.vprint("Creating new temp directory")
    os.mkdir(file.full("/tmp/tarstall-temp"))  # Creates temp directory for extracting archive
    config.vprint("Extracting archive to temp directory")
    file_extension = file.extension(program)
    program = file.spaceify(program)
    command_to_go = create_command(file_extension, program)
    config.vprint('File type detected: ' + file_extension)
    generic.progress(15, show_progress)
    if command_to_go.startswith("No") or command_to_go == "Bad Filetype":
        return command_to_go
    try:
        os.system(command_to_go)  # Extracts program archive
    except:
        config.vprint('Failed to run command: ' + command_to_go + "! Program installation halted!")
        return "Error"
    generic.progress(50, show_progress)
    config.vprint('Checking for folder in folder')
    os.chdir("/tmp/tarstall-temp/")
    if os.path.isdir(file.full('/tmp/tarstall-temp/' + program_internal_name + '/')):
        config.vprint('Folder in folder detected! Using that directory instead...')
        source = file.full('/tmp/tarstall-temp/' + program_internal_name) + '/'
        dest = file.full('~/.tarstall/bin/' + program_internal_name) + '/'
    elif len(os.listdir()) == 1 and os.path.isdir(os.listdir()[0]):
        config.vprint("Single folder detected!")
        folder = os.listdir()[0]
        source = file.full("/tmp/tarstall-temp/" + folder) + '/'
        dest = file.full("~/.tarstall/bin/" + program_internal_name) + '/'
    else:
        config.vprint('Folder in folder not detected!')
        source = file.full('/tmp/tarstall-temp') + '/'
        dest = file.full('~/.tarstall/bin/' + program_internal_name) + '/'
    config.vprint("Moving program to directory")
    if overwrite:
        if verbose:
            verbose_flag = "v"
        else:
            verbose_flag = ""
        call(["rsync", "-a{}".format(verbose_flag), source, dest], stdout=c_out)
    else:
        move(source, dest)
    generic.progress(80, show_progress)
    config.vprint('Removing old temp directory...')
    os.chdir("/tmp")
    try:
        rmtree(file.full("/tmp/tarstall-temp"))
    except FileNotFoundError:
        config.vprint('Temp folder not found so not deleted!')
    if not overwrite:
        return finish_install(program_internal_name, show_progress=show_progress)
    else:
        generic.progress(100, show_progress)
        return "Installed"


def _single_install(program, program_internal_name, reinstall=False):
    """Install Single File.

    Will create a folder to put the single file in.

    Args:
        program (str): Path to file to install
        program_internal_name (str): Name to use internally for program
        reinstall (bool, optional): Whether to reinstall or not. Defaults to False.

    """
    if not reinstall:
        config.vprint("Creating folder to house file in")
        os.mkdir(file.full("~/.tarstall/bin/{}".format(program_internal_name)))
    generic.progress(5)
    config.vprint("Marking executable as... executable")
    os.system('sh -c "chmod +x {}"'.format(program))
    generic.progress(10)
    if reinstall:
        config.vprint("Deleting old single-executable...")
        os.remove(file.full("~/.tarstall/bin/{p}/{p}".format(p=program_internal_name)))
    generic.progress(15)
    config.vprint("Moving to tarstall directory and renaming...")
    move(file.full(program), file.full("~/.tarstall/bin/{p}/{p}".format(p=program_internal_name)))
    generic.progress(90)
    return finish_install(program_internal_name, "single")


def _dir_install(program_path, program_internal_name, overwrite=False, reinstall=False):
    """Install Directory.

    Installs a directory as a program

    Args:
        program_path (str): Path to directory to install
        program_internal_name (str): Name of program
        overwrite (bool): Whether or not to assume the program is already installed and to overwite it

    Returns:
       str: A string from finish_install(), "Installed", or "No rsync"

    """
    generic.progress(10)
    if not file.check_bin("rsync") and overwrite:
        return "No rsync"
    config.vprint("Moving folder to tarstall destination")
    if overwrite:
        call(["rsync", "-a", program_path, file.full("~/.tarstall/bin/{}".format(program_internal_name))], stdout=c_out)
        rmtree(program_path)
    else:
        move(program_path, file.full("~/.tarstall/bin/"))
    if not overwrite:
        return finish_install(program_internal_name)
    else:
        return "Installed"


def uninstall(program, show_progress=True):
    """Uninstall a Program.

    Args:
        program (str): Name of program to uninstall
        show_progress (bool): Whether to show progress or not.

    Returns:
        str: Status detailing the uninstall. Can be: "Not installed" or "Success".

    """
    if not program in config.db["programs"]:
        return "Not installed"
    config.vprint("Removing program files")
    rmtree(file.full("~/.tarstall/bin/" + program + '/'))
    generic.progress(40, show_progress)
    config.vprint("Removing program from PATH and any binlinks for the program")
    file.remove_line(program, "~/.tarstall/.bashrc", 'poundword')
    generic.progress(50, show_progress)
    config.vprint("Removing program desktop files")
    if config.db["programs"][program]["desktops"]:
        progress = 50
        adder = int(30 / len(config.db["programs"][program]["desktops"]))
        for d in config.db["programs"][program]["desktops"]:
            try:
                os.remove(file.full("~/.local/share/applications/tarstall/{}.desktop".format(d)))
            except FileNotFoundError:
                pass
            progress += adder
            generic.progress(progress, show_progress)
    generic.progress(80, show_progress)
    config.vprint("Removing program from tarstall list of programs")
    del config.db["programs"][program]
    config.write_db()
    generic.progress(100, show_progress)
    return "Success"


def list_programs():
    """List Installed Programs.

    Returns:
        str[]: List of installed programs by name
    
    """
    return list(config.db["programs"].keys())

