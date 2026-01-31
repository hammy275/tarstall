import config
import file
from tarstall_error import TarstallHumanReadableError
from task.program.program_task import ProgramTask
from task.task import TaskRunner


class Pathify(ProgramTask):
    def run(self, task_runner: TaskRunner):
        if self.program.in_path:
            raise TarstallHumanReadableError("Program already added to PATH!")
        config.vprint('Adding program to PATH')
        line_to_write = f"\nexport PATH=$PATH:{config.TARSTALL_DIR}/bin/" + self.program.name + ' # ' + self.program.name
        file.add_line(line_to_write, f"{config.TARSTALL_DIR}/.bashrc")
        line_to_write = f"\nset PATH $PATH {config.TARSTALL_DIR}/bin/" + self.program.name + ' # ' + self.program.name
        file.add_line(line_to_write, f"{config.TARSTALL_DIR}/.fishrc")
        self.program.in_path = True
