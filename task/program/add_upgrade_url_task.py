from typing import Union

from program.program import Program
from task.program.program_task import ProgramTask
from task.task import TaskRunner


class AddUpgradeURLTask(ProgramTask):
    def __init__(self, program: Program, upgrade_url: str, type_in: Union[str, None] = None):
        super().__init__(program)
        self.upgrade_url = upgrade_url
        self.type_in = type_in

    def run(self, task_runner: TaskRunner):
        supported_types = [".tar.gz", ".tar.xz", ".zip", ".7z", ".rar"]
        has_type = self.type_in is not None
        if not has_type:
            for typ in supported_types:
                if self.url.endswith(typ):
                    has_type = True
                    type_in = typ
                    break
            if not has_type:
                return "Need Type"
        elif self.type_in not in supported_types:
            return "Bad Type"
        self.program.update_url = self.upgrade_url
        self.program.update_archive_type = self.type_in