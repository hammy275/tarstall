use crate::args::{InstallArgs, UpdateArgs};
use crate::config::get_program;
use crate::exec::install::gather_install_tasks;
use crate::program::{InstallType};
use crate::task::{TaskResult, Tasks};
use crate::ui::UI;
use crate::util::wait_for_tasks;

pub fn update(args: &UpdateArgs, ui: &mut dyn UI) -> TaskResult {
    if args.tarstall && args.program.is_some() {
        return Err("cannot update tarstall and other programs".to_string())
    }
    let mut tasks: Tasks = Vec::new();
    if args.tarstall {
        todo!("tarstall updating")
    } else {
        match &args.program {
            Some(program_name) => {
                let program = match get_program(program_name) {
                    Some(program) => program,
                    None => return Err(format!("{} not found", program_name))
                };
                match program.install_type {
                    InstallType::DEFAULT { update_archive_type } => {
                        let update_url = match program.update_url {
                            Some(update_url) => update_url,
                            None => return Err(format!("{} does not have an update URL, please add one", program_name))
                        };
                        let install_args = InstallArgs{
                            source: update_url,
                            name: Some(program_name.clone()),
                            file_format: update_archive_type,
                        };
                        if let Err(err) = gather_install_tasks(&install_args, &mut tasks, true) {
                            return Err(err)
                        }
                    }
                    InstallType::GIT => todo!("git updating not supported"),
                    InstallType::SINGLE => todo!("single updating not supported")
                }
            },
            None => todo!("all programs updating")
        }
    }
    wait_for_tasks(tasks, ui)
}