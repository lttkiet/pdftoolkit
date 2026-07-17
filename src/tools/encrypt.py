import fitz
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.utils.file_ops import error_box, info_box, open_pdf_path, save_pdf_path


class EncryptTool(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.doc = None
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Encrypt / Decrypt — Add or remove PDF passwords."))

        self.open_btn = QPushButton("Open PDF...")
        self.open_btn.clicked.connect(self._open)
        layout.addWidget(self.open_btn)

        self.info_label = QLabel("No file loaded")
        layout.addWidget(self.info_label)

        # Encrypt
        enc_group = QGroupBox("Encrypt PDF")
        eg = QVBoxLayout(enc_group)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("User password:"))
        self.user_pass = QLineEdit()
        self.user_pass.setEchoMode(QLineEdit.Password)
        row1.addWidget(self.user_pass)
        eg.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Owner password:"))
        self.owner_pass = QLineEdit()
        self.owner_pass.setEchoMode(QLineEdit.Password)
        row2.addWidget(self.owner_pass)
        eg.addLayout(row2)

        self.encrypt_btn = QPushButton("Encrypt")
        self.encrypt_btn.clicked.connect(self._encrypt)
        self.encrypt_btn.setEnabled(False)
        eg.addWidget(self.encrypt_btn)
        layout.addWidget(enc_group)

        # Decrypt
        dec_group = QGroupBox("Decrypt PDF")
        dg = QVBoxLayout(dec_group)

        drow = QHBoxLayout()
        drow.addWidget(QLabel("Password:"))
        self.decrypt_pass = QLineEdit()
        self.decrypt_pass.setEchoMode(QLineEdit.Password)
        drow.addWidget(self.decrypt_pass)
        dg.addLayout(drow)

        self.decrypt_btn = QPushButton("Decrypt")
        self.decrypt_btn.clicked.connect(self._decrypt)
        self.decrypt_btn.setEnabled(False)
        dg.addWidget(self.decrypt_btn)
        layout.addWidget(dec_group)

        layout.addStretch()

    def _open(self):
        path = open_pdf_path(self)
        if path:
            self.doc = fitz.open(path)
            self.info_label.setText(f"Loaded: {path} ({len(self.doc)} pages)")
            self.encrypt_btn.setEnabled(True)
            self.decrypt_btn.setEnabled(True)

    def _encrypt(self):
        if not self.doc:
            return
        out = save_pdf_path(self)
        if not out:
            return
        try:
            user = self.user_pass.text()
            owner = self.owner_pass.text()
            if not user and not owner:
                error_box(self, "Enter at least one password.")
                return

            perm = (
                fitz.PDF_PERM_ACCESSIBILITY
                | fitz.PDF_PERM_PRINT
                | fitz.PDF_PERM_COPY
                | fitz.PDF_PERM_CHANGE
            )
            new_doc = fitz.open()
            new_doc.insert_pdf(self.doc)
            new_doc.save(
                out,
                encryption=fitz.PDF_ENCRYPT_AES_256,
                user_pw=user or None,
                owner_pw=owner or None,
                permissions=perm,
            )
            new_doc.close()
            info_box(self, f"Encrypted PDF → {out}")
            self.main_window.statusbar.showMessage("PDF encrypted")
        except Exception as e:
            error_box(self, str(e))

    def _decrypt(self):
        if not self.doc:
            return
        password = self.decrypt_pass.text()
        if not password:
            error_box(self, "Enter the password.")
            return
        out = save_pdf_path(self)
        if not out:
            return
        try:
            if self.doc.is_pdf and self.doc.needs_pass:
                if not self.doc.authenticate(password):
                    error_box(self, "Wrong password.")
                    return
            new_doc = fitz.open()
            new_doc.insert_pdf(self.doc)
            new_doc.save(out)
            new_doc.close()
            info_box(self, f"Decrypted PDF → {out}")
            self.main_window.statusbar.showMessage("PDF decrypted")
        except Exception as e:
            error_box(self, str(e))
