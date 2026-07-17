import fitz
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.utils.file_ops import error_box, info_box, open_pdf_path, save_pdf_path


class ReorderTool(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.doc = None
        self.page_order: list[int] = []
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Reorder Pages — Drag or use buttons to rearrange page order."))
        self.open_btn = QPushButton("Open PDF...")
        self.open_btn.clicked.connect(self._open)
        layout.addWidget(self.open_btn)

        self.info_label = QLabel("No file loaded")
        layout.addWidget(self.info_label)

        self.page_list = QListWidget()
        self.page_list.setDragDropMode(QListWidget.InternalMove)
        self.page_list.setDefaultDropAction(Qt.MoveAction)
        layout.addWidget(self.page_list)

        btn_row = QHBoxLayout()
        self.up_btn = QPushButton("Move Up")
        self.up_btn.clicked.connect(self._up)
        self.down_btn = QPushButton("Move Down")
        self.down_btn.clicked.connect(self._down)
        btn_row.addWidget(self.up_btn)
        btn_row.addWidget(self.down_btn)
        btn_row.addStretch()
        self.save_btn = QPushButton("Save Reordered PDF")
        self.save_btn.clicked.connect(self._save)
        self.save_btn.setEnabled(False)
        btn_row.addWidget(self.save_btn)
        layout.addLayout(btn_row)

    def _open(self):
        path = open_pdf_path(self)
        if path:
            self.doc = fitz.open(path)
            self.page_order = list(range(len(self.doc)))
            self.info_label.setText(f"Loaded: {path} ({len(self.doc)} pages)")
            self.page_list.clear()
            for i in range(len(self.doc)):
                item = QListWidgetItem(f"Page {i + 1}")
                item.setData(Qt.UserRole, i)
                self.page_list.addItem(item)
            self.save_btn.setEnabled(True)

    def _get_order(self):
        order = []
        for i in range(self.page_list.count()):
            order.append(self.page_list.item(i).data(Qt.UserRole))
        return order

    def _up(self):
        row = self.page_list.currentRow()
        if row > 0:
            item = self.page_list.takeItem(row)
            self.page_list.insertItem(row - 1, item)
            self.page_list.setCurrentRow(row - 1)

    def _down(self):
        row = self.page_list.currentRow()
        if 0 <= row < self.page_list.count() - 1:
            item = self.page_list.takeItem(row)
            self.page_list.insertItem(row + 1, item)
            self.page_list.setCurrentRow(row + 1)

    def _save(self):
        if not self.doc:
            return
        order = self._get_order()
        out = save_pdf_path(self)
        if not out:
            return
        try:
            new_doc = fitz.open()
            for idx in order:
                new_doc.insert_pdf(self.doc, from_page=idx, to_page=idx)
            new_doc.save(out)
            new_doc.close()
            info_box(self, f"Saved reordered PDF → {out}")
            self.main_window.statusbar.showMessage("Pages reordered and saved")
        except Exception as e:
            error_box(self, str(e))
