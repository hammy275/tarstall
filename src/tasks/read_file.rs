use std::fs;
use std::path::PathBuf;
use std::sync::OnceLock;
use crate::task::{ProgressReporter, Task, TaskResult, ToTaskResultExt};

/// Task to read the contents of a file. The contents are stored in the contents variable.
pub struct ReadFile {
    path: PathBuf,
    pub contents: OnceLock<String>
}

impl Task for ReadFile {
    fn run(&self, _: ProgressReporter) -> TaskResult {
        let result = fs::read_to_string(self.path.clone());
        match result {
            Ok(contents) => {
                match self.contents.set(contents) {
                    Ok(_) => Ok(()),
                    err @ Err(_) => err.into()
                }
            }
            Err(_) => result.task_result()
        }
    }

    fn undo(&self) -> TaskResult {
        Ok(())
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

#[cfg(test)]
mod tests {
    use std::fs;
    use crate::task::run_task;
    use crate::tasks::read_file::ReadFile;
    use crate::util::temp_dir;

    #[test]
    fn test_read_file() {
        let file_contents = "test contents\ntest contents 2";
        let tmp = temp_dir().unwrap();
        let path = tmp.path.join("file.txt");
        fs::write(path.clone(), file_contents).unwrap();
        let read_task = ReadFile::create(path);
        assert!(run_task(&read_task).is_ok());
        assert_eq!(read_task.contents.get().unwrap(), file_contents)
    }

    #[test]
    fn test_read_missing_file() {
        let tmp = temp_dir().unwrap();
        let path = tmp.path.join("file.txt");
        let read_task = ReadFile::create(path);
        assert!(run_task(&read_task).is_err());
    }
}