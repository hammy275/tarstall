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

from interactions_base import Interactions
import config

try:
    import PySimpleGUI as sg
except ImportError:
    pass


class GUIInteractions(Interactions):
    def ask(self, question):
        layout = [
            [sg.Text(question)],
            [sg.InputText(key="answer"), sg.Button("Submit")]
        ]
        window = sg.Window("tarstall-gui", layout, disable_close=True)
        while True:
            event, values = window.read()
            if event == "Submit":
                window.Close()
                return values["answer"]

    def ask_file(self, question):
        layout = [
            [sg.Text(question)],
            [sg.InputText(key="answer"), sg.FileBrowse()],
            [sg.Button("Submit")]
        ]
        window = sg.Window("tarstall-gui", layout, disable_close=True)
        while True:
            event, values = window.read()
            if event == "Submit":
                window.Close()
                return values["answer"]

    def get_input(self, question, options, default, gui_labels=None, from_easy=False):
        if gui_labels is None:
            gui_labels = options
        if len(options) <= 5:
            button_list = []
            for o in gui_labels:
                button_list.append(sg.Button(o))
            layout = [
                [sg.Text(question)],
                button_list
            ]
            window = sg.Window("tarstall-gui", layout, disable_close=True)
            while True:
                event, values = window.read()
                if event in gui_labels:
                    window.Close()
                    return options[gui_labels.index(event)]
        else:
            layout = [
                [sg.Text(question)],
                [sg.Combo(gui_labels, key="option"), sg.Button("Submit")]
            ]
            window = sg.Window("tarstall-gui", layout, disable_close=True)
            while True:
                event, values = window.read()
                if event == "Submit":
                    window.Close()
                    return options[gui_labels.index(values["option"])]

    def pprint(self, st, title="tarstall-gui"):
        sg.Popup(st, title=title)

    def ppause(self, st, title="tarstall-gui"):
        sg.Popup(st, title=title)

    def progress(self, val, should_show=True):
        if config.install_bar is not None:
            config.install_bar.UpdateBar(val)
