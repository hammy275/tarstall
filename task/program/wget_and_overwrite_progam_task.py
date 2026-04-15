import os
from shutil import rmtree

import config
import file
from tarstall_error import TarstallHumanReadableError
from task.program.program_task import ProgramTask
from task.shared.wget_task import WgetTask
from task.task import TaskRunner, sub_task_runner, Task


class WgetAndOverwriteProgram(ProgramTask):
    def run(self, task_runner: TaskRunner):
        sub_task_runner([
            (SetupTask(self.program), 0.1),
            (WgetTask(self.program_update_url), 0.55),
            (PostWgetTask(self.program), 0.05),
            (InstallTask(), 0.25),  # TODO: Actual InstallTask here
            (CleanupTask(), 0.05)
        ], task_runner).run_tasks()


class SetupTask(ProgramTask):
    def run(self, task_runner: TaskRunner):
        if not file.check_bin("wget"):
            raise TarstallHumanReadableError(f"wget is not installed, so {self.program.name} cannot be updated.")
        else:
            config.vprint("Creating second temp folder for archive.")
            try:
                rmtree(file.full("/tmp/tarstall-temp2"))
            except FileNotFoundError:
                pass
            os.mkdir("/tmp/tarstall-temp2")
            os.chdir("/tmp/tarstall-temp2")
            task_runner.progress(1)

class PostWgetTask(ProgramTask):
    def run(self, task_runner: TaskRunner):
        files = os.listdir()
        config.vprint("Renaming archive")
        os.rename("/tmp/tarstall-temp2/{}".format(files[0]), "/tmp/tarstall-temp2/{}".format(self.program.name + self.program.update_archive_type))
        os.chdir("/tmp/")
        task_runner.progress(1)

        # TODO: Move below into installtask
        generic.progress(70 / progress_modifier, show_progress)
        config.vprint("Using install to install the program.")
        inst_status = install("/tmp/tarstall-temp2/{}".format(program + extension), True, show_progress=False)[0]
        generic.progress(95 / progress_modifier, show_progress)


class CleanupTask(Task):
    def run(self, task_runner: TaskRunner):
        try:
            rmtree(file.full("/tmp/tarstall-temp2"))
        except FileNotFoundError:
            pass
        task_runner.progress(1)