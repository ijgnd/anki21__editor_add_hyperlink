import json

from aqt.qt import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    Qt,
    QVBoxLayout,
)
from aqt.utils import (
    saveGeom,
    restoreGeom,
)

from .config import gc
from .helper_functions import (
    combine_to_hyperlink,
    escape_html_chars,
    some_percent_encoding,
)


class Hyperlink(QDialog):
    def __init__(self, editor, parent_window, selected_visible_text, selected_is_url=False):
        QDialog.__init__(self, parent_window, Qt.Window)
        self.editor_instance = editor
        self.parent_window = parent_window
        self.visible_text = selected_visible_text
        self.selected_is_url = selected_is_url
        self.setWindowTitle("Anki: Create a hyperlink")
        self.resize(500, 200)
        restoreGeom(self, "318752047__add_hyperlink")

        self.pb_ok = QPushButton("&OK", self)
        self.pb_ok.setEnabled(False)
        self.pb_ok.clicked.connect(self.store_hyperlink_and_close)

        self.pb_cancel = QPushButton("&Cancel", self)
        self.pb_cancel.clicked.connect(self.reject)

        self.url_label = QLabel("Link to:")
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("URL")
        self.url_edit.textChanged.connect(self.maybe_enable_ok_button)

        self.text_label = QLabel("Text to display:")
        self.text_edit = QLineEdit()
        self.text_edit.setPlaceholderText("Text")
        self.text_edit.textChanged.connect(self.maybe_enable_ok_button)

        self.button_bar = QHBoxLayout()
        self.button_bar.addStretch(1)
        self.button_bar.addWidget(self.pb_cancel)
        self.button_bar.addWidget(self.pb_ok)

        self.dialog_vbox = QVBoxLayout()
        self.dialog_vbox.addWidget(self.url_label)
        self.dialog_vbox.addWidget(self.url_edit)
        self.dialog_vbox.addWidget(self.text_label)
        self.dialog_vbox.addWidget(self.text_edit)
        self.dialog_vbox.addLayout(self.button_bar)
        self.setLayout(self.dialog_vbox)

        # if user already selected text, put it in self.text_edit
        if self.visible_text:
            if self.selected_is_url:
                self.url_edit.setText(self.visible_text)
                self.text_edit.setFocus()
            else:
                self.text_edit.setText(self.visible_text)
                self.url_edit.setFocus()

    def maybe_enable_ok_button(self):
        if self.url_edit.text() and self.text_edit.text():
            self.pb_ok.setEnabled(True)
        else:
            self.pb_ok.setEnabled(False)

    def reject(self):
        saveGeom(self, "318752047__add_hyperlink")
        QDialog.reject(self)

    def store_hyperlink_and_close(self):
        self.url = self.url_edit.text()
        self.text = self.text_edit.text()
        self.replacement = combine_to_hyperlink(self.url, self.text)        
        saveGeom(self, "318752047__add_hyperlink")
        self.accept()
