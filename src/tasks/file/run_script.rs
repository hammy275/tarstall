use std::path::PathBuf;
use std::process::Command;
use crate::task::{ProgressReporter, Task, TaskResult};

pub struct RunScriptTask {
    pub script_path: PathBuf
}

impl Task for RunScriptTask {
    fn run(&self, progress_reporter: ProgressReporter) -> TaskResult {
        let child = Command::new(&self.script_path).spawn();
        match child {
            Ok(mut child) => {
                match child.wait() {
                    Ok(status) => match status.success() {
                        true => Ok(()),
                        false => match status.code() {
                            Some(exit_code) => Err(format!("update script exited with non-zero exit code {}", exit_code)),
                            None => Err("update script was terminated".to_string())
                        }
                    }
                    Err(err) => Err(err.to_string())
                }
            },
            Err(err) => Err(err.to_string())
        }
    }

    fn undo(&self) -> TaskResult {
        Err("cannot undo running a shell script".to_string())
    }
}