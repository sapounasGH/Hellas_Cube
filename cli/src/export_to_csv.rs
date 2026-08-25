use std::fs::OpenOptions;
use std::path::PathBuf;
use serde_json::Value;
use csv::WriterBuilder;
use crate::commands::user::get_creds;

/// Appends a JSON result (or multiple results if history) to the CSV file.
///
/// Path resolution order:
/// 1. `custom_path`, if provided
/// 2. `csv_path` saved in config
/// 3. Default location in the user's home directory
pub fn export_to_csv(json_body: &str) -> Result<(), String> {
    let parsed: Value = serde_json::from_str(json_body)
        .map_err(|_| "Failed to parse JSON for CSV export")?;

    // Determine the export path
    let mut file_path: PathBuf = if let Ok(config) = get_creds() {
        if !config.csv_path.is_empty() {
            PathBuf::from(config.csv_path)
        } else {
            default_csv_path()?
        }
    } else {
        default_csv_path()?
    };

    // If the resolved path is a directory (existing, or looks like one because
    // it has no file extension / ends with a separator), append a default filename.
    if file_path.is_dir()
        || file_path.to_string_lossy().ends_with(std::path::MAIN_SEPARATOR)
        || file_path.extension().is_none()
    {
        file_path = file_path.join("hellas_cube_export.csv");
    }

    // Make sure the parent directory exists (OpenOptions won't create it for us)
    if let Some(parent) = file_path.parent() {
        if !parent.as_os_str().is_empty() && !parent.exists() {
            std::fs::create_dir_all(parent)
                .map_err(|e| format!("Failed to create directory {}: {}", parent.display(), e))?;
        }
    }

    let file_exists = file_path.exists();

    // Open the file in append mode. Create it if it doesn't exist.
    let file = OpenOptions::new()
        .create(true)
        .append(true)
        .open(&file_path)
        .map_err(|e| format!("Failed to open CSV file: {}", e))?;

    let mut wtr = WriterBuilder::new()
        .has_headers(!file_exists)
        .from_writer(file);

    // If the file is newly created, write the header row
    if !file_exists {
        wtr.write_record(&["Analysis", "Range", "Result Data"])
            .map_err(|e| format!("Failed to write CSV headers: {}", e))?;
    }

    // Route based on whether it's a history list or a single result
    match parsed {
        Value::Object(map) if map.contains_key("history") => {
            if let Some(arr) = map.get("history").and_then(|v| v.as_array()) {
                for item in arr {
                    write_csv_row(&mut wtr, item)?;
                }
            }
        }
        Value::Array(arr) => {
            for item in arr {
                write_csv_row(&mut wtr, &item)?;
            }
        }
        Value::Object(_) => {
            write_csv_row(&mut wtr, &parsed)?;
        }
        _ => return Err("Invalid JSON structure for CSV export".to_string()),
    }

    wtr.flush().map_err(|e| format!("Failed to flush CSV writer: {}", e))?;

    Ok(())
}

/// Default export location: `<home>/export.csv`
fn default_csv_path() -> Result<PathBuf, String> {
    let home = dirs::home_dir()
        .ok_or_else(|| "Could not determine home directory".to_string())?;
    Ok(home.join("export.csv"))
}

/// Helper to extract fields from a single JSON object and write a CSV row
fn write_csv_row(wtr: &mut csv::Writer<std::fs::File>, item: &Value) -> Result<(), String> {
    let analysis = extract_str(item, "analyzation")
        .or_else(|| extract_str(item, "analysis")) // History uses "analysis", single uses "analyzation"
        .unwrap_or_else(|| "-".to_string());

    let range = extract_str(item, "date_range").unwrap_or_else(|| "-".to_string());

    // Result data can be nested, so we flatten it to a string
    let result_data = match item.get("result").or_else(|| item.get("res_json")) {
        Some(res) => {
            // Un-escape stringified JSON if needed
            let mut parsed = res.clone();
            while let Some(s) = parsed.as_str() {
                if let Ok(v) = serde_json::from_str::<Value>(s) {
                    parsed = v;
                } else {
                    break;
                }
            }
            // Format as inline JSON string for the CSV cell
            serde_json::to_string(&parsed).unwrap_or_default()
        }
        None => "".to_string(),
    };

    wtr.write_record(&[&analysis, &range, &result_data])
        .map_err(|e| format!("Failed to write CSV row: {}", e))?;

    Ok(())
}

/// Helper to grab a string field easily
fn extract_str(val: &Value, key: &str) -> Option<String> {
    val.get(key).and_then(|v| v.as_str()).map(|s| s.to_string())
}