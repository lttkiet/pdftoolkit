def test_main_import():
    import main  # noqa: F401


def test_main_function():
    from main import main  # noqa: F401


def test_app_import():
    from src.app import TOOL_ITEMS, MainWindow  # noqa: F401


def test_viewer_import():
    from src.viewer import PDFViewer, ThumbnailList  # noqa: F401


def test_all_tool_imports():
    from src.tools.add_content import AddContentTool  # noqa: F401
    from src.tools.compress import CompressTool  # noqa: F401
    from src.tools.convert import ConvertTool  # noqa: F401
    from src.tools.encrypt import EncryptTool  # noqa: F401
    from src.tools.extract_text import ExtractTextTool  # noqa: F401
    from src.tools.merge import MergeTool  # noqa: F401
    from src.tools.metadata import MetadataTool  # noqa: F401
    from src.tools.reorder import ReorderTool  # noqa: F401
    from src.tools.rotate import RotateTool  # noqa: F401
    from src.tools.split import SplitTool  # noqa: F401
    from src.tools.watermark import WatermarkTool  # noqa: F401


def test_file_ops_import():
    from src.utils.file_ops import (  # noqa: F401
        error_box,
        info_box,
        open_image_path,
        open_multi_pdf,
        open_pdf_path,
        page_range_from_str,
        save_image_path,
        save_pdf_path,
        save_text_path,
    )


def test_tool_count():
    from src.app import TOOL_ITEMS

    assert len(TOOL_ITEMS) == 12
