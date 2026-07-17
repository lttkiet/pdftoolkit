import fitz
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QWidget,
)


class ThumbnailList(QWidget):
    page_selected = Signal(int)

    def __init__(self):
        super().__init__()
        self.setFixedWidth(150)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(120, 160))
        self.list_widget.currentRowChanged.connect(self._on_select)
        layout.addWidget(self.list_widget)

        self.doc = None

    def load(self, doc):
        self.doc = doc
        self.list_widget.clear()
        if not doc:
            return
        for i in range(len(doc)):
            page = doc[i]
            pix = page.get_pixmap(matrix=fitz.Matrix(0.25, 0.25))
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(img)
            item = QListWidgetItem(f"Page {i + 1}")
            item.setIcon(pixmap)
            item.setSizeHint(QSize(130, 180))
            self.list_widget.addItem(item)

    def _on_select(self, row):
        if row >= 0:
            self.page_selected.emit(row)


class PDFViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.doc = None
        self.current_page = 0
        self.zoom_level = 1.5

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Thumbnails
        self.thumbnails = ThumbnailList()
        self.thumbnails.page_selected.connect(self._go_to_page)

        # Main page view
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.page_label = QLabel("No document loaded")
        self.page_label.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.page_label)

        # Navigation
        nav = QWidget()
        nav_layout = QHBoxLayout(nav)
        nav_layout.setContentsMargins(4, 4, 4, 4)

        self.btn_prev = QPushButton("< Prev")
        self.btn_prev.clicked.connect(self.prev_page)
        self.page_indicator = QLabel("0 / 0")
        self.page_indicator.setAlignment(Qt.AlignCenter)
        self.btn_next = QPushButton("Next >")
        self.btn_next.clicked.connect(self.next_page)

        self.zoom_out_btn = QPushButton("-")
        self.zoom_out_btn.setFixedWidth(30)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.setFixedWidth(30)
        self.zoom_in_btn.clicked.connect(self.zoom_in)

        nav_layout.addWidget(self.btn_prev)
        nav_layout.addWidget(self.page_indicator)
        nav_layout.addWidget(self.btn_next)
        nav_layout.addSpacing(20)
        nav_layout.addWidget(self.zoom_out_btn)
        nav_layout.addWidget(self.zoom_in_btn)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(self.scroll_area, 1)
        right_layout.addWidget(nav)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.thumbnails)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        main_layout.addWidget(splitter)

    def load_document(self, doc):
        self.doc = doc
        self.current_page = 0
        self.thumbnails.load(doc)
        self._render_page()

    def _render_page(self):
        if not self.doc:
            return
        page = self.doc[self.current_page]
        mat = fitz.Matrix(self.zoom_level, self.zoom_level)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(img)
        self.page_label.setPixmap(pixmap)
        self.page_indicator.setText(f"{self.current_page + 1} / {len(self.doc)}")
        self.thumbnails.list_widget.setCurrentRow(self.current_page)

    def _go_to_page(self, page_num: int):
        self.current_page = page_num
        self._render_page()

    def prev_page(self):
        if self.doc and self.current_page > 0:
            self.current_page -= 1
            self._render_page()

    def next_page(self):
        if self.doc and self.current_page < len(self.doc) - 1:
            self.current_page += 1
            self._render_page()

    def zoom_in(self):
        self.zoom_level = min(5.0, self.zoom_level * 1.2)
        self._render_page()

    def zoom_out(self):
        self.zoom_level = max(0.3, self.zoom_level / 1.2)
        self._render_page()
