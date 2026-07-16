import fitz
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QCheckBox
)
from src.utils.file_ops import (
    open_pdf_path, save_pdf_path, info_box, error_box,
    page_range_from_str
)


class SplitTool(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.doc = None
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Split PDF — Extract page ranges into a new file."))
        self.open_btn = QPushButton("Open PDF...")
        self.open_btn.clicked.connect(self._open)
        layout.addWidget(self.open_btn)

        self.info_label = QLabel("No file loaded")
        layout.addWidget(self.info_label)

        row = QHBoxLayout()
        row.addWidget(QLabel("Page ranges:"))
        self.range_input = QLineEdit()
        self.range_input.setPlaceholderText("e.g. 1-3,5,7-9")
        row.addWidget(self.range_input)
        layout.addLayout(row)

        self.extract_btn = QPushButton("Extract Pages")
        self.extract_btn.clicked.connect(self._split)
        self.extract_btn.setEnabled(False)
        layout.addWidget(self.extract_btn)
        layout.addStretch()

    def _open(self):
        path = open_pdf_path(self)
        if path:
            self.doc = fitz.open(path)
            self.info_label.setText(f"Loaded: {path} ({len(self.doc)} pages)")
            self.extract_btn.setEnabled(True)

    def _split(self):
        if not self.doc:
            return
        pages = page_range_from_str(self.range_input.text(), len(self.doc))
        if not pages:
            error_box(self, "No valid pages in range.")
            return
        out = save_pdf_path(self)
        if not out:
            return
        try:
            new_doc = fitz.open()
            for idx in pages:
                new_doc.insert_pdf(self.doc, from_page=idx, to_page=idx)
            new_doc.save(out)
            new_doc.close()
            info_box(self, f"Extracted {len(pages)} pages → {out}")
            self.main_window.statusbar.showMessage(f"Split: {len(pages)} pages extracted")
        except Exception as e:
            error_box(self, str(e))
