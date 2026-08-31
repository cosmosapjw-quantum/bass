import importlib,importlib.util

def candidate(name):
    spec=importlib.util.find_spec('tricode.'+name)
    assert spec is not None, f'FEATURE_ABSENT: {name}; boundary RED only, not physics proof'
    return importlib.import_module('tricode.'+name)
