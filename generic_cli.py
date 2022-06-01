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

import file


def get_argument_index(short, long, args):
    """Gets the index of an argument in sys.argv

    Args:
        short (str): Short version of the argument ("e", "f", etc.)
        long (str): Long version of the argument ("first", "install", etc.)
        args (str): List of arguments

    Returns:
        int: Index of the argument, or -1 if not found

    """
    i = -1
    for s in args:
        i += 1
        if s == "-{}".format(short) or s == "--{}".format(long) or s == long:
            return i
    return -1


def has_argument(short, long, args):
    """Check sys.argv if it contains the argument.

    Args:
        short (str): Short version of the argument ("e", "f", etc.)
        long (str): Long version of the argument ("first", "install", etc.)
        args (str[]): List of arguments

    Returns:
        bool: Whether or not the argument was found

    """
    return get_argument_index(short, long, args) != -1


def get_arg_extra(short, long, args):
    """Gets Extra for Argument.

    Gets the extra value supplied for an argument. For example, "install /tmp/test" would return "/tmp/test"

    Do not use this for flags that don't expect another argument, or you'll get a value that doesn't make sense!

    Args:
        short (str): Short form of argument
        long (str): Long form of argument
        args (str[]): List of arguments

    Returns:
        str: Extra value supplied, None if none exists, or -1 if the argument was not specified.

    """
    index = get_argument_index(short, long, args)
    if index != -1:
        try:
            return args[index + 1]
        except IndexError:
            return -1
    return None


def ask_file(question):
    f = "asdf"
    while not file.exists(file.full(f)):
        f = input(question)
    return file.full(f)


def get_input(question, options, default, from_easy=False):
    options_form = list(options)  # Otherwise, Python would "link" options_form with options
    options_form[options_form.index(default)] = options_form[options_form.index(default)].upper()
    if len(options) > 3 or from_easy:
        question += "\n[" + "/".join(options_form) + "]"
    else:
        question += " [" + "/".join(options_form) + "]"
    answer = "This is a string. There are many others like it, but this one is mine."  # Set answer to something
    while answer not in options and answer != "":
        answer = input(question)
        answer = answer.lower()  # Loop ask question while the answer is invalid or not blank
    if answer == "":
        return default  # If answer is blank return default answer
    else:
        return answer  # Return answer if it isn't the default answer


def progress(val):
    try:
        try:
            columns = os.get_terminal_size()[0]
        except OSError:
            columns = 80
        start_chars = "Progress ({}%): ".format(str(int(val)))
        end_chars = "   "
        full_squares = int(val * 0.01 * (columns - len(start_chars) - len(end_chars)))
        empty_squares = columns - len(start_chars) - len(end_chars) - full_squares
        if val < 100:
            print(start_chars + "■" * full_squares + "□" * empty_squares + end_chars, end="\r")
        else:
            print(start_chars + "■" * full_squares + "□" * empty_squares + end_chars, end="")
    except IndexError:
        if val < 100:
            print("{}% complete".format(val), end="\r")
        else:
            print("{}% complete".format(val), end="")