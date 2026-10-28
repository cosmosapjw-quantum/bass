import sys,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
import pytest
from native_saved import read_locked

def test_secondary_source_identity_is_enforced(tmp_path):
 p=tmp_path/'input.json';p.write_bytes(b'{"value":1}')
 expected=hashlib.sha256(p.read_bytes()).hexdigest()
 assert read_locked(p,expected)=={'value':1}
 p.write_bytes(b'{"value":2}')
 with pytest.raises(ValueError,match='SHA'):read_locked(p,expected)
