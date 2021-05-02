import PySimpleGUI as sg


def ask(question):
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



def ask_file(question):
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


def get_input(question, options, gui_labels=[]):
    if gui_labels == []:
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