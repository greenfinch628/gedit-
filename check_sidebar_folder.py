from pathlib import Path
import tempfile
from PyQt6.QtWidgets import QApplication
from enhancements import Store, AppWindow
app = QApplication([])
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    folder = root / "folder"
    folder.mkdir()
    original = folder / "example.txt"
    original.write_text("disk text")
    window = AppWindow(Store(root / "state"))
    window.show()
    window.editor().setText("loose draft")
    window.set_folder(folder)
    window.open_path(original)
    window.editor().setText("unsaved folder draft")
    window.editor().setModified(True)
    menu = window.make_folder_title_menu()
    assert [a.text() for a in menu.actions()] == ["Close Folder"]
    menu.actions()[0].trigger()
    assert window.workspace is None
    assert not window.sidebar.isHidden() and window.tree.isHidden()
    assert window.sidebar_title.toolTip() == ""
    assert window.editor().text() == "loose draft"
    assert window.make_folder_title_menu() is None
    window.toggle_sidebar(); window.toggle_sidebar()
    assert not window.sidebar.isHidden() and window.tree.isHidden()
    window.set_folder(folder)
    assert not window.tree.isHidden()
    assert window.editor().text() == "unsaved folder draft"
    assert original.read_text() == "disk text"
    window.close()
    print("PASS: title context menu closes folder, leaves empty sidebar, preserves loose and folder drafts, and reopens folder tree")
