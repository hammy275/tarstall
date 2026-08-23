use std::fs;
use std::path::PathBuf;
use std::sync::OnceLock;
use crate::task::{ProgressReporter, Task, TaskResult};

/// Task to read the contents of a file. The contents are stored in the contents variable.
pub struct ReadFile {
    path: PathBuf,
    pub contents: OnceLock<String>
}

impl Task for ReadFile {
    fn run(&self, progress_reporter: ProgressReporter) -> TaskResult {
        let result = fs::read_to_string(self.path.clone());
        match result {
            Ok(contents) => {
                match self.contents.set(contents) {
                    Ok(_) => TaskResult::Ok,
                    err @ Err(_) => err.into()
                }
            }
            Err(_) => result.into()
        }
    }

    fn undo(&self) -> TaskResult {
        TaskResult::Ok
    }
}

impl ReadFile {
    pub fn create(path: PathBuf) -> ReadFile {
        ReadFile{
            path,
            contents: OnceLock::new(),
        }
    }
}