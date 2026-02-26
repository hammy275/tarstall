from program.program import Program
from task.program.program_task import ProgramTask
from task.task import TaskRunner


class RemoveUpgradeURLTask(ProgramTask):
    def __init__(self, program: Program):
        super().__init__(program)

    def run(self, task_runner: TaskRunner):
        self.program.update_url = None
