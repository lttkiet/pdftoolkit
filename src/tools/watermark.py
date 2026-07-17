import fitz
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from src.utils.file_ops import (
    error_box,
    info_box,
    open_image_path,
    open_pdf_path,
    page_range_from_str,
    save_pdf_path,
)


class WatermarkTool(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.doc = None
        self._image_path = None
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Watermark — Add text or image watermark to pages."))

        self.open_btn = QPushButton("Open PDF...")
        self.open_btn.clicked.connect(self._open)
        layout.addWidget(self.open_btn)

        self.info_label = QLabel("No file loaded")
        layout.addWidget(self.info_label)

        # Type
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
        trow = QHBoxLayout()
        trow.addWidget(QLabel("Text:"))
        self.text_input = QLineEdit()
        self.text_input.setText("CONFIDENTIAL")
        trow.addWidget(self.text_input)
        trow.addWidget(QLabel("Size:"))
        self.font_size = QSpinBox()
        self.font_size.setRange(6, 200)
        self.font_size.setValue(50)
        trow.addWidget(self.font_size)
        tw.addLayout(trow)

        arow = QHBoxLayout()
        arow.addWidget(QLabel("Opacity:"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setValue(30)
        arow.addWidget(self.opacity_slider)
        arow.addWidget(QLabel("Angle:"))
        self.angle_slider = QSlider(Qt.Horizontal)
        self.angle_slider.setRange(-180, 180)
        self.angle_slider.setValue(-45)
        arow.addWidget(self.angle_slider)
        tw.addLayout(arow)
        layout.addWidget(self.text_widget)

        # Image options
        self.image_widget = QWidget()
        iw = QVBoxLayout(self.image_widget)
        iw.setContentsMargins(0, 0, 0, 0)
        self.img_label = QLabel("No image selected")
        self.img_btn = QPushButton("Select Image...")
        self.img_btn.clicked.connect(self._select_image)
        iw.addWidget(self.img_label)
        iw.addWidget(self.img_btn)

        irow = QHBoxLayout()
        irow.addWidget(QLabel("Opacity:"))
        self.img_opacity = QSlider(Qt.Horizontal)
        self.img_opacity.setRange(10, 100)
        self.img_opacity.setValue(30)
        irow.addWidget(self.img_opacity)
        irow.addWidget(QLabel("Width:"))
        self.img_width = QSpinBox()
        self.img_width.setRange(10, 5000)
        self.img_width.setValue(200)
        irow.addWidget(self.img_width)
        iw.addLayout(irow)
        self.image_widget.hide()
        layout.addWidget(self.image_widget)

        self.apply_btn = QPushButton("Apply Watermark")
        self.apply_btn.clicked.connect(self._apply)
        self.apply_btn.setEnabled(False)
        layout.addWidget(self.apply_btn)
        layout.addStretch()

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
            self._image_path = path
            self.img_label.setText(path)

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

            is_image = self.type_combo.currentIndex() == 1
            img_stream = None
            if is_image:
                if not self._image_path:
                    error_box(self, "Select an image first.")
                    return
                img_opacity = self.img_opacity.value() / 100
                if img_opacity < 1:
                    import io

                    from PIL import Image as PILImage

                    pil_img = PILImage.open(self._image_path).convert("RGBA")
                    alpha = pil_img.getchannel("A").point(lambda a: int(a * img_opacity))
                    pil_img.putalpha(alpha)
                    buf = io.BytesIO()
                    pil_img.save(buf, "PNG")
                    img_stream = buf.getvalue()

            new_doc = fitz.open()
            new_doc.insert_pdf(self.doc)

            for idx in pages:
                page = new_doc[idx]
                rect = page.rect
                center_x = rect.width / 2
                center_y = rect.height / 2

                if not is_image:
                    opacity = self.opacity_slider.value() / 100
                    angle = self.angle_slider.value()
                    pivot = fitz.Point(center_x, center_y)
                    page.insert_text(
                        fitz.Point(center_x - 80, center_y),
                        self.text_input.text(),
                        fontsize=self.font_size.value(),
                        morph=(pivot, fitz.Matrix(angle)),
                        color=(0.7, 0.7, 0.7),
                        overlay=True,
                        render_mode=0,
                        stroke_opacity=opacity,
                        fill_opacity=opacity,
                    )
                else:
                    w = self.img_width.value()
                    img_rect = fitz.Rect(
                        center_x - w / 2,
                        center_y - w / 4,
                        center_x + w / 2,
                        center_y + w / 4,
                    )
                    if img_stream is not None:
                        page.insert_image(img_rect, stream=img_stream, overlay=True)
                    else:
                        page.insert_image(img_rect, filename=self._image_path, overlay=True)

            new_doc.save(out)
            new_doc.close()
            info_box(self, f"Watermark applied → {out}")
            self.main_window.statusbar.showMessage("Watermark applied")
        except Exception as e:
            error_box(self, str(e))
