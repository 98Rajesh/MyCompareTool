from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QTextEdit,
                               QPushButton, QFileDialog, QSplitter)
from PySide6.QtCore import Qt

BYTES_PER_ROW = 16

def to_hex_rows(data: bytes, bytes_per_row: int = BYTES_PER_ROW):
    rows = []
    for i in range(0, len(data), bytes_per_row):
        chunk = data[i:i+bytes_per_row]
        hexpart = ' '.join(f"{b:02X}" for b in chunk)
        asciipart = ''.join((chr(b) if 32 <= b <= 126 else '.') for b in chunk)
        rows.append((i, hexpart, asciipart, chunk))
    return rows

class HexDiffViewer(QWidget):
    def __init__(self, settings=None, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.left_path = None
        self.right_path = None

        layout = QVBoxLayout(self)
        ctrl = QHBoxLayout()
        self.left_btn = QPushButton("Left File…")
        self.right_btn = QPushButton("Right File…")
        self.compare_btn = QPushButton("Compare Hex")
        ctrl.addWidget(self.left_btn)
        ctrl.addWidget(self.right_btn)
        ctrl.addWidget(self.compare_btn)
        ctrl.addStretch(1)
        layout.addLayout(ctrl)

        splitter = QSplitter(Qt.Horizontal)
        self.left_view = QTextEdit()
        self.left_view.setReadOnly(True)
        self.right_view = QTextEdit()
        self.right_view.setReadOnly(True)
        splitter.addWidget(self.left_view)
        splitter.addWidget(self.right_view)
        layout.addWidget(splitter)

        self.left_btn.clicked.connect(self.pick_left)
        self.right_btn.clicked.connect(self.pick_right)
        self.compare_btn.clicked.connect(self.compare_files)

    def pick_left(self):
        p, _ = QFileDialog.getOpenFileName(self, "Choose Left File")
        if p:
            self.left_path = p
            self.left_view.setPlainText(f"{p} (not compared yet)")

    def pick_right(self):
        p, _ = QFileDialog.getOpenFileName(self, "Choose Right File")
        if p:
            self.right_path = p
            self.right_view.setPlainText(f"{p} (not compared yet)")

    def _read_bytes(self, p: str) -> bytes:
        with open(p, "rb") as f:
            return f.read()

    def compare_files(self):
        if not (self.left_path and self.right_path):
            return
        la = self._read_bytes(self.left_path)
        rb = self._read_bytes(self.right_path)
        bpr = getattr(self.settings, 'bytes_per_row', BYTES_PER_ROW) if self.settings else BYTES_PER_ROW
        left_rows = to_hex_rows(la, bpr)
        right_rows = to_hex_rows(rb, bpr)
        maxr = max(len(left_rows), len(right_rows))

        left_lines = []
        right_lines = []
        for i in range(maxr):
            l = left_rows[i] if i < len(left_rows) else (i*BYTES_PER_ROW, '', '', b'')
            r = right_rows[i] if i < len(right_rows) else (i*BYTES_PER_ROW, '', '', b'')
            l_hex = l[1].split()
            r_hex = r[1].split()
            merged_l = []
            merged_r = []
            for idx in range(max(len(l_hex), len(r_hex))):
                lh = l_hex[idx] if idx < len(l_hex) else "--"
                rh = r_hex[idx] if idx < len(r_hex) else "--"
                if lh == rh:
                    merged_l.append(lh)
                    merged_r.append(rh)
                else:
                    merged_l.append(f"[{lh}]")
                    merged_r.append(f"[{rh}]")
            left_lines.append(f"{l[0]:08X}: {' '.join(merged_l):<47} | {l[2]}")
            right_lines.append(f"{r[0]:08X}: {' '.join(merged_r):<47} | {r[2]}")

        self.left_view.setPlainText("\n".join(left_lines))
        self.right_view.setPlainText("\n".join(right_lines))
