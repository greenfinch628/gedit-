"""Behavior checks for file preservation and the actual QScintilla editor."""
import codecs
from pathlib import Path
import tempfile
from unittest.mock import patch

from PyQt6.QtCore import QEvent, QPoint, QPointF, Qt
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox

from editor import Editor, Window, STYLE


def run():
    app = QApplication([])
    app.setStyleSheet(STYLE)
    window = Window()
    window.show()
    app.processEvents()
    checks = []
    with tempfile.TemporaryDirectory(prefix="gedit-prototype-check-") as directory:
        root = Path(directory)
        for name, raw in [
            ("unicode.txt", "café 🐦\nsecond line\n".encode()),
            ("windows.txt", b"first\r\nsecond\r\n"),
            ("utf8-bom.txt", codecs.BOM_UTF8 + "café\n".encode()),
            ("utf16-le.txt", codecs.BOM_UTF16_LE + "café\r\n".encode("utf-16-le")),
            ("utf16-be.txt", codecs.BOM_UTF16_BE + "café\n".encode("utf-16-be")),
            ("utf16-no-bom.txt", "café\r\nsecond\r\n".encode("utf-16-le")),
            ("windows1252.txt", "café — line\r\n".encode("cp1252")),
            ("utf32.txt", codecs.BOM_UTF32_LE + "café\n".encode("utf-32-le")),
        ]:
            path = root / name
            path.write_bytes(raw)
            window.open_path(path)
            editor = window.editor()
            assert editor.text()
            assert window.save_editor(editor)
            assert path.read_bytes() == raw, name
            editor.append("end")
            assert editor.isModified()
            assert window.save_editor(editor)
            assert path.read_bytes() == raw + "end".encode(editor.encoding)
        checks.append("UTF-8, Unicode, UTF-8 BOM, UTF-16 BOM and CRLF round trips")

        current = window.editor()
        count = window.tabs.count()
        window.open_path(current.path)
        assert window.tabs.count() == count
        link = root / "alias.txt"
        link.symlink_to(current.path)
        window.open_path(link)
        assert window.tabs.count() == count
        checks.append("duplicate paths and symlinks activate the existing tab")

        current.append("unsaved")
        original = current.path.read_bytes()
        with patch.object(QMessageBox, "warning", return_value=QMessageBox.StandardButton.Cancel):
            window.close_tab(window.tabs.currentIndex())
            assert window.editor() is current and current.isModified()
        current.path.write_bytes(b"changed outside")
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.No):
            assert not window.save_editor(current)
        assert current.path.read_bytes() == b"changed outside" and current.isModified()
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Yes):
            assert window.save_editor(current)
        checks.append("Cancel retains unsaved text; external-change refusal preserves disk content")

        current.append("still unsaved")
        with patch.object(QFileDialog, "getSaveFileName", return_value=("", "")):
            assert not window.save_editor(current, as_new=True)
        assert current.isModified()
        # An invalid parent verifies that a failed atomic save leaves the document dirty.
        with patch.object(QFileDialog, "getSaveFileName", return_value=(str(root / "missing" / "file.txt"), "")), patch.object(QMessageBox, "critical"):
            assert not window.save_editor(current, as_new=True)
        assert current.isModified()
        checks.append("cancelled and failed Save As retain the dirty document")

        with patch.object(QFileDialog, "getSaveFileName", return_value=(str(root / "renamed.txt"), "")):
            assert window.save_editor(current, as_new=True)
        assert current.path == root / "renamed.txt"
        assert current.title == "renamed.txt" and not current.isModified()
        window.tabs.tabBar().moveTab(window.tabs.currentIndex(), 0)
        assert window.tabs.widget(0) is current
        window.tabs.setCurrentIndex(0)
        current.append("after reorder")
        assert window.save_current()
        assert current.path.read_bytes().endswith("after reorder".encode(current.encoding))
        pin = window.tabs.tabBar().tabButton(0, window.tabs.tabBar().ButtonPosition.LeftSide)
        window.toggle_pin(current, pin)
        window.close_tab(0)
        assert window.tabs.widget(0) is current
        window.toggle_pin(current, pin)
        window.close_tab(0)
        assert window.tabs.indexOf(current) == -1
        checks.append("Save As, tab reorder, save targeting, pin and unpin")

        window.set_folder(root)
        assert window.workspace == root
        assert window.sidebar.isVisible()
        assert window.model.isReadOnly()
        old_count = window.tabs.count()
        window.close_folder()
        assert window.workspace is None and window.tabs.count() == old_count
        checks.append("read-only folder browser and Close Folder preserve open documents")

        window.new_document()
        shortcut_tab = window.editor()
        before_close = window.tabs.count()
        shortcut_tab.setFocus()
        app.processEvents()
        QTest.keyClick(shortcut_tab, Qt.Key.Key_W, Qt.KeyboardModifier.ControlModifier)
        app.processEvents()
        assert window.tabs.count() == before_close - 1
        checks.append("Ctrl+W closes the active tab, retaining Qt's other platform close bindings")

        window.new_document()
        editor = window.editor()
        editor.setText("abcd\nefgh\nijkl\n")
        editor.SendScintilla(editor.SCI_EMPTYUNDOBUFFER)
        editor.setModified(False)
        editor.setFocus()
        app.processEvents()
        # Select columns 1..3 across three rows using actual Alt-drag mouse events.
        start_pos = 1
        end_pos = editor.positionFromLineIndex(2, 3)
        x1 = editor.SendScintilla(editor.SCI_POINTXFROMPOSITION, 0, start_pos)
        y1 = editor.SendScintilla(editor.SCI_POINTYFROMPOSITION, 0, start_pos) + 8
        x2 = editor.SendScintilla(editor.SCI_POINTXFROMPOSITION, 0, end_pos)
        y2 = editor.SendScintilla(editor.SCI_POINTYFROMPOSITION, 0, end_pos) + 8
        QTest.mousePress(editor.viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.AltModifier, QPoint(x1, y1))
        move = QMouseEvent(QEvent.Type.MouseMove, QPointF(x2, y2), QPointF(editor.viewport().mapToGlobal(QPoint(x2, y2))), Qt.MouseButton.NoButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.AltModifier)
        QApplication.sendEvent(editor.viewport(), move)
        QTest.mouseRelease(editor.viewport(), Qt.MouseButton.LeftButton, Qt.KeyboardModifier.AltModifier, QPoint(x2, y2))
        assert editor.SendScintilla(editor.SCI_SELECTIONISRECTANGLE), "Alt-drag did not select a rectangle"
        editor.copy()
        assert app.clipboard().text().replace("\r\n", "\n").rstrip("\n") == "bc\nfg\njk", repr(app.clipboard().text())
        QTest.keyClicks(editor, "X")
        assert editor.text() == "aXd\neXh\niXl\n", repr(editor.text())
        editor.undo()
        assert editor.text() == "abcd\nefgh\nijkl\n"
        QTest.keyClick(editor, Qt.Key.Key_Escape)
        assert not editor.SendScintilla(editor.SCI_SELECTIONISRECTANGLE)
        checks.append("actual Alt-drag rectangle, column copy, type across rows, single undo and Escape")

        editor.SendScintilla(editor.SCI_SETRECTANGULARSELECTIONANCHOR, 1)
        editor.SendScintilla(editor.SCI_SETRECTANGULARSELECTIONCARET, editor.positionFromLineIndex(2, 3))
        app.clipboard().setText("X\nY\nZ")
        QTest.keyClick(editor, Qt.Key.Key_V, Qt.KeyboardModifier.ControlModifier)
        assert editor.text() == "aXd\neYh\niZl\n", repr(editor.text())
        editor.undo()
        assert editor.text() == "abcd\nefgh\nijkl\n"
        editor.SendScintilla(editor.SCI_SETRECTANGULARSELECTIONANCHOR, 1)
        editor.SendScintilla(editor.SCI_SETRECTANGULARSELECTIONCARET, editor.positionFromLineIndex(2, 3))
        app.clipboard().setText("X\nY")
        with patch.object(QMessageBox, "information"):
            editor.paste()
        assert editor.text() == "abcd\nefgh\nijkl\n"
        checks.append("multiline block paste distributes rows, undoes once and rejects a mismatched row count")

        # Explicit rectangular selections cover short lines and virtual-space padding.
        editor.setText("ab\nx\n\n")
        editor.SendScintilla(editor.SCI_SETRECTANGULARSELECTIONANCHOR, 2)
        editor.SendScintilla(editor.SCI_SETRECTANGULARSELECTIONCARET, editor.positionFromLineIndex(2, 0))
        editor.SendScintilla(editor.SCI_SETRECTANGULARSELECTIONCARETVIRTUALSPACE, 2)
        QTest.keyClicks(editor, "Z")
        assert editor.text() == "abZ\nx Z\n  Z\n", repr(editor.text())
        checks.append("block typing pads short and blank rows at the chosen column")

        editor.setModified(False)
        window.tabs.setCurrentIndex(window.tabs.indexOf(editor))
        editor.setText("A\tBC\nD\tEF\n")
        editor.setModified(False)
        assert editor.tabWidth() == 2
        editor.SendScintilla(editor.SCI_SETRECTANGULARSELECTIONANCHOR, editor.positionFromLineIndex(0, 2))
        editor.SendScintilla(editor.SCI_SETRECTANGULARSELECTIONCARET, editor.positionFromLineIndex(1, 4))
        editor.cut()
        assert editor.text() == "A\t\nD\t\n", repr(editor.text())
        editor.undo()
        assert editor.text() == "A\tBC\nD\tEF\n"
        checks.append("two-column tabs and column cut undo")

    print("PASS: " + "\nPASS: ".join(checks))
    app.quit()


if __name__ == "__main__":
    run()
