use std::{env, fs, process};
use bass_s9_vigilode::{CallbackInput, Input, callbacks, run};

fn main() {
    let args:Vec<_>=env::args().collect();
    if args.len()!=4 || !["run","callbacks"].contains(&args[1].as_str()) {
        eprintln!("usage: bass-s9-vigilode (run|callbacks) INPUT.json OUTPUT.json");
        process::exit(2);
    }
    let result=(|| -> Result<bool,Box<dyn std::error::Error>> {
        let bytes=fs::read(&args[2])?;
        let (output,ok)=if args[1]=="run" {
            let input:Input=serde_json::from_slice(&bytes)?;
            let receipt=run(input);
            let ok=receipt.status=="completed";
            (serde_json::to_value(receipt)?,ok)
        } else {
            let input:CallbackInput=serde_json::from_slice(&bytes)?;
            match callbacks(input) {
                Ok(value)=>(value,true),
                Err(error)=>(serde_json::json!({"status":"failed","error":error}),false),
            }
        };
        // Every completed or failed run retains a raw, parseable receipt.
        let mut text=serde_json::to_string_pretty(&output)?; text.push('\n');
        fs::write(&args[3],text)?;
        Ok(ok)
    })();
    match result {
        Ok(true)=>(), Ok(false)=>process::exit(1), Err(error)=>{
            let failure=serde_json::json!({"schema":"BASS_S9_VIGILODE_DRIVER_FAILURE_V1",
                "status":"failed","failure":{"kind":"input_or_io_failure","error":error.to_string()}});
            let _=fs::write(&args[3],format!("{}\n",failure));
            eprintln!("{error}"); process::exit(2);
        }
    }
}
