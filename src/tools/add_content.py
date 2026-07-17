import fitz
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
)
from PySide6.QtGui import QColor
from src.utils.file_ops import (
    open_pdf_path,
    open_image_path,
    save_pdf_path,
    info_box,
    error_box,
    page_range_from_str,
)


class AddContentTool(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.doc = None
        layout = QVBoxLayout(self)

        layout.addWidget(
            QLabel("Add Content — Insert text or image overlays on pages.")
        )

        self.open_btn = QPushButton("Open PDF...")
        self.open_btn.clicked.connect(self._open)
        layout.addWidget(self.open_btn)

        self.info_label = QLabel("No file loaded")
        layout.addWidget(self.info_label)

        # Content type
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Text", "Image"])
        self.type_combo.currentIndexChanged.connect(self._toggle_type)
        type_row.addWidget(self.type_combo)
        type_row.addWidget(QLabel("Pages:"))
        self.pages_input = QLineEdit()
        self.pages_input.setPlaceholderText("all")
        type_row.addWidget(self.pages_input)
        layout.addLayout(type_row)

        # Text options
        self.text_widget = QWidget()
        tw = QVBoxLayout(self.text_widget)
        tw.setContentsMargins(0, 0, 0, 0)
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Enter text to add...")
        tw.addWidget(self.text_edit)

        pos_row = QHBoxLayout()
        pos_row.addWidget(QLabel("X:"))
        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, 9999)
        self.x_spin.setValue(72)
        pos_row.addWidget(self.x_spin)
        pos_row.addWidget(QLabel("Y:"))
        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, 9999)
        self.y_spin.setValue(72)
        pos_row.addWidget(self.y_spin)
        pos_row.addWidget(QLabel("Size:"))
        self.size_spin = QDoubleSpinBox()
        self.size_spin.setRange(4, 200)
        self.size_spin.setValue(12)
        pos_row.addWidget(self.size_spin)
        tw.addLayout(pos_row)

        layout.addWidget(self.text_widget)

        # Image options
        self.image_widget = QWidget()
        iw = QVBoxLayout(self.image_widget)
        iw.setContentsMargins(0, 0, 0, 0)
        self.img_path_label = QLabel("No image selected")
        self.img_select_btn = QPushButton("Select Image...")
        self.img_select_btn.clicked.connect(self._select_image)
        iw.addWidget(self.img_path_label)
        iw.addWidget(self.img_select_btn)

        ipos_row = QHBoxLayout()
        ipos_row.addWidget(QLabel("X:"))
        self.ix_spin = QSpinBox()
        self.ix_spin.setRange(0, 9999)
        self.ix_spin.setValue(72)
        ipos_row.addWidget(self.ix_spin)
        ipos_row.addWidget(QLabel("Y:"))
        self.iy_spin = QSpinBox()
        self.iy_spin.setRange(0, 9999)
        self.iy_spin.setValue(72)
        ipos_row.addWidget(self.iy_spin)
        ipos_row.addWidget(QLabel("Width:"))
        self.iw_spin = QSpinBox()
        self.iw_spin.setRange(1, 9999)
        self.iw_spin.setValue(200)
        ipos_row.addWidget(self.iw_spin)
        ipos_row.addWidget(QLabel("Height:"))
        self.ih_spin = QSpinBox()
        self.ih_spin.setRange(1, 9999)
        self.ih_spin.setValue(200)
        ipos_row.addWidget(self.ih_spin)
        iw.addLayout(ipos_row)

        self.image_widget.hide()
        layout.addWidget(self.image_widget)

        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self._apply)
        self.apply_btn.setEnabled(False)
        layout.addWidget(self.apply_btn)
        layout.addStretch()

        self._selected_image = None

    def _open(self):
        path = open_pdf_path(self)
        if path:
            self.doc = fitz.open(path)
            self.info_label.setText(f"Loaded: {path} ({len(self.doc)} pages)")
            self.apply_btn.setEnabled(True)

    def _toggle_type(self, idx):
        self.text_widget.setVisible(idx == 0)
        self.image_widget.setVisible(idx == 1)

    def _select_image(self):
        path = open_image_path(self)
        if path:
            self._selected_image = path
            self.img_path_label.setText(path)

    def _apply(self):
        if not self.doc:
            return
        out = save_pdf_path(self)
        if not out:
            return
        try:
            pages_text = self.pages_input.text().strip()
            if pages_text:
                pages = page_range_from_str(pages_text, len(self.doc))
            else:
                pages = list(range(len(self.doc)))

            new_doc = fitz.open()
            new_doc.insert_pdf(self.doc)

            if self.type_combo.currentIndex() == 0:
                text = self.text_edit.toPlainText()
                if not text:
                    error_box(self, "Enter some text.")
                    return
                for idx in pages:
                    page = new_doc[idx]
                    pos = fitz.Point(self.x_spin.value(), self.y_spin.value())
                    page.insert_text(pos, text, fontsize=self.size_spin.value())
            else:
                if not self._selected_image:
                    error_box(self, "Select an image first.")
                    return
                rect = fitz.Rect(
                    self.ix_spin.value(),
                    self.iy_spin.value(),
                    self.ix_spin.value() + self.iw_spin.value(),
                    self.iy_spin.value() + self.ih_spin.value(),
                )
                for idx in pages:
                    page = new_doc[idx]
                    page.insert_image(rect, filename=self._selected_image)

            new_doc.save(out)
            new_doc.close()
            info_box(self, f"Content added → {out}")
            self.main_window.statusbar.showMessage("Content added to PDF")
        except Exception as e:
            error_box(self, str(e))
