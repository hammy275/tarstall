import config
from generic_manage import c_out, wget_with_progress
from shutil import which
from subprocess import call
import sys
import tempfile
from tarstall_error import TarstallHumanReadableError
from task.task import Task, TaskRunner


class ReinstallDepsTask(Task):
    def run(self, task_runner: TaskRunner):
        if which("wget") is None:
            raise TarstallHumanReadableError("You don't have wget, please install it!")
        with tempfile.TemporaryDirectory() as temp_dir:
            config.vprint("Obtaining tarstall installer...")
            url = "https://raw.githubusercontent.com/hammy275/tarstall/{}/install_tarstall".format(
                config.db["version"]["branch"])
            # TODO: Use the task runner system here
            err = wget_with_progress(url, 5, 60)
            if err != 0:
                raise TarstallHumanReadableError("An error occurred while downloading the archive!")
            task_runner.progress(0.6)
            config.vprint("Running tarstall setup to (re)-install dependencies")
            input("")
            err = call([sys.executable, "install_tarstall", "--skip-questions"], stdout=c_out, stderr=c_out)
            task_runner.progress(1)
            if err != 0:
                raise TarstallHumanReadableError("An error occurred while running the installer")
