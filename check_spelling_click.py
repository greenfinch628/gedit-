"""Suggestions require an insertion position strictly inside a misspelled word."""
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
    cases = [(text, "qzxqzx") for text in (
        "hello qzxqzx tail", "café qzxqzx tail", "qzxqzx tail",
        "hello qzxqzx", "qzxqzx", "hello\nqzxqzx\ntail",
        "hello\ncafé qzxqzx", "qzxqzx\ntail")]
    # Control dictionary acceptance to exercise one- and two-letter words too.
    cases += [(word, word) for word in ("q", "qz", "éq")]
    clicks = 0
    for text, word in cases:
        editor.setText(text)
        with patch.object(editor.dictionary, "check", side_effect=lambda value: value != word):
            editor.check_spelling()
            record = next(value for value in editor.misspellings if value[2] == word)
            start, end, _ = record
            # Every valid insertion boundary, including multibyte letters.
            positions = [start + len(word[:i].encode("utf-8")) for i in range(len(word) + 1)]
            with patch.object(editor, "correction_menu", return_value=Mock()) as menu:
                for position in positions:
                    x = editor.SendScintilla(editor.SCI_POINTXFROMPOSITION, 0, position)
                    y = editor.SendScintilla(editor.SCI_POINTYFROMPOSITION, 0, position) + editor.textHeight(editor.lineIndexFromPosition(position)[0]) // 2
                    # Sample both sides of the insertion point, including pixels
                    # inside the first/last glyph that round to an outer boundary.
                    for click_x in ((x, x + 1) if editor.lineIndexFromPosition(position)[1] == 0 else (x - 1, x, x + 1)):
                        menu.reset_mock()
                        QTest.mouseClick(editor.viewport(), Qt.MouseButton.LeftButton,
                                         Qt.KeyboardModifier.NoModifier, QPoint(click_x, y))
                        caret = editor.SendScintilla(editor.SCI_GETCURRENTPOS)
                        assert caret == position, (text, position, click_x, caret)
                        assert menu.called == (start < position < end), (text, position, menu.called)
                        assert not editor.hasSelectedText()
                        assert editor.text() == text
                        if menu.called:
                            assert menu.call_args.args[0] == record
                        clicks += 1
    editor.spell_timer.stop()
    editor.close()
    print(f"PASS: {clicks} real clicks preserve caret placement and require strict word interiors, including short words, Unicode and line/document boundaries")


if __name__ == "__main__":
    run()
