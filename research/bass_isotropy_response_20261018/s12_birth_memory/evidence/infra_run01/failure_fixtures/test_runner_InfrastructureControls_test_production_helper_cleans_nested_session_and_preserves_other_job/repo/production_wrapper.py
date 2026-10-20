import importlib.util,json,pathlib,sys
module_path,output_path=sys.argv[1:3]
mode=sys.argv[3] if len(sys.argv)>3 else 'interrupt'
spec=importlib.util.spec_from_file_location('s12_actual_process_control',module_path)
production=importlib.util.module_from_spec(spec);spec.loader.exec_module(production)
output=pathlib.Path(output_path)
grandchild="import os,pathlib,signal,sys,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); pathlib.Path(sys.argv[1]).write_text(str(os.getpid())); time.sleep(3); pathlib.Path(sys.argv[2]).write_text('late')"
child="import signal,subprocess,sys,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); subprocess.Popen([sys.executable,'-c',sys.argv[1],sys.argv[2],sys.argv[3]]); time.sleep(10)"
if mode=='normal_exit':
    child="""import pathlib,subprocess,sys,time
subprocess.Popen([sys.executable,'-c',sys.argv[1],sys.argv[2],sys.argv[3]])
deadline=time.monotonic()+1
while not pathlib.Path(sys.argv[2]).exists() and time.monotonic()<deadline: time.sleep(.01)
assert pathlib.Path(sys.argv[2]).exists()
"""
record=production.run_owned([sys.executable,'-c',child,grandchild,str(output.parent/'nested-ready'),str(output.parent/'nested-late')],
    stdout_path=output.parent/'nested.stdout',stderr_path=output.parent/'nested.stderr',
    receipt_path=output.parent/'nested-receipt.json',timeout_s=5)
output.write_text(json.dumps({'status':record['status']}))
sys.exit(record['exit_code'])
