"""Original CE1 source locator for repo, local bundle and verified restored ancestor."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ARCHIVE_CANDIDATES=[ROOT/'dependencies/ce1ab_20261030',ROOT.parent/'dependencies/ce1ab_20261030']
arch=next((a for a in ARCHIVE_CANDIDATES if (a/'ce1aa_input/source/cellwise_gl_rust.py').is_file()),None)
if arch is not None:
    SRC=arch/'ce1aa_input/source'
    REPLAY=arch
    INPUT=arch/'ce1aa_input/input'
else:
    SRC=(ROOT/'original_source' if (ROOT/'original_source/cellwise_gl_rust.py').is_file() else ROOT.parent/'ce1aa_20261030/source')
    INPUT=(ROOT/'input' if (ROOT/'input/GL6_DOP853_coupled_41epochs.csv').is_file() else ROOT.parent/'ce1aa_20261030/input')
    REPLAY=ROOT.parent/'ce1ab_20261030'
assert (SRC/'cellwise_gl_rust.py').is_file(), 'locked six-cell original source missing'
assert (REPLAY/'replay_dop853.py').is_file(), 'original CE1-AB replay source missing'
