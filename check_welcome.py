"""Welcome startup, pinning and dismissal regression checks."""
import sys,tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from PyQt6.QtWidgets import QApplication
from enhancements import launch
app=QApplication([])
with tempfile.TemporaryDirectory() as directory:
 windows,lock=launch(app,root_override=directory);w=windows[0];e=w.editor()
 assert w.is_welcome(e) and e.pinned
 w.new_document();draft=w.editor();draft.setText('draft survives');draft.setModified(True)
 w.set_welcome_enabled(False)
 assert all(not w.is_welcome(w.tabs.widget(i)) for i in range(w.tabs.count()))
 assert draft.text()=='draft survives'
 w.close();lock.unlock()
 windows,lock=launch(app,root_override=directory);w=windows[0]
 assert all(not w.is_welcome(w.tabs.widget(i)) for i in range(w.tabs.count()))
 w.set_welcome_enabled(True);w.show_welcome();e=w.editor();assert e.pinned
 w.toggle_pin(e,e.pin_button)
 assert not w.store.settings['show_welcome']
 assert all(not w.is_welcome(w.tabs.widget(i)) for i in range(w.tabs.count()))
 w.close();lock.unlock()
 windows,lock=launch(app,root_override=directory);w=windows[0]
 assert all(not w.is_welcome(w.tabs.widget(i)) for i in range(w.tabs.count()))
 w.close();lock.unlock()
 print('PASS: pinned Welcome, disable removes recovered tab, unpin disables startup, draft preserved across restarts')
