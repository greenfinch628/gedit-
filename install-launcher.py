"""Install only the independent gedit- launcher; never replace legacy gedit."""
from pathlib import Path
import os

project = Path(__file__).resolve().parent
entry = Path.home() / ".local/share/applications/com.greenfinch628.gedit.qtprototype.desktop"
entry.parent.mkdir(parents=True, exist_ok=True)
content = f'''[Desktop Entry]
Type=Application
Name=gedit-
Comment=Independent text editor with workspace sessions and recovery
Exec="{project / 'run-prototype'}" %F
Icon={project / 'icons/app.svg'}
Terminal=false
Categories=Utility;TextEditor;Development;
StartupWMClass=gedit-qt-prototype
'''
if entry.exists() and "Independent text editor" not in entry.read_text():
    raise SystemExit("An unrelated launcher already exists at " + str(entry))
entry.write_text(content)
os.chmod(entry, 0o644)
print("Installed independent launcher:", entry)
