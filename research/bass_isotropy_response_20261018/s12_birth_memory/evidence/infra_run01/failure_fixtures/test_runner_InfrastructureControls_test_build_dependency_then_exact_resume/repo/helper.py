import json,pathlib,subprocess,sys,time
mode,output,input_path=sys.argv[1:4]
data=json.loads(pathlib.Path(input_path).read_text())
if mode=='fail': sys.exit(7)
if mode=='output_budget':
    for index in range(8):
        (pathlib.Path(output).parent/f'chunk-{index}').write_bytes(b'x'*32768)
if mode=='sleep':
    child="import pathlib,sys,time; time.sleep(2); pathlib.Path(sys.argv[1]).write_text('late')"
    subprocess.Popen([sys.executable,'-c',child,str(pathlib.Path(output).parent/'late-marker')])
    time.sleep(10)
if len(sys.argv)>4: assert pathlib.Path(sys.argv[4]).is_file()
pathlib.Path(output).write_text(json.dumps({'status':'FAIL' if mode=='reject' else 'PASS_SCOPED','value':data['value']}))
