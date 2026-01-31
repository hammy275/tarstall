from __future__ import annotations  # For forward declaring type-hints (they internally become strings)
from abc import ABC, abstractmethod

import generic


class TaskRunner:
    """Task runner.

    Task runner that runs tasks.

    Args:
        tasks list[tuple[Task, float]]: A list of tasks and the weight they should have for progress. Weights should
                                        always add up to 1.0.
    """
    def __init__(self, tasks: list[tuple[Task, float]]):
        self.tasks = tasks

        self.base_progress = 0  # Progress from all past tasks
        self.current_task_weight = 0  # Weight for the current task

    def run_tasks(self):
        """Run all tasks.

        Run all tasks provided to the task runner.
        """
        for task, weight in self.tasks:
            self.current_task_weight = weight
            task.run(self)
            self.base_progress += weight

    def progress(self, amount: float):
        """Update progress for tasks.

        Called by tasks to update progress.

        Args:
            amount (float): An amount in the range [0.0, 1.0] of how close to complete the task is.
        """
        new_progress = self.base_progress + amount * self.current_task_weight
        generic.progress(new_progress)

class Task(ABC):
    """Task.

    Task that is run by TaskRunner. Should be extended to create different implementations.
    """
    @abstractmethod
    def run(self, task_runner: TaskRunner):
        """Run task.

        Runs this task. Tasks are only required to be runnable once. They can raise any error to denote a failure,
        or should simply not do so on a success.

        Args:
            task_runner (TaskRunner): The task runner running the task.
        """
        pass