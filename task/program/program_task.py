from program.program import Program
from task.task import Task

# noinspection PyAbstractClass
class ProgramTask(Task):
    def __init__(self, program: Program):
        self.program = program