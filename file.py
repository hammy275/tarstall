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
import json
import os
import re
import shutil


def file_vprint(to_print, end=None):
    """vprint used here to prevent circular import.

    Args:
        to_print (str): String to print if verbose
        end (str): String to place at end of message (Python's end= argument in print())

    """
    from config import vprint
    vprint(to_print, end)


def check_bin(bin):
    """Check for Binary on System.

    Args:
        bin (str): Binary to check for

    Returns:
        bool: Whether or not the binary exists.

    """
    return shutil.which(bin) is not None


def get_shell_file():
    """Get Shell File.

    Attempts to automatically obtain the file used by the user's shell for PATH,
    variable exporting, etc.

    Returns:
        str: File name in home directory to store PATHs, variables, etc.

    """
    shell = os.environ["SHELL"]
    if "bash" in shell:
        file_vprint("Auto-detected bash")
        return ".bashrc"
    elif "zsh" in shell:
        file_vprint("Auto-detected zsh")
        return ".zshrc"
    elif "fish" in shell:
        file_vprint("Auto-detected fish")
        return ".config/fish/config.fish"
    else:
        file_vprint("Couldn't auto-detect shell environment!")
        return None


def get_shell_path():
    """Get Shell Path.

    Attempts to automatically obtain the file used by the user's shell for PATH,
    variable exporting, etc.

    Returns:
        str: Full path to the shell file.

    """
    shell_file = get_shell_file()
    if shell_file:
        if shell_file == ".bashrc":
            return full("~/.bashrc")
        elif shell_file == ".zshrc":
            return full("~/.zshrc")
        elif "fish" in shell_file:
            return full("~/.config/fish/config.fish")
    else:
        return None


def lock():
    """Lock tarstall.

    Lock tarstall to prevent multiple instances of tarstall being used alongside each other

    """
    create("/tmp/tarstall-lock")
    file_vprint("Lock created!")


def unlock():
    """Remove tarstall lock."""
    try:
        os.remove(full("/tmp/tarstall-lock"))
    except FileNotFoundError:
        pass
    file_vprint("Lock removed!")


def name(program):
    """Get Program Name.

    Get the name of a program given the path to its archive/folder.

    Args:
        program (str): Path to program archive

    Returns:
        str: Name of program to use internally

    """
    program_internal_name = re.sub(r'.*/', '/', program)
    extension_length = len(extension(program))
    program_internal_name = program_internal_name[program_internal_name.find('/')+1:(len(program_internal_name) - extension_length)]
    return program_internal_name


def dirname(path):
    """Get Program Name for Directory

    Args:
        path (str): Path to program folder

    Returns:
        str: Name of program to user internall

    """
    prog_int_name_temp = path[0:len(path)-1]
    if prog_int_name_temp.startswith('/'):
        program_internal_name = name(prog_int_name_temp + '.tar.gz')
    else:
        program_internal_name = name('/' + prog_int_name_temp + '.tar.gz')
    return program_internal_name


def extension(program):
    """Get Extension of Program.

    Args:
        program (str): File name of program or URL/path to program.

    Returns:
        str: Extension of program

    """
    if program[-3:].lower() == '.7z':
        return program[-3:].lower()
    elif program[-4:].lower() in ['.zip', '.rar', '.git']:
        return program[-4:]
    elif program[-7:].lower() in ['.tar.gz', '.tar.xz']:
        return program[-7:]
    else:
        # Default to returning everything after the last .
        return program[program.rfind("."):]


def exists(file_name):
    """Check if File Exists.

    Args:
        file_name (str): Path to file

    Returns:
        bool: Whether the file exists or not

    """
    try:
        return os.path.isfile(full(file_name)) or os.path.isdir(full(file_name))
    except FileNotFoundError:
        return False


def locked():
    """Get Lock State.

    Returns:
        bool: True if tarstall is locked. False otherwise.

    """
    return exists("/tmp/tarstall-lock")


def full(file_name):
    """Full Path.

    Converts ~'s, .'s, and ..'s to their full paths (~ to /home/username)

    Args:
        file_name (str): Path to convert

    Returns:
        str: Converted path

    """
    return os.path.abspath(os.path.expanduser(file_name))


def spaceify(file_name):
    """Add Backslashes.

    Adds backslashes before each space in a path.

    Args:
        file_name (str): Path to add backslashes to

    Returns:
        str: The path with backslashes

    """
    return file_name.replace(" ", "\\ ")


def replace_in_file(old, new, file_path):
    """Replace Strings in File.

    Replaces all instances of "old" with "new" in "file".

    Args:
        old (str): String to replace
        new (str): String to replace with
        file (str): Path to file to replace strings in

    """
    rewrite = """"""
    file_path = full(file_path)
    f = open(file_path, 'r')
    open_file = f.readlines()
    f.close()
    for l in open_file:
        rewrite += l.replace(old, new)
    written = open(file_path, 'w')
    written.write(str(rewrite))
    written.close()  # Write then close our new copy of the file
    return


def check_line(line, file_path, mode):
    """Check for Line.

    Checks to see if a line is inside of a file. Modes are:
    word: Split all lines into a list of WORDS, and check to see if the word supplied is in that list
    fuzzy: Check if the supplied line is in the file, even if it doesn't make up the whole line.

    Args:
        line (str): Line/word to look for
        file_path (str): Path to file to look for the line/word in
        mode (str): Mode to search with

    Returns:
        bool: Whether or not the line/word is in the file

    """
    f = open(full(file_path), 'r')
    open_file = f.readlines()
    f.close()
    for l in open_file:
        if mode == 'word':
            new_l = l.rstrip()
            new_l = new_l.split()
        elif mode == 'fuzzy':
            new_l = l.rstrip()
        if line in new_l:
            return True
    return False


def create(file_path):
    """Create Empty File.

    Args:
        file_path (str): Path to file to create

    """
    f = open(full(file_path), "w+")
    f.close()


def remove_line(line, file_path, mode):
    """Remove Line from File.

    Removes a line from a file. Uses the following modes:
    word: Removes line if supplied word is found in it (words are sets of chars seperated by spaces)
    poundword: Same as word, but line must also contain a #
    fuzzy: Removes line, matching with supplied line, even if the line being removed has more than the supplied line

    Args:
        line (str)): Line/word to remove
        file_path (str): Path to file to remove lines from
        mode (str): Mode to use to find lines to remove

    """
    rewrite = """"""
    file_path = full(file_path)
    f = open(file_path, 'r')
    open_file = f.readlines()
    f.close()
    for l in open_file:
        if mode == 'word' or mode == 'poundword':
            new_l = l.rstrip()
            new_l = new_l.split()
        elif mode == 'fuzzy':
            new_l = l.rstrip()
        if line in new_l:
            if not ('#' in new_l) and mode == 'poundword':
                rewrite += l
            else:
                pass
        else:
            rewrite += l
    written = open(file_path, 'w')
    written.write(str(rewrite))
    written.close()  # Write then close our new copy of the file
    return


def add_line(line, file_path):
    """Adds Line to a File."""
    file_path = full(file_path)
    f = open(file_path, 'a')
    f.write(line)
    f.close()


def char_check(name):
    """Check Chars.

    Checks if a string contains a # or a space.

    Returns:
        bool: True if line contains space or #; False otherwise

    """
    return ' ' in name or '#' in name
