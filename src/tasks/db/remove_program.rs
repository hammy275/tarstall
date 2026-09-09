use std::sync::{OnceLock};
use crate::config::{save_db, DB};
use crate::program::Program;
use crate::task::{ProgressReporter, Task, TaskResult};

struct RemoveProgram {
    name: String,
    old_program: OnceLock<Program>
}

impl Task for RemoveProgram {
    fn run(&self, progress_reporter: ProgressReporter) -> TaskResult {
        let mut db = match DB.write() {
            Ok(db) => db,
            Err(err) => return Err(err.to_string())
        };
        let index = match db.programs.iter().position(| program | { program.name == self.name }) {
            None => return Err(format!("program {} not found", self.name)),
            Some(index) => index
        };
        if let Err(_) = self.old_program.set(db.programs.remove(index)) {
            return Err("failed to save old program".to_string())
        };
        save_db(db)
    }

    fn undo(&self) -> TaskResult {
        match self.old_program.get() {
            None => Ok(()),
            Some(program) => {
                let mut db = match DB.write() {
                    Ok(db) => db,
                    Err(err) => return Err(err.to_string())
                };
                // Not an exact undo, since the program may end up elsewhere in the vec, but that's
                // fine enough.
                db.programs.push(program.clone());
                save_db(db)
            }
        }
    }
}