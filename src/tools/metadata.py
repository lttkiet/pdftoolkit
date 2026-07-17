import fitz
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.utils.file_ops import error_box, info_box, open_pdf_path, save_pdf_path


class MetadataTool(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.doc = None
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Metadata — View and edit PDF properties."))

        self.open_btn = QPushButton("Open PDF...")
        self.open_btn.clicked.connect(self._open)
        layout.addWidget(self.open_btn)

        form = QFormLayout()

        self.title_edit = QLineEdit()
        self.author_edit = QLineEdit()
        self.subject_edit = QLineEdit()
        self.keywords_edit = QLineEdit()
        self.creator_edit = QLineEdit()
        self.producer_edit = QLineEdit()

        form.addRow("Title:", self.title_edit)
        form.addRow("Author:", self.author_edit)
        form.addRow("Subject:", self.subject_edit)
        form.addRow("Keywords:", self.keywords_edit)
        form.addRow("Creator:", self.creator_edit)
        form.addRow("Producer:", self.producer_edit)
        layout.addLayout(form)

        btn_row = QHBoxLayout()
        self.refresh_btn = QPushButton("Reload from PDF")
        self.refresh_btn.clicked.connect(self._load_metadata)
        self.refresh_btn.setEnabled(False)
        self.save_btn = QPushButton("Save Metadata")
        self.save_btn.clicked.connect(self._save_metadata)
        self.save_btn.setEnabled(False)
        btn_row.addWidget(self.refresh_btn)
        btn_row.addWidget(self.save_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Page info
        self.info_label = QLabel("")
        layout.addWidget(self.info_label)
        layout.addStretch()

    def _open(self):
        path = open_pdf_path(self)
        if path:
            self.doc = fitz.open(path)
            self.refresh_btn.setEnabled(True)
            self.save_btn.setEnabled(True)
            self._load_metadata()

    def _load_metadata(self):
        if not self.doc:
            return
        meta = self.doc.metadata
        self.title_edit.setText(meta.get("title", ""))
        self.author_edit.setText(meta.get("author", ""))
        self.subject_edit.setText(meta.get("subject", ""))
        self.keywords_edit.setText(meta.get("keywords", ""))
        self.creator_edit.setText(meta.get("creator", ""))
        self.producer_edit.setText(meta.get("producer", ""))
        self.info_label.setText(
            f"Pages: {len(self.doc)} | "
            f"Format: {meta.get('format', 'N/A')} | "
            f"Encrypted: {self.doc.is_encrypted}"
        )

    def _save_metadata(self):
        if not self.doc:
            return
        out = save_pdf_path(self)
        if not out:
            return
        try:
            new_doc = fitz.open()
            new_doc.insert_pdf(self.doc)
            new_doc.set_metadata(
                {
                    "title": self.title_edit.text(),
                    "author": self.author_edit.text(),
                    "subject": self.subject_edit.text(),
                    "keywords": self.keywords_edit.text(),
                    "creator": self.creator_edit.text(),
                    "producer": self.producer_edit.text(),
                }
            )
            new_doc.save(out)
            new_doc.close()
            info_box(self, f"Metadata saved → {out}")
            self.main_window.statusbar.showMessage("Metadata updated")
        except Exception as e:
            error_box(self, str(e))
