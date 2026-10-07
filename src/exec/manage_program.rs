use std::env::consts::OS;
use std::string::ToString;
use directories::UserDirs;
use crate::args::{ProgramArgs, UpdateArgs};
use crate::config::{get_program, tarstall_home, DB, replace_program, save_db, get_program_with_write_lock};
use crate::exec::remove::remove;
use crate::exec::update::update;
use crate::program::Program;
use crate::task::TaskResult;
use crate::ui::{ChooseOption, UI};

pub fn manage(args: &ProgramArgs, ui: &mut dyn UI) -> TaskResult {
    let mut opts = Vec::new();
    let program = match get_program(args.program.as_str()) {
        None => return Err(format!("Program {} not found", args.program)),
        Some(program) => program
    };
    let update_msg;
    if program.can_update() {
        update_msg = format!("Update {}", args.program);
        opts.push(ChooseOption{ short: "u", msg: update_msg.as_str() });
    }
    if program.can_update_ignore_post_update_script() {
        opts.push(ChooseOption{ short: "p", msg: "Add/remove post-update script" })
    } else {
        opts.push(ChooseOption{ short: "p", msg: "Add/remove update script" })
    }
    if OS == "windows" {
        opts.push(ChooseOption{ short: "s", msg: "Add shortcut to desktop" })
    } else if OS == "linux" {
        // TODO: Linux .desktop support
    }
    let remove_msg = format!("Remove {}", args.program);
    opts.push(ChooseOption{ short: "r", msg: remove_msg.as_str() });
    opts.push(ChooseOption{ short: "e", msg: "Exit" });
    loop {
        let choice = ui.choose("Select an option: ".to_string(), &opts);
        match opts[choice].short {
            "u" => if let err @ Err(_) = update(&UpdateArgs{ tarstall: false, program: Some(args.program.clone()) }, ui) {
                return err
            }
            "s" => if let Err(err) = windows_shortcut(args, ui) {
                return Err(err)
            }
            "p" => return post_update_script(args, ui),
            "r" => return remove(args, ui),
            "e" => return Ok(()),
            _ => return Err("Invalid option".to_string())
        }
    }
}

fn post_update_script(args: &ProgramArgs, ui: &mut dyn UI) -> TaskResult {
    match ui.ask_file(tarstall_home().join("bin").join(args.program.clone()), true) {
        Ok(file_path) => {
            match DB.write() {
                Ok(mut db) => {
                    let mut program = match get_program_with_write_lock(args.program.as_str(), &db) {
                        Some(program) => program,
                        None => return Err("Program not found even though it was found earlier".to_string())
                    };
                    if file_path.as_os_str().is_empty() {
                        program.post_update_script = None;
                    } else {
                        program.post_update_script = Some(file_path)
                    }
                    match replace_program(program, &mut db) {
                        Ok(_) => save_db(db),
                        err @ Err(_) => err
                    }
                },
                Err(err) => Err(err.to_string())
            }
        }
        Err(err) => Err(err)
    }
}

#[cfg(target_os = "windows")]
fn windows_shortcut(args: &ProgramArgs, ui: &mut dyn UI) -> TaskResult {
    use lnks::Shortcut; // use in here since it's Windows-only
    // Note: Windows shortcuts are not tracked in tarstall's database since they're easily-visible
    // files.
    match ui.ask_file(tarstall_home().join("bin").join(args.program.clone()), false) {
        Ok(path) => match UserDirs::new() {
            Some(dirs) => match dirs.desktop_dir() {
                Some(desktop_dir) => {
                    let shortcut = Shortcut::new(path);
                    shortcut.save(desktop_dir.join(
                            args.program.as_str()).with_extension("lnk"))
                        .map_err(| err | { err.to_string() })
                },
                None => Err("Couldn't find desktop folder.".to_string())
            }
            None => Err("Couldn't find desktop folder.".to_string())
        },
        Err(err) => Err(err)
    }
}

#[cfg(not(target_os = "windows"))]
fn windows_shortcut(_: &ProgramArgs, _: &mut dyn UI) -> TaskResult {
    Err("Windows shortcut creation is only supported on Windows.".to_string())
}