use std::env;
use std::process::exit;
use crate::ui::{cli_ui, UI};

mod program;
mod task;
mod tasks;
mod util;
mod db;
mod config;
mod args;
mod install;
mod ui;

fn main() {
    if let Err(err) = config::load() {
        println!("Failed to load tarstall database: {}", err);
        exit(1)
    }
    if env::args_os().count() <= 1 {
        println!(
            "tarstall. A Rust-based package manager to manage archives.
Written by: hammy275

tarstall Version: {}
Internal Version Code: {}.{}
Branch: {}

For help, type \"tarstall -h\"

For additional help, visit the tarstall wiki: https://github.com/hammy275/tarstall/wiki",
            config::VERSION, config::FILE_VERSION, config::INTERNAL_PROGRAM_VERSION,
            config::DB.read().unwrap().version.branch)
    } else {
        let args = args::get_args();
        let mut ui = Box::new(cli_ui::new());
        match args::run(&args, &mut *ui) {
            Ok(_) => {}
            Err(msg) => println!("Error: {}", msg)
        }
    }
}
