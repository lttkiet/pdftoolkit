import fitz
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QFileDialog
)
from src.utils.file_ops import open_multi_pdf, save_pdf_path, info_box, error_box


class MergeTool(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Merge PDFs — Select multiple PDF files to combine into one."))
        self.file_list = QListWidget()
        layout.addWidget(self.file_list)

        btn_row = QHBoxLayout()
        self.add_btn = QPushButton("Add Files...")
        self.add_btn.clicked.connect(self._add_files)
        self.remove_btn = QPushButton("Remove Selected")
        self.remove_btn.clicked.connect(self._remove_selected)
        self.up_btn = QPushButton("Move Up")
        self.up_btn.clicked.connect(self._move_up)
        self.down_btn = QPushButton("Move Down")
        self.down_btn.clicked.connect(self._move_down)
        self.merge_btn = QPushButton("Merge")
        self.merge_btn.clicked.connect(self._merge)

        btn_row.addWidget(self.add_btn)
        btn_row.addWidget(self.remove_btn)
        btn_row.addWidget(self.up_btn)
        btn_row.addWidget(self.down_btn)
        btn_row.addStretch()
        btn_row.addWidget(self.merge_btn)
        layout.addLayout(btn_row)

        self.paths: list[str] = []

    def _add_files(self):
        paths = open_multi_pdf(self)
        for p in paths:
            if p not in self.paths:
                self.paths.append(p)
                self.file_list.addItem(p)

    def _remove_selected(self):
        row = self.file_list.currentRow()
        if row >= 0:
            self.file_list.takeItem(row)
            self.paths.pop(row)

    def _move_up(self):
        row = self.file_list.currentRow()
        if row > 0:
            self.paths[row], self.paths[row - 1] = self.paths[row - 1], self.paths[row]
            self.file_list.insertItem(row - 1, self.file_list.takeItem(row))
            self.file_list.setCurrentRow(row - 1)

    def _move_down(self):
        row = self.file_list.currentRow()
        if 0 <= row < self.file_list.count() - 1:
            self.paths[row], self.paths[row + 1] = self.paths[row + 1], self.paths[row]
            self.file_list.insertItem(row + 1, self.file_list.takeItem(row))
            self.file_list.setCurrentRow(row + 1)

    def _merge(self):
        if len(self.paths) < 2:
            error_box(self, "Add at least 2 PDF files to merge.")
            return
        out = save_pdf_path(self)
        if not out:
            return
        try:
            result = fitz.open()
            for p in self.paths:
                doc = fitz.open(p)
                result.insert_pdf(doc)
                doc.close()
            result.save(out)
            result.close()
            info_box(self, f"Merged {len(self.paths)} files → {out}")
            self.main_window.statusbar.showMessage(f"Merged {len(self.paths)} files")
        except Exception as e:
            error_box(self, str(e))
