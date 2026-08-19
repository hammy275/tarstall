use std::fs;
use std::fs::File;
use std::path::PathBuf;
use crate::task::{ProgressReporter, Task, TaskResult};

/// Task to create a file or folder on the filesystem at the specified path, creating folders as
/// needed.
pub struct FsCreate {
    pub path: PathBuf,
    pub create_type: CreateType
}

impl Task for FsCreate {
    fn run(&self, progress_reporter: ProgressReporter) -> TaskResult {
        match self.create_type {
            CreateType::FILE => {
                let path = self.path.clone();
                let parent_path = path.parent();
                if let Some(valid_parent_path) = parent_path {
                    let folder_create = fs::create_dir_all(valid_parent_path);
                    if let Err(_) = folder_create {
                        return folder_create.into()
                    }
                }
                File::create(path).into()
            },
            CreateType::FOLDER => fs::create_dir_all(self.path.clone()).into()
        }
    }

    fn undo(&self) -> TaskResult {
        match self.create_type {
            CreateType::FILE => fs::remove_file(self.path.clone()).into(),
            CreateType::FOLDER => fs::remove_dir(self.path.clone()).into()
        }
    }
}

pub enum CreateType {
    FILE,
    FOLDER
}