use std::env::consts::OS;
use std::string::ToString;
use directories::UserDirs;
use lnks::Shortcut;
use crate::args::ProgramArgs;
use crate::config::{has_program, tarstall_home};
use crate::task::TaskResult;
use crate::ui::{ChooseOption, UI};

pub fn manage(args: &ProgramArgs, ui: &mut dyn UI) -> TaskResult {
    let mut opts = Vec::new();
    if !has_program(args.program.as_str()) {
        return Err(format!("Program {} not found", args.program))
    }
    if OS == "windows" {
        opts.push(ChooseOption{ short: "s", msg: "Add shortcut to desktop" })
    } else if OS == "linux" {
        // TODO: Linux .desktop support
    }
    opts.push(ChooseOption{ short: "e", msg: "Exit" });
    loop {
        let choice = ui.choose("Select an option: ".to_string(), &opts);
        match opts[choice].short {
            "s" => if let Err(err) = windows_shortcut(args, ui) {
                return Err(err)
            }
            "e" => return Ok(()),
            _ => return Err("Invalid option".to_string())
        }
    }
}

fn windows_shortcut(args: &ProgramArgs, ui: &mut dyn UI) -> TaskResult {
    // Note: Windows shortcuts are not tracked in tarstall's database since they're easily-visible
    // files.
    match ui.ask_file(tarstall_home().join("bin").join(args.program.clone())) {
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