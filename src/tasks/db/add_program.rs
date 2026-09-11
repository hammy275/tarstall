use crate::config::{save_db, DB};
use crate::program::{InstallType, Program};
use crate::task::{ProgressReporter, Task, TaskResult};

pub struct AddProgram {
    pub name: String,
    pub install_type: InstallType,
    pub update_url: Option<String>
}

impl Task for AddProgram {
    fn run(&self, progress_reporter: ProgressReporter) -> TaskResult {
        let mut db = match DB.write() {
            Ok(db) => db,
            Err(err) => return Err(err.to_string())
        };
        let program = Program{
            name: self.name.clone(),
            install_type: self.install_type.clone(),
            shortcut_paths: Vec::new(),
            post_update_script: None,
            update_url: self.update_url.clone(),
            in_path: false,
        };
        db.programs.push(program);
        save_db(db)
    }

    fn undo(&self) -> TaskResult {
        let mut db = match DB.write() {
            Ok(db) => db,
            Err(err) => return Err(err.to_string())
        };
        db.programs.retain(|prog| { prog.name != self.name });
        save_db(db)
    }
}