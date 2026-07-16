# AGENTS.md

> Instructions for AI agents working in this repository.

## Project

Offline desktop PDF toolkit built with Python + PySide6 (Qt6). Provides viewer and 10 tools: merge, split, rotate, reorder, add content, extract text, compress, watermark, encrypt/decrypt, convert, metadata editing. Uses PyMuPDF (fitz) as the PDF engine.

## Setup

```bash
pip install -r requirements.txt
```

Requires: Python 3.10+, a display server (X11/Wayland/macOS) for the GUI.

## Common Commands

```bash
python main.py              # Launch the app
```

No test suite, linter, or typecheck configured yet.

## Architecture

```
main.py                  → Entry point, creates QApplication + MainWindow
src/app.py               → MainWindow: sidebar (tool list), QStackedWidget for tool panels, toolbar
src/viewer.py            → PDFViewer widget with thumbnails + page view + zoom + nav
src/tools/*.py           → One module per tool, each exports a *Tool(QWidget) class
src/utils/file_ops.py    → Shared file dialogs, error/info boxes, page range parser
```

- Tools are lazily imported when the user clicks a sidebar item (via `importlib.import_module` in `src/app.py:100-113`).
- All tools receive a `main_window` reference to access the currently loaded PDF (`main_window.doc`) and status bar.
- PDFs are loaded once into `main_window.doc` (a `fitz.Document`); tools operate on copies and save to new files.

## Conventions

- No comments in code unless user asks.
- Each tool class is self-contained in its module — UI + logic together.
- All file I/O goes through `src/utils/file_ops.py` helpers (dialogs, error boxes).
- Page ranges use 1-indexed strings like `"1-3,5"`, parsed by `page_range_from_str()`.
