use std::env;
use std::sync::Arc;
use std::sync::mpsc::channel;
use crate::cli::TarstallCli;
use crate::task::{TaskRunner, Tasks};
use crate::task::ProgressSender::Sender;
use crate::tasks::file_transfer::{FileTransfer, TransferMode};
use crate::tasks::folder_transfer::create_folder_transfer;
use crate::tasks::task_of_tasks::TaskOfTasks;
use crate::util::{temp_dir, TempDir};

mod program;
mod task;
mod tasks;
mod util;
mod db;
mod config;
mod cli;
fn main() {
    if env::args_os().count() <= 1 {
        println!(
"tarstall. A Rust-based package manager to manage archives.
Written by: hammy275

tarstall Version: {}
Internal Version Code: {}.{}
Branch: master

For help, type \"tarstall -h\"

For additional help, visit the tarstall wiki: https://github.com/hammy275/tarstall/wiki",
        config::VERSION, db::FILE_VERSION, db::INTERNAL_PROGRAM_VERSION)
    } else {
        let cli = cli::get_args();
        println!("{:?}", cli)
    }
}
