# AGENTS.md

## Project

Offline desktop PDF toolkit built with Python + PySide6 (Qt6). Provides PDF viewer and 11 tools: merge, split, rotate, reorder, add content, extract text, compress, watermark, encrypt/decrypt, convert, metadata editing. Uses PyMuPDF (fitz) as the PDF engine.

## Setup

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt   # dev: pytest, ruff, mypy, PyInstaller
```

Requires Python 3.10+ and a display server (X11/Wayland/macOS) for GUI use. On Linux CI (headless), Qt system libs must be installed (see `.github/workflows/build.yml`).

## Launch

```bash
python main.py
```

## Build Chain

| Command | Purpose |
|---|---|
| `ruff check .` | Lint |
| `ruff format --check .` | Format check |
| `mypy src/` | Type check (src/ only) |
| `pytest -v` | Run tests |
| `pyinstaller PDFToolkit.spec` | Package into executable |

CI runs lint → typecheck → test (Python 3.10–3.13) → package in sequence. See `.github/workflows/build.yml`.

## Architecture

```
main.py                    → Entry point, creates QApplication + MainWindow
src/app.py                 → MainWindow: sidebar (TOOL_ITEMS), QStackedWidget, QToolBar
src/viewer.py              → PDFViewer: ThumbnailList + scrollable page view + zoom/nav
src/tools/*.py             → One module per tool, each exports an *Tool(QWidget) class
src/utils/file_ops.py      → Shared file dialogs, error/info boxes, page_range_from_str()
```

- Tools are lazily imported when the sidebar item is clicked (`importlib.import_module` in `src/app.py:140-143`).
- Each tool receives a `main_window` reference to access the loaded PDF (`main_window.doc`, a `fitz.Document`) and `main_window.statusbar`.
- PDFs are loaded once into `main_window.doc`; tools operate on copies and save to new files.
- Tool modules use snake_case filenames (e.g. `add_content.py`), classes use PascalCase (e.g. `AddContentTool`).

## Conventions

- No comments in code unless user asks.
- Each tool class is self-contained — UI + logic in one module.
- All file I/O goes through `src/utils/file_ops.py` helpers (dialogs, error/info boxes).
- Page ranges use 1-indexed strings like `"1-3,5"`; `page_range_from_str()` returns a 0-indexed int list.
