from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (ROOT / "wsc0" / "bootstrap_xact.wl").read_text()


def test_bootstrap_pins_exact_xact_sha():
    assert "7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be" in SCRIPT
    assert 'FileHash[archive, "SHA256"]' in SCRIPT


def test_network_fallback_is_default_off():
    assert '"AllowNetworkFallback" -> False' in SCRIPT


def test_path_and_public_needs_are_used():
    assert 'PrependTo[$Path, root]' in SCRIPT
    assert 'Scan[Needs, contexts]' in SCRIPT
    assert 'FindFile[#]' in SCRIPT
