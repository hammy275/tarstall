use std::fs;
use std::io::stdin;
use std::path::PathBuf;
use terminal_size::{terminal_size, Height, Width};
use crate::ui::{ChooseOption, UI};

pub struct CliUI {
    /// Last progress update received
    last_progress: f64
}

impl UI for CliUI {
    fn run_ui(&mut self) -> () {
        // Intentional no-op
    }

    fn message(&mut self, msg: String) -> () {
        println!("{}", msg);
    }

    fn debug(&mut self, msg: String) -> () {
        println!("{}", msg);
    }

    fn progress(&mut self, progress: f64) -> () {
        if self.last_progress != 1.0 || progress != 1.0 {
            let terminal_width = match terminal_size() {
                Some((Width(w), Height(h))) => w as usize,
                None => 80
            };
            // -10 for "Progress: " and -12 for percentage and breathing room.
            let progress_chars = terminal_width - 10 - 12;
            let filled_chars = (progress_chars as f64 * progress) as usize;
            let unfilled_chars = progress_chars - filled_chars;
            let percentage = ((progress * 100.0) as u8).to_string();
            print!("Progress: {}{} ({}%)\r", "■".repeat(filled_chars), "□".repeat(unfilled_chars), percentage);
            if progress == 1.0 {
                println!();
            }

            self.last_progress = progress;
        }
    }

    fn choose(&mut self, msg: String, options: &Vec<ChooseOption>) -> usize {
        loop {
            println!("{}", msg);
            options.iter().for_each(| opt | { println!("{} - {}", opt.short, opt.msg) });
            let input = read_line();
            if let Some(index) = options.iter().position(| option | { option.short == input }) {
                return index
            }
            println!("Invalid option: {}", input)
        }
    }

    fn ask_file(&mut self, root_path: PathBuf) -> Result<PathBuf, String> {
        let mut dirs_in = 0;
        let mut cwd = root_path;
        loop {
            let mut folders = Vec::new();
            let mut files = Vec::new();
            match fs::read_dir(cwd.clone()) {
                Ok(results) => {
                    for child in results {
                        match child {
                            Ok(dir_entry) => {
                                let path = dir_entry.path();
                                let name = match dir_entry.file_name().to_str() {
                                    None => return Err("Encountered invalid file name.".to_string()),
                                    Some(name) => name.to_string()
                                };
                                if path.is_dir() {
                                    folders.push(name)
                                } else if path.is_file() {
                                    files.push(name)
                                }
                            }
                            Err(err) => return Err(err.to_string())
                        }
                    }
                }
                Err(err) => return Err(err.to_string())
            }
            println!("Folders: {}", folders.join(", "));
            println!("Files: {}", files.join(", "));
            if dirs_in == 0 {
                println!("Enter a folder to traverse to or a file to select: ")
            } else {
                println!("Enter a folder to traverse to, a file to select, or \"..\" to go up a directory: ")
            }
            let input = read_line();
            if files.contains(&input) {
                return Ok(cwd.join(input))
            } else if folders.contains(&input) {
                cwd = cwd.join(input);
                dirs_in += 1;
            } else if input == ".." && dirs_in != 0 {
                // Unwrap is okay. We entered some child directory to end up here, so there's
                // definitely a parent.
                cwd = cwd.parent().unwrap().to_path_buf();
                dirs_in -= 1;
            }
        }
    }
}

pub fn new() -> CliUI {
    CliUI{
        last_progress: 0.0,
    }
}

fn read_line() -> String {
    let mut res = String::new();
    _ = stdin().read_line(&mut res).expect("could not read stdin");
    res.trim_end_matches("\n").trim_end_matches("\r").to_string()
}