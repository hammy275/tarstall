use clap::{Args, Parser, Subcommand};
use crate::install::install;

#[derive(Parser, Debug)]
#[command(about)]
pub struct TarstallArgs {
    #[arg(short, long, default_value_t = false)]
    /// Enables verbose mode for this run of tarstall
    pub verbose: bool,
    #[command(subcommand)]
    pub command: Command
}

#[derive(Subcommand, Debug)]
pub enum Command {
    /// Install a program from a file path or URL
    Install(InstallArgs),
    /// Remove a program by name
    Remove(ProgramArgs),
    /// List all installed programs
    List {},
    /// Runs first-time setup
    First {},
    /// Removes tarstall from your system
    Erase {},
    /// Update tarstall and/or installed programs
    Update(UpdateArgs),
    /// Manage a program by name
    Manage(ProgramArgs),
    /// Remove tarstall's lock; only use if tarstall isn't already running
    RemoveLock {},
    /// Configure tarstall
    Config {},

}

#[derive(Args, Debug)]
pub struct InstallArgs {
    /// The archive/directory/file/git URL/archive URL to install from
    pub source: String,
    #[arg(short, long)]
    /// The name for the installed program
    pub name: Option<String>
}

#[derive(Args, Debug)]
pub struct ProgramArgs {
    /// The name of the program
    pub program: String
}

#[derive(Args, Debug)]
pub struct UpdateArgs {
    #[arg(short, long, default_value_t = false)]
    /// Update tarstall
    pub tarstall: bool,
    #[arg(short, long)]
    /// Update an installed program
    pub program: Option<String>
}

pub fn get_args() -> TarstallArgs {
    TarstallArgs::parse()
}

pub fn run(args: &TarstallArgs) -> Result<(), String> {
    match args.command {
        Command::Install(ref install_args) => install(install_args),
        Command::Remove(_) => todo!(),
        Command::List { .. } => todo!(),
        Command::First { .. } => todo!(),
        Command::Erase { .. } => todo!(),
        Command::Update(_) => todo!(),
        Command::Manage(_) => todo!(),
        Command::RemoveLock { .. } => todo!(),
        Command::Config { .. } => todo!(),
    }
}