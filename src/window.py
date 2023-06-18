import json

from aqt.qt import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    Qt,
    qtmajor,
)
from aqt.utils import (
    saveGeom,
    restoreGeom,
)

from .config import gc
from .helper_functions import (
    combine_to_hyperlink,
)

if qtmajor == 5:
    from .forms5 import dialog  # type: ignore  # noqa
else:
    from .forms6 import dialog  # type: ignore  # noqa



class Hyperlink(QDialog):
    def __init__(self, editor, parent_window, selected_visible_text, selected_is_url=False):
        QDialog.__init__(self, parent_window, Qt.WindowType.Window)
        self.editor_instance = editor
        self.parent_window = parent_window
        self.selected_visible_text = selected_visible_text
        self.selected_is_url = selected_is_url
        
        self.dialog = dialog.Ui_Dialog()
        self.dialog.setupUi(self)
        restoreGeom(self, "318752047__add_hyperlink")

        self.dialog.buttonBox.accepted.connect(self.store_hyperlink_and_close)
        self.dialog.buttonBox.rejected.connect(self.reject)

        self.dialog.url_edit.textChanged.connect(self.maybe_enable_ok_button)
        self.dialog.text_edit.textChanged.connect(self.maybe_enable_ok_button)

        self.pb_ok = self.dialog.buttonBox.button(QDialogButtonBox.StandardButton.Ok)
        self.pb_cancel = self.dialog.buttonBox.button(QDialogButtonBox.StandardButton.Cancel)

        if gc("prepend incomplete url default") == "http":
            self.dialog.rb_http.setChecked(True)
        elif gc("prepend incomplete url default") == "https":
            self.dialog.rb_https.setChecked(True)
        else:
            self.dialog.rb_nothing.setChecked(True)

        # if user already selected text, put it in self.dialog.text_edit
        if self.selected_visible_text:
            if self.selected_is_url:
                self.dialog.url_edit.setText(self.selected_visible_text)
                self.dialog.text_edit.setFocus()
            else:
                self.dialog.text_edit.setText(self.selected_visible_text)
                self.dialog.url_edit.setFocus()
        else:
            if gc("guess and auto fill fields in dialog from clipboard"):
                clip_text = QApplication.clipboard().text()
                if clip_text.startswith(("http", "www.")):
                    self.dialog.url_edit.setText(clip_text)
                    self.dialog.text_edit.setFocus()


    def maybe_enable_ok_button(self):
        if self.dialog.url_edit.text() and self.dialog.text_edit.text():
            self.pb_ok.setEnabled(True)
        else:
            self.pb_ok.setEnabled(False)

    def reject(self):
        saveGeom(self, "318752047__add_hyperlink")
        QDialog.reject(self)

    def store_hyperlink_and_close(self):
        self.url = self.dialog.url_edit.text()
        self.text = self.dialog.text_edit.text()
        if not self.url.startswith(("http", "https")):
            if self.dialog.rb_https.isChecked():
                self.url = f"https://{self.url}"
            if self.dialog.rb_http.isChecked():
                self.url = f"http://{self.url}"
        self.replacement = combine_to_hyperlink(self.url, self.text)
        saveGeom(self, "318752047__add_hyperlink")
        self.accept()
