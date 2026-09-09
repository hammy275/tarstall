use std::fs;
use std::fs::File;
use std::path::PathBuf;
use crate::task::{ProgressReporter, Task, TaskResult, ToTaskResultExt};

/// Task to create a file or folder on the filesystem at the specified path, creating folders as
/// needed.
pub struct FsCreate {
    pub path: PathBuf,
    pub create_type: CreateType
}

impl Task for FsCreate {
    fn run(&self, progress_reporter: ProgressReporter) -> TaskResult {
        progress_reporter.progress(0.0);
        match self.create_type {
            CreateType::FILE => {
                let path = self.path.clone();
                let parent_path = path.parent();
                if let Some(valid_parent_path) = parent_path {
                    let folder_create = fs::create_dir_all(valid_parent_path);
                    if let Err(_) = folder_create {
                        return folder_create.task_result()
                    }
                }
                progress_reporter.progress(0.05);
                File::create(path).task_result()
            },
            CreateType::FOLDER => fs::create_dir_all(self.path.clone()).task_result()
        }
    }

    fn undo(&self) -> TaskResult {
        match self.create_type {
            CreateType::FILE => fs::remove_file(self.path.clone()).task_result(),
            CreateType::FOLDER => fs::remove_dir(self.path.clone()).task_result()
        }
    }
}

pub enum CreateType {
    FILE,
    FOLDER
}

#[cfg(test)]
mod tests {
    use crate::task::run_task;
    use crate::util::temp_dir;
    use super::*;

    #[test]
    fn test_create_file() {
        let tmp = temp_dir().unwrap();
        let path = tmp.path.join("file.txt");
        let task = FsCreate{
            path: path.clone(),
            create_type: CreateType::FILE
        };
        assert!(run_task(&task).is_ok());
        assert!(path.is_file());
    }

    #[test]
    fn test_create_folder() {
        let tmp = temp_dir().unwrap();
        let path = tmp.path.join("folder");
        let task = FsCreate{
            path: path.clone(),
            create_type: CreateType::FOLDER
        };
        assert!(run_task(&task).is_ok());
        assert!(path.is_dir());
    }
}
