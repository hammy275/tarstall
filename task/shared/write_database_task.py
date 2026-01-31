import config
from task.task import Task, TaskRunner

class WriteDatabaseTask(Task):
    def run(self, task_runner: TaskRunner):
        config.write_db()
        task_runner.progress(1)
