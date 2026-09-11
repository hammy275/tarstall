pub mod cli_ui;

use std::path::PathBuf;

pub trait UI {
    /// Run a single frame of the UI, if applicable.
    fn run_ui(&mut self) -> ();
    /// Display a message to the end-user.
    fn message(&mut self, msg: String) -> ();
    /// Displays a verbose message to the end-user.
    fn debug(&mut self, msg: String) -> ();
    /// Sends a progress update to the UI. An implementation can assume that any progress update
    /// will be greater than or equal to the last until a 1.0 is received, at which point any
    /// further number of 1.0s may be received until a 0.0 is received, which returns to the
    /// previous rules.
    fn progress(&mut self, progress: f64) -> ();
    /// Ask the user the provided message and require them to pick one of the provided options.
    fn choose(&mut self, msg: String, options: Vec<String>) -> usize;
    /// Ask the user to select a file.
    fn ask_file(&mut self) -> PathBuf;
}