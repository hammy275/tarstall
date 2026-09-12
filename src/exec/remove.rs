use std::sync::Arc;
use crate::args::{ProgramArgs};
use crate::config::{has_program, tarstall_home};
use crate::task::{TaskResult, Tasks};
use crate::tasks::db::remove_program::{RemoveProgram};
use crate::tasks::file::delete_dir::DeleteDirTask;
use crate::ui::UI;
use crate::util::wait_for_tasks;

pub fn remove(args: &ProgramArgs, ui: &mut dyn UI) -> TaskResult {
    let mut tasks: Tasks = Vec::new();
    if !has_program(args.program.as_str()) {
        return Err(format!("{} is not installed!", args.program.as_str()))
    };
    let path = tarstall_home().join("bin").join(args.program.clone());
    // If not found, just skip deleting the folder in case the user removed it manually
    if path.is_dir() {
        tasks.push((Arc::new(DeleteDirTask{ path }), 50.0));
    }
    tasks.push((Arc::new(RemoveProgram::create(args.program.clone())), 1.0));
    wait_for_tasks(tasks, ui)
}