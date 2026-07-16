import os
import fitz
from PySide6.QtWidgets import QFileDialog, QMessageBox


def open_pdf_path(parent=None) -> str | None:
    path, _ = QFileDialog.getOpenFileName(
        parent, "Open PDF", "", "PDF Files (*.pdf);;All Files (*)"
    )
    return path or None


def open_multi_pdf(parent=None) -> list[str]:
    paths, _ = QFileDialog.getOpenFileNames(
        parent, "Select PDFs", "", "PDF Files (*.pdf);;All Files (*)"
    )
    return paths


def save_pdf_path(parent=None, default_name="output.pdf") -> str | None:
    path, _ = QFileDialog.getSaveFileName(
        parent, "Save PDF", default_name, "PDF Files (*.pdf)"
    )
    return path or None


def open_image_path(parent=None) -> str | None:
    path, _ = QFileDialog.getOpenFileName(
        parent,
        "Select Image",
        "",
        "Images (*.png *.jpg *.jpeg *.bmp *.gif *.tiff);;All Files (*)",
    )
    return path or None


def save_image_path(parent=None, default_name="output.png") -> str | None:
    path, _ = QFileDialog.getSaveFileName(
        parent,
        "Save Image",
        default_name,
        "PNG (*.png);;JPEG (*.jpg);;All Files (*)",
    )
    return path or None


def save_text_path(parent=None, default_name="output.txt") -> str | None:
    path, _ = QFileDialog.getSaveFileName(
        parent, "Save Text", default_name, "Text Files (*.txt);;All Files (*)"
    )
    return path or None


def error_box(parent, msg: str):
    QMessageBox.critical(parent, "Error", msg)


def info_box(parent, msg: str):
    QMessageBox.information(parent, "PDF Toolkit", msg)


def page_range_from_str(text: str, total: int) -> list[int]:
    """Parse page range string like '1-3,5,7-9' into 0-indexed list."""
    pages = set()
    for part in text.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            start, end = int(start.strip()), int(end.strip())
            for p in range(start, end + 1):
                if 1 <= p <= total:
                    pages.add(p - 1)
        else:
            p = int(part.strip())
            if 1 <= p <= total:
                pages.add(p - 1)
    return sorted(pages)
