import fitz
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QComboBox
)
from src.utils.file_ops import (
    open_pdf_path, save_pdf_path, info_box, error_box,
    page_range_from_str
)


class RotateTool(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.doc = None
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Rotate Pages — Select pages and rotation angle."))
        self.open_btn = QPushButton("Open PDF...")
        self.open_btn.clicked.connect(self._open)
        layout.addWidget(self.open_btn)

        self.info_label = QLabel("No file loaded")
        layout.addWidget(self.info_label)

        row = QHBoxLayout()
        row.addWidget(QLabel("Pages:"))
        self.range_input = QLineEdit()
        self.range_input.setPlaceholderText("e.g. 1-3,5 (blank = all)")
        row.addWidget(self.range_input)
        row.addWidget(QLabel("Angle:"))
        self.angle_combo = QComboBox()
        self.angle_combo.addItems(["90°", "180°", "270°"])
        row.addWidget(self.angle_combo)
        layout.addLayout(row)

        self.rotate_btn = QPushButton("Rotate")
        self.rotate_btn.clicked.connect(self._rotate)
        self.rotate_btn.setEnabled(False)
        layout.addWidget(self.rotate_btn)
        layout.addStretch()

    def _open(self):
        path = open_pdf_path(self)
        if path:
            self.doc = fitz.open(path)
            self.info_label.setText(f"Loaded: {path} ({len(self.doc)} pages)")
            self.rotate_btn.setEnabled(True)

    def _rotate(self):
        if not self.doc:
            return
        angles = [90, 180, 270]
        angle = angles[self.angle_combo.currentIndex()]
        range_text = self.range_input.text().strip()
        if range_text:
            pages = page_range_from_str(range_text, len(self.doc))
        else:
            pages = list(range(len(self.doc)))

        out = save_pdf_path(self)
        if not out:
            return
        try:
            new_doc = fitz.open()
            new_doc.insert_pdf(self.doc)
            for idx in pages:
                new_doc[idx].set_rotation((new_doc[idx].rotation + angle) % 360)
            new_doc.save(out)
            new_doc.close()
            info_box(self, f"Rotated {len(pages)} pages by {angle}° → {out}")
            self.main_window.statusbar.showMessage(f"Rotated {len(pages)} pages")
        except Exception as e:
            error_box(self, str(e))
