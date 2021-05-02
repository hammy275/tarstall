import datetime
import getpass
import json
import os
import sys
from shutil import which, rmtree, move, copyfile, copytree
from subprocess import call

import requests

import config
import generic
from generic_manage import wget_with_progress, git_clone_with_progress, c_out, can_update


def reinstall_deps():
    """Reinstall Dependencies

    Install the dependencies for tarstall by using the installer.

    Returns:
        str: "No wget", "Wget error", "Installer error", or "Success"

    """
    if which("wget") is None:
        return "No wget"
    config.vprint("Deleting and re-creating temp directory")
    try:
        rmtree("/tmp/tarstall-temp")
    except FileNotFoundError:
        pass
    os.mkdir("/tmp/tarstall-temp/")
    os.chdir("/tmp/tarstall-temp/")
    generic.progress(5)
    config.vprint("Obtaining tarstall installer...")
    url = "https://raw.githubusercontent.com/hammy3502/tarstall/{}/install_tarstall".format(config.db["version"]["branch"])
    err = wget_with_progress(url, 5, 60)
    if err != 0:
        return "Wget error"
    generic.progress(60)
    config.vprint("Creating file to skip tarstall's installer prompt")
    config.create("/tmp/dont-ask-me")
    config.vprint("Running tarstall setup to (re)-install dependencies")
    err = call([sys.executable, "install_tarstall"], stdout=c_out, stderr=c_out)
    generic.progress(95)
    config.vprint("Removing installer skip file")
    os.remove("/tmp/dont-ask-me")
    generic.progress(100)
    if err != 0:
        return "Installer error"
    return "Success"


def repair_tarstall():
    """Attempts to Repair Tarstall.

    Unlike the Database repair-er, this won't have the user lose any data.

    Returns:
        str: Any string from update()

    """
    config.vprint("Forcing tarstall update to repair tarstall!")
    return update(True, True)


def repair_db():
    """Attempts to Repair Tarstall DB.

    WARNING: THIS SHOULD NOT BE USED UNLESS THE DATABASE CANNOT BE RECOVERED OTHERWISE!!!
    BECAUSE AN EMPTY DATABASE ONLY HAS LIMITED KNOWLEDGE OF PAST OPERATIONS, SEVERAL THINGS CANNOT
    AND WILL NOT BE RECOVERED!!!!!!
    """
    config.vprint("Attempting repair of database...")

    config.vprint("Getting stock database to build off of")
    new_db = get_default_db()
    generic.progress(5)

    config.vprint("Re-discovering programs:")
    for pf in os.listdir(config.full("~/.tarstall/bin/")):
        config.vprint("Re-discovering " + pf, end="\r")
        prog_info = {pf: {"install_type": "default", "desktops": [],
        "post_upgrade_script": None, "update_url": None, "has_path": False, "binlinks": []}}
        if ".git" in os.listdir(config.full("~/.tarstall/bin/{}".format(pf))):
            prog_info[pf]["install_type"] = "git"
        elif len(os.listdir(config.full("~/.tarstall/bin/{}".format(pf)))) == 1:
            prog_info[pf]["install_type"] = "single"
        new_db["programs"].update(prog_info)

    generic.progress(20)

    config.vprint("Reading tarstall's bashrc file for further operations...")
    with open(config.full("~/.tarstall/.bashrc")) as f:
        bashrc_lines = f.readlines()

    generic.progress(25)

    config.vprint("Re-registering PATHs")
    for l in bashrc_lines:
        if l.startswith("export PATH=$PATH") and '#' in l:
            program = l[l.find("#")+2:].rstrip()
            config.vprint("Re-registering PATH for " + program, end="\r")
            new_db["programs"][program]["has_path"] = True

    generic.progress(35)

    config.vprint("Re-registering binlinks")
    for l in bashrc_lines:
        if l.startswith("alias ") and '#' in l:
            program = l[l.find("#")+2:].rstrip()
            config.vprint("Re-registering a binlink or binlinks for " + program, end="\r")
            binlinked_file = l[6:l.find("=")]
            new_db["programs"][program]["binlinks"].append(binlinked_file)

    generic.progress(60)

    config.vprint("Backing up old database...")
    date_str = datetime.datetime.today().strftime("%d-%m-%Y-%H-%M-%S")
    move(config.full("~/.tarstall/database"), config.full("~/.tarstall/database-backup-{}.bak".format(date_str)))

    generic.progress(80)

    config.vprint("Re-discovering .desktop files...")
    for d in os.listdir(config.full("~/.local/share/applications/tarstall")):
        # File name: {program}-{package}.desktop
        # Stored in DB as {program}-package
        desktop_name = config.name(config.full("~/.local/share/applications/tarstall/{}".format(d)))  # Returns "{program}-{package}"
        desktop_info = desktop_name.split("-")
        new_db["programs"][desktop_info[1]]["desktops"].append("{}-{}".format(desktop_info[0], desktop_info[1]))

    generic.progress(95)

    config.vprint("Writing new database...")
    config.db = new_db
    config.write_db()

    config.vprint("Database repair complete!")
    generic.progress(100)
    return


def change_branch(branch, reset=False):
    """Change Branch.

    Args:
        branch (str): Branch to change to (master or beta)
        reset (bool): If changing to stable, whether or not to reset tarstall. Defaults to False.

    Returns:
        str: "Bad branch" if switching to an invalid branch, "Success" on master --> beta,
        "Reset" if beta --> master and reset is complete, or "Waiting" if beta --> master
        without doing the reset.

    """
    if branch == "master":
        if not config.check_bin("git"):
            reset = False
            generic.progress(50)
    if branch not in ["master", "beta"]:
        return "Bad branch"
    config.vprint("Switching branch and writing change to file")
    config.db["version"]["branch"] = branch
    config.branch = branch
    config.write_db()
    if branch == "beta":
        config.vprint("Updating tarstall...")
        generic.progress(65)
        update()
        return "Success"
    elif branch == "master":
        generic.progress(10)
        if reset:
            config.vprint("Resetting by forcing an update of tarstall.")
            update(True, False)
            generic.progress(70)
            config.vprint("Deleting old .desktops")
            for prog in config.db["programs"]:
                if config.db["programs"][prog]["desktops"]:
                    for d in config.db["programs"][prog]["desktops"]:
                        try:
                            os.remove(config.full("~/.local/share/applications/tarstall/{}.desktop".format(d)))
                        except FileNotFoundError:
                            pass
            generic.progress(85)
            config.vprint("Writing 'refresh' key to database to tell tarstall to reset itself")
            config.db = {"refresh": True}
            config.write_db()
            generic.progress(100)
            config.unlock()
            config.vprint("Done!")
            return "Reset"
        else:
            generic.progress(100)
            return "Waiting"


def tarstall_startup(start_fts=False, del_lock=False, old_upgrade=False, force_fix=False):
    """Run on Startup.

    Runs on tarstall startup to perform any required checks and upgrades.
    This function should always be run before doing anything else with tarstall.

    Args:
        start_fts (bool): Whether or not to start first time setup
        del_lock (bool): Whether or not to remove the lock (if it exists)

    Returns:
        str: One of many different values indicating the status of tarstall. Those include:
        "Not installed", "Locked", "Good" (nothing bad happened), "Root", "Old" (happens
        when upgrading from tarstall prog_version 1), and "Unlocked" if tarstall
        was successfully unlocked. Can also return a string from first_time_setup,
        "DB Broken" if the database is corrupt, or "Missing Deps" if missing one or more dependencies.

    """
    final_status = "Good"
    missing_deps = False
    try:
        import tkinter
    except (ModuleNotFoundError, ImportError):
        missing_deps = True
    try:
        import PySimpleGUI
    except (ModuleNotFoundError, ImportError):
        missing_deps = True
    try:
        import requests
    except (ModuleNotFoundError, ImportError):
        missing_deps = True
    if missing_deps:
        final_status = "Missing Deps"
    if config.locked():  # Lock check
        config.vprint("Lock file detected at /tmp/tarstall-lock.")
        if del_lock:
            config.vprint("Deleting the lock and continuing execution!")
            config.unlock()
            return "Unlocked"
        else:
            config.vprint("Lock file removal not specified; staying locked.")
            return "Locked"
    else:
        config.lock()

    if config.db == {"refresh": True}:  # Downgrade check
        config.vprint("Finishing downgrade")
        generic.progress(5)
        config.create("~/.tarstall/database")
        create_db()
        generic.progress(15)
        config.db = config.get_db()
        config.write_db()
        generic.progress(20)
        rmtree(config.full("~/.tarstall/bin"))
        generic.progress(90)
        os.mkdir(config.full("~/.tarstall/bin"))
        generic.progress(100)
        config.vprint("Downgrade complete, returning back to tarstall execution...")

    if start_fts:  # Check if -f or --first is supplied
        return first_time_setup()

    if not(config.exists('~/.tarstall/tarstall_execs/tarstall')):  # Make sure tarstall is installed
        return "Not installed"

    if config.db == {}:
        if force_fix:
            pass
        else:
            return "DB Broken"

    file_version = get_file_version('file')
    while config.get_version('file_version') > file_version:  # Lingering upgrades check
        config.vprint("Upgrading files and database from {} to {}.".format(file_version, config.get_version("file_version")))

        if file_version == 11:
            config.vprint("Adding 'update_url' key in database for all programs!")
            for program in config.db["programs"]:
                config.db["programs"][program]["update_url"] = None

        elif file_version == 12:
            config.vprint("Adding 'has_path' and 'binlinks' to programs.")
            for program in config.db["programs"]:
                config.db["programs"][program]["has_path"] = False
                config.db["programs"][program]["binlinks"] = []

        elif file_version == 13:
            config.vprint("Adding 'UpdateURLPrograms' to config database.")
            config.db["options"]["UpdateURLPrograms"] = False

        elif file_version == 14:
            config.vprint("Adding 'PressEnterKey' to config database.")
            config.db["options"]["PressEnterKey"] = True

        elif file_version == 15:
            config.vprint("Swapping to new saving of program type")
            for program in config.db["programs"]:
                if config.db["programs"][program]["git_installed"]:
                    config.db["programs"][program]["install_type"] = "git"
                else:
                    config.db["programs"][program]["install_type"] = "default"
                del config.db["programs"][program]["git_installed"]

        elif file_version == 16:
            config.vprint("Adding WarnMissingDeps key...")
            config.db["options"]["WarnMissingDeps"] = True

        elif file_version == 17:
            config.vprint("Moving .desktop files to tarstall subdirectory")
            if not config.exists("~/.local/share/applications/tarstall"):
                config.vprint("Creating tarstall .desktop directory")
                os.mkdir(config.full("~/.local/share/applications/tarstall"))
            for program in config.db["programs"]:
                for desktop in config.db["programs"][program]["desktops"]:
                    if config.exists("~/.local/share/applications/{}.desktop".format(desktop)):
                        config.vprint("Moving {} to tarstall subdirectory".format(desktop))
                        move(config.full("~/.local/share/applications/{}.desktop".format(desktop)), config.full("~/.local/share/applications/tarstall/{}.desktop".format(desktop)))
                    elif config.exists("~/.local/share/applications/tarstall/{}.desktop".format(desktop)):
                        config.vprint("Not moving {}, it's already in our new directory!".format(desktop))

        elif file_version == 18:
            config.vprint("Deleting version.json (if it exists!)")
            if config.exists("~/.tarstall/version.json"):
                os.remove(config.full("~/.tarstall/version.json"))

        config.db["version"]["file_version"] += 1
        file_version = get_file_version('file')
        config.write_db()

    if get_file_version('prog') == 1:  # Online update broke between prog versions 1 and 2 of tarstall
        return "Old"

    if config.read_config("AutoInstall"):  # Auto-update, if enabled
        update(show_progress=False)

    username = getpass.getuser()  # Root check
    if username == 'root':
        config.vprint("We're running as root!")
        return "Root"

    return final_status


def get_default_db():
    """Get Default DB"""
    db_template = {
        "options": {
            "Verbose": False,
            "AutoInstall": False,
            "ShellFile": config.get_shell_file(),
            "SkipQuestions": False,
            "UpdateURLPrograms": False,
            "PressEnterKey": True
        },
        "version": {
            "file_version": config.file_version,
            "prog_internal_version": config.prog_internal_version,
            "branch": "master"
        },
        "programs": {
        }
    }
    return db_template


def create_db():
    """Creates Database."""
    config.db = get_default_db()
    config.write_db()


def update(force_update=False, show_progress=True):
    """Update tarstall.

    Checks to see if we should update tarstall, then does so if one is available

    Args:
        force_update (bool): Whether or not to force an update to happen. Defaults to False.
        show_progress (bool): Whether or not to show progress to the user. Defaults to True.

    Returns:
        str: "No requests" if requests isn't installed, "No internet if there isn't
        an internet connection, "Newer version" if the installed
        version is newer than the one online, "No update" if there is no update,
        "Updated" upon a successful update, "No git" if git isn't installed,
        or "Failed" if it failed.

    """
    if not can_update and not force_update:
        config.vprint("requests isn't installed.")
        return "No requests"
    elif not config.check_bin("git"):
        config.vprint("git isn't installed.")
        return "No git"
    generic.progress(5, show_progress)
    prog_version_internal = config.get_version('prog_internal_version')
    if not force_update:
        config.vprint("Checking version on GitHub")
        final_version = get_online_version('prog')
        if final_version == -1:
            generic.progress(100, show_progress)
            return "No requests"
        elif final_version == -2:
            generic.progress(100, show_progress)
            return "No internet"
        config.vprint('Installed internal version: ' + str(prog_version_internal))
        config.vprint('Version on GitHub: ' + str(final_version))
    generic.progress(10, show_progress)
    if force_update or final_version > prog_version_internal:
        try:
            rmtree("/tmp/tarstall-update")
        except FileNotFoundError:
            pass
        os.chdir("/tmp/")
        os.mkdir("tarstall-update")
        os.chdir("/tmp/tarstall-update")
        config.vprint("Cloning tarstall repository from git")
        err = git_clone_with_progress("https://github.com/hammy3502/tarstall.git", 10, 55, config.branch)
        if err != 0:
            generic.progress(100, show_progress)
            return "Failed"
        generic.progress(55, show_progress)
        config.vprint("Removing old tarstall files")
        os.chdir(config.full("~/.tarstall/"))
        files = os.listdir()
        to_keep = ["bin", "database", ".bashrc", ".fishrc"]
        progress = 55
        adder = 15 / int(len(files) - len(to_keep))
        for f in files:
            if f not in to_keep:
                if os.path.isdir(config.full("~/.tarstall/{}".format(f))):
                    rmtree(config.full("~/.tarstall/{}".format(f)))
                else:
                    os.remove(config.full("~/.tarstall/{}".format(f)))
                progress += adder
                generic.progress(progress, show_progress)
        generic.progress(70, show_progress)
        config.vprint("Moving in new tarstall files")
        os.chdir("/tmp/tarstall-update/tarstall/")
        files = os.listdir()
        to_ignore = [".git", ".gitignore", "README.md", "readme-images", "COPYING", "requirements.txt",
                     "requirements-gui.txt", "tests", "install_tarstall", "version", "version.json"]
        progress = 70
        adder = 25 / int(len(files) - len(to_ignore))
        for f in files:
            if f not in to_ignore:
                move("/tmp/tarstall-update/tarstall/{}".format(f), config.full("~/.tarstall/{}".format(f)))
                progress += adder
                generic.progress(progress, show_progress)
        generic.progress(95, show_progress)
        config.vprint("Removing old tarstall temp directory")
        os.chdir(config.full("~/.tarstall/"))
        try:
            rmtree("/tmp/tarstall-update")
        except FileNotFoundError:
            pass
        if not force_update:
            config.db["version"]["prog_internal_version"] = final_version
            config.write_db()
        generic.progress(100, show_progress)
        return "Updated"
    elif final_version < prog_version_internal:
        generic.progress(100, show_progress)
        return "Newer version"
    else:
        generic.progress(100, show_progress)
        return "No update"


def erase():
    """Remove tarstall.

    Returns:
        str: "Erased" on success, "Not installed" if tarstall isn't installed, or "No line" if the shell
        line couldn't be removed.

    """
    if not (config.exists(config.full("~/.tarstall/tarstall_execs/tarstall"))):
        return "Not installed"
    config.vprint('Removing source line from bashrc and fishrc')
    if config.get_shell_file() is not None:
        if "fish" in config.get_shell_file():
            path_to_remove = "fishrc"
        else:
            path_to_remove = "bashrc"
        config.remove_line("~/.tarstall/.{}".format(path_to_remove), config.get_shell_path(), "word")
    else:
        to_return = "No line"
    to_return = "Erased"
    generic.progress(10)
    config.vprint("Removing .desktop files")
    for prog in config.db["programs"]:
        if config.db["programs"][prog]["desktops"]:
            for d in config.db["programs"][prog]["desktops"]:
                try:
                    os.remove(config.full("~/.local/share/applications/tarstall/{}.desktop".format(d)))
                except FileNotFoundError:
                    pass
    generic.progress(40)
    config.vprint('Removing tarstall directory')
    rmtree(config.full('~/.tarstall'))
    generic.progress(90)
    try:
        rmtree("/tmp/tarstall-temp")
    except FileNotFoundError:
        pass
    generic.progress(95)
    try:
        rmtree("/tmp/tarstall-temp2")
    except FileNotFoundError:
        pass
    generic.progress(98)
    try:
        os.remove(config.full("~/.local/share/applications/tarstall/tarstall.desktop"))
    except FileNotFoundError:
        pass
    config.unlock()
    generic.progress(100)
    return to_return


def first_time_setup():
    """First Time Setup.

    Sets up tarstall for the first time.

    Returns:
        str: "Already installed" if already installed, "Success" on installation success, "Unsupported shell"
        on success but the shell being used isn't supported.

    """
    os.chdir(os.path.dirname(__file__))
    if config.exists(config.full('~/.tarstall/tarstall_execs/tarstall')):
        return "Already installed"
    print('Installing tarstall to your system...')
    generic.progress(5)
    try:
        os.mkdir(config.full("~/.tarstall"))
    except FileExistsError:
        rmtree(config.full("~/.tarstall"))
        os.mkdir(config.full("~/.tarstall"))
    try:
        os.mkdir(config.full("/tmp/tarstall-temp/"))
    except FileExistsError:
        rmtree(config.full("/tmp/tarstall-temp"))
        os.mkdir(config.full("/tmp/tarstall-temp/"))
    generic.progress(10)
    os.mkdir(config.full("~/.tarstall/bin"))
    config.create("~/.tarstall/database")
    create_db()
    config.create("~/.tarstall/.bashrc")  # Create directories and files
    if not config.exists("~/.config"):
        os.mkdir(config.full("~/.config"))
    if not config.exists("~/.config/fish"):
        os.mkdir(config.full("~/.config/fish"))
    if not config.exists("~/.config/fish/config.fish"):
        config.create("~/.config/fish/config.fish")
    config.create("~/.tarstall/.fishrc")
    generic.progress(15)
    progress = 15
    files = os.listdir()
    prog_change = int(55 / len(files))
    for i in files:
        i_num = len(i) - 3
        if i[i_num:len(i)] == '.py':
            try:
                copyfile(i, config.full('~/.tarstall/' + i))
            except FileNotFoundError:
                return "Bad copy"
        progress += prog_change
        generic.progress(progress)
    generic.progress(70)
    shell_file = config.get_shell_path()
    if shell_file is None:
        to_return = "Unsupported shell"
    else:
        to_return = "Success"
        if "shrc" in config.get_shell_file():
            config.add_line("source ~/.tarstall/.bashrc\n", shell_file)
        elif "fish" in config.get_shell_file():
            config.add_line("source ~/.tarstall/.fishrc\n", shell_file)
    generic.progress(75)
    copytree(config.full("./tarstall_execs/"), config.full("~/.tarstall/tarstall_execs/"))  # Move tarstall.py to execs dir
    generic.progress(90)
    if not config.exists("~/.local/share/applications"):
        os.mkdir(config.full("~/.local/share/applications"))
    if not config.exists("~/.local/share/applications/tarstall"):
        os.mkdir(config.full("~/.local/share/applications/tarstall"))
    generic.progress(92)
    config.add_line("export PATH=$PATH:{}".format(
                config.full("~/.tarstall/tarstall_execs")), "~/.tarstall/.bashrc")  # Add bashrc line
    config.add_line("set PATH $PATH {}".format(config.full("~/.tarstall/tarstall_execs")), "~/.tarstall/.fishrc")
    generic.progress(95)
    os.system('sh -c "chmod +x ~/.tarstall/tarstall_execs/tarstall"')
    config.unlock()
    generic.progress(100)
    return to_return


def verbose_toggle():
    """Enable/Disable Verbosity.

    Returns:
        str: "enabled"/"disabled", depending on the new state.

    """
    new_value = config.change_config('Verbose', 'flip')
    return generic.endi(new_value)


def get_online_version(type_of_replacement, branch=config.branch):
    """Get tarstall Version from GitHub.

    Args:
        type_of_replacement (str): Type of version to get (file or prog)
        branch (str): Branch to check version of (default: User's current branch)

    Returns:
        int: The specified version, -1 if requests is missing, or -2 if not connected to the internet.
    """
    if not can_update:
        config.vprint("requests library not installed! Exiting...")
        return -1
    version_url = "https://raw.githubusercontent.com/hammy3502/tarstall/{}/version.json".format(branch)
    try:
        version_raw = requests.get(version_url)
    except requests.ConnectionError:
        return -2
    version = json.loads(version_raw.text.replace("\n", "").replace(" ", "").replace("\r", ""))["versions"]
    return version[type_of_replacement]


def get_file_version(version_type):
    """Get Database Versions.

    Gets specified version of tarstall as stored in the database

    Args:
        version_type (str): Type of version to look up (file/prog)

    Returns:
        int: The specified version number

    """
    if version_type == 'file':
        return config.db["version"]["file_version"]
    elif version_type == 'prog':
        return config.db["version"]["prog_internal_version"]