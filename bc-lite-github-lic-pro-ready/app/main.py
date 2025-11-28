#!/usr/bin/env python3
import sys, os, argparse
from pathlib import Path

import chardet
from PySide6.QtWidgets import (QApplication, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QFileDialog, QTreeWidget, QTreeWidgetItem, QTextEdit, QLabel,
                               QComboBox, QMessageBox, QLineEdit, QDialog, QDialogButtonBox)
from PySide6.QtCore import Qt

from diff import myers_diff
from folder_compare import compare_dirs
from three_way_merge import merge_text
from hex_viewer import HexDiffViewer
from licensing import check_license
from settings import AppSettings, load_settings, save_settings
from syntax import CodeHighlighter, detect_language_from_suffix

# Edition detection:
# - Default: Lite
# - Override by environment variable BC_LITE_EDITION (e.g. 'pro' in Pro builds)
EDITION = os.getenv("BC_LITE_EDITION", "pro").lower()
if EDITION == "pro":
    APP_TITLE = "BC-Lite Pro"
else:
    APP_TITLE = "BC-Lite"



class FileDiffWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        self.left_btn = QPushButton("Left File…")
        self.right_btn = QPushButton("Right File…")
        self.compare_btn = QPushButton("Compare")
        top.addWidget(self.left_btn)
        top.addWidget(self.right_btn)
        top.addStretch(1)
        top.addWidget(self.compare_btn)

        self.left_path = QLineEdit()
        self.right_path = QLineEdit()
        self.left_path.setPlaceholderText("Left file path…")
        self.right_path.setPlaceholderText("Right file path…")
        path_row = QHBoxLayout()
        path_row.addWidget(self.left_path)
        path_row.addWidget(self.right_path)

        # Side-by-side views for syntax-highlighted diff
        views_row = QHBoxLayout()
        self.left_view = QTextEdit()
        self.right_view = QTextEdit()
        self.left_view.setReadOnly(True)
        self.right_view.setReadOnly(True)
        views_row.addWidget(self.left_view)
        views_row.addWidget(self.right_view)

        layout.addLayout(top)
        layout.addLayout(path_row)
        layout.addLayout(views_row)

        self.left_btn.clicked.connect(self.pick_left)
        self.right_btn.clicked.connect(self.pick_right)
        self.compare_btn.clicked.connect(self.do_compare)

        self.left_highlighter = None
        self.right_highlighter = None

    def pick_left(self):
        p, _ = QFileDialog.getOpenFileName(self, "Choose Left File")
        if p:
            self.left_path.setText(p)

    def pick_right(self):
        p, _ = QFileDialog.getOpenFileName(self, "Choose Right File")
        if p:
            self.right_path.setText(p)

    def _read_text(self, p: str) -> str:
        with open(p, "rb") as f:
            raw = f.read()
        try:
            det = chardet.detect(raw)
            return raw.decode(det.get("encoding") or "utf-8", errors="replace")
        except Exception:
            return raw.decode("utf-8", errors="replace")

    def do_compare(self):
        l = self.left_path.text().strip()
        r = self.right_path.text().strip()
        if not (l and r and os.path.isfile(l) and os.path.isfile(r)):
            QMessageBox.warning(self, "Error", "Please pick two files to compare.")
            return
        try:
            with open(l, "rb") as fl, open(r, "rb") as fr:
                if b"\0" in fl.read(8192) or b"\0" in fr.read(8192):
                    self.left_view.setPlainText("Binary file detected. Use Hex Diff tab.")
                    self.right_view.setPlainText("Binary file detected. Use Hex Diff tab.")
                    return
        except Exception as e:
            self.left_view.setPlainText(f"Error: {e}")
            self.right_view.setPlainText(f"Error: {e}")
            return

        a_lines = self._read_text(l).splitlines()
        b_lines = self._read_text(r).splitlines()
        diff = myers_diff(a_lines, b_lines)

        left_aligned = []
        right_aligned = []
        for tag, line in diff:
            if tag == " ":
                left_aligned.append(line)
                right_aligned.append(line)
            elif tag == "-":
                left_aligned.append(line)
                right_aligned.append("")
            else:
                left_aligned.append("")
                right_aligned.append(line)

        self.left_view.setPlainText("\n".join(left_aligned))
        self.right_view.setPlainText("\n".join(right_aligned))

        # Apply syntax highlighting based on file extension
        suffix = Path(l).suffix
        lang = detect_language_from_suffix(suffix)

        self.left_highlighter = CodeHighlighter(self.left_view.document(), lang)
        self.right_highlighter = CodeHighlighter(self.right_view.document(), lang)

class FolderCompareWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        ctrl = QHBoxLayout()
        self.left_btn = QPushButton("Left Folder…")
        self.right_btn = QPushButton("Right Folder…")
        self.left_path = QLineEdit()
        self.right_path = QLineEdit()
        self.mode = QComboBox()
        self.mode.addItems(["size_time", "content"])
        self.hash_check = QComboBox()
        self.hash_check.addItems(["no-hash", "sha256"])
        self.run_btn = QPushButton("Compare")
        for w in (self.left_btn, self.left_path, self.right_btn, self.right_path,
                  QLabel("Mode:"), self.mode, QLabel("Hash:"), self.hash_check, self.run_btn):
            ctrl.addWidget(w)
        layout.addLayout(ctrl)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["RelPath", "Left Size", "Right Size", "Status"])
        layout.addWidget(self.tree)

        self.left_btn.clicked.connect(self.pick_left)
        self.right_btn.clicked.connect(self.pick_right)
        self.run_btn.clicked.connect(self.run_compare)

    def pick_left(self):
        d = QFileDialog.getExistingDirectory(self, "Choose Left Folder")
        if d:
            self.left_path.setText(d)

    def pick_right(self):
        d = QFileDialog.getExistingDirectory(self, "Choose Right Folder")
        if d:
            self.right_path.setText(d)

    def run_compare(self):
        l = self.left_path.text().strip()
        r = self.right_path.text().strip()
        if not (l and r and os.path.isdir(l) and os.path.isdir(r)):
            QMessageBox.warning(self, "Error", "Please pick two folders to compare.")
            return
        do_hash = (self.hash_check.currentText() == "sha256")
        rows = compare_dirs(l, r, self.mode.currentText(), do_hash=do_hash)
        self.tree.clear()
        for row in rows:
            it = QTreeWidgetItem([row["relpath"], str(row["left_size"]), str(row["right_size"]), row["status"]])
            self.tree.addTopLevelItem(it)

class MergeDialog(QDialog):
    def __init__(self, local_path, remote_path, base_path=None, merged_path=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("BC-Lite - Merge")
        self.local_path = local_path
        self.remote_path = remote_path
        self.base_path = base_path
        self.merged_path = merged_path
        self.saved = False

        layout = QVBoxLayout(self)
        info = QLabel(f"Local: {local_path}\nRemote: {remote_path}\nBase: {base_path or '<none>'}\nMerged: {merged_path}")
        layout.addWidget(info)

        self.editor = QTextEdit()
        layout.addWidget(self.editor, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.on_save)
        buttons.rejected.connect(self.on_cancel)
        layout.addWidget(buttons)

        base_text = ""
        try:
            if self.base_path and os.path.isfile(self.base_path):
                base_text = Path(self.base_path).read_text(encoding="utf-8", errors="ignore")
        except Exception:
            base_text = ""
        try:
            local_text = Path(self.local_path).read_text(encoding="utf-8", errors="ignore")
        except Exception:
            local_text = ""
        try:
            remote_text = Path(self.remote_path).read_text(encoding="utf-8", errors="ignore")
        except Exception:
            remote_text = ""

        try:
            merged = merge_text(base_text, local_text, remote_text)
        except Exception:
            merged = local_text

        self.editor.setPlainText(merged)

    def on_save(self):
        if not self.merged_path:
            QMessageBox.warning(self, "Error", "No merged output path provided.")
            return
        try:
            Path(self.merged_path).write_text(self.editor.toPlainText(), encoding="utf-8", errors="ignore")
            self.saved = True
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Save failed", f"Failed to write merged file: {e}")

    def on_cancel(self):
        self.saved = False
        self.reject()

class SettingsDialog(QDialog):
    def __init__(self, settings: AppSettings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self._settings = settings

        layout = QVBoxLayout(self)

        # Theme (placeholder for future dark/light modes)
        theme_row = QHBoxLayout()
        theme_row.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["system", "light", "dark"])
        self.theme_combo.setCurrentText(self._settings.theme)
        theme_row.addWidget(self.theme_combo)
        layout.addLayout(theme_row)

        # Ignore whitespace
        self.ignore_ws = QCheckBox("Ignore whitespace in text diff (future)")
        self.ignore_ws.setChecked(self._settings.ignore_whitespace)
        layout.addWidget(self.ignore_ws)

        # Hex bytes per row
        hex_row = QHBoxLayout()
        hex_row.addWidget(QLabel("Hex bytes per row:"))
        self.bpr_spin = QSpinBox()
        self.bpr_spin.setRange(4, 64)
        self.bpr_spin.setValue(self._settings.bytes_per_row)
        hex_row.addWidget(self.bpr_spin)
        layout.addLayout(hex_row)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_settings(self) -> AppSettings:
        return self._settings

    def accept(self):
        self._settings.theme = self.theme_combo.currentText()
        self._settings.ignore_whitespace = self.ignore_ws.isChecked()
        self._settings.bytes_per_row = self.bpr_spin.value()
        save_settings(self._settings)
        super().accept()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        layout = QVBoxLayout(self)

        self.settings = load_settings()

        # Top bar with settings button
        top_bar = QHBoxLayout()
        top_bar.addStretch(1)
        self.settings_btn = QPushButton("Settings…")
        top_bar.addWidget(self.settings_btn)
        layout.addLayout(top_bar)

        self.tabs = QTabWidget()
        self.folder_tab = FolderCompareWidget()
        self.file_tab = FileDiffWidget()
        self.hex_tab = HexDiffViewer(settings=self.settings)
        self.tabs.addTab(self.folder_tab, "Folder Compare")
        self.tabs.addTab(self.file_tab, "File Diff")
        self.tabs.addTab(self.hex_tab, "Hex Diff")
        layout.addWidget(self.tabs)

        self.settings_btn.clicked.connect(self.show_settings)

    def show_settings(self):
        dlg = SettingsDialog(self.settings, self)
        if dlg.exec():
            self.settings = dlg.get_settings()
            # Update hex viewer bytes-per-row on next compare (already uses settings)

    def open_diff(self, left, right):
        self.file_tab.left_path.setText(left)
        self.file_tab.right_path.setText(right)
        self.file_tab.do_compare()
        idx = self.tabs.indexOf(self.file_tab)
        if idx >= 0:
            self.tabs.setCurrentIndex(idx)

def parse_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--git-diff", nargs=2, help="Open BC-Lite showing a diff between two files")
    parser.add_argument("--git-merge", action="store_true", help="Open merge mode (blocking)")
    parser.add_argument("--local", help="Local file (for merge)")
    parser.add_argument("--remote", help="Remote file (for merge)")
    parser.add_argument("--base", help="Base file (for merge)")
    parser.add_argument("--merged", help="Merged output path (for merge)")
    args, _ = parser.parse_known_args()
    out = {}
    if args.git_diff:
        out["git_diff"] = args.git_diff
    if args.git_merge:
        out["git_merge"] = True
        out["local"] = args.local
        out["remote"] = args.remote
        out["base"] = args.base
        out["merged"] = args.merged
    return out

def run_gui_with_args(cli_args):
    # For Pro edition, enforce license/trial
    if EDITION == 'pro':
        ok, msg = check_license('pro')
        if not ok:
            print(f'License error: {msg}', file=sys.stderr)
            QMessageBox.critical(None, 'License error', msg)
            return 1
        else:
            print(msg)

    app = QApplication(sys.argv)

    if cli_args.get("git_merge"):
        local = cli_args.get("local")
        remote = cli_args.get("remote")
        base = cli_args.get("base")
        merged = cli_args.get("merged")
        if not (local and remote and merged):
            print("git-merge: missing required file paths", file=sys.stderr)
            return 1
        dlg = MergeDialog(local, remote, base, merged)
        dlg.exec()
        return 0 if dlg.saved else 1

    w = MainWindow()
    w.resize(1100, 700)
    if cli_args.get("git_diff"):
        left, right = cli_args["git_diff"]
        w.open_diff(left, right)
    w.show()
    app.exec()
    return 0

if __name__ == "__main__":
    cli_args = parse_cli()
    rc = run_gui_with_args(cli_args)
    sys.exit(rc)
