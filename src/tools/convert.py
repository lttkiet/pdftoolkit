import fitz
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QSpinBox, QLineEdit
)
from PySide6.QtCore import Qt
from src.utils.file_ops import (
    open_pdf_path, open_image_path, save_pdf_path, save_image_path,
    info_box, error_box, page_range_from_str
)


class ConvertTool(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.doc = None
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Convert — Export pages as images or import images into PDF."))

        # PDF to Images
        pdf_group = QVBoxLayout()
        pdf_group.addWidget(QLabel("PDF → Images"))
        row1 = QHBoxLayout()
        self.open_btn = QPushButton("Open PDF...")
        self.open_btn.clicked.connect(self._open)
        row1.addWidget(self.open_btn)
        row1.addWidget(QLabel("Pages:"))
        self.pages_input = QLineEdit()
        self.pages_input.setPlaceholderText("all")
        row1.addWidget(self.pages_input)
        row1.addWidget(QLabel("Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPEG"])
        row1.addWidget(self.format_combo)
        row1.addWidget(QLabel("DPI:"))
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setRange(72, 600)
        self.dpi_spin.setValue(150)
        row1.addWidget(self.dpi_spin)
        pdf_group.addLayout(row1)

        self.pdf_to_img_btn = QPushButton("Export Pages as Images")
        self.pdf_to_img_btn.clicked.connect(self._pdf_to_images)
        self.pdf_to_img_btn.setEnabled(False)
        pdf_group.addWidget(self.pdf_to_img_btn)
        layout.addLayout(pdf_group)

        # Images to PDF
        img_group = QVBoxLayout()
        img_group.addWidget(QLabel("Images → PDF"))
        self.img_files_label = QLabel("No images selected")
        img_row = QHBoxLayout()
        self.select_imgs_btn = QPushButton("Select Images...")
        self.select_imgs_btn.clicked.connect(self._select_images)
        img_row.addWidget(self.select_imgs_btn)
        img_row.addWidget(self.img_files_label)
        img_group.addLayout(img_row)

        self.img_to_pdf_btn = QPushButton("Create PDF from Images")
        self.img_to_pdf_btn.clicked.connect(self._images_to_pdf)
        img_group.addWidget(self.img_to_pdf_btn)
        layout.addLayout(img_group)

        layout.addStretch()

        self._img_paths: list[str] = []

    def _open(self):
        path = open_pdf_path(self)
        if path:
            self.doc = fitz.open(path)
            self.info_label_text = f"Loaded: {path} ({len(self.doc)} pages)"
            self.pdf_to_img_btn.setEnabled(True)

    def _pdf_to_images(self):
        if not self.doc:
            return
        try:
            pages_text = self.pages_input.text().strip()
            if pages_text:
                pages = page_range_from_str(pages_text, len(self.doc))
            else:
                pages = list(range(len(self.doc)))

            dpi = self.dpi_spin.value()
            zoom = dpi / 72
            mat = fitz.Matrix(zoom, zoom)
            fmt = self.format_combo.currentText().lower()

            for idx in pages:
                page = self.doc[idx]
                pix = page.get_pixmap(matrix=mat, alpha=False)
                default = f"page_{idx + 1}.{fmt if fmt != 'jpeg' else 'jpg'}"
                out = save_image_path(self, default)
                if out:
                    pix.save(out)

            info_box(self, f"Exported {len(pages)} pages as {fmt.upper()}")
            self.main_window.statusbar.showMessage(f"Exported {len(pages)} images")
        except Exception as e:
            error_box(self, str(e))

    def _select_images(self):
        from PySide6.QtWidgets import QFileDialog
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Images", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff);;All Files (*)"
        )
        if paths:
            self._img_paths = paths
            self.img_files_label.setText(f"{len(paths)} images selected")

    def _images_to_pdf(self):
        if not self._img_paths:
            error_box(self, "Select images first.")
            return
        out = save_pdf_path(self)
        if not out:
            return
        try:
            doc = fitz.open()
            for img_path in self._img_paths:
                img_doc = fitz.open(img_path)
                pdfbytes = img_doc.convert_to_pdf()
                img_pdf = fitz.open("pdf", pdfbytes)
                doc.insert_pdf(img_pdf)
                img_doc.close()
                img_pdf.close()
            doc.save(out)
            doc.close()
            info_box(self, f"Created PDF with {len(self._img_paths)} pages → {out}")
            self.main_window.statusbar.showMessage("Images converted to PDF")
        except Exception as e:
            error_box(self, str(e))
