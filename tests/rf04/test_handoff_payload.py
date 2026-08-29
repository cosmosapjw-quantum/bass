"""Payload checks are not scientific or native-validation claims."""
from pathlib import Path
import importlib.util
import json
import shutil
import pytest

ROOT=Path(__file__).resolve().parents[2]
REL=Path('docs/rust_first_runtime/rf04_external_review_resume_20260829')


def validator():
    spec=importlib.util.spec_from_file_location('rf04_payload_validator',ROOT/REL/'validate_handoff.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def payload_copy(destination):
    contract=json.loads((ROOT/REL/'CONTRACT.json').read_text())
    paths=contract['delivery_paths']+[str(REL/'MANIFEST.sha256')]
    for name in paths:
        target=destination/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/name,target)
    return destination


def test_payload_manifest_and_profile_close():
    result=validator().validate(ROOT)
    assert result['claim']=='NO_PASS_RF04'
    assert result['source_objects']=='NOT_RUN'
    assert result['files']>0


def test_changed_payload_is_not_silently_normalized(tmp_path):
    copy=payload_copy(tmp_path/'payload')
    path=copy/'tests/rf04/rf04_dense_oracle.py'
    path.write_text(path.read_text()+'\n# mutation\n')
    with pytest.raises(ValueError,match='digest mismatch'):
        validator().validate(copy)


def test_path_escape_is_rejected(tmp_path):
    copy=payload_copy(tmp_path/'payload')
    (copy/REL/'MANIFEST.sha256').write_text('0'*64+'  ../escape\n')
    with pytest.raises(ValueError,match='unsafe'):
        validator().validate(copy)
