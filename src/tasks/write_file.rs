use std::fs;
use std::path::PathBuf;
use std::sync::OnceLock;
use crate::task::{run_task, ProgressReporter, Task, TaskResult, ToTaskResultExt};
use crate::tasks::read_file::ReadFile;

/// Task to read the contents of a file. The contents are stored in the contents variable.
pub struct WriteFile {
    pub path: PathBuf,
    pub contents: String,
    pub old_contents: OnceLock<String>
}

impl Task for WriteFile {
    fn run(&self, progress_reporter: ProgressReporter) -> TaskResult {
        // Grab the old contents of the file if we need to undo.
        let old_file_read = ReadFile::create(self.path.clone());
        let read_result = run_task(&old_file_read);
        if let Err(_) = read_result {
            return read_result
        }
        if let Some(contents) = old_file_read.contents.get() {
            _ = self.old_contents.set(contents.clone());
        }
        progress_reporter.progress(0.2);
        // Now actually write our new contents
        fs::write(self.path.clone(), self.contents.clone()).task_result()
    }

    fn undo(&self) -> TaskResult {
        match self.old_contents.get() {
            Some(old_contents) => fs::write(self.path.clone(), old_contents).task_result(),
            None => Ok(())
        }
    }
}

impl WriteFile {
    pub fn create(path: PathBuf, contents: String) -> WriteFile {
        WriteFile{
            path,
            contents,
            old_contents: OnceLock::new(),
        }
    }
}