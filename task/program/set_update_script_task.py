import file
from program.program import Program
from tarstall_error import TarstallHumanReadableError
from task.program.program_task import ProgramTask
from task.task import TaskRunner


class SetUpgradeScriptTask(ProgramTask):

    def __init__(self, program: Program, script_path: str):
        super().__init__(program)
        self.script_path = script_path

    def run(self, task_runner: TaskRunner):
        if self.script_path == "":
            self.program.post_upgrade_script = None
        elif not file.exists(file.full(self.script_path)):
            raise TarstallHumanReadableError("Script specified does not exist!")
        else:
            self.program.post_upgrade_script = file.full(self.script_path)