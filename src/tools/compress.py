import fitz
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QSpinBox, QSlider, QCheckBox
)
from PySide6.QtCore import Qt
from src.utils.file_ops import open_pdf_path, save_pdf_path, info_box, error_box


class CompressTool(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.doc = None
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Compress PDF — Reduce file size by optimizing images and structure."))

        self.open_btn = QPushButton("Open PDF...")
        self.open_btn.clicked.connect(self._open)
        layout.addWidget(self.open_btn)

        self.info_label = QLabel("No file loaded")
        layout.addWidget(self.info_label)

        row = QHBoxLayout()
        row.addWidget(QLabel("Image quality:"))
        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setRange(10, 100)
        self.quality_slider.setValue(50)
        self.quality_slider.setTickPosition(QSlider.TicksBelow)
        self.quality_slider.setTickInterval(10)
        row.addWidget(self.quality_slider)
        self.quality_label = QLabel("50")
        self.quality_slider.valueChanged.connect(
            lambda v: self.quality_label.setText(str(v))
        )
        row.addWidget(self.quality_label)
        layout.addLayout(row)

        self.garbage_check = QCheckBox("Remove unused objects (garbage collection)")
        self.garbage_check.setChecked(True)
        layout.addWidget(self.garbage_check)

        self.compress_btn = QPushButton("Compress")
        self.compress_btn.clicked.connect(self._compress)
        self.compress_btn.setEnabled(False)
        layout.addWidget(self.compress_btn)

        self.result_label = QLabel("")
        layout.addWidget(self.result_label)
        layout.addStretch()

    def _open(self):
        path = open_pdf_path(self)
        if path:
            self.doc = fitz.open(path)
            size_mb = self.doc.stream.tell() if hasattr(self.doc, 'stream') else 0
            self.info_label.setText(f"Loaded: {path} ({len(self.doc)} pages)")
            self.compress_btn.setEnabled(True)

    def _compress(self):
        if not self.doc:
            return
        out = save_pdf_path(self)
        if not out:
            return
        try:
            quality = self.quality_slider.value()
            garbage = 3 if self.garbage_check.isChecked() else 0

            new_doc = fitz.open()
            new_doc.insert_pdf(self.doc)

            for page in new_doc:
                images = page.get_images(full=True)
                for img in images:
                    xref = img[0]
                    try:
                        base_image = new_doc.extract_image(xref)
                        if not base_image:
                            continue
                        image_bytes = base_image["image"]
                        ext = base_image["ext"]
                        if ext not in ("png", "jpeg", "jpg"):
                            continue
                        import io
                        from PIL import Image as PILImage
                        pil_img = PILImage.open(io.BytesIO(image_bytes))
                        if pil_img.mode == "RGBA":
                            pil_img = pil_img.convert("RGB")
                        buf = io.BytesIO()
                        pil_img.save(buf, format="JPEG", quality=quality, optimize=True)
                        page.replace_image(
                            xref,
                            stream=buf.getvalue(),
                        )
                    except Exception:
                        continue

            new_doc.save(
                out,
                garbage=garbage,
                deflate=True,
                clean=True,
            )
            new_doc.close()

            import os
            orig_size = os.path.getsize(self.doc.name) if self.doc.name else 0
            new_size = os.path.getsize(out)
            if orig_size > 0:
                pct = (1 - new_size / orig_size) * 100
                self.result_label.setText(
                    f"Original: {orig_size/1024:.1f} KB → Compressed: {new_size/1024:.1f} KB "
                    f"({pct:.1f}% reduction)"
                )
            else:
                self.result_label.setText(f"Saved: {new_size/1024:.1f} KB")
            info_box(self, f"Compressed PDF → {out}")
            self.main_window.statusbar.showMessage("PDF compressed")
        except Exception as e:
            error_box(self, str(e))
