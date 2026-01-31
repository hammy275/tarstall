import os.path

import config
import file
from tarstall_error import TarstallHumanReadableError
from task.program.program_task import ProgramTask
from task.task import TaskRunner


class RemovePathAndBinlinksTask(ProgramTask):
    def run(self, task_runner: TaskRunner):
        if not self.program.in_path and len(self.program.binlinks) == 0:
            raise TarstallHumanReadableError("The program isn't added to PATH and has no binlinks, so none removed!")
        file.remove_line(self.program.name, os.path.join(config.TARSTALL_DIR, ".bashrc"), 'poundword')
        file.remove_line(self.program.name, os.path.join(config.TARSTALL_DIR, ".fishrc"), 'poundword')
        self.program.in_path = False
        self.program.binlinks = []
