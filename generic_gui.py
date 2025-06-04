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
    from PySide6 import QtCore, QtWidgets, QtGui
except ImportError:
    pass


class GUIInteractions(Interactions):
    def ask(self, question):
        class AskDialog(QtWidgets.QDialog):
            def __init__(self):
                super().__init__()

                self.setWindowTitle("tarstall-gui")

                self.text = QtWidgets.QLabel(question)
                self.text_input = QtWidgets.QLineEdit()
                self.submit = QtWidgets.QPushButton("Submit")
                self.submit.clicked.connect(self.on_submit)

                self.layout = QtWidgets.QVBoxLayout(self)
                self.layout.addWidget(self.text)
                self.layout.addWidget(self.text_input)
                self.layout.addWidget(self.submit)

            @QtCore.Slot()
            def on_submit(self):
                self.close()
        dialog = AskDialog()
        dialog.exec()
        return dialog.text_input.text()

    def get_input(self, question, options, default, gui_labels=None, from_easy=False):
        if gui_labels is None:
            gui_labels = options
        class AskDialog(QtWidgets.QDialog):
            def __init__(self):
                super().__init__()

                self.output = 0
                self.setWindowTitle("tarstall-gui")

                self.layout = QtWidgets.QVBoxLayout(self)
                self.text = QtWidgets.QLabel(question)
                self.layout.addWidget(self.text)

                if len(options) <= 5:
                    self.inner_layout = QtWidgets.QHBoxLayout()
                    for i in range(len(gui_labels)):
                        label = gui_labels[i]
                        button = QtWidgets.QPushButton(label)
                        def button_pushed():
                            self.output = i
                            self.close()
                        button.clicked.connect(button_pushed)
                        self.inner_layout.addWidget(button)
                    self.layout.addLayout(self.inner_layout)
                else:
                    self.dropdown = QtWidgets.QComboBox()
                    self.dropdown.addItems(gui_labels)
                    def on_dropdown_change(index):
                        self.output = index
                    self.dropdown.currentIndexChanged.connect(on_dropdown_change)
                    self.submit = QtWidgets.QPushButton("Submit")
                    def on_submit():
                        self.close()
                    self.submit.clicked.connect(on_submit)

                    self.layout.addWidget(self.dropdown)
                    self.layout.addWidget(self.submit)
        dialog = AskDialog()
        dialog.exec()
        return options[dialog.output]

    def pprint(self, st, title="tarstall-gui"):
        class PopupDialog(QtWidgets.QDialog):
            def __init__(self):
                super().__init__()

                self.setWindowTitle(title)

                self.text = QtWidgets.QLabel(st)
                self.ok = QtWidgets.QPushButton("Ok")
                self.ok.clicked.connect(self.on_ok)

                self.layout = QtWidgets.QVBoxLayout(self)
                self.layout.addWidget(self.text)
                self.layout.addWidget(self.ok)

            @QtCore.Slot()
            def on_ok(self):
                self.close()
        dialog = PopupDialog()
        dialog.exec()

    def ppause(self, st, title="tarstall-gui"):
        self.pprint(st, title=title)

    def progress(self, val, should_show=True):
        if config.install_bar is not None:
            config.install_bar.setValue(val)
