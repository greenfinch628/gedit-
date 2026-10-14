"""Asynchronous read-only Git badges for the native folder model."""
from pathlib import Path
import subprocess

from PyQt6.QtCore import QObject, QRunnable, QThreadPool, QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QFontDatabase, QFileSystemModel


def git_status(folder):
    try:
        prefix = ["git", "--no-pager", "--no-optional-locks", "-C", str(folder)]
        repository = subprocess.run(prefix + ["rev-parse", "--show-toplevel"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=5)
        if repository.returncode:
            return {}
        repository_root = Path(repository.stdout.decode("utf-8", errors="surrogateescape").rstrip("\n"))
        result = subprocess.run(prefix + ["status", "--porcelain=v1", "-z", "--untracked-files=all"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        return {}
    if result.returncode:
        return {}
    fields = result.stdout.split(b"\0")
    statuses = {}
    index = 0
    while index < len(fields):
        field = fields[index]
        index += 1
        if len(field) < 4:
            continue
        status = field[:2].decode("ascii")
        path = field[3:].decode("utf-8", errors="surrogateescape")
        if "R" in status or "C" in status:
            index += 1  # NUL-delimited porcelain gives the destination then source.
        symbol = "!" if "U" in status or status in ("AA", "DD") else "?" if status == "??" else next((code for code in "DRCATM" if code in status), "")
        full_path = repository_root / path
        if Path(folder) not in full_path.parents and full_path != Path(folder):
            continue
        statuses[str(full_path)] = symbol
        parent = full_path.parent
        while parent != Path(folder) and Path(folder) in parent.parents:
            statuses.setdefault(str(parent), symbol)
            parent = parent.parent
    return statuses


class Signals(QObject):
    ready = pyqtSignal(int, object)


class Scan(QRunnable):
    def __init__(self, folder, generation, signals):
        super().__init__()
        self.folder, self.generation, self.signals = folder, generation, signals

    def run(self):
        statuses = git_status(self.folder)
        try:
            self.signals.ready.emit(self.generation, statuses)
        except RuntimeError:
            pass  # The owning window has closed.


class GitModel(QFileSystemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.statuses = {}
        self.folder = None
        self.enabled = True
        self.generation = 0
        self.running = False
        self.signals = Signals(self)
        self.signals.ready.connect(self.finished)
        self.timer = QTimer(self)
        self.timer.setInterval(3000)
        self.timer.timeout.connect(self.scan)
        self.timer.start()
        self.setReadOnly(True)

    def setRootPath(self, path):
        self.folder = Path(path)
        self.generation += 1
        self.statuses = {}
        index = super().setRootPath(path)
        self.scan()
        return index

    def scan(self):
        if self.enabled and self.folder and not self.running:
            self.running = True
            QThreadPool.globalInstance().start(Scan(self.folder, self.generation, self.signals))

    def finished(self, generation, statuses):
        self.running = False
        if generation != self.generation:
            self.scan()
            return
        self.statuses = statuses if self.enabled else {}
        self.layoutChanged.emit()

    def set_enabled(self, enabled):
        self.enabled = enabled
        if not enabled:
            self.statuses = {}
            self.layoutChanged.emit()
        else:
            self.scan()

    def hasChildren(self, parent):
        if parent.isValid() and Path(self.filePath(parent)).is_symlink():
            return False
        return super().hasChildren(parent)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        symbol = self.statuses.get(self.filePath(index)) if self.enabled else None
        if index.column() == 1:
            if role == Qt.ItemDataRole.DisplayRole:
                return symbol or ""
            if role == Qt.ItemDataRole.TextAlignmentRole:
                return Qt.AlignmentFlag.AlignCenter
            if role == Qt.ItemDataRole.ForegroundRole and symbol:
                return QColor("#c01c28" if symbol in ("!", "D") else "#24853b" if symbol == "A" else "#986a00")
            if role == Qt.ItemDataRole.FontRole:
                font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
                owner = QObject.parent(self)
                if owner and hasattr(owner, "sidebar"):
                    font.setPointSizeF(max(8.25, owner.sidebar.font().pointSizeF() - 1.5))
                font.setWeight(QFont.Weight.DemiBold)
                return font
            if role == Qt.ItemDataRole.ToolTipRole and symbol:
                return self.filePath(index) + "\nGit: " + symbol
            return None
        value = super().data(index, role)
        if index.column() == 0 and symbol and role == Qt.ItemDataRole.ToolTipRole:
            return self.filePath(index) + "\nGit: " + symbol
        return value
