use crate::task::{ProgressReporter, ProgressSender, Task, TaskResult, TaskRunner, Tasks};

/// Task that runs multiple tasks
pub struct TaskOfTasks {
    pub tasks: Tasks
}

impl Task for TaskOfTasks {
    fn run(&self, parent_progress_reporter: ProgressReporter) -> TaskResult {
        
        let mut task_runner = TaskRunner::create(self.tasks.clone(),
                                                 ProgressSender::Reporter(parent_progress_reporter));
        task_runner.run_tasks()
            .join()
            .unwrap_or_else(|_| Err("failed to join child task runner thread".to_string()))
    }

    fn undo(&self) -> TaskResult {
        todo!("Task runners do not support undoing yet")
    }
}