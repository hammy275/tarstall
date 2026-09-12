use std::fs::remove_dir_all;
use std::path::PathBuf;
use crate::task::{ProgressReporter, Task, TaskResult};

pub struct DeleteDirTask {
    pub path: PathBuf
}

impl Task for DeleteDirTask {
    fn run(&self, progress_reporter: ProgressReporter) -> TaskResult {
        remove_dir_all(self.path.clone()).map_err(| err | { err.to_string() })
    }

    fn undo(&self) -> TaskResult {
        Err("Cannot undo deletion".to_string())
    }
}