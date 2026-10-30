#!/usr/bin/env python3
"""Restore exact inherited source/geometry evidence into this bounded CE1-AD unit.

Strict bytes on source and MPFR models; only read from PR280 protected parent.
No changes to PR270/277/280 paths. Local snapshot mode is supported.
"""
from pathlib import Path
import hashlib,json,zipfile,shutil
BASE=Path(__file__).resolve().parents[1]
PARENT=BASE.parent
CHECKSUMS={
 'EXACT_SIX_CELL_L4_SOURCE.json':'f1579a9b3ebed7bea3588d9ae759ab12b59c2714729f2b9e22a2cdf1a1b153f2',
 'GL6_SOURCE_MPFR192.json':'edd08d0276daa955f1388fbb4ac2ad73424d6b3b51f7fcdacbbb164a19f546ec',
 'GL8_SOURCE_MPFR192.json':'e02bdc353652e26a689ecc353124f9fd6efadb1d27c8f895a9db993c5c620fb3',
 'GL6_GEOMETRY_BOUND.json':'17bdb90ed8612c8123a4e407b34225fcb4b09bed3cd644e3751b248dab28e226',
 'GL8_GEOMETRY_BOUND.json':'0745717abcdc737df09c0c20fbe7bfe8b8d0a5b16cba1a52b76cea60b47452cf',
}
S1_SHA='127adc79aa39a7cb19514efab27c990dbf7c1c8da5f710cfc064f1ddb262f77e'

def main():
    target=BASE/'input';target.mkdir(parents=True,exist_ok=True)
    # On GitHub, predecessor PR277 stored full exact S1 inputs as source-inclusive ZIP.
    if not (target/'GL6_GEOMETRY_BOUND.json').exists():
        archive=PARENT/'ce1ab_20261030'/'CE1AB_S1_IMPLEMENTATION_AND_SCIENCE_20261030.zip'
        assert hashlib.sha256(archive.read_bytes()).hexdigest()==S1_SHA
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            m=json.loads(z.read('ce1ab_20261030/PACKAGE_MANIFEST_SHA256.json'))
            for name,spec in m['payload'].items():
                bs=z.read(name)
                assert len(bs)==spec['size'] and hashlib.sha256(bs).hexdigest()==spec['sha256']
            for order in (6,8):
                name=f'ce1ab_20261030/results/GL{order}_CE1AB_RANK2_N32.json'
                (target/f'GL{order}_GEOMETRY_BOUND.json').write_bytes(z.read(name))
    for order in (6,8):
        local=target/f'GL{order}_SOURCE_MPFR192.json'
        if not local.exists():
            src=PARENT/'ce1aa_20261030'/'data'/f'GL{order}_mpfr192_source_41.json'
            shutil.copyfile(src,local)
    local=target/'EXACT_SIX_CELL_L4_SOURCE.json'
    if not local.exists():shutil.copyfile(PARENT/'ce1aa_20261030'/'input'/'l4_source_and_transfer.json',local)
    for name,sha in CHECKSUMS.items():
        actual=hashlib.sha256((target/name).read_bytes()).hexdigest()
        assert actual==sha,(name,actual,sha)
    # Fresh 41-epoch physical timejet generation is carried out separately via
    # original CE1-AC generator before copying. Never treat frozen CSV as proof input.
    for order in (6,8):
        out=target/f'GL{order}_PHYSICAL_TIMEJETS.csv'
        src=PARENT/'ce1ac_20261030'/'data'/f'GL{order}_ORIGINAL_L4_TIMEJET_41.csv'
        if not out.exists() and src.exists():shutil.copyfile(src,out)
    print('RESTORE_VERIFIED 5/5 SHA + S1 payload integrity; physical timejet source=original CE1-AC',flush=True)

if __name__=='__main__':main()
