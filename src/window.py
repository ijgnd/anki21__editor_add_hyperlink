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
from .helper_functions import escape_html_chars, some_percent_encoding


# size of the dialog windows
DIALOG_SIZE_X = 500
DIALOG_SIZE_Y = 200
MIN_COMBOBOX_WIDTH = 140


class Hyperlink(QDialog):
    def __init__(self, editor, parent_window, selected_text, selected_is_url=False):
        QDialog.__init__(self, parent_window, Qt.Window)
        self.editor_instance = editor
        self.parent_window = parent_window
        self.selected_text = selected_text
        self.selected_is_url = selected_is_url
        self.setWindowTitle("Anki: Create a hyperlink")
        self.resize(DIALOG_SIZE_X, DIALOG_SIZE_Y)
        restoreGeom(self, "318752047__add_hyperlink")

        self.pb_ok = QPushButton("&OK", self)
        self.pb_ok.setEnabled(False)
        self.pb_ok.clicked.connect(lambda: self.insert_anchor(url_edit.text(), urltext_edit.text()))

        self.pb_cancel = QPushButton("&Cancel", self)
        self.pb_cancel.clicked.connect(self.reject)

        url_label = QLabel("Link to:")
        url_edit = QLineEdit()
        url_edit.setPlaceholderText("URL")
        url_edit.textChanged.connect(lambda: self.enable_ok_button(
            self.pb_ok, url_edit.text(), urltext_edit.text()))

        urltext_label = QLabel("Text to display:")
        urltext_edit = QLineEdit()
        urltext_edit.setPlaceholderText("Text")
        urltext_edit.textChanged.connect(lambda: self.enable_ok_button(
            self.pb_ok, url_edit.text(), urltext_edit.text()))

        self.button_bar = QHBoxLayout()
        self.button_bar.addStretch(1)
        self.button_bar.addWidget(self.pb_cancel)
        self.button_bar.addWidget(self.pb_ok)

        self.dialog_vbox = QVBoxLayout()
        self.dialog_vbox.addWidget(url_label)
        self.dialog_vbox.addWidget(url_edit)
        self.dialog_vbox.addWidget(urltext_label)
        self.dialog_vbox.addWidget(urltext_edit)
        self.dialog_vbox.addLayout(self.button_bar)
        self.setLayout(self.dialog_vbox)
        # if user already selected text, put it in urltext_edit
        if self.selected_text:
            if self.selected_is_url:
                url_edit.setText(self.selected_text)
                urltext_edit.setFocus()
            else:
                urltext_edit.setText(self.selected_text)
                url_edit.setFocus()

    @staticmethod
    def enable_ok_button(button, url, text):
        if url and text:
            button.setEnabled(True)
        else:
            button.setEnabled(False)

    @staticmethod
    def combine_to_hyperlink(url, text):
        # Create a hyperlink string, where `url` is the hyperlink reference
        # and `text` the content of the tag.
        text = escape_html_chars(text)
        if gc("encode_illegal_characters_in_links"):
            url = some_percent_encoding(url)
        out = "<a href=\"{0}\">{1}</a>".format(url, text)
        return out

    def reject(self):
        saveGeom(self, "318752047__add_hyperlink")
        QDialog.reject(self)

    def insert_anchor(self, url, text):
        # Inserts a HTML anchor `<a>` into the text field.
        self.replacement = self.combine_to_hyperlink(url, text)
        saveGeom(self, "318752047__add_hyperlink")
        self.accept()
