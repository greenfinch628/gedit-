"""Sidebar file rename and confirmed Trash deletion preserve documents and recovery."""
from pathlib import Path
import tempfile
from PyQt6.QtWidgets import QApplication
from enhancements import Store, AppWindow, read_session

app = QApplication([])
with tempfile.TemporaryDirectory(prefix="gedit-sidebar-check-") as directory:
    root = Path(directory)
    folder = root / "workspace"
    folder.mkdir()
    store = Store(root / "state")
    window = AppWindow(store)
    window.report = lambda *args: None
    window.set_folder(folder)
    source = folder / "closed.txt"
    source.write_text("disk contents")
    count = window.tabs.count()
    assert window.rename_sidebar_file(source, "renamed.txt")
    target = folder / "renamed.txt"
    assert target.read_text() == "disk contents" and not source.exists() and window.tabs.count() == count
    assert not window.delete_sidebar_file(target, confirm=False)
    assert target.exists()
    window.open_path(target)
    editor = window.editor()
    editor.setText("unsaved sidebar edit")
    editor.setModified(True)
    assert not window.delete_sidebar_file(target, confirm=True, trash=lambda path: (False, ""))
    assert target.exists() and editor.path == target and editor.text() == "unsaved sidebar edit"
    destination = root / "trash-fixture.txt"
    def trash(path):
        Path(path).rename(destination)
        return True, str(destination)
    assert window.delete_sidebar_file(target, confirm=True, trash=trash)
    assert not target.exists() and destination.read_text() == "disk contents"
    assert editor.path is None and editor.isModified() and editor.text() == "unsaved sidebar edit"
    snapshot = read_session(store.window_path(window.identity))
    assert any(d["path"] is None and d["text"] == "unsaved sidebar edit" for d in snapshot["documents"])
    assert not window.delete_sidebar_file(folder, confirm=True, trash=trash)
    window.close()
    print("PASS: closed-file rename, Cancel, Trash failure, successful deletion, unsaved text and recovery preserved; folders excluded")
