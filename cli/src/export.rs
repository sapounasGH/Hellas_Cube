use prettytable::{format, Table, Row, Cell};
use serde_json::Value;

pub fn export(body: &str) {
    match serde_json::from_str::<Value>(body) {
        Ok(Value::Object(map)) => format_object(&map),
        Ok(Value::Array(arr)) => {
            let mut table = Table::new();
            table.add_row(row![b->"Array List"]);
            table.add_row(row![json_to_table(&Value::Array(arr))]);
            table.printstd();
        }
        Ok(other) => println!("{}", format_value(&other)),
        Err(_) => format_plain(body),
    }
}

/* ─── Auto-detectors ─── */

fn is_analysis(map: &serde_json::Map<String, Value>) -> bool {
    map.contains_key("STATUS")
        || map.contains_key("analyzation")
        || map.contains_key("place")
        || map.contains_key("time")
        || map.contains_key("result")
}

fn is_history(map: &serde_json::Map<String, Value>) -> bool {
    map.get("history").map(|v| v.is_array()).unwrap_or(false)
}

/* ─── Format routers ─── */

fn format_object(map: &serde_json::Map<String, Value>) {
    if is_analysis(map) {
        print_analysis(map);
    } else if is_history(map) {
        print_history(map);
    } else if map.len() == 1 {
        print_single_pair(map);
    } else {
        print_generic_object(map);
    }
}

fn format_plain(text: &str) {
    let t = text.trim();
    if t.eq_ignore_ascii_case("success") || t.eq_ignore_ascii_case("sucess") {
        println!("✓  {}", t);
    } else if t.starts_with("Error") || t.starts_with("FAILED") || t.starts_with("FAIL") {
        println!("✗  {}", t);
    } else {
        println!("{}", text);
    }
}

/* ─── 1. Analysis result (NDVI/NDTI/etc) ─── */

fn print_analysis(map: &serde_json::Map<String, Value>) {
    let mut table = Table::new();
    table.set_titles(row![b->"Field", b->"Value"]);

    add_kv_row(&mut table, "Status", map.get("STATUS"));
    add_kv_row(&mut table, "Index", map.get("analyzation"));
    
    if let Some(place) = map.get("place") {
        let val_str = truncate(format_value(place), 60);
        table.add_row(row![b->"Area", val_str]);
    }
    
    add_kv_row(&mut table, "Time", map.get("time"));

    if let Some(result) = map.get("result") {
        table.add_row(row![b->"Result", json_to_table(result)]);
    }

    println!("\n##### HellasCube Analysis Result #####");
    table.printstd();
}

/* ─── 2. History list ─── */

fn print_history(map: &serde_json::Map<String, Value>) {
    let arr = map.get("history").and_then(|v| v.as_array()).unwrap();
    if arr.is_empty() {
        println!("No history found.");
        return;
    }

    println!("\n##### History ({} record(s)) #####", arr.len());

    let mut table = Table::new();
    table.set_titles(row![b->"#", b->"Analysis", b->"Range", b->"Request ID", b->"Result"]);

    for (i, item) in arr.iter().enumerate() {
        if let Some(obj) = item.as_object() {
            let analysis = get_str(obj, "analysis");
            let range = get_str(obj, "date_range");
            let req_id = truncate(get_str(obj, "request_id"), 16);

            if let Some(res) = obj.get("res_json") {
                // Unwrap stringified JSON dynamically
                let mut parsed = res.clone();
                while let Some(s) = parsed.as_str() {
                    if let Ok(v) = serde_json::from_str::<Value>(s) {
                        parsed = v;
                    } else {
                        break;
                    }
                }
                // Add the completely nested table to the cell
                table.add_row(row![
                    (i + 1).to_string(),
                    analysis,
                    range,
                    req_id,
                    json_to_table(&parsed) 
                ]);
            } else {
                table.add_row(row![
                    (i + 1).to_string(),
                    analysis,
                    range,
                    req_id,
                    "(no result)"
                ]);
            }
        }
    }
    table.printstd();
    println!();
}

/* ─── 3. Single-key responses (login, cacc) ─── */

fn print_single_pair(map: &serde_json::Map<String, Value>) {
    let mut table = Table::new();
    for (k, v) in map {
        table.add_row(row![b->capitalize(k), format_value(v)]);
    }
    table.printstd();
}

/* ─── 4. Generic object fallback ─── */

fn print_generic_object(map: &serde_json::Map<String, Value>) {
    let table = json_to_table(&Value::Object(map.clone()));
    table.printstd();
}

/* ─── Recursive Nested Table Generator ─── */

/// Converts any JSON Value (Object or Array) into a nested Table.
fn json_to_table(val: &Value) -> Table {
    let mut table = Table::new();
    // Using a clean format for inner tables prevents messy overlapping grid lines
    table.set_format(*format::consts::FORMAT_CLEAN);

    match val {
        Value::Object(map) => {
            for (k, v) in map {
                let is_complex = v.is_object() && !v.as_object().unwrap().is_empty()
                              || v.is_array() && !v.as_array().unwrap().is_empty();

                if is_complex {
                    table.add_row(row![b->k, json_to_table(v)]);
                } else {
                    table.add_row(row![b->k, format_value(v)]);
                }
            }
        }
        Value::Array(arr) => {
            for (i, v) in arr.iter().enumerate() {
                let is_complex = v.is_object() && !v.as_object().unwrap().is_empty()
                              || v.is_array() && !v.as_array().unwrap().is_empty();

                if is_complex {
                    table.add_row(row![format!("[{}]", i), json_to_table(v)]);
                } else {
                    table.add_row(row![format!("[{}]", i), format_value(v)]);
                }
            }
        }
        other => {
            table.add_row(row![format_value(other)]);
        }
    }
    table
}

/* ─── Helpers ─── */

fn add_kv_row(table: &mut Table, label: &str, val: Option<&Value>) {
    if let Some(v) = val {
        table.add_row(row![b->label, format_value(v)]);
    }
}

fn format_value(v: &Value) -> String {
    match v {
        Value::String(s) => s.clone(),
        Value::Number(n) => n.to_string(),
        Value::Bool(b) => b.to_string(),
        Value::Null => "null".to_string(),
        Value::Object(_) | Value::Array(_) => v.to_string(), // Fallback
    }
}

fn get_str(map: &serde_json::Map<String, Value>, key: &str) -> String {
    map.get(key).and_then(|v| v.as_str()).unwrap_or("-").to_string()
}

fn truncate(s: String, max: usize) -> String {
    if s.chars().count() > max {
        format!("{}…", s.chars().take(max - 1).collect::<String>())
    } else {
        s
    }
}

fn capitalize(s: &str) -> String {
    let mut c = s.chars();
    match c.next() {
        None => String::new(),
        Some(f) => f.to_uppercase().collect::<String>() + c.as_str(),
    }
}