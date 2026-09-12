use crate::config::DB;
use crate::task::TaskResult;
use crate::ui::UI;

pub fn list(ui: &mut dyn UI) -> TaskResult {
    let names: Vec<String> = DB.read().unwrap().programs.iter()
        .map(| program | { program.name.clone() })
        .collect();
    if names.is_empty() {
        ui.message("There are no installed programs.".to_string());
    } else {
        ui.message(names.join("\n"));
    }
    Ok(())
}