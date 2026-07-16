import fitz
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QListWidget,
    QListWidgetItem, QStackedWidget, QToolBar, QLabel, QSplitter,
    QStatusBar, QPushButton, QFrame
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon, QPixmap

from src.viewer import PDFViewer
from src.utils.file_ops import open_pdf_path, info_box


TOOL_ITEMS = [
    ("Viewer", "Open and view PDF files"),
    ("Merge", "Combine multiple PDFs into one"),
    ("Split", "Split PDF into separate files"),
    ("Rotate", "Rotate pages by 90/180/270 degrees"),
    ("Reorder", "Drag to reorder pages"),
    ("Add Content", "Add text or image overlays"),
    ("Extract Text", "Extract text from pages"),
    ("Compress", "Reduce PDF file size"),
    ("Watermark", "Add watermark to pages"),
    ("Encrypt", "Password protect or decrypt PDFs"),
    ("Convert", "Convert between PDF and images"),
    ("Metadata", "View and edit PDF metadata"),
]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Toolkit")
        self.setMinimumSize(1100, 700)
        self.doc = None
        self.file_path = None

        self._setup_toolbar()
        self._setup_ui()
        self._setup_statusbar()

    def _setup_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)

        toolbar.addSeparator()

        zoom_in = QAction("Zoom In", self)
        zoom_in.setShortcut("Ctrl+=")
        zoom_in.triggered.connect(lambda: self.viewer.zoom_in() if hasattr(self, "viewer") else None)
        toolbar.addAction(zoom_in)

        zoom_out = QAction("Zoom Out", self)
        zoom_out.setShortcut("Ctrl+-")
        zoom_out.triggered.connect(lambda: self.viewer.zoom_out() if hasattr(self, "viewer") else None)
        toolbar.addAction(zoom_out)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(180)
        self.sidebar.setIconSize(QSize(20, 20))
        self.sidebar.currentRowChanged.connect(self._on_tool_changed)

        for name, tooltip in TOOL_ITEMS:
            item = QListWidgetItem(name)
            item.setToolTip(tooltip)
            item.setSizeHint(QSize(180, 36))
            self.sidebar.addItem(item)

        # Stacked pages
        self.stack = QStackedWidget()

        self.viewer = PDFViewer()
        self.stack.addWidget(self.viewer)

        # Tool panels will be added lazily
        self.tool_widgets: dict[int, QWidget] = {}
        self._tool_modules = {
            1: ("src.tools.merge", "MergeTool"),
            2: ("src.tools.split", "SplitTool"),
            3: ("src.tools.rotate", "RotateTool"),
            4: ("src.tools.reorder", "ReorderTool"),
            5: ("src.tools.add_content", "AddContentTool"),
            6: ("src.tools.extract_text", "ExtractTextTool"),
            7: ("src.tools.compress", "CompressTool"),
            8: ("src.tools.watermark", "WatermarkTool"),
            9: ("src.tools.encrypt", "EncryptTool"),
            10: ("src.tools.convert", "ConvertTool"),
            11: ("src.tools.metadata", "MetadataTool"),
        }

        # Splitter for sidebar + content
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.stack)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter)

        self.sidebar.setCurrentRow(0)

    def _setup_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready — open a PDF to get started")

    def open_file(self):
        path = open_pdf_path(self)
        if not path:
            return
        try:
            self.doc = fitz.open(path)
            self.file_path = path
            self.viewer.load_document(self.doc)
            self.statusbar.showMessage(f"{path} — {len(self.doc)} pages")
        except Exception as e:
            info_box(self, f"Failed to open PDF:\n{e}")

    def _on_tool_changed(self, row: int):
        if row == 0:
            self.stack.setCurrentWidget(self.viewer)
            return

        if row not in self.tool_widgets:
            mod_path, cls_name = self._tool_modules[row]
            import importlib
            mod = importlib.import_module(mod_path)
            cls = getattr(mod, cls_name)
            widget = cls(self)
            self.tool_widgets[row] = widget
            self.stack.addWidget(widget)

        self.stack.setCurrentWidget(self.tool_widgets[row])
