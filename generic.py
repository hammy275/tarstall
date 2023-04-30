"""tarstall: A package manager for managing archives
    Copyright (C) 2022  hammy275

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

import config
import os

import file
import generic_gui
import generic_cli

if config.mode == "gui":
    try:
        import PySimpleGUI as sg
    except ImportError:
        pass  # This will be caught by tarstall.py, let's not worry about it here.


def file_browser(root_dir, stay_inside_dir=True, return_full_path=False):
    """File Browser.

    File browser for CLI that allows the choosing of files in folders.

    Args:
        root_dir (str): Path to top directory. Anything above this will be unaccessible
        stay_inside_dir (bool): Whether the user should be forced to stay inside the root_dir
        return_full_path (bol): Whether to return the full path to the chosen file.
    
    Returns:
        str: path/to/file/from/root_dir/file.txt (Path to the selected file from root_dir
        Will return full path (from / instead of from root_dir) if return_full_path is True

    """
    root_dir = file.full(root_dir)
    os.chdir(root_dir)
    all_files = os.listdir()
    folders = []
    files = []
    for f in all_files:
        if os.path.isdir("./{}".format(f)):
            folders.append(f)
        else:
            files.append(f)
    msg = "Folders: " + ' '.join(folders) + "\n" + "Files: " + ' '.join(files)
    file_chosen = 'Cool fact. This line was originally written on line 163.'
    current_folder_path = []
    while file_chosen not in files:
        all_files = os.listdir()
        folders = []
        files = []
        for f in all_files:
            if os.path.isdir("./{}".format(f)):
                folders.append(f)
            else:
                files.append(f)
        msg = "Folders: " + ' '.join(folders) + "\n" + "Files: " + ' '.join(files)
        file_chosen = ask(msg + '\n\nPlease enter a file listed above. If you would like to cancel, type exit. If you would like to go up a directory, type "..": ')
        if file_chosen == "exit":
            return None
        elif file_chosen in folders:
            os.chdir(file.full("./{}".format(file_chosen)))
            current_folder_path.append(file_chosen)
        elif file_chosen == "..":
            if os.getcwd() == root_dir and stay_inside_dir:
                pprint("\nCan't go up a directory!\n")
            else:
                os.chdir(file.full(".."))
    if current_folder_path != []:
        extra_slash = "/"
    else:
        extra_slash = ""
    if return_full_path:
        path_ret = os.getcwd()
        if not path_ret.endswith("/"):
            path_ret = path_ret + "/"
        return path_ret + file_chosen
    else:
        return "/".join(current_folder_path) + extra_slash + file_chosen


def ask(question):
    """Get Any User Input.

    Get user input, with no expected response like with get_input

    Args:
        question (str): Question to ask user

    Returns:
        str: User-supplied answer to question
    
    """
    if config.mode == "cli":
        return input(question)
    elif config.mode == "gui":
        return generic_gui.ask(question)


def ask_file(question):
    """Get User Input for File.

    Get user input for a file

    Args:
        question (str): Question to ask user

    Returns:
        str: Path to file
    
    """
    if config.mode == "cli":
        return generic_cli.ask_file(question)
    elif config.mode == "gui":
        return generic_gui.ask_file(question)


def easy_get_action(options, replacements=[]):
    """Easy get_input()

    options should contain a list of dictionaries, each representing an option.
    Dictionary should be layed out as such:
    {
        "shorthand": "b",  # One or two letters representing the option (the selector in CLI mode)
        "gui-label": "Create binlinks",  # The label for the option to show in the GUI
        "description": "Create binlinks for {program}",  # The description of the action being performed
        "is-default": False  # Optional. If specified and set to True, will be the default option on an enter press.*
    }

    *: Note: If multiple parameters are passed in as default, only the first one will actually be the default.
    Note: If default is not specified for any options, the last option will be the default.

    Args:
        options (dict[]): See dictionary format above.
        replacements (dict[]): The key should be what you want to replace and the value be what you're replacing with.

    """
    gui_labels = []
    options_list = []
    default = None
    msg = "Select an option:"
    for option in options:
        selector = option["shorthand"].lower()
        try:
            is_default = option["is-default"]
        except KeyError:
            is_default = False
        if is_default or (default is None and option is options[len(options) - 1]):
            default = option["shorthand"]
            selector = selector.upper()
        gui_labels.append(option["gui-label"])
        options_list.append(option["shorthand"])
        if config.mode == "gui":
            selector = option["gui-label"]
        msg += "\n" + selector + " - " + option["description"]
    for replacement in replacements:
        msg = msg.replace(list(replacement.keys())[0], list(replacement.values())[0])
    return get_input(msg, options_list, default, gui_labels, True)


def get_input(question, options, default, gui_labels=None, from_easy=False):
    """Get User Input.

    Get user input, except make sure the input provided matches one of the options we're looking for

    Args:
        question (str): Question to ask the user
        options (str[]): List of options the user can choose from
        default (str): Default option (used when user enters nothing)
        gui_labels (str[]): Labels to use for GUI buttons/dropdown menus (optional)

    Returns:
        str: Option the user chose

    """
    if config.mode == "cli":
        return generic_cli.get_input(question, options, default, from_easy)
    elif config.mode == "gui":
        return generic_gui.get_input(question, options, gui_labels)



def endi(state):
    """Bool to String.

    Args:
        state (bool): Bool to convert

    Returns:
        str: "enabled" if True, "disabled" if False

    """
    if state:
        return "enabled"
    return "disabled"


def pprint(st, title="tarstall-gui"):
    """Print Depending on Mode.

    Args:
        st (str): String to print or display in GUI popup.
        title (str, optional): Title for window if in GUI mode. Defaults to "tarstall-gui".

    """
    if config.mode == "gui":
        sg.Popup(st, title=title)
    elif config.mode == "cli":
        print(st)


def ppause(st, title="tarstall-gui"):
    """Print and Pause if CLI.

    Args:
        st (str): String to print or display in GUI popup.
        title (str, optional): Title for window if in GUI mode. Defaults to "tarstall-gui".

    """
    if config.mode == "gui":
        sg.Popup(st, title=title)
    elif config.mode == "cli":
        print(st)
        if config.read_config("PressEnterKey"):
            input("Press ENTER to continue...")


def progress(val, should_show=True):
    """Update Progress of Operation.

    Updates a progress bar (if we have a GUI) as tarstall processes run

    Args:
        val (int/float): Value to update the progress bar to.
        should_show (bool): If set to False, don't show the bar in CLI. Defaults to True.

    """
    if config.mode == "gui":
        if config.install_bar is not None:
            config.install_bar.UpdateBar(val)
    elif config.mode == "cli" and not config.verbose and should_show:
        generic_cli.progress(val)
