import os.path
from subprocess import call
from typing import Union

import config
from generic_manage import c_out
from program.install_type import InstallType
from tarstall_error import TarstallHumanReadableError
from task.program.program_task import ProgramTask
from task.program.update_git_program_task import UpdateGitProgramTask
from task.program.wget_and_overwrite_progam_task import WgetAndOverwriteProgram
from task.task import TaskRunner, sub_task_runner


class UpdateProgramTask(ProgramTask):
    def run(self, task_runner: TaskRunner):
        download_task: Union[ProgramTask | None] = None
        if self.program.install_type == InstallType.GIT:
            download_task = UpdateGitProgramTask(self.program)
        elif self.program.update_url is not None:
            download_task = WgetAndOverwriteProgram(self.program)

        post_upgrade_script_task: Union[RunPostUpgradeScriptTask | None] = None
        if self.program.post_upgrade_script is not None:
            post_upgrade_script_task = RunPostUpgradeScriptTask(self.program)

        tasks = []
        if download_task is not None:
            tasks.append((download_task, 0.6 if post_upgrade_script_task is not None else 1.0))
        if post_upgrade_script_task is not None:
            tasks.append((post_upgrade_script_task, 0.4 if download_task is not None else 1.0))
        
        sub_task_runner(tasks, task_runner).run_tasks()

class RunPostUpgradeScriptTask(ProgramTask):
    def run(self, task_runner: TaskRunner):
        err = call(self.program.post_upgrade_script,
                   cwd=os.path.expanduser(f"{config.TARSTALL_DIR}/bin/{self.program.name}"), stdout=c_out)
        if err != 0:
            raise TarstallHumanReadableError(f"Post upgrade script exited with exit code {err}.")