#!/usr/bin/env python3
"""Build regression: real Cherri, dummy credentials, and stub signing. No vault calls."""
import json
import os
from pathlib import Path
import plistlib
import re
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
import unittest

DUMMY = "DUMMY_BUILD_CREDENTIAL_7851"
REPO = Path(__file__).resolve().parent.parent


def stub(tool):
    root = Path(os.environ["BUILD_TEST_ROOT"])
    mode = os.environ.get("BUILD_TEST_MODE", "success")
    args = sys.argv[1:]
    if tool == "op":
        assert args[0] == "inject", "Tests must never call a real vault"
        template = Path(args[args.index("-i") + 1]).read_text()
        refs = re.findall(r"op://[^\s\"']+", template)
        (root / "refs.json").write_text(json.dumps(refs))
        if mode == "inject_fail":
            print(DUMMY, file=sys.stderr)
            return 12
        value = re.sub(r"op://[^\s\"']+", DUMMY, template)
        if "-o" in args:
            Path(args[args.index("-o") + 1]).write_text(value)
        else:
            sys.stdout.write(value)
        return 0
    if tool == "cherri":
        # Observe the real user's build before the compiler reads its input.
        leaks = [str(p.relative_to(root)) for p in root.rglob("*")
                 if p.suffix == ".cherri" and stat.S_ISREG(p.stat().st_mode)
                 and DUMMY.encode() in p.read_bytes()]
        (root / "source-leaks.json").write_text(json.dumps(leaks))
        if mode == "compiler_early_fail":
            return 15  # Fail before opening the FIFO; the producer must stop.
        os.execv(os.environ["BUILD_TEST_CHERRI"], ["cherri", *args])
    assert tool == "shortcuts" and args[0] == "sign"
    unsigned = Path(args[args.index("-i") + 1])
    assert stat.S_IMODE(unsigned.stat().st_mode) == 0o600
    assert stat.S_IMODE(unsigned.parent.stat().st_mode) == 0o700
    data = unsigned.read_bytes()
    pl = plistlib.loads(data)
    text = str(pl)
    assert DUMMY in text
    assert "LOCAL_ENDPOINT" in text and "DEFAULT_ENDPOINT" not in text
    assert "DEFAULT_ONLY" in text
    assert "ZHVtbXkgYXNzZXQ=" in text, "source-relative asset not embedded"
    form = next(a for a in pl["WFWorkflowActions"]
                if a["WFWorkflowActionIdentifier"] == "is.workflow.actions.downloadurl")
    items = form["WFWorkflowActionParameters"]["WFFormValues"]["Value"]["WFDictionaryFieldValueItems"]
    assert items[0]["WFItemType"] == 5, "file form patch was skipped"
    output = Path(args[args.index("-o") + 1])
    if mode in ("sign_fail", "interrupt"):
        output.write_bytes(data)  # A failing signer can leave a partial output.
        if mode == "interrupt":
            (root / "signing-ready").write_text(str(os.getpid()))
            time.sleep(20)
        print(DUMMY)
        print(DUMMY, file=sys.stderr)
        return 13
    output.write_bytes(b"STUB_SIGNED\n" + data)
    return 0


class CompileShortcutTest(unittest.TestCase):
    shortcut_name = "Build Probe"

    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(prefix="compile-shortcut-test-")
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        (self.root / "scripts").mkdir()
        for name in ("compile-shortcut.sh", "patch-shortcut-plist.py"):
            shutil.copy2(REPO / "scripts" / name, self.root / "scripts" / name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        for tool in ("op", "cherri", "shortcuts"):
            path = self.bin / tool
            path.write_text(f"#!{sys.executable}\nimport runpy\nrunpy.run_path({str(Path(__file__).resolve())!r}, init_globals={{'STUB_TOOL': {tool!r}}}, run_name='__main__')\n")
            path.chmod(0o700)
        self.env = dict(os.environ, PATH=str(self.bin) + os.pathsep + os.environ["PATH"],
                        BUILD_TEST_ROOT=str(self.root), BUILD_TEST_CHERRI=shutil.which("cherri"))
        self.env.pop("OP_SERVICE_ACCOUNT_TOKEN", None)
        (self.root / "constants.txt").write_text("ENDPOINT=DEFAULT_ENDPOINT\nFALLBACK=DEFAULT_ONLY\n")
        (self.root / "constants.local.txt").write_text("ENDPOINT=LOCAL_ENDPOINT\n")
        self.source_dir = self.root / "source folder"
        self.source_dir.mkdir()
        (self.source_dir / "assets").mkdir()
        (self.source_dir / "assets" / "sample.txt").write_text("dummy asset")
        self.source = self.source_dir / "first.cherri"
        self.source.write_text('''#define name Build Probe
#include 'actions/web'
#include 'actions/crypto'
@credential = "<<secret:TEST_KEY>>"
@endpoint = "<<constant:ENDPOINT>>"
@fallback = "<<constant:FALLBACK>>"
const Asset = embedFile("assets/sample.txt")
formRequest("https://example.com", "POST", { "file": "{Asset}" })
showNotification(@credential)
'''.replace('#define name Build Probe', '#define name ' + self.shortcut_name))
        self.destination = self.source_dir / (self.shortcut_name + '.shortcut')
        self.destination.write_bytes(b"PREVIOUS_SIGNED_OUTPUT")

    def build(self, mode="success", files=None):
        env = dict(self.env, BUILD_TEST_MODE=mode)
        return subprocess.run(["bash", "scripts/compile-shortcut.sh", *(files or [str(self.source)])],
                              cwd=self.root, env=env, capture_output=True, timeout=15)

    def assert_clean(self, result, allowed=()):
        self.assertNotIn(DUMMY.encode(), result.stdout + result.stderr, "credential in diagnostics")
        if (self.root / "source-leaks.json").exists():
            self.assertEqual(json.loads((self.root / "source-leaks.json").read_text()), [],
                             "plaintext credential-bearing Cherri input existed during build")
        for p in self.root.rglob("*"):
            if p.is_file() and p not in allowed:
                self.assertNotIn(DUMMY.encode(), p.read_bytes(), f"credential left in {p.relative_to(self.root)}")
            self.assertFalse(p.is_fifo(), f"FIFO left in {p.relative_to(self.root)}")
        self.assertEqual(sorted(p.name for p in self.source_dir.iterdir()),
                         sorted(["assets", "first.cherri", self.destination.name] +
                                [p.name for p in allowed if p != self.destination and p.parent == self.source_dir]))

    def test_sign_failure_preserves_destination_and_removes_credentials(self):
        result = self.build("sign_fail")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.destination.read_bytes(), b"PREVIOUS_SIGNED_OUTPUT")
        self.assert_clean(result)

    def test_success_preserves_constants_assets_patch_and_multiple_files(self):
        second = self.source_dir / "second.cherri"
        second.write_text(self.source.read_text().replace("#define name " + self.shortcut_name, "#define name Second Probe"))
        output = self.source_dir / "Second Probe.shortcut"
        result = self.build(files=[str(self.source), str(second)])
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        for p in (self.destination, output):
            self.assertTrue(p.read_bytes().startswith(b"STUB_SIGNED\n"))
            self.assertIn(DUMMY.encode(), p.read_bytes())
        self.assert_clean(result, allowed=(self.destination, output, second))
        self.assertEqual(json.loads((self.root / "refs.json").read_text()),
                         ["op://uk3hfwomwjxl33uxpjurzpr7z4/p6cdlljtfcdwbyzznatrcmohdi/TEST_KEY"])

    def test_injection_failure_is_quiet_and_cleans_up(self):
        result = self.build("inject_fail")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.destination.read_bytes(), b"PREVIOUS_SIGNED_OUTPUT")
        self.assert_clean(result)

    def test_compile_failure_cleans_up_and_hides_source_diagnostics(self):
        self.source.write_text(self.source.read_text() + "invalidAction(@credential)\n")
        result = self.build()
        self.assertNotEqual(result.returncode, 0)
        self.assert_clean(result)

    def test_patch_failure_cleans_up(self):
        (self.root / "scripts" / "patch-shortcut-plist.py").write_text("raise SystemExit(14)\n")
        result = self.build()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.destination.read_bytes(), b"PREVIOUS_SIGNED_OUTPUT")
        self.assert_clean(result)

    def test_compiler_failure_before_fifo_open_stops_producer(self):
        result = self.build("compiler_early_fail")
        self.assertNotEqual(result.returncode, 0)
        self.assert_clean(result)

    def test_termination_stops_signer_and_removes_partial_output(self):
        proc = subprocess.Popen(["bash", "scripts/compile-shortcut.sh", str(self.source)],
                                cwd=self.root, env=dict(self.env, BUILD_TEST_MODE="interrupt"),
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        try:
            deadline = time.monotonic() + 5
            while not (self.root / "signing-ready").exists():
                self.assertIsNone(proc.poll(), "build exited before signing")
                self.assertLess(time.monotonic(), deadline, "signer did not start")
                time.sleep(0.02)
            signer_pid = int((self.root / "signing-ready").read_text())
            proc.send_signal(signal.SIGTERM)
            stdout, stderr = proc.communicate(timeout=3)
            self.assertNotEqual(proc.returncode, 0)
            with self.assertRaises(ProcessLookupError):
                os.kill(signer_pid, 0)
            self.assertEqual(self.destination.read_bytes(), b"PREVIOUS_SIGNED_OUTPUT")
            self.assert_clean(subprocess.CompletedProcess(proc.args, proc.returncode, stdout, stderr))
        finally:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.communicate()


class LeadingDotCompileShortcutTest(CompileShortcutTest):
    shortcut_name = ".Build Probe"


if __name__ == "__main__":
    tool = globals().get("STUB_TOOL", Path(sys.argv[0]).name)
    if tool in ("op", "cherri", "shortcuts"):
        raise SystemExit(stub(tool))
    unittest.main()
