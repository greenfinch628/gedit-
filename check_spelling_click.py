"""Spelling suggestions must follow the clicked character, not caret rounding."""
from unittest.mock import Mock, patch

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication

from enhancements import DEFAULTS, EnhancedEditor


def run():
    app = QApplication([])
    editor = EnhancedEditor(dict(DEFAULTS, spell=True))
    editor.resize(700, 240)
    editor.show()
    app.processEvents()
    assert editor.dictionary is not None
    for text in ("hello qzxqzx tail", "café qzxqzx tail", "qzxqzx tail"):
        editor.setText(text)
        editor.check_spelling()
        record = next(value for value in editor.misspellings if value[2] == "qzxqzx")
        start, end, _ = record
        x = lambda pos: editor.SendScintilla(editor.SCI_POINTXFROMPOSITION, 0, pos)
        y = editor.SendScintilla(editor.SCI_POINTYFROMPOSITION, 0, start) + editor.textHeight(0) // 2
        # Both halves of the first and last character must work. Whitespace
        # immediately outside either edge must leave the suggestions closed.
        cases = [(x(start) - 1, False), (x(start) + 1, True),
                 ((x(start) + x(start + 1)) // 2 + 1, True),
                 (x(end - 1) + 1, True), (x(end) - 1, True),
                 (x(end) + 1, False)]
        with patch.object(editor, "correction_menu", return_value=Mock()) as menu:
            for click_x, expected in cases:
                menu.reset_mock()
                QTest.mouseClick(editor.viewport(), Qt.MouseButton.LeftButton,
                                 Qt.KeyboardModifier.NoModifier, QPoint(click_x, y))
                assert menu.called == expected, (text, click_x, expected)
                if expected:
                    assert menu.call_args.args[0] == record
    editor.spell_timer.stop()
    editor.close()
    print("PASS: suggestions require clicks inside word characters, including both edge characters and Unicode prefixes")


if __name__ == "__main__":
    run()
