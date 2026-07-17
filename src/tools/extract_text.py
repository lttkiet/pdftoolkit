import fitz
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.utils.file_ops import (
    info_box,
    open_pdf_path,
    page_range_from_str,
    save_text_path,
)


class ExtractTextTool(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.doc = None
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Extract Text — Pull text from selected pages."))

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
        self.extract_btn = QPushButton("Extract")
        self.extract_btn.clicked.connect(self._extract)
        self.extract_btn.setEnabled(False)
        row.addWidget(self.extract_btn)
        layout.addLayout(row)

        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        layout.addWidget(self.text_output)

        self.save_btn = QPushButton("Save to File...")
        self.save_btn.clicked.connect(self._save)
        self.save_btn.setEnabled(False)
        layout.addWidget(self.save_btn)

    def _open(self):
        path = open_pdf_path(self)
        if path:
            self.doc = fitz.open(path)
            self.info_label.setText(f"Loaded: {path} ({len(self.doc)} pages)")
            self.extract_btn.setEnabled(True)

    def _extract(self):
        if not self.doc:
            return
        range_text = self.range_input.text().strip()
        if range_text:
            pages = page_range_from_str(range_text, len(self.doc))
        else:
            pages = list(range(len(self.doc)))

        text_parts = []
        for idx in pages:
            page = self.doc[idx]
            text = page.get_text()
            text_parts.append(f"--- Page {idx + 1} ---\n{text}")

        self.text_output.setPlainText("\n\n".join(text_parts))
        self.save_btn.setEnabled(True)
        self.main_window.statusbar.showMessage(f"Extracted text from {len(pages)} pages")

    def _save(self):
        text = self.text_output.toPlainText()
        if not text:
            return
        path = save_text_path(self)
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            info_box(self, f"Text saved → {path}")
