use std::sync::Arc;
use std::sync::mpsc::Sender;
use std::thread;
use std::thread::JoinHandle;

/// A type alias for a tuple containing a task and its weight.
pub type TaskWithWeight = (Arc<dyn Task>, f64);
/// A type alias for the list of tasks.
pub type Tasks = Vec<TaskWithWeight>;

/// Something that runs one or more tasks, keeping active progress as it progresses.
pub struct TaskRunner {
    tasks: Tasks,
    progress_sender: ProgressSender
}

impl TaskRunner {

    /// Run the tasks contained within the task runner. These run on a separate thread.
    pub fn run_tasks(&mut self) -> JoinHandle<TaskResult> {
        self.normalize_task_weights();
        let tasks = self.tasks.clone();
        let mut progress_reporter = ProgressReporter{
            prev_task_progress: 0.0,
            current_weight: 0.0,
            sender: Box::new(self.progress_sender.clone()),
        };
        thread::spawn(move || {
            progress_reporter.sender.raw_progress(0.0);
            for (task, weight) in tasks {
                progress_reporter.current_weight = weight;
                let result: TaskResult = task.run(progress_reporter.clone());
                match result {
                    Ok(_) => {
                        // Say that the task is done so the task itself doesn't have to.
                        progress_reporter.progress(1.0);
                        // Then prepare for the next task.
                        progress_reporter.prev_task_progress += weight
                    },
                    Err(_) => {
                        todo!("Perform rollback");
                        return result
                    }
                }
            }
            // Send exactly 1.0 to mark that we're done.
            progress_reporter.sender.raw_progress(1.0);
            Ok(())
        })
    }

    /// Normalize the task weights so they add up to 1.0.
    fn normalize_task_weights(&mut self) {
        let total: f64 = self.tasks.iter()
            .map(| task_and_weight | { task_and_weight.1 })
            .sum();
        for task in self.tasks.iter_mut() {
            (*task).1 = (*task).1 / total
        }
    }

    /// Create a task runner from the provided tasks and progress sender.
    pub fn create(tasks: Tasks, progress_sender: ProgressSender) -> TaskRunner {
        TaskRunner {
            tasks,
            progress_sender,
        }
    }
}

/// Run a single task immediately. Useful for quick-to-run tasks that aren't part of a main
/// operation.
pub fn run_task(task: &dyn Task) -> TaskResult {
    task.run(ProgressReporter{
        prev_task_progress: 0.0,
        current_weight: 0.0,
        sender: Box::new(ProgressSender::None),
    })
}

/// Something that handles progress reporting. Unlike the progress sender, which simply handles
/// moving a progress update from point A to point B, a progress reporter is what is provided to
/// tasks to report their progress, where it is modified by its weighting and overall progress
/// before being sent.
#[derive(Clone)]
pub struct ProgressReporter {
    prev_task_progress: f64,
    current_weight: f64,
    sender: Box<ProgressSender>
}

impl ProgressReporter {
    /// Main method to be called by tasks to report their progress so far.
    pub fn progress(&self, progress: f64) {
        // Use min here to prevent rounding errors with weights from sending above 1.0
        let amount = f64::min(1.0, self.prev_task_progress + self.current_weight * progress);
        self.sender.raw_progress(amount)
    }
}

/// Something that sends progress.
#[derive(Clone)]
pub enum ProgressSender {
    /// A sender that passes along the final value to a receiver.
    Sender(Sender<f64>),
    /// Another ProgressReporter, allowing for chaining multiple ProgressReporters together.
    Reporter(ProgressReporter),
    /// Progress is not actually sent anywhere
    None
}

impl ProgressSender {
    // Sends the progress amount provided without any modification
    pub fn raw_progress(&self, amount: f64) {
        match self {
            ProgressSender::Sender(sender) => _ = sender.send(amount),
            ProgressSender::Reporter(progress_reporter) => progress_reporter.progress(amount),
            ProgressSender::None => ()
        }
    }
}

/// The result of running a task.
pub type TaskResult = Result<(), String>;

/// An extension trait to allow converting other Results into TaskResults.
pub trait ToTaskResultExt {
    fn task_result(&self) -> TaskResult;
}

impl<O, E: ToString> ToTaskResultExt for Result<O, E> {
    /// Convert this result into a TaskResult. If this Result is Ok, it loses its result. If this
    /// Result is an Err, the inner error is converted to a string.
    fn task_result(&self) -> TaskResult {
        match self {
            Ok(_) => Ok(()),
            Err(err) => Err(err.to_string())
        }
    }
}

/// A task that performs some operation, marking progress using the provided task runner, then
/// returns a success or failure.
pub trait Task: Send + Sync {
    /// Called when the task is run. Progress should be reported via the provided ProgressReporter.
    fn run(&self, progress_reporter: ProgressReporter) -> TaskResult;
    /// Called when the task fails, and it should undo any changes it made (if any). One should
    /// especially expect this to be called if run() returns an Error.
    fn undo(&self) -> TaskResult;
}