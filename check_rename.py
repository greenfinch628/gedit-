"""Tab renaming preserves edits, refuses collisions and saves new documents in the workspace."""
from pathlib import Path
import json
import tempfile
from PyQt6.QtWidgets import QApplication
from enhancements import AppWindow, Store, read_session

app = QApplication([])
with tempfile.TemporaryDirectory(prefix="gedit-rename-check-") as directory:
    root = Path(directory)
    workspace = root / "workspace"
    workspace.mkdir()
    store = Store(root / "recovery")
    window = AppWindow(store)
    errors = []
    window.report = lambda title, error: errors.append(str(error))
    window.set_folder(workspace)
    original = workspace / "original.txt"
    original.write_text("saved text")
    window.open_path(original)
    editor = window.editor()
    editor.setText("unsaved edit")
    editor.setModified(True)
    editor.tab_color = "#dde8fa"
    archived = store.archive(window.document_record(editor))
    assert window.rename_document(editor, "renamed.md")
    renamed = workspace / "renamed.md"
    assert not original.exists() and renamed.read_text() == "saved text"
    assert editor.path == renamed and editor.text() == "unsaved edit" and editor.isModified()
    assert editor.tab_color == "#dde8fa" and editor.language_name == "Markdown"
    assert json.loads(archived.read_text())["path"] == str(renamed)
    collision = workspace / "taken.txt"
    collision.write_text("keep me")
    assert not window.rename_document(editor, collision.name)
    assert collision.read_text() == "keep me" and editor.path == renamed
    assert not window.rename_document(editor, "../outside.txt")
    window.new_document()
    draft = window.editor()
    draft.setText("new document 🐦")
    draft.setModified(True)
    assert window.rename_document(draft, "new file.txt")
    assert (workspace / "new file.txt").read_text() == "new document 🐦"
    assert draft.path.parent == workspace and not draft.isModified()
    snapshot = read_session(store.window_path(window.identity))
    assert any(d["path"] == str(renamed) and d["modified"] and d["text"] == "unsaved edit" for d in snapshot["documents"])
    window.close()
    print("PASS: named rename, unsaved text and color preserved, syntax updated, archived paths updated, collisions refused, untitled saved in sidebar folder and recovery retained")
