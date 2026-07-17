import os
import tempfile

import fitz


def test_create_pdf():
    doc = fitz.open()
    assert len(doc) == 0
    doc.close()


def test_add_page():
    doc = fitz.open()
    doc.new_page()
    assert len(doc) == 1
    doc.close()


def test_insert_text_and_retrieve():
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Hello world", fontsize=20)
    text = page.get_text()
    assert "Hello world" in text
    doc.close()


def test_insert_pdf():
    src = fitz.open()
    src.new_page()
    src.new_page()
    dst = fitz.open()
    dst.insert_pdf(src)
    assert len(dst) == 2
    src.close()
    dst.close()


def test_metadata():
    doc = fitz.open()
    doc.set_metadata({"title": "Test", "author": "Tester"})
    meta = doc.metadata
    assert meta.get("title") == "Test"
    assert meta.get("author") == "Tester"
    doc.close()


def test_page_rotation():
    doc = fitz.open()
    page = doc.new_page()
    assert page.rotation == 0
    page.set_rotation(90)
    assert page.rotation == 90
    doc.close()


def test_encrypt_decrypt():
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        tmp_path = f.name
    try:
        doc = fitz.open()
        doc.new_page()
        doc.save(tmp_path, encryption=fitz.PDF_ENCRYPT_AES_256, user_pw="secret")
        doc.close()

        doc = fitz.open(tmp_path)
        assert doc.needs_pass
        assert doc.authenticate("secret")
        doc.close()
    finally:
        os.unlink(tmp_path)


def test_page_range_from_str():
    from src.utils.file_ops import page_range_from_str

    assert page_range_from_str("1-3,5,7-9", 10) == [0, 1, 2, 4, 6, 7, 8]
    assert page_range_from_str("1,2,3", 5) == [0, 1, 2]
    assert page_range_from_str("1-1", 5) == [0]
    assert page_range_from_str("10", 5) == []
    assert page_range_from_str("", 5) == []
    assert page_range_from_str("  1 , 3-4  ", 5) == [0, 2, 3]
