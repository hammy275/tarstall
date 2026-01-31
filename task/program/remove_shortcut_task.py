import config
import file
import os

from program.program import Program
from task.program.program_task import ProgramTask
from task.task import TaskRunner


class RemoveShortcutTask(ProgramTask):
    def __init__(self, program: Program, shortcut_name: str):
        super().__init__(program)
        self.shortcut_name = shortcut_name

    def run(self, task_runner: TaskRunner):
        try:
            os.remove(file.full(os.path.join("~", "local", "share", "applications", "tarstall", f"{self.shortcut_name}.desktop")))
            os.remove(file.full("~/.local/share/applications/tarstall/{}.desktop".format(self.shortcut_name)))
        except FileNotFoundError:
            pass
        self.program.shortcuts.remove(self.shortcut_name)
        config.db["programs"][program]["desktops"].remove(desktop)
        config.write_db()