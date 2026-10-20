use bass_s10_optimization::{CallbackInput,Input,Mode,callbacks_with_mode,run_independent,run_with_mode};
use serde_json::{Value,json};
use std::{env,fs,process};

fn main() {
    let args:Vec<_>=env::args().collect();
    let valid=(args.len()==5 && matches!(args[1].as_str(),"run"|"callbacks"))
        || (args.len()==6 && args[1]=="batch");
    if !valid {
        eprintln!("usage: bass-s10-optimization (run|callbacks) MODE INPUT.json OUTPUT.json\n       bass-s10-optimization batch MODE WORKERS INPUTS.json OUTPUT.json");
        process::exit(2);
    }
    let output_path=&args[args.len()-1];
    let result=(||->Result<bool,Box<dyn std::error::Error>> {
        let mode:Mode=args[2].parse().map_err(std::io::Error::other)?;
        let bytes=fs::read(&args[args.len()-2])?;
        let (output,ok):(Value,bool)=match args[1].as_str() {
            "run"=>{
                let input:Input=serde_json::from_slice(&bytes)?;
                let receipt=run_with_mode(input,mode);
                let ok=receipt.status=="completed";
                (serde_json::to_value(receipt)?,ok)
            },
            "callbacks"=>{
                let input:CallbackInput=serde_json::from_slice(&bytes)?;
                match callbacks_with_mode(input,mode) {
                    Ok(value)=>(value,true),
                    Err(error)=>(json!({"status":"failed","error":error}),false),
                }
            },
            "batch"=>{
                let inputs:Vec<Input>=serde_json::from_slice(&bytes)?;
                let workers=args[3].parse::<usize>()?;
                let receipts=run_independent(inputs,mode,workers).map_err(std::io::Error::other)?;
                let ok=receipts.iter().all(|r|r.status=="completed");
                (serde_json::to_value(receipts)?,ok)
            },
            _=>unreachable!(),
        };
        let mut text=serde_json::to_string_pretty(&output)?;text.push('\n');
        fs::write(output_path,text)?;
        Ok(ok)
    })();
    match result {
        Ok(true)=>(),Ok(false)=>process::exit(1),Err(error)=>{
            let failure=json!({"schema":"BASS_S10_DRIVER_FAILURE_V1","status":"failed",
                "failure":{"kind":"input_or_io_failure","error":error.to_string()}});
            let _=fs::write(output_path,format!("{failure}\n"));
            eprintln!("{error}");process::exit(2);
        }
    }
}
