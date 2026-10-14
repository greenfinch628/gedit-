"""A second launch focuses/opens paths in the same application instance."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

with tempfile.TemporaryDirectory(prefix="gedit-launch-check-") as temporary:
    root = Path(temporary)
    data = root / "state"
    first = root / "first.txt"
    second = root / "second.txt"
    first.write_text("first file")
    second.write_text("second file")
    command = [sys.executable, str(Path(__file__).parent / "editor.py"), "--data-dir", str(data)]
    environment = dict(os.environ, QT_QPA_PLATFORM="offscreen")
    running = subprocess.Popen(command + [str(first)], env=environment, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        deadline = time.monotonic() + 8
        while not (data / "editor.sock").exists() and time.monotonic() < deadline:
            if running.poll() is not None:
                raise AssertionError(running.stderr.read().decode())
            time.sleep(0.05)
        assert (data / "editor.sock").exists()
        result = subprocess.run(command + [str(second)], env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=8)
        assert result.returncode == 0, result.stderr.decode()
        while time.monotonic() < deadline:
            records = list((data / "windows").glob("*.json"))
            current = [path for path in records if ".previous." not in path.name]
            if len(current) == 1:
                record = json.loads(current[0].read_text())
                if any(document["text"] == "second file" for document in record["documents"]):
                    break
            time.sleep(0.05)
        else:
            raise AssertionError("Second launch did not open its file in the existing window")
        assert any(document["text"] == "first file" for document in record["documents"])
        assert first.read_text() == "first file" and second.read_text() == "second file"
        print("PASS: second launch forwards files into the existing instance and preserves originals")
    finally:
        running.terminate()
        running.wait(timeout=5)
