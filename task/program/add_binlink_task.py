import config
import file
from program.program import Program
from tarstall_error import TarstallHumanReadableError
from task.program.program_task import ProgramTask
from task.task import TaskRunner


class AddBinlinkTask(ProgramTask):
    """Add binlink task.

    Task that adds a binlink for the provided program.

    Args:
        program (Program): Program to add a binlink for.
        file_chosen (str): Absolute path to file that has the binlink.

    """
    def __init__(self, program: Program, file_chosen: str):
        super().__init__(program)
        self.file_chosen = file_chosen

    def run(self, task_runner: TaskRunner):
        binlink_name = self.file_chosen
        if "/" in binlink_name:
            binlink_name += ".tar.gz"
            binlink_name = file.name(binlink_name)
        if binlink_name in self.program.binlinks:
            raise TarstallHumanReadableError("Binlink not added since it already exists!")
        line_to_add = '\nalias ' + binlink_name + "='cd " + file.full(
            f'{config.TARSTALL_DIR}/bin/' + self.program.name) + \
                      '/ && ./' + self.file_chosen + "' # " + self.program.name
        config.vprint("Adding alias to bashrc and fishrc")
        file.add_line(line_to_add, f"{config.TARSTALL_DIR}/.bashrc")
        line_to_add = "\nfunction " + binlink_name + ";cd " + file.full(
            f"{config.TARSTALL_DIR}/bin/" + self.program.name) + "/;./" + self.file_chosen + ";end # " + self.program.name
        file.add_line(line_to_add, f"{config.TARSTALL_DIR}/.fishrc")
        self.program.binlinks.append(binlink_name)
