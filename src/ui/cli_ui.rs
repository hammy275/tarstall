use std::path::PathBuf;
use terminal_size::{terminal_size, Height, Width};
use crate::ui::UI;

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

    fn choose(&mut self, msg: String, options: Vec<String>) -> usize {
        todo!()
    }

    fn ask_file(&mut self) -> PathBuf {
        todo!()
    }
}

pub fn new() -> CliUI {
    CliUI{
        last_progress: 0.0,
    }
}