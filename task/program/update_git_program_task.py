import config
import file
from subprocess import run
from tarstall_error import TarstallHumanReadableError
from task.program.program_task import ProgramTask
from task.task import TaskRunner


class UpdateGitProgramTask(ProgramTask):
    def run(self, task_runner: TaskRunner):
        if not file.check_bin("git"):
            raise TarstallHumanReadableError("Git isn't installed, please install it!")
        task_runner.progress(5)
        outp = run(["git", "pull"], cwd=file.full(f"{config.TARSTALL_DIR}/bin/{program}"), stdout=PIPE, stderr=PIPE)
        task_runner.progress(95)
        err = outp.returncode
        output = str(outp.stdout) + "\n\n\n" + str(outp.stderr)
        if err != 0:
            raise TarstallHumanReadableError("Error while updating through git!")
        else:
            if "Already up to date." in output:
                raise TarstallHumanReadableError(f"{program} is already up to date!")
            else:
                task_runner.progress(100)