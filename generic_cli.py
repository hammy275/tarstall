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
import os

import config
import file
from interactions_base import Interactions


class CLIInteractions(Interactions):
    def ask(self, question):
        return input(question)

    def get_input(self, question, options, default, gui_labels=None, from_easy=False):
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

    def pprint(self, st, title="tarstall-gui"):
        print(st)

    def ppause(self, st, title="tarstall-gui"):
        print(st)
        if config.read_config("PressEnterKey"):
            input("Press ENTER to continue...")

    def progress(self, val, should_show=True):
        if not config.verbose and should_show:
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
